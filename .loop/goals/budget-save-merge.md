# A worker's run-record save never overwrites a budget, depth or pre-flight answer that the operation session set after the worker loaded its state: every writer (role.py save, fit.py save, goal.py save) merges only the fields it changed, as goal.py save already does (#5350, TD210)

- Slug: budget-save-merge
- Touches: skills/workflow-delivery/scripts/role.py, skills/workflow-delivery/scripts/fit.py, skills/workflow-delivery/scripts/goal.py, dev/toy/test-goal.sh, .loop/regression.tsv
- ETA: 250 active minutes (estimate 199m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal whose worker loaded its run record, when goal.py set raises its budget to 360 and the worker then saves through role.py or fit.py, then the record still shows 360 and the record named by goal.py set, and the worker's own changed fields are kept
2. Given the same toy with the old whole-state write restored, then it fails (negative control), so the row is seen red
3. Given this goal's diff, then no shipped file is added, role.py and fit.py are not larger than on main (both are over 19,000: they reuse goal.py's merge instead of adding code, net zero or smaller), net regression rows are 0 or fewer, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
