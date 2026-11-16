# pr-body-cap plan

Checked: role.py `lane_part` (line 302) holds the inline 300-line cap; role.py is 18,927 LF bytes (73 to spare); goal.py (18,992) is not touched; the body is built in goal.py from `state["pr_lane"]`.

## Build steps
1. In role.py add `cap_rows(rows, lines=300, chars=30000)`: keep leading rows that fit both limits, return them plus `... N more` for the rest. Call it from `lane_part` in place of the inline slice. Trim role.py elsewhere so it stays under 19,000.
2. `dev/toy/test-pr-body-cap.py`: temp git dir with a fake `<slug>.pr-lane.last` and `.txt`; cases for 1,000 rows, 20 very long rows, 5 rows.
3. Rows `pr-body-cap-large` (done 1) and `pr-body-cap-small` (done 2), each seen failing against a break (large: restore the uncapped list; small: cap at 3 rows).

## Test per done line
Done 1: pr-body-cap-large. Done 2: pr-body-cap-small.

## What could break
Other callers of `lane_part` output (the body builder reads it as one string); a trim in role.py changing behavior (the not-runnable, pr-queue and adoption toys cover it).

## Out of scope
goal.py, the lane's own output size, gh's other limits.

PENDING: none
