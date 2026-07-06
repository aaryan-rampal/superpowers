"""CLI dispatch: extract, bind, anchor, diff, pick via main(argv)."""

import json

from chorus_obsidian import cli

TANDEM_BLOCK = (
    "```tandem-comments\n"
    '{ "aaaa": { "anchor": {"exact": "the claim", "pos": 0}, "status": "open",'
    ' "thread": [{"author": "Me", "ts": "t", "text": "hi"}] } }\n'
    "```\n"
)


def _run(argv, capsys, stdin=None):
    if stdin is not None:
        import io
        import sys

        sys.stdin = io.StringIO(stdin)
    code = cli.main(argv)
    out = capsys.readouterr().out
    return code, out


def test_extract_prints_prose_without_block(tmp_path, capsys) -> None:
    f = tmp_path / "note.md"
    f.write_text("---\nchorus_doc_id: abc\n---\n# T\n\nBody.\n\n" + TANDEM_BLOCK)
    code, out = _run(["extract", str(f)], capsys)
    assert code == 0
    assert out == "# T\n\nBody.\n"


def test_bind_writes_doc_id_into_frontmatter(tmp_path, capsys) -> None:
    f = tmp_path / "note.md"
    f.write_text("# T\n\nBody.\n")
    code, _ = _run(["bind", str(f), "--doc-id", "o0x11rggAEDH"], capsys)
    assert code == 0
    assert "chorus_doc_id: o0x11rggAEDH" in f.read_text()


def test_bind_writes_watermark_when_given(tmp_path, capsys) -> None:
    f = tmp_path / "note.md"
    f.write_text("# T\n\nBody.\n")
    _run(["bind", str(f), "--doc-id", "abc", "--watermark", "1783356565478"], capsys)
    assert "chorus_watermark: 1783356565478" in f.read_text()


def test_anchor_prints_json_for_match(tmp_path, capsys) -> None:
    f = tmp_path / "note.md"
    f.write_text("# T\n\nSee the claim here.\n")
    code, out = _run(["anchor", str(f), "--quote", "the claim"], capsys)
    assert code == 0
    assert json.loads(out)["exact"] == "the claim"


def test_anchor_prints_ORPHAN_when_absent(tmp_path, capsys) -> None:
    f = tmp_path / "note.md"
    f.write_text("# T\n\nNothing matches.\n")
    code, out = _run(["anchor", str(f), "--quote", "missing quote"], capsys)
    assert code == 0
    assert out.strip() == "ORPHAN"


def test_diff_reads_json_files_and_prints_plan(tmp_path, capsys) -> None:
    tandem = tmp_path / "t.json"
    chorus = tmp_path / "c.json"
    tandem.write_text("{}")
    chorus.write_text(
        json.dumps(
            [
                {
                    "comment_num": 3,
                    "author": "mahinsk",
                    "content": "enforce",
                    "created_at": 1000,
                    "anchor": {"quote": "or skips"},
                    "replies": [],
                }
            ]
        )
    )
    code, out = _run(["diff", "--tandem", str(tandem), "--chorus", str(chorus)], capsys)
    assert code == 0
    plan = json.loads(out)
    assert plan["pull"][0]["chorus_num"] == 3
    assert plan["watermark"] == 1000


def test_pick_prints_numbered_list_non_tty(tmp_path, capsys) -> None:
    docs = tmp_path / "docs.json"
    docs.write_text(json.dumps([{"doc_id": "abc", "title": "Design notes"}]))
    code, out = _run(["pick", "--docs", str(docs)], capsys)
    assert code == 0
    assert out.splitlines()[0] == "0) [create new doc]"
    assert "Design notes" in out
