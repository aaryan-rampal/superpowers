# Setup for `ai-history` CLI

The launcher (`./ai-history`) needs a `.venv` next to it. `.venv` is gitignored,
so a fresh clone won't have one — build it once. Runtime needs **zero
dependencies** (pure stdlib); the venv only pins Python 3.13.

## Bootstrap (run from this `cli/` directory)

**Preferred — uv:**

```bash
uv venv --python 3.13 .venv
```

**Fallback — stdlib venv** (needs a 3.13 interpreter on PATH):

```bash
python3.13 -m venv .venv   # or: python3 -m venv .venv, if it's 3.13
```

That's it — `./ai-history search "foo"` should now work.

## Running the tests (optional, for schema-contract checks)

The tests need `pytest`. Install it into the venv:

```bash
uv pip install -e ".[dev]"          # uv
# or
.venv/bin/python -m pip install pytest==9.1.1   # stdlib venv
.venv/bin/python -m pytest
```

## Troubleshooting

- ``.venv/bin/python: No such file`` → venv not built; run the bootstrap above.
- Wrong Python version → delete `.venv` and rebuild with an explicit `--python 3.13`.
- `rg` missing → fine, the CLI falls back to pure-Python search (just slower).
