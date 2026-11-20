# Design: budget-save-merge (#5350)

## Problem
goal.py save merges only the fields the caller changed (against what it loaded). role.py save and fit.py's run saver write the whole state, so a worker saving after the operation session ran goal.py set wipes the new budget (360 went back to 240, twice).

## Approaches
1. role.save and fit's saver call goal.save, with the load baseline recorded where state is loaded (role.goal_state, fit.budget_stop). One merge, no new code. Risk: a second import of goal when goal.py is main, fixed by registering the main module as "goal".
2. Copy the merge into role.py and fit.py. Both are over 19,000 bytes and may not grow.

## Chosen
Approach 1. goal.py 18,972, role.py 19,997, fit.py 19,647 LF bytes: each not larger than main.

## Done lines
1. A toy check (folded into worker-save-159, no new row) sets 360 and 480 after a load, saves through role.save and fit's saver, and finds both budgets and the worker's own step kept.
2. The same check against main's scripts prints BAD (budget back at 240).
3. Sizes and rows as above; no file added; no requirement text changed.

## Open questions
flow.py's own token write (whole state) is outside the touches; follow-up.
