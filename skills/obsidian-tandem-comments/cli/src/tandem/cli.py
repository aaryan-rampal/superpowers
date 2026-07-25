"""argparse dispatch for the `tc` CLI.

Read verbs print to stdout. Write verbs mutate the parsed doc and atomically write it back.
Unknown comment ids raise KeyError, which is surfaced as a non-zero exit without touching
the file (the write only happens after the verb returns successfully).
"""

from __future__ import annotations

import argparse
import json
import sys

from tandem import block, verbs


def _add_file(p: argparse.ArgumentParser) -> None:
    p.add_argument("file", help="path to the Markdown file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tc", description="tandem-comments CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="compact list of comments + watermark")
    _add_file(p_list)
    p_list.add_argument("--all", action="store_true", help="include resolved comments")

    p_since = sub.add_parser("since", help="entries at or after a watermark timestamp")
    _add_file(p_since)
    p_since.add_argument("watermark", help="ISO-8601 timestamp from a prior list/since call")
    p_since.add_argument(
        "--seen", default="", help="comma-separated ids already seen at the boundary"
    )

    p_show = sub.add_parser("show", help="full thread for one comment id")
    _add_file(p_show)
    p_show.add_argument("id")

    p_reply = sub.add_parser("reply", help="append a reply (single or --batch from stdin)")
    _add_file(p_reply)
    p_reply.add_argument("id", nargs="?", help="comment id (omit when using --batch)")
    p_reply.add_argument("--text", help="reply text (single mode)")
    p_reply.add_argument("--batch", action="store_true", help="read [{id,text},...] from stdin")
    p_reply.add_argument("--author", default="Claude")
    p_reply.add_argument("--ts", required=True, help="ISO-8601 timestamp for the reply")

    p_unans = sub.add_parser("unanswered", help="open threads where the user replied last")
    _add_file(p_unans)
    p_unans.add_argument("--user", default="Me", help="the user's author name")

    p_resolve = sub.add_parser("resolve", help="mark a comment resolved")
    _add_file(p_resolve)
    p_resolve.add_argument("id")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    doc = block.read_document(args.file)
    if doc.error:
        print(f"error: {args.file}: {doc.error}", file=sys.stderr)
        return 1

    if args.cmd == "list":
        print(verbs.list_comments(doc, scope="all" if args.all else "open"))
        return 0
    if args.cmd == "since":
        seen = [s for s in args.seen.split(",") if s]
        print(verbs.since(doc, args.watermark, seen_ids=seen))
        return 0
    if args.cmd == "show":
        print(verbs.show(doc, args.id))
        return 0
    if args.cmd == "unanswered":
        print(verbs.unanswered(doc, user_author=args.user))
        return 0

    if args.cmd == "reply":
        if args.batch:
            items = json.loads(sys.stdin.read())
            verbs.reply_batch(doc, items, author=args.author, ts=args.ts)
        else:
            if not args.id or args.text is None:
                print("error: reply requires id and --text (or use --batch)", file=sys.stderr)
                return 2
            verbs.reply(doc, args.id, author=args.author, ts=args.ts, text=args.text)
        block.write_document(args.file, doc)
        return 0
    if args.cmd == "resolve":
        verbs.resolve(doc, args.id)
        block.write_document(args.file, doc)
        return 0

    return 2


def _entry() -> None:
    try:
        sys.exit(main())
    except KeyError as e:
        print(f"error: unknown comment id {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _entry()
