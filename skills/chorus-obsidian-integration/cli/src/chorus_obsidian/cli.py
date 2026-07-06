"""argparse dispatch for the `co` CLI (chorus-obsidian-integration helper).

Read verbs print to stdout; `bind` rewrites the note atomically. No verb ever calls
Chorus — the agent does that via MCP and feeds JSON in/out of these verbs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from chorus_obsidian import verbs


def _write_atomic(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="co", description="chorus-obsidian helper CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_extract = sub.add_parser("extract", help="print prose without frontmatter or tandem block")
    p_extract.add_argument("file")

    p_bind = sub.add_parser("bind", help="set chorus_doc_id / chorus_watermark in frontmatter")
    p_bind.add_argument("file")
    p_bind.add_argument("--doc-id", required=True)
    p_bind.add_argument("--watermark")

    p_anchor = sub.add_parser("anchor", help="match a Chorus quote to a tandem anchor or ORPHAN")
    p_anchor.add_argument("file")
    p_anchor.add_argument("--quote", required=True)

    p_diff = sub.add_parser("diff", help="compute the sync plan from tandem + chorus JSON")
    p_diff.add_argument("--tandem", required=True, help="path to tandem comment-map JSON")
    p_diff.add_argument("--chorus", required=True, help="path to Chorus comments-search JSON")

    p_pick = sub.add_parser("pick", help="numbered Chorus doc candidates (non-TTY path)")
    p_pick.add_argument("--docs", required=True, help="path to docs JSON [{doc_id,title}]")
    p_pick.add_argument("--query")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "extract":
        print(verbs.extract(Path(args.file).read_text()), end="")
        return 0
    if args.cmd == "bind":
        raw = Path(args.file).read_text()
        bound = verbs.bind(raw, doc_id=args.doc_id, watermark=args.watermark)
        _write_atomic(Path(args.file), bound)
        return 0
    if args.cmd == "anchor":
        prose = verbs.extract(Path(args.file).read_text())
        a = verbs.anchor(prose, args.quote)
        print("ORPHAN" if a is None else json.dumps(a, ensure_ascii=False))
        return 0
    if args.cmd == "diff":
        tandem = json.loads(Path(args.tandem).read_text())
        chorus = json.loads(Path(args.chorus).read_text())
        print(json.dumps(verbs.diff(tandem=tandem, chorus=chorus), ensure_ascii=False))
        return 0
    if args.cmd == "pick":
        docs = json.loads(Path(args.docs).read_text())
        print(verbs.render_picklist(docs, query=args.query))
        return 0

    return 2


def _entry() -> None:
    sys.exit(main())


if __name__ == "__main__":
    _entry()
