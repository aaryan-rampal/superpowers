---
name: work-log-capture
description: Use when the user says "work log", "daily capture", "what did I do today", or "log my work"
---

# Work Log Capture

Captures what the user worked on. If triggered at end of day, target is today. Covers all missed weekdays since the last entry.

## Orientation

ALWAYS run `date` first to get the current date and day of week.

## Catch-up Logic

Before asking anything:
1. Run `date` to get today's date.
2. Read `/home/aarampal/obsidian/Work Log.md`.
3. Determine the last entry date in that file.
4. Calculate all **weekdays** (Mon-Fri) from the day after the last entry through to TODAY (inclusive).
5. If there are multiple missing days, ask about them **one by one**, oldest first. Complete one day's entry fully (draft, approval, commit) before moving to the next.
6. If there are no missing days, say so and stop.

## Flow (per day)

1. Send: "What did you work on [Day, Month Date]?" (If catching up: "You're missing entries for [list of days]. Let's start with [Day, Month Date] — what did you work on?")
2. Wait for user's reply (they'll give a brief, informal summary)
3. **Research**: Use available tools to fill in details they didn't mention:
   - Check git logs in workspace packages (commits from THAT day)
   - Check Slack DMs for relevant context (CRs shared, blockers resolved)
   - Read any files they mention to get accurate details (line counts, function names, etc.)
4. **Draft**: Write a rich entry in their voice. Casual, first-person, stream-of-consciousness.
   Include specifics: file names, line counts, commit subjects, who helped, what was blocked
   and how it got unblocked.
5. **Show the draft** to the user and wait for explicit approval before writing anything.
6. **On approval**: append to `/home/aarampal/obsidian/Work Log.md` with format:
   - Two blank lines
   - `**Month Day**` header (e.g. `**June 16**`)
   - Then the entry text
7. **Commit**:
   ```bash
   cd /home/aarampal/obsidian && git add -A && git commit -m "work log: [date]"
   ```
   Do NOT push.
8. Move to the next missing day, or stop if caught up.

## Tone

Match the style of existing entries in `Work Log.md`. Casual, honest, includes frustrations
and uncertainties. Not corporate. Not polished. Like talking to a friend about your day.

## Enrichment prompts

When drafting or asking follow-up questions, nudge toward these themes if they didn't naturally come up:
- **LP (Leadership Principles)**: Was there a moment that maps to a specific LP? Don't force it -- if it fits, note it in the entry or ask about it.
- **Culture**: Did anything feel distinctly Amazon? Anything surprising, uncomfortable, or interesting about how people work, communicate, or make decisions?

## Key directories

- Workspace: `/home/aarampal/work/onboarding-acis/src/`
- Obsidian: `/home/aarampal/obsidian/`
- Work log file: `/home/aarampal/obsidian/Work Log.md`

## Rules

- Never write to disk without explicit user approval of the draft
- Always read existing entries before drafting to match voice and style
- Specific details beat vague summaries — use actual file names, function names, commit messages
