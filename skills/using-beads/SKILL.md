---
name: using-beads
description: Use when working in a repository managed with Beads issue tracker - create issues for discovered work, update status as you progress, manage dependencies, and close when work is complete
---

## IMPORTANT: The --json Flag

Most `bd` commands support `--json` output for programmatic parsing. This is essential when you need to parse command results programmatically.

```bash
bd create "Task" --json          # Returns JSON with issue ID and details
bd list --json                   # Returns all issues as JSON array
bd show <id> --json              # Returns issue details as JSON
```

## Understanding Beads JSON Output Structure

**CRITICAL: Even `bd show --json` for a single issue returns an ARRAY, not a single object.**

### Single Issue Output

```bash
# Command returns: [{"id": "cosmos-explorer-yo6", "title": "...", "status": "open", ...}]
bd show cosmos-explorer-yo6 --json

# CORRECT: Access with array index [0]
bd show cosmos-explorer-yo6 --json | jq '.[0].title'        # → "Tests work..."
bd show cosmos-explorer-yo6 --json | jq '.[0].status'       # → "open"
bd show cosmos-explorer-yo6 --json | jq '.[0].dependents[]'  # → Array of dependent issues

# INCORRECT: Direct access fails
bd show cosmos-explorer-yo6 --json | jq '.title'      # ✗ Error
bd show cosmos-explorer-yo6 --json | jq '.dependents' # ✗ Error
```

### Multiple Issues Output

```bash
# Command returns: [{"id": "...", ...}, {"id": "...", ...}, ...]
bd list --json

# CORRECT: Iterate over array with .[]
bd list --json | jq '.[].title'                            # → All issue titles
bd list --json | jq '.[] | select(.status == "open")'     # → Only open issues
bd list --json | jq '.[] | {id, title, status}'           # -> Specific fields
```

### Key Takeaways

| Command | Returns | jq Pattern |
|---------|---------|------------|
| `bd show <id> --json` | Single-element array `[{...}]` | Use `.[0]` to access properties |
| `bd list --json` | Multi-element array `[{...}, {...}]` | Use `.[]` to iterate elements |
| `bd ready --json` | Multi-element array | Use `.[]` to iterate elements |

## VERY CRITICAL: NEVER Search for .beads Directory

**STOP IMMEDIATELY: Do NOT search for, look for, or check the `.beads/` directory.**

- Run `bd` commands directly without any setup/checks
- If `bd` works, continue working
- If `bd` doesn't work, STOP and ask the user immediately
- NEVER attempt to diagnose or fix installation issues on your own
- NEVER search for `.beads/` directory with `ls`, `find`, `glob`, or any other tool

The presence or absence of `.beads/` is irrelevant. Use the tool; if it fails, escalate to the user.

# Using Beads

## Overview

Beads is a git-native, AI-friendly issue tracker stored in `.beads/` within your repository. Issues live in code, sync with git, and support dependency tracking.

## When to Use

- Repository has `.beads/` directory initialized
- You discover new work to track
- You're claiming work and progressing through it
- You encounter dependencies between tasks
- Work is complete and customer is satisfied

## Core Workflow

### 1. Creating Issues

When you discover work, create an issue immediately:

```bash
bd create "Brief description of work"
```

With options:
```bash
bd create "Add user authentication" -d "Implement OAuth2 with GitHub provider" -p 0 -t feature --json
```

Flags:
- `-d` / `--description`: Detailed explanation
- `-p` / `--priority`: 0-4 (0 = highest)
- `-t` / `--type`: `bug|feature|task|epic|chore|merge-request|molecule|gate|agent|role|rig|convoy|event`
- `--assignee`: Assign to someone (optional)
- `--parent <id>`: Create as child of parent issue (for epic/subtask hierarchy)
- `--json`: Output in JSON format

**Key point:** Create issues when you discover work, not just when explicitly asked. This keeps the repo's work inventory synchronized.

**Important: No 'subtask' type exists** - use `--parent <parent-id>` instead

#### Creating Epic and Subtask Hierarchies

```bash
# First create the epic
bd create "Convert ScreenshotHelper to Singleton" -t epic --json

# Then create subtasks
bd create "Transform ScreenshotHelper.cs to singleton" --parent cosmos-explorer-gih -p 1 --json
bd create "Update FunctionalTest.cs to use Instance" --parent cosmos-explorer-gih -p 2 --json
```

The `--parent` flag automatically creates a `parent-child` dependency between the epic and subtask.

### 2. Updating Status as You Work

When you start work on an issue, immediately update its status:

```bash
bd update <issue-id> --status in_progress --json
```

If work is blocked or needs to be deferred:

```bash
bd update <issue-id> --status blocked --json
bd update <issue-id> --status deferred --json
```

When the work is complete and verified:

```bash
bd close <issue-id> --json
# or
bd update <issue-id> --status closed --json
```

Status values: `open`, `in_progress`, `blocked`, `deferred`, `closed`

### 3. Managing Dependencies

When you discover that one task blocks another, create the dependency:

```bash
bd dep add <blocking-id> <blocked-id> --json
```

This means: `<blocked-id>` cannot proceed until `<blocking-id>` is complete.

Example:
```bash
bd dep add auth-1 frontend-2 --json
```

This means: frontend-2 (UI for login) is blocked by auth-1 (authentication system).

**Alternative syntax** that reads more naturally:
```bash
bd dep add frontend-2 --blocked-by auth-1 --json
bd dep add frontend-2 --depends-on auth-1 --json
```

Both `--blocked-by` and `--depends-on` are aliases with the same meaning.

Check for ready work (no blockers):
```bash
bd ready --json
```

This shows only issues that are open and have no blocking dependencies - perfect for claiming next work.

### 4. Closing Issues

When work is complete and the customer is satisfied:

```bash
bd close <issue-id> --json
```

With reason:
```bash
bd close <issue-id> --reason "Implemented OAuth2 authentication, tested, merged to main" --json
```

## Quick Reference

| Task | Command |
|------|---------|
| Create new issue | `bd create "Description" --json` |
| List all issues | `bd list --json` |
| Show issue details | `bd show <id> --json` |
| Start work | `bd update <id> --status in_progress --json` |
| Mark blocked | `bd update <id> --status blocked --json` |
| Defer issue | `bd update <id> --status deferred --json` |
| View ready work | `bd ready --json` |
| Add dependency | `bd dep add <blocking> <blocked> --json` |
| Check dependencies | `bd dep tree <id> --json` |
| Close issue | `bd close <id> --json` |
| Sync with git | `bd sync --json` |

Add `--json` to any command to get structured JSON output instead of human-readable text.

## Dependency Types

- `blocks`: Task B must complete before task A (most common)
- `related`: Soft connection, doesn't block
- `parent-child`: Epic and subtasks
- `discovered-from`: Auto-created when agent finds related work

## Common Workflow

1. **Discover work** → `bd create "Task name" --json`
2. **Claim it** → `bd update <id> --status in_progress --json`
3. **Implement** → Make code changes
4. **If blocked or deferred** → `bd update <id> --status blocked --json` or `bd update <id> --status deferred --json`
5. **Done** → `bd close <id> --json` (when customer confirms satisfaction)

## Git Sync

Beads automatically syncs with git:
- Issues are exported to `.beads/issues.jsonl`
- Changes are tracked in git
- Pull from remote to import others' issues
- Run `bd sync --json` to explicitly sync with remote

No manual export/import needed - it's automatic.

## Viewing Work

```bash
# List operations (return arrays, use .[] iteration)
bd list --json            # All issues as JSON array
bd list --json | jq '.[] | select(.status == "open")'  # Filter open issues
bd list --json | jq '.[] | {id, title, status}'        # Extract specific fields
bd ready --json           # Issues ready to work (no blockers) as JSON array

# Single issue operations (return single-element array, use .[0] access)
bd show <id> --json      # Issue details as JSON array
bd show cosmos-explorer-yo6 --json | jq '.[0].title'   # Get issue title
bd show cosmos-explorer-yo6 --json | jq '.[0].status'  # Get issue status
bd show cosmos-explorer-yo6 --json | jq '.[0].dependents[] | .id'  # Get subtask IDs

# Dependency operations
bd dep tree <id> --json  # Dependency tree as JSON array
```

**Critical JSON Access Patterns:**
- **`bd show <id> --json`**: Returns `[{"id": "...", ...}]` - Use `jq '.[0].property'`
- **`bd list --json`**: Returns `[{"id": "...", ...}, {"id": "...", ...}, ...]` - Use `jq '.[].property'`
- **`bd ready --json`**: Returns array of ready issues - Use `jq '.[]'` to iterate

**Common Queries:**

```bash
# Get all open issue titles
bd list --json | jq '.[] | select(.status == "open") | .title'

# Get subtask IDs from an epic
bd show cosmos-explorer-yo6 --json | jq '.[0].dependents[] | .id'

# Count issues by status
bd list --json | jq 'group_by(.status) | map({status: .[0].status, count: length})'
```

**Important:** `bd dep tree` shows blocking dependencies only. To see parent-child (epic/subtask) hierarchical relationships, use `bd show <parent-id> --json | jq '.[0].dependents'` instead.

## Common Mistakes

- **Not creating issues for discovered work** → Dependencies become unclear, work inventory invisible
- **Not updating status as you progress** → Team/customer can't see what you're actually working on
- **Forgetting to mark ready before closing** → Customer doesn't know it's waiting for approval
- **Not managing dependencies** → Work gets duplicated or blocked without visibility
- **Creating issues but never closing them** → Database becomes cluttered with stale work

## Known Issues and Limitations

### 1. No Batch Update Capability
There is no `--bulk` or batch update option. Each issue must be updated individually:
```bash
bd update issue-1 --description "..."
bd update issue-2 --description "..."
```

### 2. No Title Update Flag
The `bd update` command does not support updating titles. To change a title, you must delete and recreate the issue (which loses history).

### 3. Closed Tasks Not Visible by Default
Closed issues don't appear in `bd list` output by default. This makes it harder to see the complete picture of work done:
```bash
bd list --json | jq '.[] | select(.status == "closed")'
```

### 4. No Dry-Run Mode
There is no way to preview changes before applying them. Commands execute immediately.

### 5. Dependency Command Order Can Be Confusing
While `bd dep add <blocked> --blocked-by <blocker>` is clearer, the positional syntax `bd dep add <blocker> <blocked>` can be error-prone. Always verify with `bd ready` after adding dependencies.

### 6. Phases Don't Auto-Sequence
When creating phase epics, they all show as "ready" simultaneously by default. You must manually add blocking dependencies between phases:
```bash
bd dep add phase-2 --blocked-by phase-1
bd dep add phase-3 --blocked-by phase-2
```

## Tips for Agents

- Always `bd create` when you discover work, even if small
- Update status frequently to maintain accurate work state
- Use `bd ready` to find next work with no blockers
- Create dependencies proactively when you see ordering constraints
- Close with a reason so others understand what was delivered
