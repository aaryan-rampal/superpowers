"""Minimal YAML frontmatter handling for Obsidian notes.

Only the flat `key: value` subset Obsidian uses for note properties is supported —
no nested structures. Values are treated as strings; the two keys this skill cares
about (`chorus_doc_id`, `chorus_watermark`) are scalars.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FENCE = "---"


@dataclass
class Frontmatter:
    keys: dict[str, str] = field(default_factory=dict)
    body: str = ""
    present: bool = False


def _split(raw: str) -> tuple[str | None, str]:
    """Return (frontmatter_text, body). frontmatter_text is None when absent.

    Frontmatter must open on the very first line with `---` and close at the next
    `---` on its own line.
    """
    if not raw.startswith(FENCE + "\n") and raw != FENCE:
        return None, raw
    rest = raw[len(FENCE) + 1 :]
    close = rest.find("\n" + FENCE)
    if close < 0:
        return None, raw
    fm_text = rest[:close]
    after = rest[close + 1 + len(FENCE) :]
    if after.startswith("\n"):
        after = after[1:]
    return fm_text, after


def parse(raw: str) -> Frontmatter:
    fm_text, body = _split(raw)
    if fm_text is None:
        return Frontmatter(keys={}, body=raw, present=False)
    keys: dict[str, str] = {}
    for line in fm_text.split("\n"):
        if not line.strip() or ":" not in line:
            continue
        k, _, v = line.partition(":")
        keys[k.strip()] = v.strip()
    return Frontmatter(keys=keys, body=body, present=True)


def render(fm: Frontmatter) -> str:
    """Serialize frontmatter + body. Drops the fence entirely when there are no keys."""
    if not fm.keys:
        return fm.body
    lines = [f"{k}: {v}" for k, v in fm.keys.items()]
    return FENCE + "\n" + "\n".join(lines) + "\n" + FENCE + "\n" + fm.body
