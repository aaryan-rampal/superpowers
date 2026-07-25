---
name: obsidian-tandem-comments
description: Read, write, reply to and resolve comments in Markdown files that use the tandem-comments format (a ```tandem-comments fenced JSON block at the end of the file, quote-anchored via W3C TextQuoteSelector). Trigger whenever a Markdown file contains a tandem-comments block, or the user asks to comment on / annotate / review text in an Obsidian note, reply to a comment, or resolve comments.
---

# Obsidian Tandem Comments — comments in Markdown

Comments live in a ```tandem-comments fenced JSON block at the **end of the file**.
The prose above stays **100% untouched** — never write markers into the body text.

## Use the `tc` CLI — do not read or edit the block as text

The raw JSON block is large (tens of KB) and re-reading it fills context fast.
A bundled CLI reads and writes it compactly. **Always** prefer `tc` over `Read`-ing
the whole file or `Edit`-ing the JSON block.

```bash
tc=skills/obsidian-tandem-comments/cli/tc   # adjust to the skill's install path
```

| Verb | Use | Output |
|------|-----|--------|
| `tc list FILE [--all]` | triage; first call of a round | one line/thread + `watermark:` |
| `tc since FILE TS [--seen ids]` | "I added more" mid-round | only entries at/after `TS` + new `watermark:` |
| `tc show FILE ID` | full thread for one comment | thread only, no prose |
| `tc reply FILE ID --text "..." --ts TS` | answer one thread | (writes, atomic) |
| `tc reply FILE --batch --ts TS` | answer many; reads `[{id,text},...]` on stdin | (one atomic write) |
| `tc unanswered FILE [--user Me]` | verify none left for the user | threads where the user replied last |
| `tc resolve FILE ID` | close a thread | (writes, atomic) |

`--ts` is an ISO-8601 UTC timestamp (the reply time). `--author` defaults to `Claude`,
`--user` (for `unanswered`) defaults to `Me` — match the author names already in the file.

## The reply loop

When the user says *"I added comments"* / *"reply to all"* / *"did you reply to all?"*:

1. `tc list FILE` — see every open thread, who replied last, and the watermark.
   Keep the `watermark:` value; if the user adds more mid-session, use
   `tc since FILE <watermark>` instead of re-listing everything.
2. Triage. For substantive comments, dispatch a subagent to research, then post the
   finding into that thread. For quick answers, answer directly.
3. Write all replies in **one** `tc reply --batch` call (stdin `[{id,text},...]`).
   One atomic write — no per-edit stale-file errors.
4. `tc unanswered FILE` — **post-condition: this must print "(none …)"** before you
   yield. No open thread may end with the user as the final commenter.

## Rules

- **Never edit the prose** while commenting. Never hand-edit the JSON block — use `tc`.
- **Reading the doc body:** if you need the prose (e.g. to anchor a new comment), read
  only the prose — the block is the last thing in the file, so `Read` with a line
  `limit` that stops before the fence, or rely on `tc` for anything comment-related.
- **Resolving:** `tc resolve` sets `status: "resolved"` (kept in the block, hidden from
  `tc list` unless `--all`). If the user instead wants resolved threads *deleted* to keep
  files clean, do that as an explicit Edit — confirm which they want.
- **New comments** (creating an anchor from a prose quote) are **not yet** a `tc` verb —
  do those by hand per the schema below, or ask. The anchor-matching logic is the v2 work.
- Comment text may contain Markdown; the CLI handles JSON escaping.
- **Round-tripping to Chorus:** to publish the note's prose to a Chorus doc and sync these
  comments with Chorus (chorus.aws.dev), use the `chorus-obsidian-integration` skill. It
  reads this block but never uploads it, and stamps mirrored comments with `chorus_num` /
  `origin` keys (which the verbs here safely ignore).

## Schema (for the hand-edited cases above)

```
"<id>": {                                  // 4-digit hex id
  "anchor": { "exact": "...", "prefix": "...", "suffix": "...", "pos": 123 },
  "status": "open" | "resolved",
  "thread": [ { "author": "...", "ts": "<ISO-8601 UTC>", "text": "..." } ]
}
```

`anchor.exact` = exact quote from the prose; `prefix`/`suffix` = ~20 chars of context
on each side; `pos` = character offset into the prose (disambiguates duplicate quotes).

## The CLI

Source: `cli/` (Python 3.13, stdlib only, run via `cli/tc`). Tests: `cd cli && PYTHONPATH=src .venv/bin/python -m pytest`.
A parity test asserts the CLI's writes are byte-identical to the plugin's own output, so
the two never drift. Deferred to v2: `tc new` (create comment) and `tc check-anchors`
(flag stale anchors) — both need the TextQuoteSelector matching logic ported.
