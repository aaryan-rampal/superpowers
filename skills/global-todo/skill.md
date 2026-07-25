---
name: global-todo
description: "Use when the user says to do something 'for later', 'add to todo', 'global todo', or any variant meaning they want to park an idea. Appends a checkbox with context to ~/personal/obsidian/TODO.md."
---

# Global TODO

Append a deferred task to the user's global TODO list in their Obsidian vault.

## Trigger phrases

Activate when the user says any of:
- "do this later" / "for later" / "something to do later"
- "add to todo" / "global todo" / "add a todo"
- "remind me to" / "note that" / "park this"

## Steps

1. **Extract the task** — distill the user's intent into a short, actionable phrase (≤10 words)
2. **Write context** — one sentence explaining what project/conversation this came from, so future-you has enough to act without re-reading the whole thread
3. **Append to TODO.md** — add the entry at the bottom of `/Users/aaryanrampal/personal/obsidian/TODO.md` in this format:

```
- [ ] <task> — <context sentence>
```

4. **Confirm** — tell the user what was added, one line

## Format rules

- Use `- [ ]` (GitHub-flavored markdown checkbox)
- Task: imperative mood, no trailing period
- Context: one sentence after an em dash `—`, lowercase start, present tense preferred
- No timestamp unless the user asks for one
- Never rewrite or reorder existing entries — append only

## Example output

```
- [ ] make thunderbird MCP global — from thunderbird-mcp session, want it available in all Claude projects not just this repo
```

## Bash command

Use the Write or Edit tool to append to the file. If the file doesn't exist yet, create it with a `# TODO` header first.
