"""Verb behavior: list, since, show, reply, reply --batch, unanswered, resolve."""

import pytest

from tandem import block, verbs

USER_AUTHOR = "Me"
CLAUDE_AUTHOR = "Claude"


def _doc(comments: dict) -> block.ParsedDoc:
    return block.ParsedDoc(prose="The prose body.\n", comments=comments)


def _comment(status="open", thread=None, exact="passage"):
    return {
        "anchor": {"exact": exact, "pos": 4},
        "status": status,
        "thread": thread or [],
    }


def _entry(author, ts, text):
    return {"author": author, "ts": ts, "text": text}


# --- list ---------------------------------------------------------------


def test_list_open_only_by_default() -> None:
    doc = _doc(
        {
            "aaaa": _comment("open", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q")]),
            "bbbb": _comment("resolved", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "done")]),
        }
    )
    out = verbs.list_comments(doc, scope="open")
    assert "aaaa" in out
    assert "bbbb" not in out


def test_list_all_includes_resolved() -> None:
    doc = _doc(
        {
            "aaaa": _comment("open", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q")]),
            "bbbb": _comment("resolved", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "done")]),
        }
    )
    out = verbs.list_comments(doc, scope="all")
    assert "aaaa" in out and "bbbb" in out


def test_list_emits_watermark_from_max_entry_ts() -> None:
    doc = _doc(
        {
            "aaaa": _comment(
                "open",
                [
                    _entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q"),
                    _entry(CLAUDE_AUTHOR, "2026-06-30T20:47:12Z", "a"),
                ],
            ),
        }
    )
    out = verbs.list_comments(doc, scope="open")
    assert "watermark: 2026-06-30T20:47:12Z" in out


# --- since --------------------------------------------------------------


def test_since_returns_only_entries_after_watermark() -> None:
    doc = _doc(
        {
            "aaaa": _comment(
                "open",
                [
                    _entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "old"),
                    _entry(USER_AUTHOR, "2026-06-30T19:00:00Z", "new question"),
                ],
            ),
        }
    )
    out = verbs.since(doc, "2026-06-30T18:00:00Z")
    assert "new question" in out
    assert "old" not in out


def test_since_is_boundary_inclusive_to_avoid_missing_same_ts() -> None:
    # Two entries share the exact same ts; a strict > would skip the second.
    doc = _doc(
        {
            "aaaa": _comment("open", [_entry(USER_AUTHOR, "2026-06-30T18:00:00Z", "first")]),
            "bbbb": _comment("open", [_entry(USER_AUTHOR, "2026-06-30T18:00:00Z", "second")]),
        }
    )
    out = verbs.since(doc, "2026-06-30T18:00:00Z", seen_ids=["aaaa"])
    assert "second" in out
    assert "first" not in out  # already seen


def test_since_emits_new_watermark() -> None:
    doc = _doc({"aaaa": _comment("open", [_entry(USER_AUTHOR, "2026-06-30T19:30:00Z", "x")])})
    out = verbs.since(doc, "2026-06-30T18:00:00Z")
    assert "watermark: 2026-06-30T19:30:00Z" in out


# --- show ---------------------------------------------------------------


def test_show_renders_full_thread_for_one_id() -> None:
    doc = _doc(
        {
            "aaaa": _comment(
                "open",
                [
                    _entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "the question"),
                    _entry(CLAUDE_AUTHOR, "2026-01-02T00:00:00Z", "the answer"),
                ],
            ),
        }
    )
    out = verbs.show(doc, "aaaa")
    assert "the question" in out and "the answer" in out


def test_show_unknown_id_raises() -> None:
    doc = _doc({"aaaa": _comment()})
    with pytest.raises(KeyError):
        verbs.show(doc, "zzzz")


# --- reply --------------------------------------------------------------


def test_reply_appends_entry_to_thread() -> None:
    doc = _doc({"aaaa": _comment("open", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q")])})
    verbs.reply(doc, "aaaa", author=CLAUDE_AUTHOR, ts="2026-06-30T20:00:00Z", text="my answer")
    thread = doc.comments["aaaa"]["thread"]
    assert len(thread) == 2
    assert thread[-1] == _entry(CLAUDE_AUTHOR, "2026-06-30T20:00:00Z", "my answer")


def test_reply_unknown_id_raises() -> None:
    doc = _doc({"aaaa": _comment()})
    with pytest.raises(KeyError):
        verbs.reply(doc, "zzzz", author=CLAUDE_AUTHOR, ts="t", text="x")


def test_reply_batch_appends_to_multiple_threads() -> None:
    doc = _doc(
        {
            "aaaa": _comment("open", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q1")]),
            "bbbb": _comment("open", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q2")]),
        }
    )
    items = [
        {"id": "aaaa", "text": "answer 1"},
        {"id": "bbbb", "text": "answer 2"},
    ]
    verbs.reply_batch(doc, items, author=CLAUDE_AUTHOR, ts="2026-06-30T20:00:00Z")
    assert doc.comments["aaaa"]["thread"][-1]["text"] == "answer 1"
    assert doc.comments["bbbb"]["thread"][-1]["text"] == "answer 2"


def test_reply_batch_unknown_id_raises_before_any_write() -> None:
    doc = _doc({"aaaa": _comment("open", [_entry(USER_AUTHOR, "t", "q")])})
    items = [{"id": "aaaa", "text": "ok"}, {"id": "zzzz", "text": "bad"}]
    with pytest.raises(KeyError):
        verbs.reply_batch(doc, items, author=CLAUDE_AUTHOR, ts="t")
    # all-or-nothing: aaaa must NOT have been mutated
    assert len(doc.comments["aaaa"]["thread"]) == 1


# --- unanswered ---------------------------------------------------------


def test_unanswered_lists_open_threads_where_user_is_last() -> None:
    doc = _doc(
        {
            "aaaa": _comment(
                "open",
                [
                    _entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q"),
                    _entry(USER_AUTHOR, "2026-01-02T00:00:00Z", "follow up"),
                ],
            ),
            "bbbb": _comment(
                "open",
                [
                    _entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q"),
                    _entry(CLAUDE_AUTHOR, "2026-01-02T00:00:00Z", "answered"),
                ],
            ),
        }
    )
    out = verbs.unanswered(doc, user_author=USER_AUTHOR)
    assert "aaaa" in out
    assert "bbbb" not in out


def test_unanswered_ignores_resolved_threads() -> None:
    doc = _doc(
        {
            "aaaa": _comment("resolved", [_entry(USER_AUTHOR, "2026-01-01T00:00:00Z", "q")]),
        }
    )
    out = verbs.unanswered(doc, user_author=USER_AUTHOR)
    assert "aaaa" not in out


# --- resolve ------------------------------------------------------------


def test_resolve_flips_status() -> None:
    doc = _doc({"aaaa": _comment("open")})
    verbs.resolve(doc, "aaaa")
    assert doc.comments["aaaa"]["status"] == "resolved"


def test_resolve_unknown_id_raises() -> None:
    doc = _doc({"aaaa": _comment()})
    with pytest.raises(KeyError):
        verbs.resolve(doc, "zzzz")
