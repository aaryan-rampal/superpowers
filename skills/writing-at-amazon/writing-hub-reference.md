# Writing Hub Reference

Lookup material for `writing-at-amazon`. Authoritative sources are Amazon's internal
Writing Hub and Working Backwards wikis. Read the live pages with `ReadInternalWebsites`
(Midway-authenticated) when you need the full text — links are below.

## Canonical sources (cite these)

| Topic | URL |
|-------|-----|
| Writing Hub home | https://w.amazon.com/bin/view/WritingHub/ |
| Narrative guidance (structure) | https://w.amazon.com/bin/view/WritingHub/Document_Repository/Narrative/ |
| Standard document templates | https://w.amazon.com/bin/view/WritingHub/Resources/Writing_Handbook/Template |
| Document repository (templates + examples + Doc Bar Raiser) | https://w.amazon.com/bin/view/WritingHub/Resources/Document_Repository/ |
| Working Backwards — PR/FAQ | https://w.amazon.com/bin/view/WorkingBackwards/PRFAQS/ |
| PR/FAQ examples | https://w.amazon.com/bin/view/WorkingBackwards/PRFAQExamples/ |
| 5 Customer Questions (lightweight precursor) | https://w.amazon.com/bin/view/WorkingBackwards/5QCS/ |
| Weasel Words (the canonical list) | https://w.amazon.com/bin/view/WeaselWords/ |
| Weasel-word detection scripts | https://w.amazon.com/bin/view/WeaselWordsScripts |
| Field Engineering doc/narrative tips + formatting | https://w.amazon.com/bin/view/Field_Engineering/Process/DocAndNarrativeWriting/ |
| Example index + downloadable templates | https://w.amazon.com/bin/view/B2B/pastot/Writing-Guide-Examples/ |

Tools the hub points to: Doc Bar Raiser Reviewer
(https://console.harmony.a2z.com/doc-bar-raiser-reviewer/), Working Backwards AI, Pippin.

## Full weasel-word lists

**Never use (these add no information — delete or replace):**
about, aim to, believe, could, easy, effectively, enable, essentially, expect, key, may,
might, seamless / seamlessly, should, streamline, strive, synergy, think, try, typically,
utilize, very, various, would.

**Use only with a number attached (otherwise they are claims with no evidence):**
always, better, comprehensive, efficient, faster, few, frequently, high / higher, large /
larger, many, most, optimize, significant / significantly, strong / strongly, worse.

> "leverage," "robust," and "comprehensive" are common AI tells *and* weasel words. Double offense.

**Status words in plans** — replace vague status with quantified status:
- "Green" → "X of Y milestones done" or "ETA earlier than target date."
- "Yellow" → why the milestone is at risk and the specific action that brings it to Green. If
  there's no such action, the status is actually Red.

**Code/class naming** is covered too: `BeerUtility`, `BeerHelper`, `Constants` are weasel
names. "All classes should be useful, or you should delete them."

## AI writing tells to strip

These are not Amazon-specific but they read as machine-generated and undercut credibility.

| Tell | Fix |
|------|-----|
| Em-dash overuse ("— the expensive part —") | Use colons, commas, or periods. Reserve em-dashes for rare emphasis. |
| Antithesis: "X, not Y" / "It's not just X, it's Y" | State the positive claim once. |
| Rule-of-three filler triples ("fast, reliable, and scalable") | Keep the one that carries weight. |
| `— dash` bullet lead-ins | Use `**Bold label.**` lead-ins instead. |
| Furthermore / Moreover / Additionally chains | Start the sentence with its subject. |
| "It's worth noting that," "It's important to," "Notably" | Delete; just state the thing. |
| Closing paragraphs that restate the section | Cut. The reader just read it. |
| "delve," "navigate the complexities," "underscore," "testament to," "in today's landscape" | Plain verbs. |
| Title-Case Headings With A Colon: Subtitle | Sentence case, no decorative subtitle. |
| Emoji, exclamation marks, hype ("HUGE," "game-changer") | Remove. |

## Document-type structures

### One-pager
Communicates the high-level goal, tenets, and design of a project; forces crispness about
value. "Often actually a two-pager — no strict limit." Same skeleton as the six-pager,
compressed: problem → solution → metrics. Lets the audience understand the project, weigh
benefits and risks, and make a high-level call quickly.

### Six-pager / narrative
Hard rule: six pages of narrative, unlimited appendices. The narrative must stand on its own;
appendices are reference-only (not overflow). Typical sections:
1. **Purpose** — reason for the doc, summary recommendation, immediate action required.
2. **Background** — context the reader needs; active voice, who did what.
3. **Problem / opportunity** — the situation, with data.
4. **Recommendations** — usually several options, one final pick (the one with the most pros).
5. **Next steps** — scope, schedule, staffing, cost.
6. **Appendices** — contributors, FAQs, supporting data, tenets.

Tenets go near the front when readers are new to the space, or in the appendix (where they
risk going stale). FE simplified default: Purpose → Background/Current state → Proposed
solution → Next steps. Delete any section you don't need.

### PR/FAQ (Working Backwards)
Three parts: **Press release** (≤ 1 page, never more), **FAQs**, **Visuals**. Whole thing ≤ 6
pages. Written from the customer's perspective before building. Many teams start with the
lighter **5 Customer Questions** doc.

PR paragraph order: heading (headline + one-sentence gist + future launch date) → summary and
who the customer is → opportunity/problem → solution → quote from a real Amazon leader (don't
invent it) → customer experience → customer testimonial (specific, believable) → call to
action → footer "Amazon Confidential."

FAQ = customer questions (problem, who, pricing, function, limits) + internal questions
(feasibility, build, risk, success metrics). For open questions, write "TBD" plus how and when
you'll resolve it — don't drop them.

## Attention-to-detail / formatting (formal docs)

Reviewers read these as signals of care. From FE/S-Team formatting guidance:
- **Footer:** number every page and include "Amazon Confidential."
- **Font:** Calibri 10pt minimum, consistent.
- **Spacing:** single (before 0pt / after 0pt). **Margins:** ≥ 1 inch.
- **Acronyms:** spelled out on first use.
- **Lists:** only for actual lists, ordered by importance.
- **Numbers:** spell out below 10; "MM" = millions, "K" = thousands; full years (no "'15");
  consistent capitalization and spelling of recurring terms (YoY, S-Team, WW, Buy Box).

## Checklists to run against

**Writing Hub final checklist:** clear purpose; data describing the problem; recommended
solution and next steps; data supporting the recommendation; concise style with no subjective
descriptors or vague words; visually clean; addresses likely concerns; ≤ 6 pages + appendices;
supporting data in appendices; reviewed by others.

**Field Engineering four questions:** Is it clear? Is it data-focused? Is it tested? Is it
concise?

**Decision rules:** the 70% rule (decide with 70% of the information; if you can't pick a path,
do more research). The Bezos rule (2017 shareholder letter): great memos are written,
rewritten, shared, set aside, and edited with a fresh mind — "a great memo probably should take
a week or more."

## Worked example: a one-pager, before and after

**Before (baseline draft — structure is fine, but note the flagged spans):**

> RecommendationService p99 latency spikes every morning. The pattern lines up with our
> nightly deploy cycle: each deploy brings up fresh hosts with empty caches, and a meaningful
> fraction of requests fall through to the slower backend path. A nightly cache-warming job
> would smooth this out and give us more predictable dashboards. We should warm the
> high-value entries and it's worth measuring the cost.

Problems: "lines up with" and "a meaningful fraction" state an unverified hypothesis as fact;
"smooth," "more predictable," "high-value," "worth measuring" are weasel words; no ask, no
success measure.

**After:**

> **Ask:** approve a one-week prototype of a nightly cache-warming job for
> RecommendationService, measured by morning p99 reduction against added compute cost.
>
> RecommendationService p99 rises every morning between 07:00 and 09:00 (dashboard: [link]).
> Each nightly deploy brings up hosts with cold caches; I believe the morning spike is the
> cold-cache penalty, but I have not yet confirmed the two correlate — that measurement is
> step one. A warming job that replays recent high-frequency request keys against the new
> fleet after deploy would populate caches before traffic ramps. Success: p99 in the 07:00–09:00
> window drops below [target] ms with under [N]% added backend call volume.

Note what changed: the ask leads; the success measure is explicit; the unknown ("I haven't
confirmed they correlate") is stated once and paired with the step that resolves it; weasel
words are gone; the known facts are stated flat.
