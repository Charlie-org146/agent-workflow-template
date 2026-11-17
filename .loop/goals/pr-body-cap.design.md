# pr-body-cap design

## Problem
`role.lane_part()` writes one line per selected row into the PR body's "Rows and why they ran" block. A change that selects all
~1,000 rows made a 67,758-character body and `gh pr create` refused it (limit 65,536, #4531). A 300-line cap is already in
`role.py` (added inside ci-fail-output), but it has no test, and it caps by line count only: 300 long lines can still push the
body past the limit.

## Approaches
1. Keep the 300-line cap and add a toy that feeds 400 selected rows. Cheapest, but a body of 300 very long lines is not covered.
2. Cap by lines and by characters in one small helper, `role.cap_rows(rows)`: keep rows while they fit in 300 lines and 30,000
   characters, then add `... N more` with the count of the rest. Cost: a few lines in `role.py`, which has 73 bytes of room under
   19,000, so something else there gets trimmed. Risk: a body that was fine before could now be cut, but only past 30,000
   characters of rows, well above any small selection.

## Chosen
Approach 2: it meets done line 1 whatever the row text length, and done line 2 holds because nothing changes below the caps.

## What each done line needs
1. `dev/toy/test-pr-body-cap.py`: build a fake pr-lane log with 1,000 SELECTED lines, call `lane_part`, and check the block lists
   fewer rows than were selected, ends with the exact count of the rest, and the whole part is far under 65,536 characters. A
   second case with a few very long rows is also capped.
2. The same toy: 5 selected rows are all listed, with no `more` line.
Both go in rows seen failing before the change (the first against the uncapped expression) and passing after.

## Open questions
None. goal.py is not touched; the cap lives in role.py, so goal.py stays at 18,992.
