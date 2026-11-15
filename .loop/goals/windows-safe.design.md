# windows-safe: design

## Problem
Main keeps losing Windows: a merge reintroduced `fcntl` (#2871), `dev/package.py` fails on main today (#3800: `prd.py` uses `__import__`, and `batch` is missing from `listing.json`), and `test-pods.sh size` has per-script caps below the committed sizes (#3919). Nothing stops the next break where the author works, because the lanes run on Linux and the POSIX-only names only fail on Windows.

## Approaches
1. **Static check as a regression row.** `dev/toy/test-windows-safe.py` scans `skills/*/scripts/*.py` for the POSIX-only names and fails the pull request lane on any Linux runner, with a toy tree that proves it can fail. Cost: one toy file and one row, no new shipped file. Risk: a line scan misses a name behind an alias.
2. **Run the lane on a Windows runner.** Catches everything, but needs a runner the repo does not have; the issue calls it a later step.

I chose 1. A name counts as guarded when its line, or one of the 3 lines above it, holds `hasattr(`, `getattr(`, `os.name`, `sys.platform`, `posix-only` or `windows:`, or when it sits in the `try: import fcntl` shim block. The tree's own uses get the marker comment they lack.

## What each done line needs
1. Done line 1: the toy scanner (a function the row calls), a toy tree with one bad line per name that must fail with its file and line, and the real tree passing. The row lists `skills` in its reads so any script edit runs it.
2. Done line 2: `prd.py` imports `audit` lazily with `importlib.import_module` (no `__import__`), `listing.json` names the `batch` command, and `dev/package.py` passes.
3. Done line 3: the `caps` loop in `test-pods.sh size` uses the package cap (20,480) for every script, so it cannot go stale below the committed sizes.

## Open questions
None the owner must decide. The Linux-only checks of #3919 (two merge-lock checks) stay an off-machine to-do.
