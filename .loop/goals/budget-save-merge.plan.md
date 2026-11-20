# Plan: budget-save-merge (#5350)

Checked: goal.save merges against goal.SEEN[slug]; role.save(path, state) and fit.run_saver's save write whole state; flow.py loads state with plain json (so fit.budget_stop must record the baseline itself).

## Build steps
1. role.py: goal_state records goal.SEEN[slug]; save calls goal.save.
2. fit.py: run_saver's save calls goal.save; budget_stop records goal.SEEN[slug] when given a saver.
3. goal.py: register the running module as "goal" in sys.modules so role and fit share one SEEN; trim two bytes' worth of text to stay not larger than main.
4. dev/toy/test-worker-save.sh (row worker-save-159): add the #5350 check.

## Tests per done line
1. The new check prints OK (360 and 480 kept, steps plan and build kept).
2. Run against main's scripts it prints BAD.
3. wc -c: goal 18,972, role 19,997, fit 19,647; regression.tsv unchanged.

## Could break
goal.save also reports step changes through role.report for these saves; it already does so for every goal.py save. Out of scope: flow.py's token write, trimming to 19,000.
