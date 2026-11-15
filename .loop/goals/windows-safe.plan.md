# windows-safe: plan

Claims checked against the tree: `prd.py:126` calls `__import__("audit").owned` and `audit.owned` exists (`audit.py:198`); `listing.json` `commands` lacks `batch`, which `wiki.py:324` adds as a parser; `dev/toy/test-pods.sh:249` holds the per-script `caps` loop; a row's `# reads:` header takes whole directories.

## Build steps
1. `dev/toy/test-windows-safe.py` (`# reads:` each `skills/*/scripts/` folder, `# windows: ok`): a `scan(root)` that reads every `skills/*/scripts/*.py` and reports `file:line name` for each of `fcntl`, `os.getuid`, `os.killpg`, `os.getpgrp`, `os.O_NOFOLLOW`, `signal.SIGHUP`, `os.kill(pid, 0)` and `os.WNOHANG` that has no guard. A guard is `hasattr(`, `getattr(`, `os.name`, `sys.platform`, `posix-only` or `windows:` on the line or the 3 lines above, a docstring or comment line, or the `try: import fcntl` shim block. It prints `PASS`/`FAIL` lines.
2. Run it on the real tree; add a `# posix-only branch` marker to each real use it flags and nothing else, so the tree passes.
3. Toy tree inside the test: one bad line per name must fail naming its file and line, the same line with a guard must pass, and an `import fcntl` inside a `try:` shim must pass.
4. `prd.py`: replace `__import__("audit")` with `importlib.import_module("audit")` (one import line). `listing.json`: add `batch` to `commands`. Run `dev/package.py`: it passes.
5. `dev/toy/test-pods.sh`: set every `caps` pair to 20480.
6. Rows in `.loop/regression.tsv`: `windows-safe-posix-names` (done line 1, defect, issue 2871), `package-passes-3800` (done line 2, `python3 dev/package.py`, defect, issue 3800), `pods-caps-3919` (done line 3, `bash dev/toy/test-pods.sh size`, defect, issue 3919). Each seen failing first: the scan on a tree with a bad line, `package.py` before step 4, the caps before step 5.
7. Docs: the wiki page that owns the Windows-safe requirement gets a true line if a page goes stale; reviewed pages are not edited.

## What could break
The line scan flags a real use I mark wrongly; a marker comment pushes a script over the 20 KB cap (check sizes after step 2); `test-pods.sh size` runs on bash only, so on Windows the row skips.

## Out of scope
The two Linux-only merge-lock checks of #3919 (an off-machine to-do), a Windows runner, any change to `lanekit`'s shim.

PENDING: none
