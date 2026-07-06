"""pick: render Chorus doc candidates. Unit tests cover the non-TTY (agent) rendering."""

from chorus_obsidian import verbs

DOCS = [
    {"doc_id": "o0x11rggAEDH", "title": "Ambient insight feedback tool (draft)"},
    {"doc_id": "abc123", "title": "Design notes"},
]


def test_render_list_numbers_docs_and_offers_new_at_top() -> None:
    out = verbs.render_picklist(DOCS)
    lines = out.splitlines()
    assert lines[0] == "0) [create new doc]"
    assert "1) Ambient insight feedback tool (draft)  (o0x11rggAEDH)" in lines[1]
    assert "2) Design notes  (abc123)" in lines[2]


def test_render_list_filters_by_query_case_insensitive() -> None:
    out = verbs.render_picklist(DOCS, query="ambient")
    assert "Ambient insight feedback tool (draft)" in out
    assert "Design notes" not in out


def test_render_list_still_offers_new_when_query_matches_nothing() -> None:
    out = verbs.render_picklist(DOCS, query="nomatch")
    assert out.splitlines()[0] == "0) [create new doc]"
    assert "o0x11rggAEDH" not in out
