"""MeshClaw adapter: parse ~/.meshclaw/sessions/*.jsonl into Session records."""

from pathlib import Path

from ai_history.adapters import meshclaw


def _write(p: Path, lines: list[str]) -> None:
    p.write_text("\n".join(lines) + "\n")


def test_parses_title_and_timestamp_from_metadata_line(tmp_path: Path) -> None:
    f = tmp_path / "dashboard_chat-1-1780694021.jsonl"
    _write(
        f,
        [
            '{"_type":"metadata","created_at":"2026-06-05T21:42:18.150529+00:00",'
            '"title":"My Chat","model":"claude-opus-4.8"}',
            '{"role":"user","content":"hello there","ts":"2026-06-05T21:42:20"}',
        ],
    )
    s = meshclaw.load_session(f)
    assert s.tool == "meshclaw"
    assert s.title == "My Chat"
    assert s.timestamp is not None
    assert s.timestamp.year == 2026
    assert s.path == str(f)


def test_falls_back_to_first_user_message_when_no_title(tmp_path: Path) -> None:
    f = tmp_path / "1781675616.582509.jsonl"
    _write(
        f,
        [
            '{"_type":"metadata","created_at":"2026-06-17T01:53:00"}',
            '{"role":"assistant","content":"hi"}',
            '{"role":"user","content":"what is the meaning of life"}',
        ],
    )
    s = meshclaw.load_session(f)
    assert "meaning of life" in s.title


def test_archive_type_metadata_still_loads(tmp_path: Path) -> None:
    f = tmp_path / "dashboard_chat-1__20260702.jsonl"
    _write(
        f,
        [
            '{"_type":"archive","archived_at":"2026-07-02T21:34:59","reason":"consolidated","count":5}',
            '{"role":"user","content":"archived question"}',
        ],
    )
    s = meshclaw.load_session(f)
    assert s.tool == "meshclaw"
    assert "archived question" in s.title


def test_unreadable_file_returns_none(tmp_path: Path) -> None:
    f = tmp_path / "private.jsonl"
    _write(f, ['{"_type":"metadata","title":"secret"}'])
    f.chmod(0o000)
    try:
        assert meshclaw.load_session(f) is None
    finally:
        f.chmod(0o644)


def test_discover_skips_non_jsonl_and_dirs(tmp_path: Path) -> None:
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    _write(sessions / "a.jsonl", ['{"_type":"metadata","title":"A"}'])
    (sessions / "b.tmp").write_text("junk")
    (sessions / "somedir").mkdir()
    found = list(meshclaw.discover(sessions))
    assert found == [sessions / "a.jsonl"]


def test_empty_file_returns_none(tmp_path: Path) -> None:
    f = tmp_path / "empty.jsonl"
    f.write_text("")
    assert meshclaw.load_session(f) is None
