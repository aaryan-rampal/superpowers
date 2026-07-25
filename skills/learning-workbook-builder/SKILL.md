---
name: learning-workbook-builder
description: Use when someone wants to learn a specific topic or skill under a deadline (days to a few weeks), or to get ready to defend or extend their own work — a notebook, codebase, or paper — including from scratch with no background. Triggers include "make me a study plan or course for X", "get me ready for my interview or exam on Y by <date>", "help me learn the concepts in this repo". Not for open-ended, no-deadline mastery.
---

# Learning Workbook Builder

## Overview

Build a deadline-bound, module-structured learning workbook for one learner. The spine is a **prerequisite graph grounded in fetched authoritative sources**. An artifact the learner owns (notebook, repo, paper), if one exists, is *supplementary* grounding — not the only source, and never the only check.

**Core principle:** the hard, valuable work is producing a *correct, source-grounded prerequisite graph*. The sequencing algorithm is trivial. So put effort into grounding and verification, not clever scheduling — and **never let the model perform the verification or the ordering in its head; run the script.**

## When to use

- "Learn X by `<date>`", "study plan / crash course", "prep for my interview or exam", "get me able to defend or extend this notebook/repo".
- Horizon is bounded and short (days to ~1 month) and focused. Break a big goal into smaller deadline-bound chunks and run this per chunk.

**Not for:** open-ended "get good over months with no test" (needs a feedback-driven review scheduler — out of scope); single-fact lookups.

## Workflow

**1. Interrogate first — do not assume.** Ask (use the question tool):

- the *capability* — a verb plus a performance event (defend / extend / pass / ship), not just a topic;
- the **deadline** and hours/day — an input you gather, never a default;
- background, and any evidence of it; the **artifact** to ground in, if one exists (read it fully);
- method preferences and vetoes;
- whether they want **autograded test cells** in the notebooks — warn that generating and running these can burn a lot of tokens, so default to off unless they opt in.

Confirm the answers back before building.

**2. Research and ground — always, even with an artifact.** Fetch authoritative sources for the domain (syllabi, textbook tables of contents, canonical papers/docs). Detect the regime: *artifact + background* vs *cold-start, no background*. In cold-start, build the graph from fetched sources, never from model memory.

**3. Build the prerequisite graph (your judgment).** Concepts are nodes; "A before B" is an edge. Each node and edge **must cite a source** (a URL or `artifact:<loc>`). Weight each node `core/high/medium` by hunting **threshold concepts** — transformative, counter-intuitive, gateway ideas; this is a property of the *domain*, so it needs no learner model. Mark each node's `delta` from the learner's background. Emit as JSON — see `example-graph.json`.

**4. Validate and order — deterministic, run it.**

```
python3 validate_graph.py graph.json
```

It fails loudly on cycles, missing provenance, and dangling references, and prints the teaching order. **Paste its real output. Do not hand-sort, and do not assert "it's valid" — that is the exact failure this step exists to prevent.**

**5. Reconcile artifact vs. canon.** When they disagree: *minor* (both valid, stylistic) → annotate inline and continue. *Major* (hits a core/threshold concept, or changes the order) → escalate: **ask the user** in the artifact regime (they know their own work best); **defer to the most authoritative source** in cold-start (the user has no basis to adjudicate). Never silently overwrite the artifact — the divergence is often the most valuable thing to study.

**6. Author modules in the validated order**, as Jupyter notebooks, keeping the learn → immediately-practice loop. Write each module first as a jupytext *percent* `.py` (`# %%` code cells, `# %% [markdown]` prose), then convert and delete the source (requires `pip install jupytext`):

```
jupytext --to notebook NN-topic.py && rm NN-topic.py
```

Each module, in cells:

1. why it's here (tie to artifact/source) → 2. your delta → 3. one curated source with "watch for X" → 4. first principles → 5. practice: warm-up / core / stretch → 6. connect to the artifact → 7. solution behind an attempt-first gate.

**Author each practice item with a one-line *purpose*** — the single new thing it tests. The purpose is a spoiler: ship it hidden with the solution behind the gate, never above the problem. No two items in a module share a purpose unless the repetition is deliberate (drill → formalize); deliberate repetition gets a visible label ("same content on purpose — the new thing is X"), which is method legibility, not a spoiler. Unlabeled duplication reads as the course not noticing it repeated itself.

**Curated reading must be span-precise and from the graph's own sources.** "One curated source" means a specific section / page range / timestamped segment of an authoritative source — ideally one the graph already cites as provenance — plus a one-line "watch for X". Never "go read this site". For threshold concepts, prefer the primary source (the paper, the canonical text) over secondary explainers: the learner should regularly read real, verifiable prose that no LLM synthesized, and the course should visibly outsource what the canon already wrote better (this is the cheap hedge against LLM-authored-everything bias).

**Refresher nodes with prior evidence: ask what the learner optimizes before shortening anything.** A test-out (re-attempt 2–3 of their own old problems cold; pass → skip ahead; fail → expand only the rungs missed) is right only when the goal is time-boxed coverage — and even then, offer it, don't impose it. Learners who chose the topic for depth or joy often want to re-learn, not skip ("I want to learn this again" is a real answer; respect it, learned the hard way). For those learners, prior mastery makes the module *richer*, not shorter: keep the full module and weave 1–2 of their own old problems in as cold **rematches** — restate the problem verbatim, they re-solve from scratch, grade on the normal rubric, THEN they diff against their old write-up in a few sentences. Their own old problems beat any bank: retrieval practice with a personal baseline. Old solutions are post-grade comparison, never cribs — and never spoil in the problem statement what the old attempt got wrong; catching it is the payoff. Either way: the plan's calendar deadlines are the clock; don't add per-module stopwatches unless the learner asks. Expect first-attempt rust when the evidence is years old; grade the final attempt, don't auto-expand on friction.

**Fade the scaffolding — within each module, not just across the course.** An all-scaffolded module reads as the course not trusting the learner (live-course feedback). Reserve step-by-step skeletons for genuinely non-obvious tricks; give other items claim-only with a *hint gate* separate from the solution gate; make at least one item per module fully cold once the learner has the mechanics. Hand over more structure each module — the learner should feel the guardrail let go. Cold ≠ lower bar: everything is graded on the same rubric.

**Use Mermaid freely.** Put mental-model diagrams in `# %% [markdown]` cells — the prerequisite graph, data/architecture flow, decision trees. They render in VS Code and JupyterLab, and a picture of the structure beats a paragraph. Don't be shy.

**Autograded tests are opt-in — only if the learner said yes in intake** (they burn tokens). When on, ship `checks.py` next to the notebooks, `from checks import *`, and add a test cell after each practice block. Prefer **property tests**: `check_fn(name, your_fn, ref_fn, cases)` verifies the learner's formula against a reference on many inputs *without revealing the closed form*. The loop is fill-a-stub → run-the-cell → ✅/❌/⬜.

If the horizon is more than ~a week, add light spaced re-exposure: bring a core concept back as an interleaved problem in a later module. Do not build a formal spacing scheduler — not worth it at this scale.

**Horizon honesty — state what the timeline buys; never hide the tradeoff.** If ≤ ~2 days: this is a cramming layout — strong for the event, weak for retention past it. Say so plainly, and switch to retrieve-to-criterion (recall each core concept correctly 2–3× across the sessions available) instead of calendar spacing. If ≤ ~1 week and high-stakes, default to successive relearning to criterion over calendar spacing. Never present a plan whose retention the horizon can't deliver as if it were complete.

**Verify re-exposure coverage — don't assert it.** After authoring, emit a short ledger in `00-intake.md`: one row per core/threshold concept → where first taught, where it recurs as an interleaved problem. Zero recurrences → add a callback, or flag it with the reason (e.g. prereq-bound too late in the sequence). This is the spacing analogue of `validate_graph.py`: coverage is checked, not narrated. Tag each deliberate re-exposure in the module (`↻`) so the learner sees the spacing is intentional, not redundant.

**7. If the event is spoken** (interview/defense), emit a *separate* speak-it-cold Q&A instrument; articulation under retrieval is its own skill.

## Who owns what

| Step | Owner |
|---|---|
| Intake answers (esp. the deadline) | the **user** (ask) |
| Sources, graph, weights, module prose | the **agent** (grounded + cited) |
| Cycle / provenance / dangling checks + ordering | the **script** (executed) |
| Major artifact-vs-canon conflict, artifact regime | the **user** |
| Autograded test cells (opt-in) | the **agent**, via `checks.py` |

## Common mistakes

- **Performing the sort/validation instead of running `validate_graph.py`.** A model narrating an algorithm is not executing it; it misses cycles and drifts between runs.
- Generating the graph from model memory instead of fetched sources (hallucinated prerequisites).
- Letting canon silently overwrite the learner's artifact.
- Assuming intake — especially the deadline — instead of asking.
- Over-building: formal Knowledge Space Theory or a spacing scheduler is unnecessary at this horizon (KST is a later upgrade).
- Adding autograded tests without asking — they cost tokens; confirm in intake first.
- **Imposing an opaque pipeline.** Make the method legible — show *why* the loop and the re-exposure
  are there; gather method vetoes at intake and honor them. Over-prescriptive, unexplained learning
  systems are a known failure mode.
- Shipping the intermediate `.py` instead of converting to `.ipynb` and deleting the source.

## Evidence base

Threshold concepts (Meyer & Land) for learner-independent weighting; knowledge components / KLI (Koedinger 2012) for decomposition; grounding-as-verification (RAG) against LLM curriculum hallucination; spacing and retrieval practice (Cepeda 2008; Dunlosky 2013), applied lightly and only above a ~1-week horizon.
