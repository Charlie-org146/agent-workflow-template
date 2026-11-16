# Design: ff-stash-fix

Problem: operate.py fast_forward stashes a dirty .loop/regression-runs.tsv, fast-forwards, then applies the stash. When the apply conflicts, `git checkout -- RUNS` cannot clear the unmerged index entry, so the file stays UU with conflict markers (seen live on main after #4400).

Approaches: (1) on a failed apply, `git checkout -q HEAD -- RUNS`, which clears the unmerged state and restores origin's copy; the dirty results stay in the named stash, which the note prints (chosen, one line). (2) Merge the two lane records by row. Rejected: lane results are regenerated and the stash keeps the local ones.

Done line: a toy case `ffconflict` is red on the old code (file left UU) and green on the new; operate.py stays 18,564 bytes. Open questions: none.
