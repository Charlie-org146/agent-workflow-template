# Replaces v2fix-bundle, whose done line 2 (test-tree.sh clean) cannot hold tonight because its last FAIL, the rerun fraction, needs a redesign (#5694) (Operation TD599 fallback, TD602): carries the same commits from loop/v2fix-bundle, which fix #5344, #5308, #5078, #5359, #5346 and #5317, each after its own Claude review passed, with each fix's defect row; gives the toys their reads headers so lanes_cli.py check is clean (Refs #5679); and adds the defect rows for #88, #5635 and #5638

- Slug: v2fix-bundle-2
- Touches: skills, dev/toy, .loop/regression.tsv, docs/wiki, skills/loop-files.md
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each carried fix, then its own defect row was seen failing (on main or by a recorded break) and passes on this branch, and the toys its review ran still pass
2. Given lanes_cli.py check, then it is clean on this branch, and the rows for #88, #5635 and #5638 are seen failing then passing; test-tree.sh's remaining rerun-fraction FAIL is named in the pull request body with #5694
3. Given this goal's diff, then only the carried fixes, the toys' headers, the new rows, re-rendered pages and the goal's own records change; no check is weakened, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
