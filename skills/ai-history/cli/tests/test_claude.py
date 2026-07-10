"""Claude Code adapter: parse ~/.claude/projects/<slug>/<uuid>.jsonl."""

import json
from pathlib import Path

from ai_history.adapters import claude


def _line(obj: dict) -> str:
    return json.dumps(obj)


def test_uses_ai_title_record_when_present(tmp_path: Path) -> None:
    f = tmp_path / "sess.jsonl"
    f.write_text(
        "\n".join(
            [
                _line(
                    {
                        "type": "user",
                        "sessionId": "s1",
                        "cwd": "/w",
                        "timestamp": "2026-07-01T12:00:00.000Z",
                        "message": {"role": "user", "content": "first prompt"},
                    }
                ),
                _line({"type": "ai-title", "aiTitle": "Curated Title", "sessionId": "s1"}),
            ]
        )
        + "\n"
    )
    s = claude.load_session(f)
    assert s.tool == "claude"
    assert s.session_id == "s1"
    assert s.title == "Curated Title"
    assert s.cwd == "/w"
    assert s.timestamp.year == 2026


def test_falls_back_to_first_user_message(tmp_path: Path) -> None:
    f = tmp_path / "s.jsonl"
    f.write_text(
        _line(
            {
                "type": "user",
                "sessionId": "s2",
                "cwd": "/w",
                "timestamp": "2026-07-01T12:00:00Z",
                "message": {"role": "user", "content": "how do I reset the stack"},
            }
        )
        + "\n"
    )
    s = claude.load_session(f)
    assert "reset the stack" in s.title


def test_string_and_block_content_both_handled(tmp_path: Path) -> None:
    # user content can be a plain string OR a list of blocks.
    f = tmp_path / "s.jsonl"
    f.write_text(
        _line(
            {
                "type": "user",
                "sessionId": "s3",
                "cwd": "/w",
                "timestamp": "2026-07-01T12:00:00Z",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "block-style prompt"}],
                },
            }
        )
        + "\n"
    )
    s = claude.load_session(f)
    assert "block-style prompt" in s.title


def test_empty_file_returns_none(tmp_path: Path) -> None:
    f = tmp_path / "empty.jsonl"
    f.write_text("")
    assert claude.load_session(f) is None


def test_discover_walks_project_subdirs(tmp_path: Path) -> None:
    proj = tmp_path / "-w-proj"
    proj.mkdir()
    (proj / "a.jsonl").write_text(
        _line({"type": "user", "sessionId": "a", "message": {"role": "user", "content": "x"}})
        + "\n"
    )
    found = list(claude.discover(tmp_path))
    assert found == [proj / "a.jsonl"]
