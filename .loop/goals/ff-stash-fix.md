# operate.py's fast_forward never leaves the main checkout's .loop/regression-runs.tsv unmerged: when the stash apply conflicts it resolves with git checkout HEAD -- the file, keeps the dirty results in the named stash, and prints the stash name

- Slug: ff-stash-fix
- Touches: skills/workflow-monitoring/scripts/operate.py, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. When the stash apply of a dirty .loop/regression-runs.tsv conflicts during fast_forward, the file is restored with git checkout HEAD -- so it is never left unmerged (UU) or holding conflict markers; the dirty results stay in the named stash, which the step prints; a toy case is proven red on the old code; operate.py does not grow past 19,000 bytes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
