"""normalize_ts: every store's timestamp flavor -> one tz-aware UTC datetime."""

from datetime import UTC

from ai_history.records import normalize_ts


def test_epoch_seconds_int() -> None:
    dt = normalize_ts(1781913916)
    assert dt.tzinfo == UTC
    assert dt.year == 2026


def test_naive_iso_assumed_utc() -> None:
    # MeshClaw message ts often has no offset.
    dt = normalize_ts("2026-06-17T01:57:05.959987")
    assert dt.tzinfo == UTC
    assert dt.hour == 1


def test_aware_iso_converted_to_utc() -> None:
    dt = normalize_ts("2026-06-17T01:57:05+05:00")
    assert dt.tzinfo == UTC
    assert dt.hour == 20  # 01:57 +05:00 == 20:57 prev day UTC... 01-5 = -4 -> 20:57 on 16th
    assert dt.day == 16


def test_zulu_suffix() -> None:
    dt = normalize_ts("2026-06-20T00:05:12.797124Z")
    assert dt.tzinfo == UTC
    assert dt.minute == 5


def test_kiro_nanosecond_precision_truncated() -> None:
    # Kiro emits 9 fractional digits; datetime only takes 6.
    dt = normalize_ts("2026-06-20T00:05:12.797124666Z")
    assert dt.tzinfo == UTC
    assert dt.microsecond == 797124


def test_none_returns_none() -> None:
    assert normalize_ts(None) is None


def test_garbage_returns_none() -> None:
    assert normalize_ts("not a date") is None
