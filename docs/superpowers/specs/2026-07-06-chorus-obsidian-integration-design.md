# chorus-obsidian-integration — design

**Date:** 2026-07-06
**Status:** Approved (design), not yet implemented
**Companion to:** `obsidian-tandem-comments`

## Purpose

Bind an Obsidian note to a Chorus document (`chorus.aws.dev`) so that:

- **Push**: the note's prose is uploaded to Chorus (create a new doc or overwrite an
  existing one).
- **Sync**: comments move between the two — Chorus comments come into the Obsidian
  tandem-comments block, and tandem comments go up to Chorus — "as best it can",
  given the constraints below.

Obsidian is the **source of truth for prose**. Chorus is where people comment. The
prose sync is push-only (Obsidian → Chorus); it is never pulled back.

## Hard constraints (from the Chorus MCP surface)

These shape the whole design and are not negotiable without a richer MCP:

1. **Chorus is reachable only through MCP tools** (`reveal`, `markdown`, `comments`,
   `docs`, `folders`, `search`), which only the agent can call. A standalone CLI
   cannot talk to Chorus. Therefore the Chorus side is **agent-driven**, and the skill
   is primarily a playbook, not a monolithic CLI.
2. **`comments add` has no anchor parameter.** An agent posting a comment to Chorus can
   only create a **floating (unanchored)** comment. Chorus anchors use opaque CRDT node
   ids assigned by the editor, not addressable via MCP. Consequence: **Obsidian → Chorus
   comments are unanchored**; the anchored quote is inlined into the comment body instead.
3. **Reading Chorus comments is high fidelity.** `comments search` returns each comment's
   `anchor.quote` plus author, `comment_num`, `created_at`, replies, and resolved flag.
   Consequence: **Chorus → Obsidian re-anchoring works** by matching the quote in prose.

## Architecture

Agent playbook (`SKILL.md`) + a small stdlib-only Python helper (`cli/co`). Mirrors the
existing `tc` / tandem split. The agent calls Chorus MCP tools directly; `co` does the
mechanical, MCP-free, unit-testable work.

```
chorus-obsidian-integration/
  SKILL.md          # agent playbook: push / sync loops
  cli/
    co              # python entrypoint (stdlib only)
    src/...         # verbs
    tests/...
```

The two skills cross-link: tandem's SKILL references this one for Chorus round-tripping;
this one references tandem for the block format and the `tc` CLI.

## Binding model

The Obsidian note's YAML frontmatter carries the pairing:

```yaml
chorus_doc_id: o0x11rggAEDH
chorus_watermark: 1783356565478   # epoch ms; last-synced Chorus activity
```

- Frontmatter has `chorus_doc_id` → that is the pairing; push defaults to overwriting it.
- Absent → the picker runs, the chosen id (or a freshly created doc's id) is written back
  via `co bind`.

## `co` helper verbs (no MCP; pure functions over files / JSON)

| Verb | Does |
|------|------|
| `co extract FILE` | Emit the prose **without** the ```` ```tandem-comments ```` block — the payload to push. |
| `co pick --docs <json> [--query q]` | Render candidate Chorus docs. **TTY → scrollable filter menu** (arrow keys, filter-as-you-type). No TTY → numbered list to stdout for the agent. Emits chosen `doc_id` or `NEW`. |
| `co bind FILE --doc-id ID` | Write/update `chorus_doc_id` (and clear/set `chorus_watermark`) in frontmatter. |
| `co anchor FILE --quote "..."` | Match a Chorus quote to a tandem anchor (`exact`/`prefix`/`suffix`/`pos`) against the note's prose; print anchor JSON, or `ORPHAN` if no confident match. |
| `co diff --tandem <json> --chorus <json> --since <ts>` | Dedup engine. Given both comment sets, the watermark, and the stored `chorus_num`↔hex-id map, output three sets: to-pull, to-push, to-resolve. |

The picker is agent-first: when the agent drives (no TTY), it has already fetched the docs
list via MCP `docs search` and shows the candidates to the user in chat, passing the chosen
id. When a human runs `co` directly at a terminal, they get the scrollable menu. Same list,
two front-ends.

## Push flow (prose Obsidian → Chorus)

1. Resolve binding: read frontmatter; if no `chorus_doc_id`, run the picker
   (`docs search` → `co pick`) → `co bind`. Top of the picker list is always "Create new".
2. If a bound id exists → default to overwriting it. The picker only reappears on first
   bind or an explicit rebind request.
3. `co extract FILE` → `reveal` → `markdown write` (overwrite existing `doc_id`) or
   `markdown create` (new doc; then `co bind` with the returned id).
4. The ```` ```tandem-comments ```` block is **never** uploaded.

## Sync flow (comments, bidirectional)

1. Read `chorus_doc_id` + `chorus_watermark` from frontmatter. `comments search`
   (`include_resolved: true`) for the Chorus side; read the tandem side (`tc`/block).
2. `co diff` computes three sets using the stored cross-reference stamps and watermark:
   - **Chorus → tandem** (new Chorus comments/replies since watermark): anchor each via
     `co anchor`. Unmatchable ones are imported **floating**, with the original quote
     inlined: `> <chorus quote>\n\n<comment>`, and flagged in the report.
   - **tandem → Chorus** (new tandem comments/replies): `comments add` (unanchored; quote
     inlined into the body). The returned `comment_num` is stamped back onto the tandem
     entry.
   - **resolve (Obsidian → Chorus only)**: tandem threads with `status: resolved` →
     `comments update --resolve` on the matched Chorus comment. Chorus resolve-state is
     **never** pulled back.
3. A closed (resolved) thread that gets **new Chorus activity** afterwards is **not
   reopened** — it is surfaced in the sync report.
4. Update `chorus_watermark`. Print a report: pushed / pulled / orphaned / resolved /
   post-resolve-activity.

### Replies

Replies sync **both directions**, matched at reply granularity via the same
`chorus_num`↔hex-id map, using the watermark to avoid re-sending.

## Data stamps

Extra keys added to tandem entries. `tc` ignores unknown keys (schema allows them), so
this does not break the existing CLI or the plugin parity test.

- On a mirrored comment/reply: `origin: "chorus" | "obsidian"`, `chorus_num: N`.
- In frontmatter: `chorus_doc_id`, `chorus_watermark` (epoch ms).

## Known lossiness (by design)

- **Obsidian → Chorus comments are unanchored** (MCP limitation); quote is inlined in body.
- **Chorus → Obsidian** is high fidelity (quote re-anchored).
- **Prose drift**: Chorus-only prose edits (allowed — you may edit Chorus directly) mean a
  Chorus comment's quote may not exist in the Obsidian prose. Those import as floating +
  reported. This is expected, not an error.

## Testing

`co` is stdlib-only and pure → unit tests per verb:

- `co extract`: strips the tandem block exactly, leaves prose byte-identical otherwise.
- `co anchor`: exact-match, duplicate-quote-with-`pos`, and orphan (no match) cases.
- `co diff`: dedup across a simulated re-run (no duplicate pushes/pulls); reply-granularity;
  resolve set only from tandem side.
- `co bind`: frontmatter round-trip (create when absent, update when present, preserve
  other keys).
- Picker non-TTY path (numbered list to stdout) is testable; the TTY scroll path is manual.

No MCP in tests. The agent orchestration (MCP calls, the playbook loops) is exercised by hand.

## Deferred / out of scope

- Bidirectional **prose** sync (pulling Chorus edits back into the note).
- Anchored Obsidian → Chorus comments (blocked until MCP `comments add` accepts an anchor).
- Fuzzy anchor matching for drifted prose (v1 orphans + reports instead).
