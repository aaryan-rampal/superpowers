"""MeshClaw adapter.

Store: ~/.meshclaw/sessions/*.jsonl (+ archive/). Line 1 is a metadata object
(`_type` in {metadata, archive}); subsequent lines are messages
(`{role, content, ts}`). Titles live on the metadata line when present, else
fall back to the first user message. ~19% of files are owner-only (skip on
PermissionError); a stray dir and a .tmp file also live in the sessions dir.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path

from ai_history.records import Session, normalize_ts

ROOT = Path(os.path.expanduser("~/.meshclaw/sessions"))


def discover(root: Path = ROOT) -> Iterator[Path]:
    """Yield transcript files under root, skipping non-.jsonl and directories."""
    if not root.is_dir():
        return
    for p in sorted(root.glob("*.jsonl")):
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

    meta = _first_json(lines[0])
    title = ""
    ts = None
    if meta is not None and meta.get("_type") in ("metadata", "archive"):
        title = str(meta.get("title") or "").strip()
        ts = normalize_ts(meta.get("created_at") or meta.get("archived_at"))

    if not title:
        title = _first_user_content(lines)

    return Session(
        tool="meshclaw",
        session_id=path.stem,
        title=title or path.stem,
        timestamp=ts,
        cwd=str(meta.get("project", "")) if meta else "",
        path=str(path),
    )


def iter_texts(path: Path) -> Iterator[str]:
    """Yield full text of each user/assistant message (for embedding, no truncation)."""
    try:
        lines = path.read_text().splitlines()
    except (OSError, PermissionError):
        return
    for line in lines:
        obj = _first_json(line)
        if obj is None or obj.get("role") not in ("user", "assistant"):
            continue
        content = obj.get("content", "")
        if isinstance(content, str) and content.strip():
            yield content.strip()


def _first_json(line: str) -> dict | None:
    try:
        obj = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def _first_user_content(lines: list[str]) -> str:
    for line in lines:
        obj = _first_json(line)
        if obj and obj.get("role") == "user":
            return str(obj.get("content", "")).strip()[:120]
    return ""
