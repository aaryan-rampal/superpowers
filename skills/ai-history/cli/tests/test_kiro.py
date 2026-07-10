"""Kiro adapter: parse ~/.kiro/sessions/cli/<uuid>.jsonl (+ paired .json)."""

import json
from pathlib import Path

from ai_history.adapters import kiro


def _cli_session(dir_: Path, uuid: str, *, title=None, prompt="hello") -> Path:
    ts = "2026-06-20T00:05:12.797124666Z"
    meta = {"session_id": uuid, "cwd": "/home/x/work", "created_at": ts}
    if title is not None:
        meta["title"] = title
    (dir_ / f"{uuid}.json").write_text(json.dumps(meta))
    jsonl = dir_ / f"{uuid}.jsonl"
    jsonl.write_text(
        json.dumps(
            {
                "kind": "Prompt",
                "version": "v1",
                "data": {
                    "content": [{"kind": "text", "data": prompt}],
                    "meta": {"timestamp": 1781913916},
                    "message_id": "m1",
                },
            }
        )
        + "\n"
    )
    return jsonl


def test_parses_cli_session_uses_json_metadata(tmp_path: Path) -> None:
    _cli_session(tmp_path, "02e231ba", title="Real Title")
    s = kiro.load_session(tmp_path / "02e231ba.jsonl")
    assert s.tool == "kiro"
    assert s.session_id == "02e231ba"
    assert s.title == "Real Title"
    assert s.cwd == "/home/x/work"
    assert s.timestamp.year == 2026
    assert s.timestamp.microsecond == 797124  # nanoseconds truncated


def test_ignores_boilerplate_title_uses_first_prompt(tmp_path: Path) -> None:
    _cli_session(
        tmp_path,
        "abc",
        title="[SESSION CONTEXT -- background stuff]",
        prompt="how do I deploy the stack",
    )
    s = kiro.load_session(tmp_path / "abc.jsonl")
    assert "deploy the stack" in s.title


def test_null_title_uses_first_prompt(tmp_path: Path) -> None:
    _cli_session(tmp_path, "def", title=None, prompt="real question here")
    s = kiro.load_session(tmp_path / "def.jsonl")
    assert "real question" in s.title


def test_empty_jsonl_returns_none(tmp_path: Path) -> None:
    (tmp_path / "e.json").write_text('{"session_id":"e","created_at":"2026-01-01T00:00:00Z"}')
    (tmp_path / "e.jsonl").write_text("")
    assert kiro.load_session(tmp_path / "e.jsonl") is None


def test_discover_finds_jsonl_ignores_locks_and_task_subdirs(tmp_path: Path) -> None:
    cli = tmp_path / "cli"
    cli.mkdir()
    _cli_session(cli, "s1")
    (cli / "orphan.lock").write_text('{"pid":123}')  # orphan lock, no jsonl
    (cli / "s1").mkdir()
    (cli / "s1" / "tasks").mkdir()
    (cli / "s1" / "tasks" / "1.json").write_text('{"todo":"x"}')  # must not be picked up
    found = list(kiro.discover(cli))
    assert found == [cli / "s1.jsonl"]
