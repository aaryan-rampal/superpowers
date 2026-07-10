#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic linter for the writing-at-amazon skill.

Flags the mechanically detectable issues the skill describes: weasel words,
"only with a number" claims that carry no number, "X, not Y" antithesis, and
the common AI stylistic tells. It does NOT judge whether a claim is an
unverified assumption (failure mode 1) — that needs a human or a reviewing
agent.

Output is context-rich and suggestion-free by design: each finding gives the
category, the exact matched span, and the lines before/after so an agent can
locate and rewrite the text itself. No fix is proposed.

Usage:
    uv run check_writing.py DOC.md [DOC2.md ...]
    uv run check_writing.py --json DOC.md
    uv run check_writing.py --context 3 DOC.md
    cat DOC.md | uv run check_writing.py -        # read stdin

Exit code is 1 if any findings, 0 if clean (useful in CI / pre-commit).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

# --- Word lists (from writing-hub-reference.md, the authoritative source) ----

# "Never use" — these add no information; delete or replace.
# leverage/robust are in the SKILL.md list and flagged as double-offense tells.
NEVER_USE = [
    "about", "aim to", "believe", "could", "easy", "effectively", "enable",
    "essentially", "expect", "key", "leverage", "may", "might", "robust",
    "seamless", "seamlessly", "should", "streamline", "strive", "synergy",
    "think", "try", "typically", "utilize", "various", "very", "would",
]

# A few "never use" words are context-dependent: the skill endorses them when
# they honestly mark an unverified belief (failure mode 1). A deterministic
# check can't tell weasel-hedge from honest-hedge, so it flags and says so.
NUANCE_NOTES = {
    "believe": "'believe' is a weasel hedge UNLESS it honestly marks an "
    "unverified claim paired with the step that resolves it (e.g. 'I believe "
    "X, but I haven't confirmed it — that measurement is step one'). Confirm "
    "which case this is.",
    "expect": "'expect' is a weasel hedge unless it marks a genuine, stated "
    "uncertainty; otherwise state what you know flat.",
    "think": "'think' is a weasel hedge unless it honestly marks an opinion "
    "you cannot yet back with evidence.",
}

# "Use only with a number attached" — otherwise a claim with no evidence.
# Flagged only when the same line contains no digit.
NUMBER_REQUIRED = [
    "always", "better", "comprehensive", "efficient", "faster", "few",
    "frequently", "high", "higher", "large", "larger", "many", "most",
    "optimize", "significant", "significantly", "strong", "strongly", "worse",
]

# AI stylistic tells: (label, regex). Case-insensitive unless noted.
AI_TELL_PATTERNS = [
    ("antithesis: 'X, not Y'", re.compile(r",\s+not\s+\w", re.I)),
    ("antithesis: 'not just X but Y'", re.compile(r"\bnot\s+(just|only)\b.*?\b(but|it'?s)\b", re.I)),
    ("Furthermore/Moreover/Additionally chain", re.compile(r"(?:^|(?<=[.!?])\s)(Furthermore|Moreover|Additionally)\b")),
    ("filler lead-in ('It's worth noting', 'Notably')", re.compile(r"\b(it'?s worth noting( that)?|it is worth noting( that)?|it'?s important to|it is important to|notably)\b", re.I)),
    ("hype verb/phrase ('delve', 'underscore', 'testament to')", re.compile(r"\b(delve|delving|underscore[sd]?|testament to|navigat\w* the complexit\w+|in today'?s (landscape|world|fast-paced))\b", re.I)),
    ("hype word ('HUGE', 'game-changer', 'revolutionary')", re.compile(r"\b(huge|game[-\s]?chang\w+|revolutionar\w+|cutting[-\s]?edge|best[-\s]?in[-\s]?class|world[-\s]?class|next[-\s]?level|unlock\w*|supercharg\w+)\b", re.I)),
    ("em-dash (reserve for rare emphasis)", re.compile(r"—")),
    ("exclamation mark", re.compile(r"!")),
    ("emoji", re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002190-\U000021FF⬀-⯿️]")),
]

# Emoji check false-positives on some arrows/symbols used legitimately; keep it
# narrow to the pictographic blocks plus common dingbats.
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U0001F000-\U0001F0FF\U00002600-\U000026FF"
    "\U00002700-\U000027BF\U0001F1E6-\U0001F1FF️]"
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
DIGIT_RE = re.compile(r"\d")
# Short words we ignore when judging Title Case (articles/preps/conjunctions).
TITLE_CASE_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "nor", "for", "of", "to", "in",
    "on", "at", "by", "as", "vs", "with", "from", "into", "per", "via",
}


@dataclass
class Finding:
    file: str
    line: int
    column: int
    category: str
    detail: str
    match: str
    line_content: str
    context_before: list[str]
    context_after: list[str]


def _phrase_regex(phrase: str) -> re.Pattern[str]:
    """Word-boundary, whitespace-flexible, case-insensitive matcher for a phrase."""
    parts = [re.escape(p) for p in phrase.split()]
    body = r"\s+".join(parts)
    return re.compile(rf"\b{body}\b", re.I)


NEVER_USE_RES = [(w, _phrase_regex(w)) for w in NEVER_USE]
NUMBER_REQUIRED_RES = [(w, _phrase_regex(w)) for w in NUMBER_REQUIRED]


def is_title_case_heading(text: str) -> bool:
    """True if a heading capitalizes multiple significant words (Title Case)."""
    words = re.findall(r"[A-Za-z][\w'-]*", text)
    significant = [w for w in words if w.lower() not in TITLE_CASE_STOPWORDS]
    if len(significant) < 2:
        return False
    capped = sum(1 for w in significant if w[0].isupper())
    # All-caps acronyms shouldn't count as "Title Case styling".
    return capped >= 2 and capped >= len(significant) - 1


def scan_line(
    file: str,
    lineno: int,
    line: str,
    all_lines: list[str],
    context: int,
) -> list[Finding]:
    findings: list[Finding] = []
    has_digit = bool(DIGIT_RE.search(line))

    def ctx_before() -> list[str]:
        start = max(0, lineno - 1 - context)
        return [f"{i + 1}: {all_lines[i]}" for i in range(start, lineno - 1)]

    def ctx_after() -> list[str]:
        end = min(len(all_lines), lineno + context)
        return [f"{i + 1}: {all_lines[i]}" for i in range(lineno, end)]

    def add(col: int, category: str, detail: str, match: str) -> None:
        findings.append(
            Finding(
                file=file,
                line=lineno,
                column=col,
                category=category,
                detail=detail,
                match=match,
                line_content=line.rstrip("\n"),
                context_before=ctx_before(),
                context_after=ctx_after(),
            )
        )

    # Weasel: never use.
    for word, rx in NEVER_USE_RES:
        for m in rx.finditer(line):
            detail = NUANCE_NOTES.get(
                word.lower(), f"'{word}' adds no information; delete or replace")
            add(m.start() + 1, "weasel-word (never use)", detail, m.group(0))

    # Weasel: needs a number, and the line has none.
    if not has_digit:
        for word, rx in NUMBER_REQUIRED_RES:
            for m in rx.finditer(line):
                add(m.start() + 1, "weasel-word (needs a number)",
                    f"'{word}' is a claim with no evidence; attach a number or cut",
                    m.group(0))

    # AI tells.
    for label, rx in AI_TELL_PATTERNS:
        if label == "emoji":
            rx = EMOJI_RE
        for m in rx.finditer(line):
            add(m.start() + 1, "ai-tell", label, m.group(0))

    # Title-case heading.
    hm = HEADING_RE.match(line)
    if hm and is_title_case_heading(hm.group(2)):
        add(len(hm.group(1)) + 2, "ai-tell",
            "Title-Case heading; use sentence case", hm.group(2).rstrip())

    # Em-dash bullet lead-in (bullet whose content starts with an em-dash).
    if re.match(r"^\s*[-*+]\s+—", line):
        add(1, "ai-tell", "em-dash bullet lead-in; use a '**Bold label.**' lead-in",
            line.strip())

    return findings


def scan_text(text: str, file: str, context: int, include_code: bool) -> list[Finding]:
    lines = text.splitlines()
    findings: list[Finding] = []
    in_fence = False
    for idx, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence and not include_code:
            continue
        findings.extend(scan_line(file, idx + 1, line, lines, context))
    return findings


def render_text(findings: list[Finding]) -> str:
    if not findings:
        return "No findings.\n"
    out: list[str] = []
    by_cat: dict[str, int] = {}
    for f in findings:
        by_cat[f.category] = by_cat.get(f.category, 0) + 1
    out.append(f"{len(findings)} finding(s):")
    for cat, n in sorted(by_cat.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"  {n:>3}  {cat}")
    out.append("")
    for f in findings:
        out.append(f"{f.file}:{f.line}:{f.column}  [{f.category}]")
        out.append(f"    {f.detail}")
        out.append(f"    match: {f.match!r}")
        for c in f.context_before:
            out.append(f"      {c}")
        out.append(f"  > {f.line}: {f.line_content}")
        for c in f.context_after:
            out.append(f"      {c}")
        out.append("")
    return "\n".join(out) + "\n"


def read_source(arg: str) -> tuple[str, str]:
    if arg == "-":
        return sys.stdin.read(), "<stdin>"
    p = Path(arg)
    return p.read_text(encoding="utf-8"), str(p)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Deterministic writing-at-amazon linter: weasel words, "
        "'X not Y', and AI tells, with surrounding context.",
    )
    ap.add_argument("files", nargs="+", help="Markdown/text files, or '-' for stdin")
    ap.add_argument("--json", action="store_true", help="Emit findings as JSON")
    ap.add_argument("--context", type=int, default=2,
                    help="Lines of context before/after each finding (default 2)")
    ap.add_argument("--include-code", action="store_true",
                    help="Also scan fenced code blocks (default: skip them)")
    args = ap.parse_args()

    all_findings: list[Finding] = []
    for arg in args.files:
        try:
            text, name = read_source(arg)
        except (OSError, UnicodeDecodeError) as e:
            print(f"error reading {arg}: {e}", file=sys.stderr)
            return 2
        all_findings.extend(scan_text(text, name, args.context, args.include_code))

    if args.json:
        print(json.dumps([asdict(f) for f in all_findings], indent=2))
    else:
        sys.stdout.write(render_text(all_findings))

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
