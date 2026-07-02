---
name: global-todo
description: Use when the user says "global todo", "add to global todo", "add this to my todo", or wants to track something for later in a persistent list
---

# Global Todo

## Overview

Manages a persistent kanban board at `~/obsidian/Kanban.md`. Each item is added to the **Backlog** column with a short label only.

## When to Use

- User says "global todo", "add to global todo", "add this to my todo list"
- User wants to remember something for later outside the current task

## Steps

1. **Read** `~/obsidian/Kanban.md` to see current contents and find the `## Backlog` section
2. **Append** new item(s) under `## Backlog` using the format below
3. **Create a linked note** at `~/obsidian/kanban-notes/<Task name>.md` with full context (what, why, blockers, links, commands)
4. **Write** the updated Kanban file
5. **Commit** both files:
   ```bash
   cd ~/obsidian && git add Kanban.md kanban-notes/ && git commit -m "chore: add todo item"
   ```

## Card Format (in Kanban.md)

```markdown
- [ ] [[Short task name]]
```

Optionally add a blocker emoji or date:
```markdown
- [ ] [[Short task name]] ⛔
- [ ] [[Short task name]] 📅 2026-07-15
```

### Rules for card text

- **MAX ~8 words** on the card line. No sentences.
- **NO `(context: ...)` inline.** All context goes in the linked note.
- The card title should be scannable at a glance on a kanban board.
- Use `⛔` to mark blocked items visually.

## Linked Note Format (in kanban-notes/)

```markdown
# Task Name

Brief description of what this is and why it matters.

## Current State

What's the status right now? Blockers, last attempt, etc.

## What to Do

Steps or commands to complete this.

## Relationships

### Blocked by
- ...

### Blocks
- ...
```

Not every section is required. Use what's relevant.

## Rules

- Always read the file first before writing
- Always commit after every change
- Card text MUST be short (title only). Details go in the linked note.
- If the user gives multiple items, add them all in one write + one commit
- Do NOT write to Todo.md (deprecated)
- Do NOT put walls of text in Kanban.md cards
