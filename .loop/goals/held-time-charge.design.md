# held-time-charge design

## Problem
A goal's `time_budget_minutes` and its ETA read `board_log.active_minutes`. #3878 stopped charging a pr-queue wait, a `goal.py wait` pause and a session hold, but tonight's records show three shapes still charged: `session report: paused for PC memory` and `session report: waiting for ...` (the waiting words matched only an entry that began with them, 417 and 414 minutes), and a session that stayed `running` but silent (nothing in the log for hours, waiting for a message the app's cap blocked: 418 to 838 minutes, operator-setup 1478 for about 1077 of work).

## Approaches
1. **Recognise the report shapes, and cap silence at the idle limit** (chosen). The wait pattern also matches a session report that says waiting or paused. `active_minutes` passes the idle limit (`graph.silent_limit`, `silent_minutes` = 30, `LOOP_SESSION_QUIET` overrides) to `flow_seconds`: after an entry that does not start a step or the pr lane, a gap or the time to now is charged at most the limit. Cost: about 25 lines in board_log.py, 6 in fit.py. Risk: a worker that builds silently for more than 30 minutes is charged 30; it sends a `sessions.py report` as a heartbeat.
2. Charge only between `start X` and its end entry. Exact, but build (no log entries of its own) would never be charged, and the ETA model counts build.
3. Read the session's live heartbeat. Needs the app; the budget gate must work from the run record alone.

`flow_seconds` without a limit is unchanged, so the estimate model and its history read as before; `eta_spent` and the budget gate use the capped charge. `goal.py show` adds `minutes: {charged, wall}`.

## What each done line needs
1. A fixture goal (30 min run, 300 paused, 20 run) is charged 50 for each pause shape; the same goal running 350 minutes is charged 350 and stopped by a smaller budget (row held-charge-pauses).
2. A silent session is charged the limit, not the gap, until its next entry; a running step is charged in full; show prints both numbers (rows held-charge-idle, held-charge-show), all through `fit.budget_stop`.

## Open questions
None for the owner. Existing records and budgets are not changed; two older toys' "really runs 360 minutes" fixtures now carry `start` entries.
