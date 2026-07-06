"""Verb logic for the chorus-obsidian helper CLI.

Pure functions over strings/dicts. The CLI layer handles file and stdin/stdout I/O.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from chorus_obsidian import block, frontmatter

_CONTEXT = 20


def _find_span(prose: str, quote: str) -> tuple[int, int] | None:
    """Locate quote in prose. Exact first; then whitespace-tolerant. Returns (start, end)."""
    idx = prose.find(quote)
    if idx >= 0:
        return idx, idx + len(quote)
    pattern = r"\s+".join(re.escape(tok) for tok in quote.split())
    m = re.search(pattern, prose)
    if m:
        return m.start(), m.end()
    return None


def extract(raw: str) -> str:
    """Return the prose to upload to Chorus: no YAML frontmatter, no tandem block."""
    body = frontmatter.parse(raw).body
    return block.parse_document(body).prose


def bind(raw: str, *, doc_id: str, watermark: str | None = None) -> str:
    """Set chorus_doc_id (and optionally chorus_watermark) in the note's frontmatter.

    Creates the frontmatter fence when absent; preserves all other keys and the body.
    """
    fm = frontmatter.parse(raw)
    fm.keys["chorus_doc_id"] = doc_id
    if watermark is not None:
        fm.keys["chorus_watermark"] = watermark
    return frontmatter.render(fm)


def anchor(prose: str, quote: str) -> dict | None:
    """Match a Chorus quote to a tandem anchor against the prose.

    Returns {exact, prefix, suffix, pos} for the first occurrence, or None if the
    quote is not found (an orphaned comment — its anchored text is not in this note).
    """
    span = _find_span(prose, quote)
    if span is None:
        return None
    start, end = span
    return {
        "exact": prose[start:end],
        "prefix": prose[max(0, start - _CONTEXT) : start],
        "suffix": prose[end : end + _CONTEXT],
        "pos": start,
    }


def render_picklist(docs: list[dict], query: str | None = None) -> str:
    """Numbered candidate list for the non-TTY (agent) picker. Index 0 is 'create new'."""
    if query:
        q = query.lower()
        docs = [d for d in docs if q in d["title"].lower()]
    lines = ["0) [create new doc]"]
    for i, d in enumerate(docs, start=1):
        lines.append(f"{i}) {d['title']}  ({d['doc_id']})")
    return "\n".join(lines)


def _iso(created_at: int) -> str:
    return datetime.fromtimestamp(created_at / 1000, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pull_entry(c: dict) -> dict:
    return {
        "author": c["author"],
        "ts": _iso(c["created_at"]),
        "text": c["content"],
        "chorus_num": c["comment_num"],
    }


def _entry_nums(thread: list[dict]) -> set[int]:
    return {e["chorus_num"] for e in thread if "chorus_num" in e}


def _root_index(tandem: dict) -> dict[int, str]:
    """Map a Chorus top-level comment_num to the hex id of its mirrored tandem thread."""
    return {c["chorus_num"]: hid for hid, c in tandem.items() if "chorus_num" in c}


def _pull(tandem: dict, chorus: list[dict], by_root: dict[int, str]) -> tuple[list, list]:
    pull: list[dict] = []
    report: list[dict] = []
    for c in chorus:
        hid = by_root.get(c["comment_num"])
        if hid is None:
            entries = [_pull_entry(c)] + [_pull_entry(r) for r in c.get("replies", [])]
            pull.append(
                {
                    "kind": "new_thread",
                    "chorus_num": c["comment_num"],
                    "quote": (c.get("anchor") or {}).get("quote"),
                    "entries": entries,
                }
            )
            continue
        thread = tandem[hid]["thread"]
        known = _entry_nums(thread)
        fresh = [_pull_entry(r) for r in c.get("replies", []) if r["comment_num"] not in known]
        if not fresh:
            continue
        if tandem[hid].get("status") == "resolved":
            report.extend({"hex_id": hid, "chorus_num": e["chorus_num"]} for e in fresh)
        else:
            pull.append({"kind": "append", "hex_id": hid, "entries": fresh})
    return pull, report


def _push(tandem: dict) -> list[dict]:
    push: list[dict] = []
    for hid, c in tandem.items():
        thread = c.get("thread", [])
        if "chorus_num" not in c:
            push.append(
                {
                    "kind": "new_comment",
                    "hex_id": hid,
                    "quote": c.get("anchor", {}).get("exact"),
                    "entries": thread,
                }
            )
            continue
        fresh = [e for e in thread if "chorus_num" not in e]
        if fresh:
            push.append(
                {"kind": "reply", "hex_id": hid, "chorus_num": c["chorus_num"], "entries": fresh}
            )
    return push


def _resolve(tandem: dict) -> list[dict]:
    return [
        {"hex_id": hid, "chorus_num": c["chorus_num"]}
        for hid, c in tandem.items()
        if c.get("status") == "resolved"
        and "chorus_num" in c
        and not c.get("chorus_resolved")
    ]


def _watermark(chorus: list[dict]) -> int | None:
    stamps = [
        c["created_at"] for c in chorus
    ] + [r["created_at"] for c in chorus for r in c.get("replies", [])]
    return max(stamps) if stamps else None


def diff(*, tandem: dict, chorus: list[dict]) -> dict:
    """Compute the sync plan between a tandem comment map and Chorus comments-search output.

    Returns dict with keys:
      pull    — Chorus->tandem actions (new_thread / append)
      push    — tandem->Chorus actions (new_comment / reply)
      resolve — Obsidian-authoritative resolves to apply in Chorus
      report  — post-resolve Chorus activity, surfaced but not reopened
      watermark — max Chorus created_at seen (epoch ms) or None
    """
    by_root = _root_index(tandem)
    pull, report = _pull(tandem, chorus, by_root)
    return {
        "pull": pull,
        "push": _push(tandem),
        "resolve": _resolve(tandem),
        "report": report,
        "watermark": _watermark(chorus),
    }
