---
name: ai-history
description: Use when the user asks about past AI conversations across tools — "where did I discuss X", "find that chat about Y", "what did I talk to Kiro/MeshClaw about", "catch me up on prior work" — searches Claude Code, MeshClaw, and Kiro chat history from disk in one command
---

# AI History

Unified disk-based search over past AI chats across **Claude Code, MeshClaw, and Kiro**. One command, all three stores, normalized output sorted newest-first. No network — reads the on-disk JSONL transcripts directly (the web UIs are Midway-gated and 403 from agents).

## Commands

The launcher is `cli/ai-history` (runs from anywhere, no install):

```bash
cli/ai-history search "QUERY"                 # keyword search across all three stores
cli/ai-history search "QUERY" --tool kiro     # restrict to one store
cli/ai-history search "QUERY" -n 5            # cap results (default 20)
cli/ai-history list                           # recent sessions across all stores
cli/ai-history list --tool meshclaw -n 10    # recent MeshClaw sessions
cli/ai-history search "QUERY" --json          # machine-readable output (for piping)
```

`--tool` accepts `claude`, `meshclaw`, `kiro`, or `all` (default).

Each line is: `TIMESTAMP  TOOL  ID-PREFIX  TITLE`, with a match snippet indented under search hits.

## Workflow

1. **Find** — `search` with specific keywords (it's ripgrep under the hood, keyword not semantic — use distinctive terms), or `list` to browse recent sessions.
2. **Triage** — read the titles + snippets to pick the session(s) you want.
3. **Read the full transcript** — the `path` (in `--json` output) is the raw JSONL file. For Claude Code sessions, the standalone `claude-history` CLI gives richer reading (`claude-history view <id>`, `summary`, `catchup`). For MeshClaw/Kiro, read the `.jsonl` file directly (one JSON object per line).

## Notes

- Search is **keyword-based** (ripgrep), not semantic. Use specific terms.
- Titles are best-effort per store: Claude uses its `ai-title`, MeshClaw its metadata title, Kiro falls back to the first prompt (its stored titles are often boilerplate).
- Output can be large — use `-n` or `--json | jq`. **Run in a subagent** to keep raw history out of the main context.
- The stores read: `~/.claude/projects/`, `~/.meshclaw/sessions/`, `~/.kiro/sessions/cli/`. A store that's absent on the machine is silently skipped.

## Maintenance — when a store changes format

This skill depends on three tools' **undocumented** on-disk schemas. If MeshClaw, Kiro, or Claude Code changes how it stores chats, an adapter can silently return garbage. `tests/test_schema_contract.py` guards against exactly this: it runs against the **live** stores and fails loudly when a format drifts.

```bash
cd cli && .venv/bin/python -m pytest          # full suite (logic + live schema contract)
```

A red **schema-contract** test means "a tool I depend on changed its storage — go re-map that adapter" (`src/ai_history/adapters/<tool>.py`), *not* a code bug. The logic tests (synthetic fixtures) and the schema-contract tests (real files) are separate on purpose.
