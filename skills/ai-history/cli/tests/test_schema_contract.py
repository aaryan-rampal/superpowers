"""Schema-contract tests — run against the REAL on-disk stores.

These pin the undocumented storage formats of Claude Code, MeshClaw, and Kiro
that the adapters depend on. Unlike the logic tests (synthetic tmp files), these
read the newest live file in each store. A failure here means a tool changed how
it stores chats and the corresponding adapter needs re-mapping — NOT a code bug.

Each store is skipped if absent (portable across machines), but if a store IS
present it must conform. The final assertions are end-to-end: parsing + title +
timestamp must all succeed together, over the whole real store, without raising.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_history import core
from ai_history.adapters import claude, kiro, meshclaw


def _newest(paths: list[Path]) -> Path | None:
    real = [p for p in paths if p.is_file() and p.stat().st_size > 0]
    return max(real, key=lambda p: p.stat().st_mtime) if real else None


# ---------- Claude Code ----------


def test_claude_store_present_and_globs():
    if not claude.ROOT.is_dir():
        pytest.skip("no Claude Code store on this machine")
    files = list(claude.discover())
    assert files, f"{claude.ROOT} exists but no <slug>/<uuid>.jsonl found — layout changed?"


def test_claude_line_schema_contract():
    if not claude.ROOT.is_dir():
        pytest.skip("no Claude Code store")
    f = _newest(list(claude.discover()))
    if f is None:
        pytest.skip("no non-empty Claude sessions")
    kinds = set()
    saw_message_turn = False
    for line in f.read_text().splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if not isinstance(obj, dict):
            continue
        kinds.add(obj.get("type"))
        if obj.get("type") in ("user", "assistant") and "message" in obj:
            saw_message_turn = True
    assert saw_message_turn, (
        "No user/assistant record with a 'message' key in the newest Claude "
        f"session ({f.name}). The type-discriminated line schema changed."
    )


# ---------- MeshClaw ----------


def test_meshclaw_store_present_and_globs():
    if not meshclaw.ROOT.is_dir():
        pytest.skip("no MeshClaw store on this machine")
    files = list(meshclaw.discover())
    assert files, f"{meshclaw.ROOT} exists but no *.jsonl found — layout changed?"


def test_meshclaw_line_schema_contract():
    if not meshclaw.ROOT.is_dir():
        pytest.skip("no MeshClaw store")
    f = _newest(list(meshclaw.discover()))
    if f is None:
        pytest.skip("no non-empty MeshClaw sessions")
    lines = f.read_text().splitlines()
    meta = json.loads(lines[0])
    assert meta.get("_type") in ("metadata", "archive"), (
        f"MeshClaw line 1 of {f.name} is not a metadata/archive record — "
        "the first-line-is-metadata contract changed."
    )
    # At least one message line must carry a string `content`.
    assert any(
        isinstance(json.loads(ln), dict)
        and "role" in json.loads(ln)
        and isinstance(json.loads(ln).get("content"), str)
        for ln in lines[1:]
        if ln.strip()
    ), f"No {{role, content(str)}} message line in {f.name} — message schema changed."


# ---------- Kiro ----------


def test_kiro_store_present_and_globs():
    if not kiro.ROOT.is_dir():
        pytest.skip("no Kiro cli store on this machine")
    files = list(kiro.discover())
    assert files, f"{kiro.ROOT} exists but no cli/<uuid>.jsonl found — layout changed?"


def test_kiro_line_and_metadata_contract():
    if not kiro.ROOT.is_dir():
        pytest.skip("no Kiro cli store")
    f = _newest(list(kiro.discover()))
    if f is None:
        pytest.skip("no non-empty Kiro sessions")
    kinds = set()
    for line in f.read_text().splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict) and "kind" in obj:
            kinds.add(obj["kind"])
    assert kinds & {"Prompt", "AssistantMessage", "ToolResults"}, (
        f"No known kind ({{Prompt,AssistantMessage,ToolResults}}) in {f.name} — "
        "the {kind,data} transcript schema changed."
    )
    meta_path = f.with_suffix(".json")
    assert meta_path.is_file(), f"Kiro transcript {f.name} has no paired .json — pairing changed."
    meta = json.loads(meta_path.read_text())
    assert "session_id" in meta and "created_at" in meta, (
        "Kiro .json metadata lost session_id/created_at — metadata schema changed."
    )


# ---------- End-to-end normalization over the whole real store ----------


@pytest.mark.parametrize("mod", [claude, meshclaw, kiro])
def test_adapter_normalizes_real_store_without_crashing(mod):
    if not mod.ROOT.is_dir():
        pytest.skip(f"no store at {mod.ROOT}")
    count = 0
    for path in mod.discover():
        s = mod.load_session(path)  # must never raise on any real file
        if s is not None:
            assert s.title, f"empty title for {path}"
            count += 1
    assert count > 0, f"parsed zero sessions from a present {mod.ROOT}"


def test_search_over_all_real_stores_completes():
    # The integration guarantee: a search across every live store returns
    # without raising, even over unreadable/empty/oddly-named files.
    results = core.search("the")  # ubiquitous token; we only assert it doesn't blow up
    assert isinstance(results, list)
