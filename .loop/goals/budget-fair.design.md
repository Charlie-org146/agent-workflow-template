# Design: budget-fair

## Problem
A goal's `time_budget_minutes` is meant to count active step time only (`fit.active_minutes`, which reads
`board_log.flow_seconds`). #3878 added pause rules for a stop, a hold, a free, a pr-queue wait and an owner answer, and
`dev/toy/test-held-time-budget.py` covers them. #4261 found the gap: a pr lane that ends in BASE_MOVED (`merge.py` refuses,
`autorelease.reopen` logs `merge refused (exit 2): ...`) or in "main moved" (`pool.pr_moved` logs `main moved, try not
counted`) is charged to the `pr` step in full. On the real blockers-first run (#4182) 405 of 429 active minutes sat on `pr`,
and five lost lanes ran a budget of 400 out with the branch ready.

## Approaches
1. **Log a held entry at the refusal.** `autorelease.reopen` and `pool.pr_moved` write an extra "held" entry and
   `flow_seconds` pauses after it. Cost: two release/pool edits. Risk: the lane time is already behind the entry, so the pause
   starts too late and the lost lane is still charged.
2. **Read the lost lane out of the log at accounting time (chosen).** `board_log.lost_lanes` (a new function in an existing script, because the package gate caps shipped files) names the
   gaps to drop: the gap that ends in a lost-lane entry (`merge refused (exit N)`, `main moved, try not counted`), and when
   that refusal follows a `pr` entry, the gap ending in that `pr` entry too (the lane that produced the pull request the base
   then left behind). `flow_seconds` skips those gaps. Cost: one function in `board_log.py` and a three-line call in `flow_seconds`. Risk: the
   rule must not drop a lane that really failed; a `try N failed` entry is not a lost lane and stays charged.

## Choice
Approach 2: it fixes past runs as well as new ones, because accounting reads only the log the goals already wrote, and it needs
no change to the release or pool scripts. The 81-minute failed try (`try 1 failed: regression lane failed`) stays charged: that
lane really failed.

## What each done line needs
1. BASE_MOVED lane held, not charged: `held.lost(log)` plus the call in `flow_seconds`; toy `dev/toy/test-budget-fair.py`
   replays five BASE_MOVED lanes and the real blockers-first shape (a 15-minute lane, refused, repeated) and reads the budget unspent;
   a `merge refused` after a lane that really spent time elsewhere (a build, a review) leaves those steps charged.
2. #3878: the toy also replays a pr-queue wait, a hold, an owner answer and a stop around active time and reads only the active
   time; the row proves it red by breaking the pause rules. Anything #3878 still lists as open is closed with that proof in the
   pull request.
3. Size: `board_log.py` is 8,412 bytes and grows by about 200; `fit.py`, `pool.py`, `autorelease.py`
   and `merge.py` stay untouched.

## Open questions
- None for the owner. Whether `max_moved` should shrink is not part of this goal.
