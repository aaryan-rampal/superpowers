"""Optional semantic (RAG) search — behind the `--semantic` flag and the `[semantic]` extra.

The base CLI is dependency-free; this module lazy-imports sentence-transformers and
numpy so importing it never drags torch into the ripgrep path. The index is a cache,
not source data: transcripts on disk stay the source of truth. It lives under
~/.cache/ai-history/ and is refreshed incrementally by transcript mtime.

Chunking is per-window, not per-session: all-MiniLM-L6-v2's context is ~256 tokens, so
one vector per session would only "see" each chat's opening. We split each session into
~200-word windows, embed each, and rank a session by its best-matching chunk.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ai_history.adapters import claude, kiro, meshclaw
from ai_history.records import Session

ADAPTERS = {"claude": claude, "meshclaw": meshclaw, "kiro": kiro}
MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_DIR = Path(os.path.expanduser("~/.cache/ai-history"))
CHUNK_WORDS = 200

_MISSING = (
    "Semantic search needs the optional extra. From the skill's cli/ dir:\n"
    '    uv pip install -e ".[semantic]"\n'
    "then build the index once:\n"
    "    ./ai-history index"
)


def _require_deps():
    """Import the heavy deps lazily; raise an actionable error if the extra is absent."""
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as e:
        raise SystemExit(f"{_MISSING}\n\n(missing: {e.name})") from e
    return np, SentenceTransformer


def _chunks(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []
    return [" ".join(words[i : i + CHUNK_WORDS]) for i in range(0, len(words), CHUNK_WORDS)]


def _iter_chunks(tool: str, path: Path):
    """Yield (chunk_text) for one transcript, windowed across all its turns."""
    for turn in ADAPTERS[tool].iter_texts(path):
        yield from _chunks(turn)


def _model(SentenceTransformer):
    return SentenceTransformer(MODEL_NAME)


def build_index(tools: list[str] | None = None, roots=None) -> tuple[int, int]:
    """(Re)build the on-disk index incrementally. Returns (sessions_indexed, chunks)."""
    np, SentenceTransformer = _require_deps()
    resolved = roots or {name: mod.ROOT for name, mod in ADAPTERS.items()}
    selected = tools or list(resolved)

    old = _load_raw(np)
    seen_mtime = old["mtime"] if old else {}

    texts: list[str] = []
    meta: list[dict] = []
    fresh_vecs = []
    reused = 0

    model = None
    for name in selected:
        mod = ADAPTERS[name]
        for path in mod.discover(resolved[name]):
            key = str(path)
            mtime = path.stat().st_mtime
            if old and seen_mtime.get(key) == mtime:
                idx = [i for i, m in enumerate(old["meta"]) if m["path"] == key]
                for i in idx:
                    meta.append(old["meta"][i])
                    fresh_vecs.append(old["vecs"][i])
                    seen_mtime[key] = mtime
                    reused += 1
                continue
            chunks = list(_iter_chunks(name, path))
            if not chunks:
                continue
            if model is None:
                model = _model(SentenceTransformer)
            vecs = model.encode(chunks, normalize_embeddings=True)
            for chunk, vec in zip(chunks, vecs, strict=True):
                texts.append(chunk)
                meta.append({"tool": name, "path": key, "chunk": chunk})
                fresh_vecs.append(vec)
            seen_mtime[key] = mtime

    if not meta:
        return 0, 0

    matrix = np.array(fresh_vecs, dtype="float32")
    live_paths = {m["path"] for m in meta}
    mtime = {k: v for k, v in seen_mtime.items() if k in live_paths}
    _save_raw(np, matrix, meta, mtime)
    sessions = len({m["path"] for m in meta})
    return sessions, len(meta)


def search(query: str, tools: list[str] | None = None, roots=None) -> list[Session]:
    """Semantic search: rank sessions by their best-matching chunk's cosine similarity."""
    np, SentenceTransformer = _require_deps()
    raw = _load_raw(np)
    if not raw:
        raise SystemExit(f"No semantic index yet.\n{_MISSING}")

    model = _model(SentenceTransformer)
    q = model.encode([query], normalize_embeddings=True)[0]
    sims = raw["vecs"] @ q  # cosine: both sides are L2-normalized

    selected = set(tools) if tools else None
    best: dict[str, tuple[float, dict]] = {}
    for i, m in enumerate(raw["meta"]):
        if selected and m["tool"] not in selected:
            continue
        score = float(sims[i])
        cur = best.get(m["path"])
        if cur is None or score > cur[0]:
            best[m["path"]] = (score, m)

    ranked = sorted(best.values(), key=lambda t: t[0], reverse=True)
    out: list[Session] = []
    for score, m in ranked:
        s = ADAPTERS[m["tool"]].load_session(Path(m["path"]))
        if s is None:
            continue
        snippet = m["chunk"]
        s.snippet = f"[{score:.2f}] {snippet[:160]}"
        out.append(s)
    return out


def _save_raw(np, matrix, meta: list[dict], mtime: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(CACHE_DIR / "vecs.npy", matrix)
    (CACHE_DIR / "meta.json").write_text(json.dumps({"meta": meta, "mtime": mtime}))


def _load_raw(np):
    vpath = CACHE_DIR / "vecs.npy"
    mpath = CACHE_DIR / "meta.json"
    if not (vpath.exists() and mpath.exists()):
        return None
    data = json.loads(mpath.read_text())
    return {"vecs": np.load(vpath), "meta": data["meta"], "mtime": data["mtime"]}
