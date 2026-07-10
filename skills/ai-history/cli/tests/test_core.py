"""core: registry, recency-sorted listing, and ripgrep-backed search across stores."""

import json
from pathlib import Path

from ai_history import core


def _mesh(dir_: Path, name: str, title: str, created: str, body: str) -> None:
    (dir_ / f"{name}.jsonl").write_text(
        json.dumps({"_type": "metadata", "title": title, "created_at": created})
        + "\n"
        + json.dumps({"role": "user", "content": body})
        + "\n"
    )


def test_list_sorts_by_timestamp_descending(tmp_path: Path) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "old", "Old Chat", "2026-01-01T00:00:00", "old body")
    _mesh(root, "new", "New Chat", "2026-06-01T00:00:00", "new body")
    sessions = core.list_sessions(roots={"meshclaw": root})
    assert [s.title for s in sessions] == ["New Chat", "Old Chat"]


def test_list_across_multiple_tools(tmp_path: Path) -> None:
    mesh = tmp_path / "mesh"
    mesh.mkdir()
    _mesh(mesh, "m", "Mesh Chat", "2026-05-01T00:00:00", "hi")
    kiro_dir = tmp_path / "kiro"
    kiro_dir.mkdir()
    (kiro_dir / "k.json").write_text(
        json.dumps({"session_id": "k", "created_at": "2026-04-01T00:00:00Z"})
    )
    (kiro_dir / "k.jsonl").write_text(
        json.dumps(
            {
                "kind": "Prompt",
                "version": "v1",
                "data": {"content": [{"kind": "text", "data": "kiro q"}]},
            }
        )
        + "\n"
    )
    sessions = core.list_sessions(roots={"meshclaw": mesh, "kiro": kiro_dir})
    tools = {s.tool for s in sessions}
    assert tools == {"meshclaw", "kiro"}


def test_search_returns_only_matching_sessions_with_snippet(tmp_path: Path) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "hit", "Hit", "2026-05-01T00:00:00", "the quick brown fox jumps")
    _mesh(root, "miss", "Miss", "2026-05-02T00:00:00", "nothing relevant here")
    results = core.search("brown fox", roots={"meshclaw": root})
    assert len(results) == 1
    assert results[0].title == "Hit"
    assert "brown fox" in results[0].snippet


def test_search_case_insensitive(tmp_path: Path) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "a", "A", "2026-05-01T00:00:00", "Deployment Pipeline Failed")
    results = core.search("deployment pipeline", roots={"meshclaw": root})
    assert len(results) == 1


def test_search_no_matches_returns_empty(tmp_path: Path) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "a", "A", "2026-05-01T00:00:00", "some text")
    assert core.search("zzznotfound", roots={"meshclaw": root}) == []
