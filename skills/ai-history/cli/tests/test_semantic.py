"""Semantic search: dep-free logic runs always; the embed round-trip is skipped without the extra.

The base suite must stay green on a torch-free install, so only the ranking test needs the
[semantic] extra. Chunking, the per-adapter text seams, and the missing-dep error are pure
stdlib and guard the seams the schema-contract test doesn't cover.
"""

import importlib.util
import json
from pathlib import Path

import pytest

from ai_history import semantic
from ai_history.adapters import claude, kiro, meshclaw

HAS_ST = importlib.util.find_spec("sentence_transformers") is not None


def test_chunks_windows_long_text() -> None:
    text = " ".join(str(i) for i in range(450))
    chunks = semantic._chunks(text)
    assert len(chunks) == 3  # 200 + 200 + 50
    assert chunks[0].split()[0] == "0"
    assert chunks[1].split()[0] == "200"


def test_chunks_empty() -> None:
    assert semantic._chunks("   ") == []


def test_iter_texts_claude(tmp_path: Path) -> None:
    p = tmp_path / "s.jsonl"
    p.write_text(
        json.dumps({"type": "user", "message": {"content": "hello world"}})
        + "\n"
        + json.dumps(
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "hi back"}]}}
        )
        + "\n"
        + json.dumps({"type": "summary", "summary": "ignored"})
        + "\n"
    )
    assert list(claude.iter_texts(p)) == ["hello world", "hi back"]


def test_iter_texts_meshclaw(tmp_path: Path) -> None:
    p = tmp_path / "s.jsonl"
    p.write_text(
        json.dumps({"_type": "metadata", "title": "T"})
        + "\n"
        + json.dumps({"role": "user", "content": "a question"})
        + "\n"
        + json.dumps({"role": "assistant", "content": "an answer"})
        + "\n"
    )
    assert list(meshclaw.iter_texts(p)) == ["a question", "an answer"]


def test_iter_texts_kiro(tmp_path: Path) -> None:
    p = tmp_path / "s.jsonl"
    p.write_text(
        json.dumps({"kind": "Prompt", "data": {"content": [{"kind": "text", "data": "q text"}]}})
        + "\n"
        + json.dumps(
            {"kind": "AssistantMessage", "data": {"content": [{"kind": "text", "data": "a text"}]}}
        )
        + "\n"
    )
    assert list(kiro.iter_texts(p)) == ["q text", "a text"]


def test_search_without_deps_or_index_is_actionable(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(semantic, "CACHE_DIR", tmp_path / "cache")
    with pytest.raises(SystemExit):
        semantic.search("anything")


@pytest.mark.skipif(not HAS_ST, reason="needs the [semantic] extra (sentence-transformers)")
def test_semantic_ranks_by_meaning(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(semantic, "CACHE_DIR", tmp_path / "cache")
    root = tmp_path / "mesh"
    root.mkdir()

    def mesh(name, body):
        (root / f"{name}.jsonl").write_text(
            json.dumps({"_type": "metadata", "title": name, "created_at": "2026-05-01T00:00:00"})
            + "\n"
            + json.dumps({"role": "user", "content": body})
            + "\n"
        )

    mesh("dogs", "my golden retriever loves chasing balls at the park")
    mesh("finance", "quarterly revenue and tax deductions for the fiscal year")

    roots = {"meshclaw": root}
    semantic.build_index(tools=["meshclaw"], roots=roots)
    results = semantic.search("puppy playing outside", tools=["meshclaw"], roots=roots)
    assert results[0].title == "dogs"  # semantic match despite zero shared keywords
