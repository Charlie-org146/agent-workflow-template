# Rows that PRs genuinely add to .loop/regression.tsv and .loop/regression-issues.tsv merge without conflict, by one of two designs chosen in the plan and proven: one file per goal assembled at release (towncrier) or git's built-in merge=union driver in .gitattributes with a stable sort at release (TD231; git merge drivers, towncrier)

- Slug: append-rows-merge
- Touches: .gitattributes, .loop/regression.tsv, .loop/regression-issues.tsv, skills/workflow-regression/scripts/regression.py, skills/workflow-release/scripts/wiki.py, dev/toy/test-lanes.sh
- ETA: 290 active minutes (estimate 230m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given three fixture PRs that each add a regression row to the same table, when they merge in any order, then no conflict, and after release the table is byte-identical whichever order they merged in, with duplicate ids refused
2. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main, net regression rows are 0, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
