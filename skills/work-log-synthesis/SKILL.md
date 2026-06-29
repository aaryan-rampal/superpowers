---
name: work-log-synthesis
description: Use when the user says "synthesis", "work log insights", "reflect on my work", or "spaced synthesis"
---

# Work Log Synthesis

Asks targeted questions about past entries and synthesizes insights. Covers all entries missing insights, one by one.

## Orientation

ALWAYS run `date` first to get the current date and day of week.

## Catch-up Logic

Before asking anything:
1. Run `date` to get today's date. Determine yesterday (if today is Monday, yesterday = Friday).
2. Read `/home/aarampal/obsidian/Work Log.md` to get all entries.
3. Read `/home/aarampal/obsidian/Work-Log-Insights.md` (create if missing) to find which entries have insights.
4. Find all entries WITHOUT a corresponding insight, from oldest through yesterday (inclusive).
5. If there are multiple missing days, ask about them **one by one**, oldest first. Complete one day's synthesis fully (questions, approval, commit) before moving to the next.
6. If all entries have insights, tell the user "All caught up on insights!" and stop.

## Flow (per day)

1. Start with the oldest entry missing an insight. **Ask ONE probing question.** Be specific, reference exact things they wrote in that entry.
2. Wait for reply. Ask follow-ups (2-4 total questions) until you have enough depth.
3. Synthesize into 3-5 bullet-point insights. Append to
   `/home/aarampal/obsidian/Work-Log-Insights.md` under header:
   `## Month Day (synthesized Month Day)` (or `## Month Day-Day` for grouped entries).
4. **Commit**:
   ```bash
   cd /home/aarampal/obsidian && git add -A && git commit -m "insights: [date]"
   ```
   Do NOT push.
5. Move to the next missing day, or stop if caught up.

## Good questions

- Why did you choose X over Y?
- What were you uncertain about?
- Did you follow up on [thing mentioned]?
- What would you do differently with hindsight?
- How does this connect to your larger project goals?
- What's the risk if [approach] doesn't work out?
- Does this moment connect to any of the LPs? (e.g. Dive Deep, Ownership, Bias for Action)
- Did anything feel distinctly Amazon about how this played out?

## Bad questions (avoid)

- Generic "how did that go?"
- Anything they already answered in the entry
- Yes/no questions

## Key directories

- Work log: `/home/aarampal/obsidian/Work Log.md`
- Insights file: `/home/aarampal/obsidian/Work-Log-Insights.md`
- Obsidian repo: `/home/aarampal/obsidian/`
