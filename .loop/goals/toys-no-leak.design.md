# toys-no-leak design

## Problem
The CI runner's four LEAK rows (worker-runs-release, pr-body-no-checks, defect-owed, suite-time-recorded) each ran lane code under the runner's real HOME and added `lanes/port-0` or `lanes/counter.lock` to `~/.workflow-loop` (#4555). The home guard has since been told to ignore `lanes/` and all of `schedule/`, which hides the symptom and means a toy writing the real schedule registry passes unnoticed (#4683).

## Approaches
1. **A temp lane pool for every toy, and judge schedule/ except the scheduler's own files** (chosen). `reap.sh` exports `LOOP_LANES_DIR` at a temp folder unless a toy names its own, so lane code in any toy can't reach the real pool. `homeguard.py` keeps ignoring `lanes/` (another lane's tickets are legitimate while a toy runs) but judges `schedule/` except `log/`, each repo's `health-report.txt` and `tree/`; `TOY_GUARD_STRICT` judges a fresh home in full. Cost: 3 lines in reap.sh, a rule function in homeguard.py. Risk: toys that rely on the shared real pool for cross-process port exclusion get a private pool (none do; the lane's own port lease is taken before the row).
2. Fix each of the four toys. They are Linux-only here, so unprovable on this PC, and the next toy leaks the same way.
3. Make the guard stop ignoring lanes/. Fails whenever another lane runs.

## What each done line needs
1. The four rows are not marked windows: ok, so they skip on this PC. `test-toys-no-leak.py` is the proof that works anywhere: a toy that takes a lane lease leaves a fresh, strictly judged `~/.workflow-loop` empty; the control aimed at the real lanes/ is caught (row toys-no-leak-lane-pool). Linux CI runs the four rows themselves.
2. `test-home-guard.py` already fails a toy that rewrites or adds a file there; it now also fails a write to the schedule registry or a new schedule entry, and lets lanes/ tickets and the scheduler's own files through (rows home-guard-catches-leak, toys-no-leak-schedule).

## Open questions
None for the owner. The four LEAK rows' own run on Linux CI is the owed confirmation; it is not a held step.
