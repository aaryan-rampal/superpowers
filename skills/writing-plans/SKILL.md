---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Early Write Access Check

**CRITICAL FIRST STEP:** Before creating the full plan, test write access:

1. Calculate the full path: `docs/plans/YYYY-MM-DD-<feature-name>.md`
2. Write just the header and title to file

```markdown
# [Feature Name] Implementation Plan
```

3. **If write fails:** Immediately inform user and stop. Do not generate any more content.
4. **If write succeeds:** Proceed with full plan creation.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Remember
- Exact file paths always
- Pseudocode first, tiny snippet(s) only (signatures, short shape examples — NOT complete implementations)
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## Decision Traceability

Each phase in the plan must trace back to decisions in the approved design summary:
- Link phase objectives to specific design decisions
- If a step requires architecture not present in approved design summary, stop and ask; do not infer.
- Document which approved decision each phase implements

## Phase Structure

Every phase MUST include:

```markdown
### Phase N: [Name]
- **Objective:** What this phase accomplishes
- **Approved decisions implemented:** Which design decisions this phase satisfies
- **Pseudocode flow:** High-level logic (not complete code)
- **Tiny snippet(s) only:** Minimal illustrative examples
- **Validation criteria:** How to verify success
- **Language-specific gotchas:** Common pitfalls for this implementation
```

## Guardrails

- **Stop and ask:** If implementation reveals ambiguity requiring architecture change, do not proceed — ask the user
- **No new abstractions:** Do not introduce unapproved patterns or structures during planning

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

**If Parallel Session chosen:**
- **REQUIRED SUB-SKILL:** New session uses superpowers:executing-plans
