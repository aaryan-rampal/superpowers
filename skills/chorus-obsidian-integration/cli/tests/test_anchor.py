"""anchor: match a Chorus quote to a tandem anchor (exact/prefix/suffix/pos) or ORPHAN."""

from chorus_obsidian import verbs

PROSE = (
    "The rater sees three axes: accuracy, sensitivity, and tone. "
    "Each axis has a loaded meaning. The rater sees three axes again later.\n"
)


def test_anchor_exact_match_returns_anchor_with_pos() -> None:
    a = verbs.anchor(PROSE, "three axes")
    assert a is not None
    assert a["exact"] == "three axes"
    assert a["pos"] == PROSE.index("three axes")


def test_anchor_includes_prefix_and_suffix_context() -> None:
    a = verbs.anchor(PROSE, "accuracy")
    assert a is not None
    assert a["exact"] == "accuracy"
    # prefix/suffix are context on each side, drawn from the prose
    assert a["prefix"].endswith("axes: ")
    assert a["suffix"].startswith(",")


def test_anchor_duplicate_quote_uses_first_occurrence() -> None:
    a = verbs.anchor(PROSE, "The rater sees three axes")
    assert a is not None
    assert a["pos"] == PROSE.index("The rater sees three axes")  # the first one


def test_anchor_absent_quote_returns_none() -> None:
    assert verbs.anchor(PROSE, "quote that does not appear") is None


def test_anchor_matches_across_whitespace_differences() -> None:
    # Chorus may collapse newlines/spaces in the quote it returns.
    prose = "the export is written\nas partitioned Parquet to a bucket.\n"
    a = verbs.anchor(prose, "written as partitioned Parquet")
    assert a is not None
    # exact is the real span from the prose (with its original whitespace)
    assert a["exact"] == "written\nas partitioned Parquet"
