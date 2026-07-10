"""Kiro adapter.

Store: ~/.kiro/sessions/cli/<uuid>.jsonl paired with <uuid>.json metadata.
Transcript lines are `{kind, version, data}` with kind in
{Prompt, AssistantMessage, ToolResults}; content lives in `data.content[]`.
The `.json` title is unreliable (truncated raw prompt / boilerplate / null),
so a boilerplate-looking title falls back to the first Prompt's text. Key off
.jsonl existence, not .lock (orphan locks exist); guard empty transcripts;
skip <uuid>/tasks/*.json subdirs.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path

from ai_history.records import Session, normalize_ts

ROOT = Path(os.path.expanduser("~/.kiro/sessions/cli"))


def discover(root: Path = ROOT) -> Iterator[Path]:
    """Yield <uuid>.jsonl transcripts directly under root (not task subdirs)."""
    if not root.is_dir():
        return
    for p in sorted(root.glob("*.jsonl")):
        if p.is_file():
            yield p


def load_session(path: Path) -> Session | None:
    """Parse one cli transcript + its paired .json into a Session, or None."""
    try:
        lines = path.read_text().splitlines()
    except (OSError, PermissionError):
        return None
    if not lines:
        return None

    meta = _load_meta(path.with_suffix(".json"))
    raw_title = str(meta.get("title") or "").strip()
    title = raw_title if _is_usable_title(raw_title) else ""
    if not title:
        title = _first_prompt_text(lines)

    return Session(
        tool="kiro",
        session_id=meta.get("session_id") or path.stem,
        title=title or path.stem,
        timestamp=normalize_ts(meta.get("created_at")),
        cwd=str(meta.get("cwd", "")),
        path=str(path),
    )


def _load_meta(json_path: Path) -> dict:
    try:
        obj = json.loads(json_path.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def _is_usable_title(title: str) -> bool:
    """Reject boilerplate titles Kiro stamps from a raw system/context prompt."""
    return bool(title) and not title.startswith("[")


def _first_prompt_text(lines: list[str]) -> str:
    for line in lines:
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(obj, dict) or obj.get("kind") != "Prompt":
            continue
        for item in obj.get("data", {}).get("content", []):
            if isinstance(item, dict) and item.get("kind") == "text":
                return str(item.get("data", "")).strip()[:120]
    return ""
