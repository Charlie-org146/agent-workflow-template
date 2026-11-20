# goal.py pr regenerates .loop/START.md (entry.py write) and the goal's wiki pages (wiki.py prepare --commit) before its final push, so the head the lane passes on is the head merge.py accepts and a MERGE-GO is not voided by a stale generated page (#5317)

- Slug: pr-regen-start
- Touches: skills/workflow-delivery/scripts/goal.py, skills/workflow-delivery/scripts/fit.py, dev/toy/test-goal.sh, .loop/regression.tsv
- ETA: 250 active minutes (estimate 199m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal branch whose inputs to .loop/START.md changed after its last commit, when goal.py pr runs, then it commits the regenerated START.md and stamped pages before the push, and merge.py on that head prints no stale-page refusal
2. Given nothing generated is stale, when goal.py pr runs, then it adds no commit, with a negative control that skipping the regeneration makes merge.py refuse in the toy
3. Given this goal's diff, then no shipped file is added, goal.py and fit.py are not larger than on main (goal.py 18,999, fit.py over 19,000: net zero or smaller), net regression rows are 0 or fewer, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
