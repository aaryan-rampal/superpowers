"""Parse/serialize round-trip and parity against real plugin-written fixtures."""

from pathlib import Path

import pytest

from tandem import block

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE_FILES = sorted(FIXTURES.glob("*.md"))


@pytest.mark.parametrize("path", FIXTURE_FILES, ids=lambda p: p.name)
def test_parse_serialize_is_byte_identical_to_plugin_output(path: Path) -> None:
    raw = path.read_text()
    doc = block.parse_document(raw)
    assert doc.error is None
    assert block.serialize_document(doc) == raw


def test_parse_extracts_prose_and_comments() -> None:
    raw = (
        "Hello world.\n\n```tandem-comments\n"
        "{\n"
        '  "a1b2": {\n'
        '    "anchor": { "exact": "Hello", "pos": 0 },\n'
        '    "status": "open",\n'
        '    "thread": [\n'
        '      { "author": "Me", "ts": "2026-06-30T18:00:00Z", "text": "hi" }\n'
        "    ]\n"
        "  }\n"
        "}\n```\n"
    )
    doc = block.parse_document(raw)
    assert doc.prose == "Hello world.\n"
    assert list(doc.comments.keys()) == ["a1b2"]
    assert doc.comments["a1b2"]["status"] == "open"
    assert doc.comments["a1b2"]["thread"][0]["author"] == "Me"


def test_parse_file_with_no_block_returns_prose_only() -> None:
    raw = "Just prose, no comments.\n"
    doc = block.parse_document(raw)
    assert doc.prose == raw
    assert doc.comments == {}
    assert doc.error is None


def test_parse_invalid_json_block_sets_error_and_does_not_lose_prose() -> None:
    raw = "Prose.\n\n```tandem-comments\n{ not valid json\n```\n"
    doc = block.parse_document(raw)
    assert doc.error is not None
    assert doc.prose == raw
    assert doc.comments == {}


def test_serialize_empty_comments_returns_prose_unchanged() -> None:
    doc = block.ParsedDoc(prose="Only prose.\n", comments={}, error=None)
    assert block.serialize_document(doc) == "Only prose.\n"


def test_serialize_refuses_document_with_error() -> None:
    doc = block.ParsedDoc(prose="x", comments={}, error="boom")
    with pytest.raises(ValueError, match="parse error"):
        block.serialize_document(doc)
