# Fixes #5344, #5308, #5346, #5350, #5359, #5317 and #5078, each fix carried only after its own Claude review passed, each keeping its own defect row (Operation TD585), and fixes #5679 by giving the toys their missing reads headers so lanes_cli.py check is clean, with the defect rows for #88, #5635 and #5638 (defect-rows-2). A fix still in review or rework joins only once it passes, or moves to a second bundle

- Slug: v2fix-bundle
- Touches: skills, dev/toy, .loop/regression.tsv, docs/wiki, skills/loop-files.md
- ETA: 260 active minutes (estimate 205m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each carried fix, then its own defect row was seen failing (on main or by a recorded break) and passes on this branch, and the toys its review ran still pass
2. Given lanes_cli.py check and dev/toy/test-tree.sh, then both are clean on this branch, and the rows for #88, #5635 and #5638 are seen failing then passing
3. Given this goal's diff, then only the carried fixes, the toys' headers, the new rows, re-rendered pages and the goal's own records change; no check is weakened, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
