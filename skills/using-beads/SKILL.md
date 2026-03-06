---
name: using-beads
description: Use when working in a repository managed with Beads issue tracker - create issues for discovered work, update status as you progress, manage dependencies, and close when work is complete
---



---

## IMPORTANT: The --json Flag

Most `bd` commands support `--json` output for programmatic parsing. Add `--json` to get structured JSON output instead of human-readable text. This is essential when you need to parse command results programmatically.

Example:
```bash
bd create "Task" --json          # Returns JSON with issue ID and details
bd list --json                   # Returns all issues as JSON array
bd show <id> --json              # Returns issue details as JSON
```

When in doubt, add `--json` to any command.

---

## Understanding Beads JSON Output Structure

**CRITICAL: Even `bd show --json` for a single issue returns an ARRAY, not a single object.**

### Single Issue Output Structure

```bash
# Command returns: [{"id": "cosmos-explorer-yo6", "title": "...", "status": "open", ...}]
bd show cosmos-explorer-yo6 --json
```

**CORRECT: Access with array index `[0]`:**
```bash
bd show cosmos-explorer-yo6 --json | jq '.[0].title'        # → "Tests work..."
bd show cosmos-explorer-yo6 --json | jq '.[0].status'       # → "open"
bd show cosmos-explorer-yo6 --json | jq '.[0].dependents[]'  # → Array of dependent issues
```

**INCORRECT: Direct access fails:**
```bash
bd show cosmos-explorer-yo6 --json | jq '.title'      # ✗ Error: Cannot index array with string "title"
bd show cosmos-explorer-yo6 --json | jq '.dependents' # ✗ Error: Cannot index array with string "dependents"
```

### Multiple Issues Output Structure

```bash
# Command returns: [{"id": "...", ...}, {"id": "...", ...}, ...]
bd list --json
```

**CORRECT: Iterate over array with `.[]`:**
```bash
bd list --json | jq '.[].title'                            # → All issue titles
bd list --json | jq '.[] | select(.status == "open")'     # → Only open issues
bd list --json | jq '.[] | {id, title, status}'           # -> Specific fields
```

### Practical Examples

```bash
# Get all subtask IDs from an epic
bd show cosmos-explorer-yo6 --json | jq '.[0].dependents[] | .id'

# Count open issues
bd list --json | jq '[.[] | select(.status == "open")] | length'

# Get issue by ID from list
bd list --json | jq '.[] | select(.id == "cosmos-explorer-yo6")'

# Extract specific nested property
bd show cosmos-explorer-yo6 --json | jq '.[0].dependents[] | .title'
```

### Key Takeaways

| Command | Returns | jq Pattern |
|---------|---------|------------|
| `bd show <id> --json` | Single-element array `[{...}]` | Use `.[0]` to access properties |
| `bd list --json` | Multi-element array `[{...}, {...}]` | Use `.[]` to iterate elements |
| `bd ready --json` | Multi-element array | Use `.[]` to iterate elements |

---

## VERY CRITICAL: NEVER Search for .beads Directory

**STOP IMMEDIATELY: Do NOT search for, look for, or check the `.beads/` directory.**

This is ALWAYS a waste of time and annoys the user.

- Run `bd` commands directly without any setup/checks
- If `bd` works, continue working
- If `bd` doesn't work, STOP and ask the user immediately
- NEVER attempt to diagnose or fix installation issues on your own
- NEVER search for `.beads/` directory with `ls`, `find`, `glob`, or any other tool

The presence or absence of `.beads/` is irrelevant. Use the tool; if it fails, escalate to the user.

---

# Using Beads



## Overview



Beads is a git-native, AI-friendly issue tracker stored in `.beads/` within your repository. Issues live in code, sync with git, and support dependency tracking. When working in a Beads-managed repo, you create issues for work, update their status as you progress, manage dependencies between tasks, and close them when complete.



## When to Use



- Repository has `.beads/` directory initialized
- You discover new work to track
- You're claiming work and progressing through it
- You encounter dependencies between tasks
- Work is complete and customer is satisfied



## Core Workflow



### 1. Creating Issues



When you discover work (either assigned by the user or discovered during investigation), create an issue immediately:



```bash
bd create "Brief description of work"
```



For more detail:
```bash
bd create "Add user authentication" -d "Implement OAuth2 with GitHub provider" -p 0 -t feature --json
```



Flags:
- `-d` / `--description`: Detailed explanation
- `-p` / `--priority`: 0-4 (0 = highest)
- `-t` / `--type`: `bug|feature|task|epic|chore|merge-request|molecule|gate|agent|role|rig|convoy|event`
  - **Important: No 'subtask' type exists** - use `--parent <parent-id>` instead
- `--assignee`: Assign to someone (optional)
- `--parent <id>`: Create as child of parent issue (for epic/subtask hierarchy)
- `--json`: Output in JSON format (good for programmatic parsing)



**Key point:** Create issues when you discover work, not just when explicitly asked. This keeps the repo's work inventory synchronized.

#### Creating Epic and Subtask Hierarchies

To create a subtask of an existing epic, use the `--parent` flag:

```bash
# First create the epic
bd create "Convert ScreenshotHelper to Singleton" -t epic --json

# Then create subtasks
bd create "Transform ScreenshotHelper.cs to singleton" --parent cosmos-explorer-gih -p 1 --json
bd create "Update FunctionalTest.cs to use Instance" --parent cosmos-explorer-gih -p 2 --json
```

The `--parent` flag automatically creates a `parent-child` dependency between the epic and subtask. This is the correct way to create hierarchical work - do NOT use a "subtask" issue type (it doesn't exist).



### 2. Updating Status as You Work



When you start work on an issue, immediately update its status:



```bash
bd update <issue-id> --status in_progress --json
```



If work is blocked or needs to be deferred, update its status:



```bash
bd update <issue-id> --status blocked --json
bd update <issue-id> --status deferred --json
```



When the work is complete and verified, close the issue:



```bash
bd close <issue-id> --json
# or
bd update <issue-id> --status closed --json
```



Status values: `open`, `in_progress`, `blocked`, `deferred`, `closed`



### 3. Managing Dependencies



When you discover that one task blocks another, create the dependency:

**CRITICAL SYNTAX:**
```bash
bd dep add <blocked-id> <blocking-id> --json
```

- `<blocked-id>`: The issue that cannot proceed (depends on the blocker)
- `<blocking-id>`: The issue that must complete first (blocks the other)

**Mnemonic:** First argument is the issue being acted upon (the one that gets a blocker added), second is what it depends on.

**Example:**
```bash
bd dep add frontend-2 auth-1 --json
```
This means: frontend-2 (UI for login) depends on auth-1 (authentication system). In other words: auth-1 blocks frontend-2.

**To remove a dependency:**
```bash
bd dep remove <blocked-id> <blocking-id> --json
```



Check for ready work (no blockers):
```bash
bd ready --json
```

**Checking What An Issue Depends On (Blockers):**
```bash
bd show frontend-2 --json | jq '.[0].dependencies[] | select(.dependency_type == "blocks") | .id'
```
This returns the IDs of issues that block `frontend-2`.

**Checking What Blocks An Issue:**
```bash
bd show frontend-2 --json | jq '.[0].dependencies[] | select(.dependency_type == "blocks") | .id'
```
Same as above - use `bd show <id>` and look at the `dependencies` array.

**Checking What An Issue Blocks (Dependents):**
```bash
bd show auth-1 --json | jq '.[0].dependents[] | select(.dependency_type == "blocks") | .id'
```
This returns the IDs of issues that are blocked by `auth-1`.

**Key Data Structures:**
- `.dependencies[]`: Issues that THIS issue depends on (blockers)
- `.dependents[]`: Issues that depend on THIS issue (tasks it blocks)
- `.dependency_type`: Type of relationship ("blocks", "related", "parent-child", "discovered-from")



This shows only issues that are open and have no blocking dependencies - perfect for claiming next work.



### 4. Closing Issues



When work is complete and the customer is satisfied, close the issue:



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
| Add dependency (A is blocked by B) | `bd dep add <blocked-id> <blocking-id> --json` |
| Remove dependency | `bd dep remove <blocked-id> <blocking-id> --json` |
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
bd list --json            # All issues as JSON array
bd list --json | jq '.[] | select(.status == "open")'  # Filter open issues
bd list --json | jq '.[] | {id, title, status}'        # Extract specific fields
bd ready --json           # Issues ready to work (no blockers) as JSON array

# Single issue operations (return single-element array, use .[0] access)
bd show <id> --json      # Issue details as JSON array
bd show cosmos-explorer-yo6 --json | jq '.[0].title'   # Get issue title
bd show cosmos-explorer-yo6 --json | jq '.[0].status'  # Get issue status
bd show cosmos-explorer-yo6 --json | jq '.[0].dependents[] | .id'  # Get subtask IDs

# Dependency operations
bd dep tree <id> --json  # Dependency tree as JSON array
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
- **Reversing dependency arguments** → `bd dep add blocking-id blocked-id` is WRONG! It's `bd dep add blocked-id blocking-id`
  - First argument = the issue that gets a blocker (blocked task)
  - Second argument = the blocker (must complete first)
- **Assuming invalid flags exist** → `--blocked-by` and `--depends-on` flags do NOT exist. Use the positional arguments only.
- **Not using `bd ready` before starting work** → You might start on a task that's still blocked
- **Creating cyclic dependencies** → Beads will error; use `bd dep cycles` to detect



## Tips for Agents



- Always `bd create` when you discover work, even if small
- Update status frequently to maintain accurate work state
- Use `bd ready` to find next work with no blockers
- Create dependencies proactively when you see ordering constraints
- Close with a reason so others understand what was delivered
- **VERIFY DEPENDENCIES IMMEDIATELY** after creating them:
  ```bash
  bd show <blocked-id> --json | jq -r '.[0].dependencies[] | select(.dependency_type == "blocks") | .id'
  ```
  Should return the blocker ID. If not, the dependency wasn't created correctly.
- **ALWAYS** use `--json` flag for programmatic operations
- **NEVER** read `.beads/` directory or `issues.jsonl` directly - use `bd` commands only
