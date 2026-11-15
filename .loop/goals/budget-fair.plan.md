# Plan: budget-fair

Checked against the code: `fit.budget_stop` and `fit.active_minutes` (workflow-delivery/scripts/fit.py) read
`board_log.flow_seconds` (workflow-monitoring/scripts/board_log.py:103). `autorelease.reopen` (workflow-release) logs
`merge refused (exit N): run goal.py pr, then merge.py again`; `pool.pr_moved` (workflow-monitoring) logs
`main moved, try not counted (K of M)`. `board_model.py` also calls `flow_seconds` for the board's time left, so the fix also keeps
a lost lane out of the estimate (MON-4 already leaves held time out).

## Build steps
1. New function `lost_lanes(log)` in `skills/workflow-monitoring/scripts/board_log.py` (not a new script: the package gate caps shipped files at 98) that returns the set of log indexes whose preceding gap is a lost
   lane. An entry is a lost-lane end when its text starts `merge refused (exit` or `main moved, try not counted`. When a
   `merge refused` entry follows an entry whose step word is `pr`, the gap ending in that `pr` entry is lost too (the lane
   that opened the pull request the base then left behind). Pure function of the log.
2. `board_log.flow_seconds`: skip a gap whose end index is in `lost_lanes(log)`, with a skip beside the
   existing `pause` rule. `fit.py`, `pool.py`, `autorelease.py` and `merge.py` stay as they are.
3. `dev/toy/test-budget-fair.py`: replays (a) five BASE_MOVED lanes of 15 minutes behind one real pr entry each, with a 400
   minute budget: `fit.budget_stop` does not refuse and active minutes stay under the lanes' time; (b) the real blockers-first
   shape (a failed try, a pr-queue wait, holds), asserting the lost lanes drop out and a `try N failed` lane stays charged;
   (c) a pr-queue wait, a session hold, an owner-answer wait and a stop around 20 active minutes read 20 (#3878); (d) a goal
   that truly runs past its budget is still refused.
4. `.loop/regression.tsv` rows: `budget-fair-base-moved` (done line 1) and `budget-fair-held-time` (done line 2) and `budget-fair-failed-stays`, each seen red with a
   break that disables the rule (`regression.py red`), requirement MON-4 as the nearest reviewed requirement (no wording changes).
5. Pages: Tests re-rendered; the Monitoring page is Reviewed and untouched; Home only if the check says so.

## Test for each done line
1. `budget-fair-base-moved`: five lost lanes leave the budget unspent; red before the change (the same replay reads the full lane
   time).
2. `budget-fair-held`: queue wait, hold, owner answer, stop never charged; seen red by breaking the pause rule with sed.
3. The package gate (dev/package.py, headroom): every touched script at or under 19,000 bytes (`board_log.py` about 9.4 KB;
   measured LF).

## What could break
- A lane that really spent time before a refusal in a different step (build, review) must stay charged: `lost` only drops gaps
  ending in a lost-lane entry or the `pr` entry just before it.
- The board's estimate shifts for goals with lost lanes (less spent); intended, and MON-4's own held rule already says so.

## Out of scope
`max_moved`, the pr queue order, merge slots (#4261 names a merge slot as an alternative; the operation session chose held time).
