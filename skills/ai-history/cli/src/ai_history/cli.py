"""ai-history CLI: search | list across Claude Code, MeshClaw, and Kiro history."""

from __future__ import annotations

import argparse
import json
import sys

from ai_history import core
from ai_history.adapters import claude, kiro, meshclaw  # noqa: F401 (patch targets)
from ai_history.records import Session

TOOLS = ("claude", "meshclaw", "kiro", "all")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai-history", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name in ("list", "search"):
        sp = sub.add_parser(name)
        if name == "search":
            sp.add_argument("query")
            sp.add_argument(
                "--semantic",
                action="store_true",
                help="rank by meaning via a local embedding index (needs the [semantic] extra + `index`)",
            )
        sp.add_argument("--tool", choices=TOOLS, default="all")
        sp.add_argument("-n", "--limit", type=int, default=20)
        sp.add_argument("--json", action="store_true", dest="as_json")

    ip = sub.add_parser("index", help="build/refresh the local semantic index (incremental)")
    ip.add_argument("--tool", choices=TOOLS, default="all")

    args = parser.parse_args(argv)
    tools = None if args.tool == "all" else [args.tool]

    if args.cmd == "index":
        from ai_history import semantic

        sessions_n, chunks_n = semantic.build_index(tools=tools)
        print(f"Indexed {sessions_n} sessions ({chunks_n} chunks) → {semantic.CACHE_DIR}")
        return 0

    if args.cmd == "list":
        sessions = core.list_sessions(tools=tools)
    elif args.cmd == "search" and args.semantic:
        from ai_history import semantic

        sessions = semantic.search(args.query, tools=tools)
    else:
        sessions = core.search(args.query, tools=tools)

    sessions = sessions[: args.limit]

    if args.as_json:
        print(json.dumps([_to_dict(s) for s in sessions]))
        return 0

    if not sessions:
        print("No matches." if args.cmd == "search" else "No sessions.")
        return 0

    for s in sessions:
        print(_render(s, show_snippet=args.cmd == "search"))
    return 0


def _to_dict(s: Session) -> dict:
    return {
        "tool": s.tool,
        "session_id": s.session_id,
        "title": s.title,
        "timestamp": s.timestamp.isoformat() if s.timestamp else None,
        "cwd": s.cwd,
        "path": s.path,
        "snippet": s.snippet,
    }


def _render(s: Session, *, show_snippet: bool) -> str:
    when = s.timestamp.strftime("%Y-%m-%d %H:%M") if s.timestamp else "---------------"
    title = " ".join(s.title.split())
    head = f"{when}  {s.tool:<9} {s.session_id[:8]}  {title}"
    if show_snippet and s.snippet:
        return head + f"\n    {' '.join(s.snippet.split())}"
    return head


def _entry() -> None:
    sys.exit(main())


if __name__ == "__main__":
    _entry()
