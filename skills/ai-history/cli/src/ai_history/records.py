"""The normalized record every adapter yields, plus timestamp normalization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class Session:
    """One chat session, normalized across all three stores.

    Attributes:
        tool: Source store — "claude", "meshclaw", or "kiro".
        session_id: The store's native session identifier.
        title: Human-readable label (best-effort per store).
        timestamp: tz-aware UTC datetime for sorting, or None if undeterminable.
        cwd: Working directory the session ran in, if known.
        path: Absolute path to the transcript file on disk.
        snippet: Optional match context (populated by search, not by list).
    """

    tool: str
    session_id: str
    title: str
    timestamp: datetime | None
    cwd: str
    path: str
    snippet: str = ""


def normalize_ts(value: object) -> datetime | None:
    """Coerce a store's timestamp into a tz-aware UTC datetime.

    Handles epoch seconds (int/float), ISO-8601 with a `Z` suffix, tz-aware
    ISO offsets, naive ISO (assumed UTC), and Kiro's 9-digit nanosecond
    fractions (truncated to microseconds). Returns None on anything unparseable.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)
    if not isinstance(value, str):
        return None

    text = value.strip().replace("Z", "+00:00")
    text = _truncate_fraction(text)
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _truncate_fraction(text: str) -> str:
    """Clip sub-second fractions to 6 digits so datetime.fromisoformat accepts them."""
    dot = text.find(".")
    if dot == -1:
        return text
    end = dot + 1
    while end < len(text) and text[end].isdigit():
        end += 1
    frac = text[dot + 1 : end]
    if len(frac) <= 6:
        return text
    return text[:dot] + "." + frac[:6] + text[end:]
