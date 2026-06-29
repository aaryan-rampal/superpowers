---
name: obsidian-tandem-comments
description: Read, write, reply to and resolve comments in Markdown files that use the tandem-comments format (a ```tandem-comments fenced JSON block at the end of the file, quote-anchored via W3C TextQuoteSelector). Trigger whenever a Markdown file contains a tandem-comments block, or the user asks to comment on / annotate / review text in an Obsidian note, reply to a comment, or resolve comments.
---

# Obsidian Tandem Comments — comments in Markdown

Comments live in a fenced block at the **end of the file**. The prose above stays
**100% untouched** — never write markers into the body text.

````markdown
```tandem-comments
// Schema: { "<id>": { anchor:{exact,prefix,suffix,pos?}, status:open|resolved, thread:[{author,ts,text}] } }
// Anchor = quote from the prose. To locate: search for "exact", disambiguate via prefix/suffix.
{
  "a1f3": {
    "anchor": { "exact": "cut prices hard", "prefix": "we should ", "suffix": " in Q3", "pos": 22 },
    "status": "open",
    "thread": [
      { "author": "Leon", "ts": "2026-06-10T10:24:00Z", "text": "Too aggressive?" }
    ]
  }
}
```
````

## Rules

- **Locating a passage:** search the prose for `anchor.exact`; on multiple hits
  disambiguate via `prefix`/`suffix`, falling back to the hit closest to `pos`
  (character offset into the prose).
- **Replying:** append `{ "author": "Claude", "ts": "<ISO-8601 UTC>", "text": "..." }`
  to the `thread` array.
- **New comment:** add a new key (4-digit hex id, e.g. `"7c2e"`) with `anchor` +
  `status: "open"` + `thread`. Anchor: `exact` = exact quote from the prose,
  `prefix`/`suffix` = ~20 chars of context before/after, `pos` = character offset.
- **Resolving:** **remove the entry entirely** — the user wants Markdown files kept
  clean. Only if history is explicitly requested, set `status` to `"resolved"` instead.
- **Block lifecycle:** when no comments remain, **remove the block entirely**
  (including the single separating newline before it). If no block exists yet, append
  it at the end of the file: exactly one \n between prose and the ```tandem-comments line.
- **Never** modify the prose while commenting. Comment text may contain Markdown;
  JSON strings escape newlines as \\n.

