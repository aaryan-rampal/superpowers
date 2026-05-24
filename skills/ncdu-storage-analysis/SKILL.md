---
name: ncdu-storage-analysis
description: Use when analyzing ncdu JSON exports, disk-usage snapshots, or storage cleanup requests where the user wants quick wins, reclaimable blockers, or safe deletion candidates.
---

# NCDU Storage Analysis

Treat `ncdu` output as storage triage. The useful answer is not "largest paths"; it is "what can be freed with low regret, what needs inspection, and what is personal/app state."

## Core Workflow

1. Find and identify the export.

```bash
fd 'ncdu.*json' .
head -c 1200 ncdu.json
```

2. Parse with `jq`. Do not use Python unless the current directory has a valid `.venv`.

```bash
jq -r '
  def bytes: (.dsize // .asize // 0);
  def total:
    if type == "array"
    then ((.[0] | bytes) + ([.[1:][]? | total] | add // 0))
    else bytes
    end;
  def nm: if type == "array" then .[0].name else .name end;
  [.[3][1:][] | {name: nm, size: total}]
  | sort_by(.size) | reverse
  | .[:40][]
  | "\(.size)\t\(.name)"
' ncdu.json
```

3. Drill down before recommending cleanup.

```bash
jq -r '
  def bytes: (.dsize // .asize // 0);
  def total:
    if type == "array"
    then ((.[0] | bytes) + ([.[1:][]? | total] | add // 0))
    else bytes
    end;
  def nm: if type == "array" then .[0].name else .name end;
  def child($n): .[1:][] | select(nm == $n);
  .[3] | child("Library") | child("Application Support")
  | [.[1:][] | {name: nm, size: total}]
  | sort_by(.size) | reverse
  | .[:40][]
  | "\(.size)\tLibrary/Application Support/\(.name)"
' ncdu.json
```

4. Classify paths:

- **Easy wins**: installers, old downloads, screen recordings, archives, package-manager caches, browser/app caches, stale `node_modules`, stale `.venv`, Android emulator images.
- **Check first**: Colima/Docker data, local databases, app backups, worktrees, large git repos, app profiles.
- **Personal/app state**: Photos, Messages attachments, mail profiles, browser profiles, note vaults. Report sizes and paths, but do not push deletion.

5. Verify live state before deletion. `ncdu` exports are snapshots and may be stale.

```bash
du -sh PATH...
ls -la PATH...
```

## Common Targets

- **Colima**: use `colima status`, `colima list`, then `docker --context colima system df`. If startup fails, inspect `~/.colima/_lima/colima/ha.stderr.log` before suggesting fixes.
- **Android**: `~/.android/avd/*.avd` is usually emulator state. Preserve `adbkey`, `adbkey.pub`, and small config unless the user asks to remove all Android state.
- **pg0/Hindsight**: inspect `instance.json` and `postmaster.pid`; do not raw-delete a possible running Postgres instance.
- **Package caches**: `~/.bun/install/cache`, `~/.npm/_npx`, `~/.yarn/berry/cache`, and `~/Library/pnpm/store` are generally redownloadable.
- **Worktrees**: run `git worktree list` before removing; prefer proper worktree removal over raw directory deletion.

## node_modules

Use `-I` so ignored dependency directories are included. Count only install roots, not every nested dependency copy:

```bash
fd -H -I -t d '^node_modules$' /Users/aaryanrampal \
  | awk '{s=$0; n=gsub(/\/node_modules\//,"",s); if (n == 1) print $0}' \
  | while IFS= read -r d; do du -sk "$d"; done \
  | sort -rn \
  | head -60
```

## Cleanup Rules

- Start read-only. Do not delete during the first pass.
- Use `trash` on macOS; avoid permanent deletion.
- Say when space will not be fully reclaimed until Trash is emptied.
- For Docker/Colima, list containers/images/volumes before pruning or deleting.
- For personal media and app profiles, ask before cleanup.

## Output Shape

Lead with decisions:

```text
Easy wins:
- 4.0G Desktop screen recording
- 3.5G Bun cache
- 2.5G Android emulator

Check first:
- 16G Colima VM
- 2.5G pg0 Hindsight database

Generated code:
- 9G top-level node_modules across 130 installs
- 7G project-local venvs
```

Always include exact paths for cleanup candidates.
