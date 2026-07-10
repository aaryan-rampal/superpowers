"""Cross-store engine: registry, recency-sorted listing, ripgrep-backed search.

Every adapter exposes the same shape — a `ROOT` Path, `discover(root)`, and
`load_session(path)` — so the engine treats all three stores uniformly. Search
uses ripgrep to find files that contain the query (all stores are line-JSON, so
a raw match is reliable), then lets the owning adapter re-parse only the hits.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from ai_history.adapters import claude, kiro, meshclaw
from ai_history.records import Session

ADAPTERS = {"claude": claude, "meshclaw": meshclaw, "kiro": kiro}

_EPOCH = datetime.min.replace(tzinfo=UTC)


def _roots(roots: dict[str, Path] | None) -> dict[str, Path]:
    if roots is not None:
        return roots
    return {name: mod.ROOT for name, mod in ADAPTERS.items()}


def _sort_key(s: Session) -> datetime:
    return s.timestamp or _EPOCH


def list_sessions(
    tools: list[str] | None = None,
    roots: dict[str, Path] | None = None,
) -> list[Session]:
    """Return all sessions across the selected stores, newest first."""
    resolved = _roots(roots)
    selected = tools or list(resolved)
    out: list[Session] = []
    for name in selected:
        mod = ADAPTERS[name]
        root = resolved[name]
        for path in mod.discover(root):
            s = mod.load_session(path)
            if s is not None:
                out.append(s)
    out.sort(key=_sort_key, reverse=True)
    return out


def search(
    query: str,
    tools: list[str] | None = None,
    roots: dict[str, Path] | None = None,
) -> list[Session]:
    """Find sessions whose transcript matches query (case-insensitive), newest first.

    Each result's `snippet` carries the first matching line's context.
    """
    resolved = _roots(roots)
    selected = tools or list(resolved)
    out: list[Session] = []
    for name in selected:
        mod = ADAPTERS[name]
        root = resolved[name]
        for path, snippet in _grep_files(query, mod.discover(root)):
            s = mod.load_session(path)
            if s is not None:
                s.snippet = snippet
                out.append(s)
    out.sort(key=_sort_key, reverse=True)
    return out


def _grep_files(query: str, paths) -> list[tuple[Path, str]]:
    """Yield (path, snippet) for each file containing query. ripgrep if present."""
    files = list(paths)
    if not files:
        return []
    if shutil.which("rg"):
        return _grep_rg(query, files)
    return _grep_python(query, files)


def _grep_rg(query: str, files: list[Path]) -> list[tuple[Path, str]]:
    proc = subprocess.run(
        ["rg", "-i", "-m", "1", "-H", "--no-heading", "-F", query, *map(str, files)],
        capture_output=True,
        text=True,
        check=False,
    )
    hits: list[tuple[Path, str]] = []
    for line in proc.stdout.splitlines():
        path_str, _, matched = line.partition(":")
        hits.append((Path(path_str), _clip(matched, query)))
    return hits


def _grep_python(query: str, files: list[Path]) -> list[tuple[Path, str]]:
    needle = query.lower()
    hits: list[tuple[Path, str]] = []
    for path in files:
        try:
            for line in path.read_text().splitlines():
                if needle in line.lower():
                    hits.append((path, _clip(line, query)))
                    break
        except (OSError, PermissionError):
            continue
    return hits


def _clip(line: str, query: str, width: int = 60) -> str:
    """Return a window of `line` centered on the first case-insensitive match."""
    idx = line.lower().find(query.lower())
    if idx == -1:
        return line.strip()[: width * 2]
    start = max(0, idx - width)
    end = min(len(line), idx + len(query) + width)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(line) else ""
    return prefix + line[start:end].strip() + suffix
