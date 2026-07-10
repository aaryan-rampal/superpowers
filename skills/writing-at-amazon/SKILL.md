---
name: writing-at-amazon
description: Use when drafting or editing any document, doc, or written content meant for an audience other than Aaryan himself — one-pagers, six-pagers/narratives, PR/FAQs, design docs, proposals, alignment docs, status updates, CR descriptions, wiki pages, or anything reviewed by managers, peers, or other teams. Applies whenever the output is prose that another person will read at Amazon.
---

# Writing at Amazon

## Overview

Amazon documents are judged on clarity, honesty, and concision. A capable draft already gets
structure right; what sinks docs is weasel words, assumptions written as fact, and AI
stylistic tells. This skill targets those.

**Core principle:** State what you know flatly, mark what you don't honestly, and cut every
word that isn't doing work. The goal isn't to remove uncertainty — it's to make it legible.

This skill applies to anything another person reads: one-pagers, narratives, PR/FAQs, design
docs, proposals, status updates, CR descriptions, wiki pages, Slack posts that matter. It does
NOT apply to Aaryan's own notes, scratch files, or todos.

**Heavy reference:** `writing-hub-reference.md` (in this skill dir) has the full weasel-word
lists, AI-tell table, document-type structures, formatting rules, and source URLs. Read it
when drafting a formal doc or when you need the complete lists.

## The three failure modes (in priority order)

### 1. Assumptions stated as fact — the most damaging

A draft that says "the morning spike is caused by cold caches" when you have not measured the
correlation is lying to the reader, even if it's a good guess. Reviewers catch this and it
costs you credibility on everything else in the doc.

- **Know it?** State it flat, ideally with the evidence: "p99 rises 07:00–09:00 (dashboard: [link])."
- **Believe it but haven't verified?** Say exactly that, once, and name the step that resolves
  it: "I believe X causes Y, but I haven't confirmed they correlate — that measurement is step one."
- **Genuinely open?** Frame it as a decision or open question, don't pre-decide it in a P.S.

Never let the goal/summary contradict the body (don't say "I must build X" when X already exists).

### 2. Weasel words — claims with no evidence

Amazon maintains a canonical weasel-word list. Two buckets (full lists in the reference):

- **Never use** (add no information): about, believe-as-hedge, could, easy, effectively,
  enable, essentially, key, may, might, seamless, should, streamline, strive, try, typically,
  utilize, very, various, would, leverage, robust.
- **Only with a number** (otherwise unsupported claims): better, comprehensive, efficient,
  faster, few, frequently, high(er), large(r), many, most, optimize, significant(ly), strong.

"Significantly faster" is a weasel phrase. "30% faster (p99 240ms → 168ms)" is a fact. If you
can't attach the number, you don't yet know the thing — say so or go measure it.

Keep honest hedges for real unknowns. The rule is: cut hedging where you actually know the
answer; keep it where you genuinely don't.

### 3. AI stylistic tells — they read as machine-written

Strip these (full table in the reference): em-dash overuse, "X, not Y" antithesis, rule-of-three
filler triples, `— dash` bullet lead-ins (use `**Bold label.**`), Furthermore/Moreover chains,
"It's worth noting that," closing paragraphs that restate the section, "delve/underscore/
testament to/in today's landscape," Title Case Headings, emoji, exclamation marks, hype words.

## Every doc must

1. **Lead with the ask.** First paragraph states the purpose and, if a decision is needed, the
   decision being requested. A reader should know in ~10 seconds why the doc exists.
2. **Define success.** The recommendation carries its own measure of done: "Success: p99 drops
   below X ms with under Y% added cost."
3. **Show the alternatives.** Don't just present one baked answer; lay out the options you
   considered with the load-bearing pros/cons, then pick one. If you can't pick, do more research.
4. **Use active voice and prose.** Say who does what. Bullets are for actual lists, in order of
   importance — prose is the default.
5. **Spell out acronyms on first use.** Outside readers don't know SLAB, ACIS, CCS.

## Document types

Pick structure by type — details and templates in the reference:
- **One-pager:** problem → solution → metrics, compressed. Alignment and high-level decisions.
- **Six-pager/narrative:** Purpose → Background → Problem → Recommendations (options + one pick)
  → Next steps → Appendices (reference-only). Six pages of narrative, hard limit.
- **PR/FAQ:** customer-perspective press release (≤1 page) + FAQs + visuals. Working Backwards.

Don't over-format for the doc type. Tenets, FAQs, and a strict template are overkill for a
simple alignment doc; don't force a formal skeleton onto a scoping note.

## Formal-doc attention-to-detail

For docs that get reviewed formally (S-Team-style), missing these reads as carelessness:
number every page, footer "Amazon Confidential," consistent font/spacing/margins, acronyms
spelled out, consistent capitalization of recurring terms. See the reference for specifics.

## Workflow

1. Draft with the structure for the doc type. Lead with the ask, define success.
2. Pass for failure mode 1: every factual claim — do you know it, believe it, or is it open?
   Rewrite each accordingly. (No tool catches this; it needs judgment.)
3. Run the deterministic checker (below) for failure modes 2 and 3. Fix each finding: attach a
   number, cut the word, or rewrite the tell. Re-run until it reports what's left is intentional.
4. For high-stakes docs, dispatch a reviewer subagent (see below) and address what it finds.
5. Read it aloud in your head; cut anything that isn't carrying weight.

## Deterministic checker

After drafting, run `check_writing.py` (in this skill dir) on the file. It flags what's
mechanically detectable — weasel words (both lists), "X, not Y" antithesis, em-dashes, hype
words, Title-Case headings, and the other AI tells — with the exact match and surrounding lines
so you know where to rewrite. It does NOT judge failure mode 1 (assumptions-as-fact) — that's
still on you.

```bash
uv run /local/home/aarampal/repos/superpowers/skills/writing-at-amazon/check_writing.py DOC.md
```

Each finding gives the category, why it's flagged, the matched span, and context before/after.
It reports no fix by design — read the line and rewrite it yourself. A clean exit (code 0) means
nothing matched; remaining findings should be ones you've decided are intentional (a real list
that reads as a filler triple, a `believe` that honestly marks an unknown). Flags: `--json`,
`--context N`, `--include-code` (code fences are skipped by default), `-` for stdin.

## Reviewer subagent (for high-stakes docs)

For docs going to a manager or skip-level, dispatch a subagent framed as a skeptical reviewer
with Writing Hub access. Past reviews caught: inconsistent decision numbering breaking
cross-references, a load-bearing fact left hedged with no evidence, the same item described as
working in one section and broken in another, undecoded acronyms, key terms never defined, and
real decisions buried in a P.S. Have it flag claims doing persuasive work without support.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| "X is caused by Y" when unverified | "I believe X is caused by Y; confirming it is step one." |
| "significantly faster," "much better" | Attach the number, or cut the adjective. |
| Removing all hedges to sound confident | Keep hedges for real unknowns; cut only where you know the answer. |
| No ask, doc opens with background | First paragraph states the purpose and the decision needed. |
| Recommendation with no success measure | Add "Success: [metric] reaches [target]." |
| One answer presented as the only option | Show the alternatives you considered with pros/cons. |
| Em-dashes, "not just X but Y," filler triples | Plain punctuation; one clear claim. |
| Acronyms undefined for outside readers | Spell out on first use. |
| Goal/summary contradicts the body | Make them consistent; the summary states what the body proves. |
