# qa-not-runnable plan

Checked against the code: `runs.execute` (state), `regression.py cmd_run` (exit and RESULT), `lane.py` (line, `ran` regex),
`role.need_lane` / `goal.py cmd_record` (qa gate and note), `runs.owed_issue` (milestone lookup, now `notrun.milestone`).

## Build steps
1. `skills/workflow-regression/scripts/notrun.py`: `unrunnable`, `milestone`, `todo`.
2. `runs.py`: classify in `execute`; `owed_issue` uses `notrun.milestone`.
3. `regression.py`: unproven ignores NOTRUN rows, files the to-do, prints `NOTRUNNABLE n: ids`.
4. `lane.py`: line gets `N pass; M not runnable here (ids)`. `role.py` `lane_note`; `goal.py` record uses it as the step note.
5. Toy `dev/toy/test-not-runnable.py`, three rows `not-runnable-lane|qa|todo`, each seen red.

## Test per done line
Rows above (seen red against a broken `unrunnable`, passing now). Sizes stay at or under 19,000 LF bytes in the regression scripts.

## What could break
A real failure with a matching pattern is shown as not runnable; the patterns are narrow and the toy has a control.

## Out of scope
#4321 (config change marks every row affected); auto-proving the rows on the other machine.

PENDING: none
