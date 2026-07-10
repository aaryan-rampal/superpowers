"""CLI: argument parsing and human/JSON rendering over the core engine."""

import json
from pathlib import Path

from ai_history import cli


def _mesh(dir_: Path, name: str, title: str, created: str, body: str) -> None:
    (dir_ / f"{name}.jsonl").write_text(
        json.dumps({"_type": "metadata", "title": title, "created_at": created})
        + "\n"
        + json.dumps({"role": "user", "content": body})
        + "\n"
    )


def test_list_renders_titles(tmp_path, capsys, monkeypatch) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "a", "Alpha Chat", "2026-05-01T00:00:00", "hi")
    monkeypatch.setattr(cli.meshclaw, "ROOT", root)
    rc = cli.main(["list", "--tool", "meshclaw"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Alpha Chat" in out
    assert "meshclaw" in out


def test_search_renders_snippet(tmp_path, capsys, monkeypatch) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "a", "Alpha", "2026-05-01T00:00:00", "the deploy pipeline broke today")
    monkeypatch.setattr(cli.meshclaw, "ROOT", root)
    rc = cli.main(["search", "deploy pipeline", "--tool", "meshclaw"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "deploy pipeline" in out


def test_json_output_is_machine_readable(tmp_path, capsys, monkeypatch) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "a", "Alpha", "2026-05-01T00:00:00", "hi")
    monkeypatch.setattr(cli.meshclaw, "ROOT", root)
    rc = cli.main(["list", "--tool", "meshclaw", "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data[0]["title"] == "Alpha"
    assert data[0]["tool"] == "meshclaw"


def test_search_no_results_exits_zero(tmp_path, capsys, monkeypatch) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "a", "Alpha", "2026-05-01T00:00:00", "hi")
    monkeypatch.setattr(cli.meshclaw, "ROOT", root)
    rc = cli.main(["search", "zzznotfound", "--tool", "meshclaw"])
    assert rc == 0
    assert "No matches" in capsys.readouterr().out


def test_render_collapses_multiline_title_to_one_line(tmp_path, capsys, monkeypatch) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    _mesh(root, "a", "First line\nsecond line\tthird", "2026-05-01T00:00:00", "hi")
    monkeypatch.setattr(cli.meshclaw, "ROOT", root)
    rc = cli.main(["list", "--tool", "meshclaw"])
    out = capsys.readouterr().out
    assert rc == 0
    # exactly one output line for the session (no wrapping from embedded newlines)
    assert len([ln for ln in out.splitlines() if ln.strip()]) == 1
    assert "First line second line third" in out


def test_limit_flag_truncates(tmp_path, capsys, monkeypatch) -> None:
    root = tmp_path / "sessions"
    root.mkdir()
    for i in range(5):
        _mesh(root, f"s{i}", f"Chat {i}", f"2026-05-0{i + 1}T00:00:00", "hi")
    monkeypatch.setattr(cli.meshclaw, "ROOT", root)
    rc = cli.main(["list", "--tool", "meshclaw", "-n", "2", "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert len(json.loads(out)) == 2
