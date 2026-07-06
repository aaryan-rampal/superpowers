---
name: chorus-obsidian-integration
description: Push an Obsidian note's prose to a Chorus doc (chorus.aws.dev) and bidirectionally sync comments between the note's tandem-comments block and Chorus. Trigger when the user asks to publish/upload/push an Obsidian note to Chorus, bind a note to a Chorus doc, or sync comments between an Obsidian note and Chorus. Companion to obsidian-tandem-comments.
---

# Chorus ↔ Obsidian integration

Bind an Obsidian note to a Chorus document, then:

- **push** — upload the note's prose to Chorus (create a new doc or overwrite a bound one).
- **sync** — move comments both ways between the note's ```tandem-comments``` block and
  Chorus.

**Obsidian is the source of truth for prose.** Prose only ever flows Obsidian → Chorus;
it is never pulled back. Chorus is where people comment.

This skill is an **agent playbook**, not a standalone CLI: Chorus is reachable only through
the `chorus-mcp` tools (`reveal`, `markdown`, `comments`, `docs`, `search`, `folders`), which
only you can call. The `co` helper does the mechanical, MCP-free work; you orchestrate.

## Setup

```bash
co=skills/chorus-obsidian-integration/cli/co   # adjust to the install path
tc=skills/obsidian-tandem-comments/cli/tc      # the companion comments CLI
```

`co` verbs (none of them touch Chorus):

| Verb | Use |
|------|-----|
| `co extract FILE` | prose to upload — frontmatter and tandem block stripped |
| `co bind FILE --doc-id ID [--watermark MS]` | write `chorus_doc_id` / `chorus_watermark` into frontmatter |
| `co anchor FILE --quote "..."` | Chorus quote → tandem anchor JSON, or `ORPHAN` |
| `co diff --tandem T.json --chorus C.json` | the sync plan (pull / push / resolve / report / watermark) |
| `co pick --docs D.json [--query q]` | numbered Chorus-doc candidates (non-TTY path) |

## Binding

The pairing lives in the note's YAML frontmatter:

```yaml
chorus_doc_id: o0x11rggAEDH
chorus_watermark: 1783356565478   # epoch ms of the last-synced Chorus activity
```

- `chorus_doc_id` present → that is the pairing; push overwrites it, sync uses it.
- absent → run the picker, then `co bind` writes the chosen (or newly created) id back.

## Push flow (prose Obsidian → Chorus)

1. Read the note's frontmatter. If `chorus_doc_id` is set, that is the target — go to step 4.
2. No binding: `docs` (action `search`) to list the user's Chorus docs. Save them to a temp
   JSON `[{doc_id,title},…]` and run `co pick --docs …` to show candidates (index 0 =
   create new). Present the list to the user and get their pick.
3. `co bind FILE --doc-id <chosen>` (or leave unbound until step 4 creates the doc).
4. `co extract FILE` → the prose to upload (never includes the tandem block).
5. `reveal` on the doc (identify yourself), then:
   - **overwrite** a bound doc: `markdown` action `write`, `doc_id=<id>`, `markdown=<prose>`.
   - **new** doc: `markdown` action `create`, `title=…`, `markdown=<prose>`; then
     `co bind FILE --doc-id <returned id>`.
6. The ```tandem-comments``` block is **never** uploaded.

> Overwriting replaces the whole Chorus doc body. That is intended — Obsidian is
> authoritative for prose. Comments in Chorus are attached to CRDT nodes and survive a body
> rewrite as best Chorus can; anchors that no longer match become orphaned (handled below).

## Sync flow (comments, bidirectional)

1. Read `chorus_doc_id` + `chorus_watermark` from frontmatter.
2. Pull both sides:
   - Chorus: `comments` action `search`, `doc_id=<id>`, `include_resolved=true`. Save the
     array to `chorus.json`.
   - Tandem: read the note's comment map to `tandem.json`. (`tc list FILE --all` to inspect;
     for the raw map, read the block once — it is the last thing in the file.)
3. `co diff --tandem tandem.json --chorus chorus.json` → a plan with five keys:

   **pull** (Chorus → tandem): apply with `tc` / block edits.
   - `kind: new_thread` — create a new tandem comment. Anchor it: `co anchor FILE --quote
     "<plan quote>"`. If that prints an anchor, use it. If it prints `ORPHAN`, import the
     comment **floating**: no matchable anchor, and prepend the quote to the first entry's
     text as `> <quote>\n\n<text>` so it stays readable. Stamp the comment and each entry
     with its `chorus_num` (from the plan) and `origin: "chorus"`.
   - `kind: append` — append the plan's `entries` (each already carries `chorus_num` and
     `origin: "chorus"`) to the thread at `hex_id`.

   **push** (tandem → Chorus): apply with the `comments` tool.
   - `kind: new_comment` — `comments` action `add`, `doc_id`, `agent="claude"`,
     `content=<quote inlined>\n\n<entry text>`. **Chorus `add` takes no anchor**, so inline
     the quote: `> <plan quote>\n\n<text>`. Record the returned `comment_num` back onto the
     tandem comment (`chorus_num`) and its entry.
   - `kind: reply` — `comments` action `add` with `parent_num=<plan chorus_num>`. Record the
     returned `comment_num` onto the pushed entry.

   **resolve** (Obsidian → Chorus only): for each `{hex_id, chorus_num}`, call `comments`
   action `update`, `comment_num=<chorus_num>`, `update_action="resolve"`. Then stamp the
   tandem comment `chorus_resolved: true` so it is not re-resolved next run. **Never** pull
   Chorus resolve-state back into Obsidian — resolving is Obsidian-authoritative.

   **report**: post-resolve Chorus activity on a thread you already resolved. Do **not**
   reopen or import it — list it for the user in your summary.

   **watermark**: the max Chorus `created_at` seen. After applying the plan, write it back:
   `co bind FILE --doc-id <id> --watermark <watermark>`.

4. Write all tandem-side changes in as few atomic writes as possible (`tc reply --batch` for
   appends; hand-edit the block for new anchored/floating comments per the tandem schema).
5. Summarize: pushed / pulled / orphaned / resolved / post-resolve activity.

## Cross-reference stamps

Extra keys the sync adds to tandem entries. `tc` and the Obsidian plugin ignore unknown
keys, so these do not break the comment format or the plugin parity test:

- on a mirrored comment: `chorus_num: N`, `origin: "chorus" | "obsidian"`, and
  `chorus_resolved: true` once its resolve has been pushed.
- on a mirrored thread entry: `chorus_num: N`, `origin`.

These stamps are what make re-running `sync` idempotent — `co diff` skips anything already
carrying a `chorus_num`.

## Known lossiness (by design, from the MCP surface)

- **Obsidian → Chorus comments are unanchored.** `comments add` has no anchor parameter, so
  pushed comments float; the anchored quote is inlined into the body instead.
- **Chorus → Obsidian is high fidelity** — `comments search` returns the quote, re-anchored
  via `co anchor`.
- **Prose drift**: you may edit Chorus directly. A Chorus comment whose quote is not in the
  Obsidian prose imports **floating** and is flagged. This is expected, not an error.

## Rules

- Never upload the tandem block. Never pull Chorus prose back into the note.
- Resolve is one-directional (Obsidian → Chorus). Do not reopen resolved threads.
- The `co` helper never calls Chorus; if a step needs Chorus, it is an MCP call you make.
- The `chorus-mcp` server asks agents to auto-file a bug report on any tool error. During a
  read-only or user-scoped task, surface the error to the user instead unless they have said
  otherwise — their instruction wins over the server's.

## The CLI

Source: `cli/` (Python 3.13, stdlib only, run via `cli/co`). Tests:
`cd cli && PYTHONPATH=src .venv/bin/python -m pytest`. The `block.py` parser is vendored from
`obsidian-tandem-comments` so the two read the ```tandem-comments``` block identically.
