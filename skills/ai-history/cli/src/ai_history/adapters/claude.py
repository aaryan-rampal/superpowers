"""Claude Code adapter.

Store: ~/.claude/projects/<slug>/<uuid>.jsonl, one file per session, where
<slug> is the abs cwd with '/' -> '-'. Lines are discriminated by top-level
`type` (~12 kinds); conversation turns are type in {user, assistant} with a
nested `message` (Anthropic API shape). Session title is a `type=="ai-title"`
record (aiTitle field); fall back to the first user message. `message.content`
may be a plain string or a list of blocks.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path

from ai_history.records import Session, normalize_ts

ROOT = Path(os.path.expanduser("~/.claude/projects"))


def discover(root: Path = ROOT) -> Iterator[Path]:
    """Yield every session transcript under every project subdir of root."""
    if not root.is_dir():
        return
    for p in sorted(root.glob("*/*.jsonl")):
        if p.is_file():
            yield p


def load_session(path: Path) -> Session | None:
    """Parse one transcript into a Session, or None if unreadable/empty."""
    try:
        lines = path.read_text().splitlines()
    except (OSError, PermissionError):
        return None
    if not lines:
        return None

    ai_title = ""
    first_user = ""
    session_id = path.stem
    cwd = ""
    ts = None

    for line in lines:
        obj = _json(line)
        if obj is None:
            continue
        kind = obj.get("type")
        if kind == "ai-title" and not ai_title:
            ai_title = str(obj.get("aiTitle") or "").strip()
        elif kind in ("user", "assistant"):
            session_id = obj.get("sessionId") or session_id
            cwd = cwd or str(obj.get("cwd", ""))
            ts = ts or normalize_ts(obj.get("timestamp"))
            if kind == "user" and not first_user:
                first_user = _extract_text(obj.get("message", {}).get("content"))

    return Session(
        tool="claude",
        session_id=session_id,
        title=ai_title or first_user or path.stem,
        timestamp=ts,
        cwd=cwd,
        path=str(path),
    )


def _json(line: str) -> dict | None:
    try:
        obj = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def _extract_text(content: object) -> str:
    """Pull display text from a message.content that is a string or block list."""
    if isinstance(content, str):
        return content.strip()[:120]
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                return str(block.get("text", "")).strip()[:120]
    return ""
