# Plan: ff-stash-fix

1. operate.py fast_forward: on a failed `stash apply`, run `git checkout -q HEAD -- RUNS` and say `stays in stash entry <tag>, <sha12>` (built).
2. dev/toy/test-merge-unblock.py: case `ffconflict` (red on the old code: file UU; green now).
3. .loop/regression.tsv row ff-stash-conflict-never-unmerged (DEL-5); render the Tests tables; re-stamp Monitoring.

What could break: the ff and ffconflict cases share setup, the plain ff case still passes. Out of scope: the other operate.py paths. PENDING: none.
