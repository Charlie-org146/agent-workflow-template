# Plan: config-lane

Checked against the code: `lanes.plan` (skills/workflow-regression/scripts/lanes.py:347) loops `for path in since[...]` and
calls `touches(...)` for every changed path; `names_any` (lanes.py:337) and `narrow.names` exist; `.loop/config.json` is not in
`NO_EFFECT`. `lanes.py` is 20,732 bytes and `narrow.py` 20,131 on main, so the build waits for scripts-c's trim.

## Build steps
1. Wait until scripts-c's Release line is on origin/main; merge main.
2. Add `config_keys(root, commit)` to the trimmed `narrow.py`: the `(key path, value)` multiset of `.loop/config.json` at a commit or in
   the worktree, read with `object_pairs_hook` (duplicates count); None if it does not parse. Add `config_changed(root, commit)`:
   the set of last key names in the symmetric difference, or None (unparseable, so fail wide).
3. In `lanes.plan`, a branch `elif path == ".loop/config.json"`: stale when the keys are None, or `touches(...)` and
   `names_any(root, row["command"], keys, cache)`; memoise the key set per prior commit in `since`'s style.
4. Keep both files at or under 19,000 bytes LF (measured as the package gate does); if they do not fit send the operation session the byte count.
5. Toy `dev/toy/test-config-lane.py` (python: runs without bash on Windows) with a temp git repo of two rows.

## Tests per done line (regression rows, each seen red)
- `config-lane-duplicate-key`: remove a duplicate `min_free_memory_gb`; only the row naming it is to_run. Red: drop the branch.
- `config-lane-key-change`: added, removed and changed keys each pick only readers; a reformat-only change picks none. Red: make
  the branch always stale.
- `config-lane-unparseable`: a config that does not parse picks every row that reaches it. Red: treat None as no change.
- Size and package rows already exist (package-headroom): they stay green.

## What could break
A script that iterates config keys without naming them is missed (a changed key reruns nothing there). The toy for that case
greps the repo for such readers; any found get a `# reads:` declaration. `.loop/config.json` rows in the lane would still
fail wide on a parse error.

## Out of scope
Per-row key declarations; other `.loop/` tables (regression.tsv, known.tsv keep their own rules).

PENDING: none
