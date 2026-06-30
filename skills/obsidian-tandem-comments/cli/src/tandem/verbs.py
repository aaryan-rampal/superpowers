"""Verb logic over a ParsedDoc. Read verbs return compact text; write verbs mutate in place.

These functions are pure with respect to the filesystem: the CLI layer reads the doc,
calls a verb, and (for writes) atomically writes the doc back.
"""

from __future__ import annotations

from collections.abc import Iterable

from tandem.block import ParsedDoc

_MAX_EXCERPT = 50


def _excerpt(comment: dict) -> str:
    exact = comment.get("anchor", {}).get("exact", "")
    flat = " ".join(exact.split())
    if len(flat) > _MAX_EXCERPT:
        flat = flat[: _MAX_EXCERPT - 1] + "…"
    return flat


def _last(comment: dict) -> dict | None:
    thread = comment.get("thread", [])
    return thread[-1] if thread else None


def _max_ts(comments: dict) -> str | None:
    timestamps = [e["ts"] for c in comments.values() for e in c.get("thread", [])]
    return max(timestamps) if timestamps else None


def _watermark_line(comments: dict) -> str:
    ts = _max_ts(comments)
    return f"watermark: {ts}" if ts else "watermark: (none)"


def list_comments(doc: ParsedDoc, scope: str = "open") -> str:
    lines: list[str] = []
    for cid, c in doc.comments.items():
        if scope == "open" and c.get("status") != "open":
            continue
        last = _last(c)
        n = len(c.get("thread", []))
        tail = f"{n} repl{'y' if n == 1 else 'ies'}"
        last_author = last["author"] if last else "-"
        lines.append(f'[{cid}] {c.get("status")} "{_excerpt(c)}" {tail}, last: {last_author}')
    if not lines:
        lines.append("(no comments)")
    lines.append(_watermark_line(doc.comments))
    return "\n".join(lines)


def since(doc: ParsedDoc, watermark: str, seen_ids: Iterable[str] | None = None) -> str:
    """Return entries with ts >= watermark, excluding threads in seen_ids.

    Boundary-inclusive (>=) plus seen_ids de-dup: same-second entries are never skipped,
    but entries already seen at the boundary are filtered out by id.
    """
    seen = set(seen_ids or [])
    lines: list[str] = []
    for cid, c in doc.comments.items():
        if cid in seen:
            continue
        fresh = [e for e in c.get("thread", []) if e["ts"] >= watermark]
        if not fresh:
            continue
        lines.append(f'[{cid}] {c.get("status")} "{_excerpt(c)}"')
        for e in fresh:
            lines.append(f"  {e['author']} @ {e['ts']}: {e['text']}")
    if not lines:
        lines.append("(nothing new)")
    lines.append(_watermark_line(doc.comments))
    return "\n".join(lines)


def show(doc: ParsedDoc, comment_id: str) -> str:
    c = doc.comments[comment_id]
    lines = [f'[{comment_id}] {c.get("status")} "{_excerpt(c)}"']
    for e in c.get("thread", []):
        lines.append(f"  {e['author']} @ {e['ts']}: {e['text']}")
    return "\n".join(lines)


def reply(doc: ParsedDoc, comment_id: str, *, author: str, ts: str, text: str) -> None:
    c = doc.comments[comment_id]
    c["thread"].append({"author": author, "ts": ts, "text": text})


def reply_batch(doc: ParsedDoc, items: list[dict], *, author: str, ts: str) -> None:
    """Append a reply to each (id, text) item. All-or-nothing: validate ids first."""
    for item in items:
        if item["id"] not in doc.comments:
            raise KeyError(item["id"])
    for item in items:
        reply(doc, item["id"], author=author, ts=ts, text=item["text"])


def unanswered(doc: ParsedDoc, *, user_author: str) -> str:
    lines: list[str] = []
    for cid, c in doc.comments.items():
        if c.get("status") != "open":
            continue
        last = _last(c)
        if last is not None and last["author"] == user_author:
            lines.append(f'[{cid}] "{_excerpt(c)}" last: {last["author"]}')
    if not lines:
        lines.append("(none — every open thread has a reply after you)")
    return "\n".join(lines)


def resolve(doc: ParsedDoc, comment_id: str) -> None:
    doc.comments[comment_id]["status"] = "resolved"
