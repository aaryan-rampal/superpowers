"""extract: prose suitable for upload — no tandem block, no YAML frontmatter."""

from chorus_obsidian import verbs

TANDEM_BLOCK = (
    "```tandem-comments\n"
    '// Schema: {...}\n'
    '{ "aaaa": { "anchor": {"exact": "x", "pos": 0}, "status": "open", "thread": [] } }\n'
    "```\n"
)


def test_extract_strips_trailing_tandem_block() -> None:
    raw = "# Title\n\nSome prose.\n\n" + TANDEM_BLOCK
    assert verbs.extract(raw) == "# Title\n\nSome prose.\n"


def test_extract_returns_whole_body_when_no_block() -> None:
    raw = "# Title\n\nSome prose.\n"
    assert verbs.extract(raw) == "# Title\n\nSome prose.\n"


def test_extract_strips_leading_frontmatter() -> None:
    raw = "---\nchorus_doc_id: o0x11rggAEDH\ntitle: Note\n---\n# Title\n\nBody.\n"
    assert verbs.extract(raw) == "# Title\n\nBody.\n"


def test_extract_strips_both_frontmatter_and_block() -> None:
    raw = (
        "---\nchorus_doc_id: abc\n---\n"
        "# Title\n\nBody prose.\n\n" + TANDEM_BLOCK
    )
    assert verbs.extract(raw) == "# Title\n\nBody prose.\n"


def test_extract_leaves_body_horizontal_rule_alone() -> None:
    # A --- inside the body is not frontmatter; only a leading fence counts.
    raw = "# Title\n\nAbove.\n\n---\n\nBelow.\n"
    assert verbs.extract(raw) == raw
