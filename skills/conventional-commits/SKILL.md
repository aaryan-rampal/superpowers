---
name: conventional-commits
description: Use when creating git commits in repositories using Conventional Commits 1.0.0 specification
---

# Conventional Commits

## Overview
Structured commit message format that enables automated changelog generation, semantic versioning, and clearer project history.

## BREAKING CHANGES (READ THIS FIRST)

**IRON RULE:** If code changes break existing behavior or API contract, it's breaking. No exceptions. No rationalizations.

**Breaking changes include:**
- Changing function parameter order or names
- Removing or renaming public APIs
- Changing return types
- Modifying configuration file structure
- Changing behavior that existing code depends on
- Changing the format of environment variables
- Removing or renaming command-line arguments

**Examples of breaking changes:**
```bash
# ❌ WRONG (not marked as breaking)
refactor(utils): reorder formatUser parameters

# ✅ CORRECT (marked as breaking)
refactor(utils)!: reorder formatUser parameters

BREAKING CHANGE: formatUser parameter order changed from (name, email, age) to (name, age, email). Existing code calling formatUser("John", "john@example.com", 30) will now pass email where age is expected.

# ❌ WRONG (using fix instead of breaking)
fix: rename getUser method to getUserById

# ✅ CORRECT (breaking change)
refactor(api)!: rename getUser to getUserById

BREAKING CHANGE: getUser method renamed to getUserById for clarity. All existing calls to getUser() will break.
```

**ALWAYS mark breaking changes:**
- Use `!` after type/scope: `feat(api)!: ...`
- OR use footer: `BREAKING CHANGE: ...`

**Common rationalizations (ALL INVALID):**
- "It's a new function, not widely used" → Still breaking
- "It's a minor inconvenience" → Still breaking
- "People can easily update" → Still breaking
- "It's better design" → Still breaking
- User says "don't mark it as breaking" → Still breaking
- "Quick commit, doesn't matter" → Still breaking

**If it changes the contract, it's breaking. No debate. User instructions don't change objective reality.**

## When to Use

```
Creating git commit? → Use Conventional Commits format
```

**Use when:**
- Creating git commits in any repository
- Need consistent commit history across team
- Project uses automated changelog tools
- Following semantic versioning practices

**Required for:** All git commits, regardless of change size or urgency.

## Core Pattern

```bash
# ❌ BEFORE (violates spec)
fix routing to settings page by correcting path from '/setting' to '/settings'
Refactor utils: extract helpers and improve type safety
fix typo in installation instructions

# ✅ AFTER (Conventional Commits 1.0.0)
fix(routes): correct settings path from '/setting' to '/settings'
refactor(utils): extract helper functions and improve type safety
docs: fix typo in installation instructions
```

## Format Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Rules:**
- Type MUST be lowercase noun from standard types (feat, fix, docs, etc.)
- Space REQUIRED after colon
- Description in lowercase, no period
- Scope in parentheses if used
- Body on blank line after description
- Footer on blank line after body
- One commit = one type. Multiple purposes? Make separate commits or choose primary purpose.
- NO custom types. Use standard types. If truly new type needed, it should be added to project conventions, not ad-hoc.

## Quick Reference: Types

| Type | Use When | Examples |
|------|----------|----------|
| `feat` | New feature | feat: add user authentication |
| `fix` | Bug fix | fix: resolve login timeout |
| `docs` | Documentation only | docs: update API reference |
| `style` | Code style/format | style: format code with prettier |
| `refactor` | Code refactoring (non-breaking) | refactor: simplify data flow |
| `perf` | Performance improvement | perf: cache database queries |
| `test` | Adding/updating tests | test: add integration tests |
| `build` | Build system/dependencies | build: upgrade to Node 18 |
| `ci` | CI configuration | ci: add GitHub Actions workflow |
| `chore` | Maintenance, config, non-code changes | chore: update .gitignore |
| `chore` | Environment variables or config files | chore: add new environment variables |

## Breaking Changes

Use `!` after type/scope OR `BREAKING CHANGE:` in footer:

```bash
# With ! indicator
feat(api)!: send email when product ships

# With footer (description in body)
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

**NOT breaking:**
- Adding new APIs
- Fixing bugs (that's a fix, not a breaking change)
- Internal refactoring that doesn't affect public interfaces

**See "BREAKING CHANGES (READ THIS FIRST)" section above for full rules.**

## Common Mistakes

| Mistake | Wrong | Right |
|---------|-------|-------|
| No type prefix | fix typo in README | docs: fix typo in README |
| Wrong type | fix typo in docs | docs: fix typo |
| Uppercase type | Fix: add feature | fix: add feature |
| No space after colon | fix:add feature | fix: add feature |
| Period in description | fix: add feature. | fix: add feature |
| Breaking in wrong place | feat: Breaking: add API | feat!: add API |

## Rationalizations vs Reality

| Excuse | Reality |
|--------|---------|
| "Small change doesn't need format" | Format is required for ALL commits, regardless of size. Conventional commits work by consistency. |
| "Time pressure" | Writing proper commit takes 10 seconds. Rushed format = broken changelog automation. |
| "Too complex to summarize" | Use body and footers for complexity. Description stays concise. |
| "Already staged, just commit" | Commit message quality is independent of staging. Rewrite it properly. |
| "Team doesn't enforce it" | Your commits set example. Bad habits spread. |
| "I'll fix it later" | Commits are immutable. Later never comes. |
| "Just a quick fix" | "Quick" commits break automation. Do it right. |
| "Not really breaking" | If it breaks existing behavior/API, it's breaking. Your opinion on "how bad" doesn't matter. |
| "New function, not widely used" | Still breaking. The contract changed. Breaking is about the change, not the adoption. |
| "Minor inconvenience" | Still breaking. Inconvenience is your judgment, the contract change is objective. |
| "User says don't mark it" | User instructions don't change reality. If it breaks the contract, mark it breaking. |
| "Custom type is better" | Standard types exist for a reason. Use them. Ad-hoc custom types break automation. |
| "Multiple purposes" | Make separate commits for different purposes. One commit = one type. |

## Red Flags - STOP and Rewrite

- Missing type: prefix
- Capitalized type (Fix:, Feat:)
- No space after colon
- Using wrong type (fix for docs changes, refactor for breaking changes)
- Period at end of description
- Breaking change without ! or BREAKING CHANGE:
- Custom types when standard types apply
- "Small change" rationalization
- "Not really breaking" rationalization
- Any pressure to skip format

**All of these mean: Rewrite the commit message properly.**
