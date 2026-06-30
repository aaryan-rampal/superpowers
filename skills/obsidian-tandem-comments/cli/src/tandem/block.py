"""Parse and serialize the ```tandem-comments fenced JSON block.

Mirrors the plugin's store.ts so the CLI's writes are byte-identical to what the
Obsidian plugin produces. A parity test against real plugin-written fixtures guards
against drift.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

CommentMap = dict[str, dict]

FENCE_OPEN = "```tandem-comments"
SCHEMA_HINT_LINES = [
    '// Schema: { "<id>": { anchor:{exact,prefix,suffix,pos?}, status:open|resolved, '
    "thread:[{author,ts,text}] } }",
    '// Anchor = quote from the prose. To locate: search for "exact", disambiguate via '
    "prefix/suffix.",
]


@dataclass
class ParsedDoc:
    prose: str
    comments: CommentMap
    error: str | None = None


def _find_block(raw: str) -> tuple[int, str] | None:
    """Return (prose_end, body) for the trailing tandem block, or None.

    The block must be the last content of the file (only whitespace after it).
    """
    idx = raw.rfind("\n" + FENCE_OPEN + "\n")
    if idx >= 0:
        prose_end = idx
        body_start = idx + len(FENCE_OPEN) + 2
    elif raw.startswith(FENCE_OPEN + "\n"):
        prose_end = 0
        body_start = len(FENCE_OPEN) + 1
    else:
        return None
    rest = raw[body_start:]
    close_idx = rest.rfind("\n```")
    if close_idx < 0:
        return None
    if rest[close_idx + 4 :].strip() != "":
        return None
    return prose_end, rest[:close_idx]


def _parse_block_body(body: str) -> CommentMap:
    lines = body.split("\n")
    i = 0
    while i < len(lines) and (lines[i].startswith("//") or lines[i].strip() == ""):
        i += 1
    data = json.loads("\n".join(lines[i:]))
    if not isinstance(data, dict):
        raise ValueError("tandem-comments: top level must be an object")
    return data


def parse_document(raw: str) -> ParsedDoc:
    blk = _find_block(raw)
    if blk is None:
        return ParsedDoc(prose=raw, comments={})
    prose_end, body = blk
    try:
        comments = _parse_block_body(body)
    except (json.JSONDecodeError, ValueError) as e:
        return ParsedDoc(prose=raw, comments={}, error=str(e))
    return ParsedDoc(prose=raw[:prose_end], comments=comments)


def serialize_document(doc: ParsedDoc) -> str:
    if doc.error:
        raise ValueError("refusing to serialize a document with a parse error: " + doc.error)
    if not doc.comments:
        return doc.prose
    hint = "\n".join(SCHEMA_HINT_LINES) + "\n"
    body = json.dumps(doc.comments, indent=2, ensure_ascii=False)
    return doc.prose + "\n" + FENCE_OPEN + "\n" + hint + body + "\n```\n"


def read_document(path: str | Path) -> ParsedDoc:
    return parse_document(Path(path).read_text())


def write_document(path: str | Path, doc: ParsedDoc) -> None:
    """Atomically write the document: serialize to a temp file, then os.replace.

    Atomic replace closes the read-then-edit window that causes Obsidian's
    "file modified since read" failures during multi-comment batches.
    """
    path = Path(path)
    text = serialize_document(doc)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
