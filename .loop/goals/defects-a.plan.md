# Plan: defects-a

## Build steps (in order)

1. dev/toy/test-defects-a.py with cases 3841, 3840, 3839, 4184; run each red first (done: each failed on the old code).
2. #3841: private.py `HOME_DIR` (Unix and Windows home folders); role.py `lane_part` runs the row lines through `private.plain`.
3. #3839: render.py `workflow_file(root)` (automation registry, default regression.yml) passed to `full_page` and `run_cell`.
4. #3840: spend.py `lane_checks`; private.py `pr_result` posts only for them; goal.py posts on the real head after the bookkeeping commit; test-statuses.sh gains a workflow with the lane jobs.
5. #4184: spend.py `app_only`; flow.py refuses a new step for an unbound goal with `workers: app`.
6. #3862: no code; row monitor-stray-runs-3862 proves the fix of v0.28.51.
7. Rows in .loop/regression.tsv (category defect, link, seen red), Tests tables re-rendered.

## Test per done line

#3862 monitor-stray-runs-3862; #3841 pr-body-no-home-3841; #3840 pr-statuses-only-lane-3840; #3839 tests-links-workflow-3839; #4184 app-refuses-headless-4184. Each toy case prints PASS only after the fix.

## What could break

- Size caps: private.py (+49 bytes), flow.py (+242), role.py (+15), goal.py (+20); helpers live in spend.py.
- test-statuses.sh posts no statuses without a lane job in the workflow; it now has one. It skips on Windows (Linux CI).
- A private repo whose required check is not a lane-only job now gets BLOCKS instead of a status: intended (#3840).

## Out of scope

Auto-binding a session in `goal.py new`; any change to a Reviewed requirement's wording.

PENDING: none
