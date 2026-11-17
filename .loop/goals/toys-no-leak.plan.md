# toys-no-leak plan

Checked against the code: `homeguard.scan`, `reap.sh` (LOOP_FLOW and the schedule variables), `lanekit.lanes_dir` (reads LOOP_LANES_DIR), `slots.lanes_dir`, `test-home-guard.py`, the four rows in regression.tsv all exist as read.

## Build steps
1. reap.sh: export LOOP_LANES_DIR to a temp pool unless set.
2. homeguard.py: `other_runs(top, here, name)` decides what is not judged; strict mode judges all.
3. test-home-guard.py: schedule/ own files pass, the registry and a new entry fail, strict judges lanes/, the harness points LOOP_LANES_DIR at a temp path.
4. test-toys-no-leak.py (fresh strict home; lease; control) and rows toys-no-leak-schedule, toys-no-leak-lane-pool, each seen red; done lines covered.
5. Regression and Tests re-rendered; DECISIONS.

## Tests per done line
1. fresh strict home empty after a lane lease; control caught.
2. registry write and new entry fail; own files and lanes/ tickets pass.

## What could break
A toy that reads the real lanes pool on purpose sets LOOP_LANES_DIR itself (test-lane-ports, test-tiers and others already do). A real repos.json change by another session during a toy now reads as a leak.

## Out of scope
Editing the four Linux-only toys; running them (Linux CI); changing the lanes/ allowance.
