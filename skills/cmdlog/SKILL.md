---
name: cmdlog
description: Use when a cmdlogged command (aps, brazil, brazil-build, brazil-recursive-cmd, cr) was run and you want its output, or when wrapping/unwrapping a command for logging. Reads captured argv/cwd/stdout/stderr/exit from ~/cmdlogs instead of re-running.
---

# cmdlog

Transparent command logging. Wrapped commands run through a C shim (`~/.cmdlog/engine`) that records every invocation to disk while behaving exactly like the real command (streams still go to the terminal, exit code preserved, fails open if logging breaks).

**Currently wrapped:** `aps`, `brazil`, `brazil-build`, `brazil-recursive-cmd`, `cr`.

## Read a past run instead of re-running

Logs live at `~/cmdlogs/<cmd>/<UTC-timestamp>.log`, one file per invocation, newest last.

```bash
# Latest run of a command
ls -t ~/cmdlogs/brazil-build/*.log | head -1 | xargs cat

# The one before that
ls -t ~/cmdlogs/brazil-build/*.log | sed -n 2p | xargs cat
```

If a cmdlogged command was just run and you need to see why it failed, **read the latest log — do not re-run the build.**

### Log format

```
--- APS INVOCATION LOG ---
start_utc: 2026-07-28T19:24:56Z
cwd: /local/home/.../src/SomePackage
argv: brazil-build release
real: /home/aarampal/.toolbox/bin/brazil-build
pid: 1852971
---
[OUT] ...stdout lines...
[ERR] ...stderr lines...
--- END ---
elapsed_s: 2.995
exit_code: 1
```

Each output line is tagged `[OUT]` or `[ERR]`. Useful greps:

```bash
f=$(ls -t ~/cmdlogs/cr/*.log | head -1)
grep -E '^(exit_code|argv|cwd):' "$f"     # verdict at a glance
grep '^\[ERR\]' "$f"                       # just stderr
grep -rl 'exit_code: [^0]' ~/cmdlogs/brazil-build/  # every failed build
```

Output may contain ANSI color codes — pipe through `sed 's/\x1b\[[0-9;]*m//g'` if they get in the way.

## Wrap / unwrap (zsh functions from `~/.cmdlog/cmdlog.zsh`)

```bash
wrap <cmd> [logdir]   # start logging cmd; creates a shim in ~/.cmdlog/bin (first on PATH)
unwrap <cmd>          # stop logging; removes the shim
wrapped               # list currently wrapped commands
```

`wrap` shadows the real binary with a shim in `~/.cmdlog/bin`. It refuses to double-wrap, and only works on PATH commands (not shell builtins/functions). Default log root is `$CMDLOG_DIR` (`~/cmdlogs`).

## Notes

- Logs are never rotated — the dirs grow unbounded. `find ~/cmdlogs/<cmd> -mtime +30 -delete` to prune.
- Fails open: if the shim can't write a log, the real command still runs. A missing log ≠ the command didn't run.
- Source of truth: shims in `~/.cmdlog/bin/`, engine `~/.cmdlog/engine` (built from `~/.cmdlog/src/aps.c`).
