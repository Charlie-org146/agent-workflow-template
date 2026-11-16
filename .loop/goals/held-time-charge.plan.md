# held-time-charge plan

Checked against the code: `board_log.WAIT`, `flow_seconds`, `active_minutes`, `graph.silent_limit`, `fit.active_minutes`, `fit.budget_stop`, `fit.cmd_show`, `auto.eta_spent` all exist as read.

## Build steps
1. board_log.py: WAIT also matches a `session report: ... waiting|paused` entry; RUNS marks the entries after which something runs; `flow_seconds(..., limit)` caps a gap or tail after any other entry; `active_minutes(run, at, cfg)` passes `graph.silent_limit(cfg)`; `wall_minutes`.
2. fit.py: `active_minutes` and `budget_stop` pass cfg; `cmd_show` adds `minutes: {charged, wall}`. auto.py `eta_spent` reads `bs.active_minutes` (board_status re-exports it).
3. Toy `dev/toy/test-held-time-charge.py` and rows held-charge-pauses, held-charge-idle, held-charge-show, each seen red with `regression.py red --break`; done lines covered by done-held-time-charge-1 and -2.
4. Two older toys (budget-fair, held-time-budget) gain `start` entries in their "truly runs 360 minutes" fixtures.
5. Re-render Delivery, Monitoring and Tests; commands.md section; DECISIONS entry.

## Tests per done line
1. pauses: 50 charged for goal.py wait, a waiting report and a paused report; 350 for the unpaused control; the gate stops at 50 but not 60.
2. idle: 60 charged after 300 silent minutes; 80 after the next step; 350 for a running step; show prints charged 60, wall 300.

## What could break
Estimates (flow_seconds without a limit) read as before except that a waiting or paused session report now pauses the clock. Goals that work silently for more than 30 minutes read lower on the budget; the owner can see wall minutes in show.

## Out of scope
Changing the records of trim-scripts-98, how-to-use-docs, ci-fail-causes, size-warn-at-cap, sweep-regression or operator-setup; a heartbeat command; a new setting.
