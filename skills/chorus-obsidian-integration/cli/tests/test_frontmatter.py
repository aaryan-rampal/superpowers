"""Frontmatter parse/render and the bind verb (set chorus_doc_id / chorus_watermark)."""

from chorus_obsidian import frontmatter, verbs


def test_parse_absent_frontmatter_keeps_body_and_flags_absent() -> None:
    raw = "# Title\n\nBody.\n"
    fm = frontmatter.parse(raw)
    assert fm.present is False
    assert fm.keys == {}
    assert fm.body == raw


def test_parse_reads_flat_keys() -> None:
    raw = "---\nchorus_doc_id: o0x11rggAEDH\ntitle: My Note\n---\n# Title\n\nBody.\n"
    fm = frontmatter.parse(raw)
    assert fm.present is True
    assert fm.keys["chorus_doc_id"] == "o0x11rggAEDH"
    assert fm.keys["title"] == "My Note"
    assert fm.body == "# Title\n\nBody.\n"


def test_render_round_trips_parsed_frontmatter() -> None:
    raw = "---\nchorus_doc_id: abc\ntitle: My Note\n---\n# Title\n\nBody.\n"
    assert frontmatter.render(frontmatter.parse(raw)) == raw


def test_render_without_keys_drops_the_fence() -> None:
    fm = frontmatter.Frontmatter(keys={}, body="# Title\n\nBody.\n", present=False)
    assert frontmatter.render(fm) == "# Title\n\nBody.\n"


# --- bind verb ----------------------------------------------------------


def test_bind_creates_frontmatter_when_absent() -> None:
    raw = "# Title\n\nBody.\n"
    out = verbs.bind(raw, doc_id="o0x11rggAEDH")
    fm = frontmatter.parse(out)
    assert fm.keys["chorus_doc_id"] == "o0x11rggAEDH"
    assert fm.body == raw


def test_bind_updates_existing_id_and_preserves_other_keys() -> None:
    raw = "---\nchorus_doc_id: old\ntitle: Keep Me\n---\n# Title\n\nBody.\n"
    out = verbs.bind(raw, doc_id="new")
    fm = frontmatter.parse(out)
    assert fm.keys["chorus_doc_id"] == "new"
    assert fm.keys["title"] == "Keep Me"


def test_bind_sets_watermark_when_given() -> None:
    raw = "# Title\n\nBody.\n"
    out = verbs.bind(raw, doc_id="abc", watermark="1783356565478")
    fm = frontmatter.parse(out)
    assert fm.keys["chorus_watermark"] == "1783356565478"


def test_bind_leaves_body_prose_untouched() -> None:
    raw = "---\ntitle: Keep\n---\n# Title\n\nBody with --- dashes.\n"
    out = verbs.bind(raw, doc_id="abc")
    assert frontmatter.parse(out).body == "# Title\n\nBody with --- dashes.\n"
