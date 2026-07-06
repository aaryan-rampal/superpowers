"""diff: the dedup engine. Computes pull / push / resolve / report sets.

Cross-reference stamps:
- a mirrored tandem comment dict carries `chorus_num` (its Chorus top-level comment)
- a mirrored tandem thread entry carries `chorus_num` (its Chorus reply)
Dedup correctness rests on the set of known `chorus_num`s, so re-runs never duplicate.
"""

from chorus_obsidian import verbs


def _c_comment(num, author, content, created_at, quote=None, replies=None, resolved=False):
    """A Chorus comments-search top-level comment."""
    return {
        "comment_num": num,
        "author": author,
        "content": content,
        "created_at": created_at,
        "anchor": {"quote": quote} if quote else None,
        "replies": replies or [],
        "resolved": resolved,
    }


def _c_reply(num, author, content, created_at, parent_num):
    return {
        "comment_num": num,
        "author": author,
        "content": content,
        "created_at": created_at,
        "parent_num": parent_num,
    }


def _t_comment(status="open", thread=None, exact="passage", chorus_num=None):
    c = {"anchor": {"exact": exact, "pos": 0}, "status": status, "thread": thread or []}
    if chorus_num is not None:
        c["chorus_num"] = chorus_num
    return c


def _t_entry(author, ts, text, chorus_num=None):
    e = {"author": author, "ts": ts, "text": text}
    if chorus_num is not None:
        e["chorus_num"] = chorus_num
    return e


# --- pull: Chorus -> tandem ---------------------------------------------


def test_pull_new_chorus_comment_becomes_new_thread() -> None:
    chorus = [_c_comment(3, "mahinsk", "enforce answering", 1000, quote="or skips")]
    out = verbs.diff(tandem={}, chorus=chorus)
    assert len(out["pull"]) == 1
    action = out["pull"][0]
    assert action["kind"] == "new_thread"
    assert action["chorus_num"] == 3
    assert action["quote"] == "or skips"
    assert action["entries"][0]["text"] == "enforce answering"
    assert action["entries"][0]["chorus_num"] == 3


def test_pull_carries_replies_of_a_new_thread() -> None:
    chorus = [
        _c_comment(
            2, "aarampal", "stretch goal", 1000, quote="ExportSink",
            replies=[_c_reply(7, "mahinsk", "write to 2PR bucket", 1100, parent_num=2)],
        )
    ]
    out = verbs.diff(tandem={}, chorus=chorus)
    action = out["pull"][0]
    assert action["kind"] == "new_thread"
    assert [e["text"] for e in action["entries"]] == ["stretch goal", "write to 2PR bucket"]
    assert [e["chorus_num"] for e in action["entries"]] == [2, 7]


def test_pull_new_reply_appends_to_already_mirrored_thread() -> None:
    tandem = {
        "aaaa": _t_comment(
            thread=[_t_entry("aarampal", "2026-01-01T00:00:00Z", "stretch goal", chorus_num=2)],
            chorus_num=2,
        )
    }
    chorus = [
        _c_comment(
            2, "aarampal", "stretch goal", 1000, quote="ExportSink",
            replies=[_c_reply(7, "mahinsk", "later reply", 1100, parent_num=2)],
        )
    ]
    out = verbs.diff(tandem=tandem, chorus=chorus)
    assert len(out["pull"]) == 1
    action = out["pull"][0]
    assert action["kind"] == "append"
    assert action["hex_id"] == "aaaa"
    assert action["entries"][0]["text"] == "later reply"
    assert action["entries"][0]["chorus_num"] == 7


def test_pull_is_empty_on_rerun_when_everything_mirrored() -> None:
    tandem = {
        "aaaa": _t_comment(
            thread=[_t_entry("mahinsk", "2026-01-01T00:00:00Z", "enforce answering", chorus_num=3)],
            chorus_num=3,
        )
    }
    chorus = [_c_comment(3, "mahinsk", "enforce answering", 1000, quote="or skips")]
    out = verbs.diff(tandem=tandem, chorus=chorus)
    assert out["pull"] == []


# --- push: tandem -> Chorus ---------------------------------------------


def test_push_new_obsidian_thread_becomes_new_comment() -> None:
    tandem = {
        "aaaa": _t_comment(
            exact="the claim",
            thread=[_t_entry("Me", "2026-01-01T00:00:00Z", "I disagree")],
        )
    }
    out = verbs.diff(tandem=tandem, chorus=[])
    assert len(out["push"]) == 1
    action = out["push"][0]
    assert action["kind"] == "new_comment"
    assert action["hex_id"] == "aaaa"
    assert action["quote"] == "the claim"
    assert action["entries"][0]["text"] == "I disagree"


def test_push_new_obsidian_reply_on_mirrored_thread() -> None:
    tandem = {
        "aaaa": _t_comment(
            thread=[
                _t_entry("mahinsk", "2026-01-01T00:00:00Z", "enforce answering", chorus_num=3),
                _t_entry("Me", "2026-01-02T00:00:00Z", "good point"),
            ],
            chorus_num=3,
        )
    }
    out = verbs.diff(tandem=tandem, chorus=[_c_comment(3, "mahinsk", "enforce answering", 1000)])
    assert len(out["push"]) == 1
    action = out["push"][0]
    assert action["kind"] == "reply"
    assert action["chorus_num"] == 3
    assert action["entries"][0]["text"] == "good point"


def test_push_empty_when_all_entries_have_chorus_num() -> None:
    tandem = {
        "aaaa": _t_comment(
            thread=[_t_entry("mahinsk", "2026-01-01T00:00:00Z", "enforce answering", chorus_num=3)],
            chorus_num=3,
        )
    }
    out = verbs.diff(tandem=tandem, chorus=[_c_comment(3, "mahinsk", "enforce answering", 1000)])
    assert out["push"] == []


# --- resolve: Obsidian -> Chorus only -----------------------------------


def test_resolve_lists_resolved_mirrored_threads() -> None:
    tandem = {
        "aaaa": _t_comment(
            status="resolved",
            thread=[_t_entry("mahinsk", "2026-01-01T00:00:00Z", "done", chorus_num=3)],
            chorus_num=3,
        )
    }
    out = verbs.diff(tandem=tandem, chorus=[_c_comment(3, "mahinsk", "done", 1000)])
    assert out["resolve"] == [{"hex_id": "aaaa", "chorus_num": 3}]


def test_resolve_skips_already_pushed() -> None:
    tandem = {
        "aaaa": {
            "anchor": {"exact": "x", "pos": 0},
            "status": "resolved",
            "chorus_num": 3,
            "chorus_resolved": True,
            "thread": [_t_entry("mahinsk", "2026-01-01T00:00:00Z", "done", chorus_num=3)],
        }
    }
    out = verbs.diff(tandem=tandem, chorus=[_c_comment(3, "mahinsk", "done", 1000)])
    assert out["resolve"] == []


def test_resolve_skips_unmirrored_thread() -> None:
    # A resolved obsidian-only thread has nothing to resolve in Chorus yet.
    tandem = {"aaaa": _t_comment(status="resolved", thread=[_t_entry("Me", "t", "done")])}
    out = verbs.diff(tandem=tandem, chorus=[])
    assert out["resolve"] == []


# --- report: post-resolve Chorus activity is not reopened ---------------


def test_post_resolve_chorus_reply_is_reported_not_pulled() -> None:
    tandem = {
        "aaaa": _t_comment(
            status="resolved",
            thread=[_t_entry("mahinsk", "2026-01-01T00:00:00Z", "done", chorus_num=3)],
            chorus_num=3,
        )
    }
    chorus = [
        _c_comment(
            3, "mahinsk", "done", 1000, resolved=False,
            replies=[_c_reply(9, "mahinsk", "actually wait", 1200, parent_num=3)],
        )
    ]
    out = verbs.diff(tandem=tandem, chorus=chorus)
    # not pulled into the resolved thread
    assert out["pull"] == []
    # surfaced in the report instead
    assert len(out["report"]) == 1
    assert out["report"][0]["chorus_num"] == 9
    assert out["report"][0]["hex_id"] == "aaaa"


# --- watermark ----------------------------------------------------------


def test_diff_reports_new_watermark_as_max_created_at() -> None:
    chorus = [
        _c_comment(1, "a", "x", 1000),
        _c_comment(2, "b", "y", 3000, replies=[_c_reply(5, "c", "z", 5000, parent_num=2)]),
    ]
    out = verbs.diff(tandem={}, chorus=chorus)
    assert out["watermark"] == 5000
