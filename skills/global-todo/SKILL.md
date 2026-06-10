---
name: global-todo
description: Use when the user says "global todo", "add to global todo", "add this to my todo", or wants to track something for later in a persistent list
---

# Global Todo

## Overview

Manages a persistent todo list at `~/obsidian/Todo.md`. Each item includes brief context so the user knows where it came from when reviewing later.

## When to Use

- User says "global todo", "add to global todo", "add this to my todo list"
- User wants to remember something for later outside the current task

## Steps

1. **Read** `~/obsidian/Todo.md` to see current contents
2. **Append** new item(s) with context note:
   ```
   - [ ] task description (context: brief note — e.g. "from onboarding project", "from ACIS dashboard work")
   ```
3. **Write** the updated file
4. **Commit** the todo file:
   ```bash
   cd ~/obsidian && git add Todo.md && git commit -m "chore: add todo item"
   ```

## Format

```markdown
- [ ] Do the thing (context: what project/conversation this came from)
```

Context should be 3-8 words — just enough to jog memory. Don't write a sentence.

## Rules

- Always read the file first before writing
- Always commit after every change — never leave Todo.md in a dirty state
- Add context even if the user didn't ask for it; they'll thank you later
- If the user gives multiple items, add them all in one write + one commit
