# regression-fix: design

## Problem
Seven regression rows began failing during the 2026-11-15 releases, and health finding keys differ between Windows (backslash
paths) and Mac or Linux (forward slashes), so each run reopens the other's issues (#4379). Windows skips the POSIX toys, so
the rows were only ever exercised by Actions on Linux, and the failures there were read from the run logs of v0.28.75 to v0.28.81.

## Where each row first fails (Actions, per release)
- #4364 mon8-silent-30 and #4366 grd8-silent-worker: v0.28.78 (dead-loop-alert, commit 592b25ac, #4359). The check-in now
  prints STALLED for a quiet goal with no goal.py, flow.py or lane process; the toy `test-monitoring-prd.sh` case mon8 ran no
  process, so the line it greps ("its worker has sent nothing") became "STALLED ...". The code is right (MON-8 still shows the
  goal under Needs you, with a better line); the toy was stale. Fix: the case sets LOOP_PROCS for both goals, as
  test-silent-worker.py already does.
- #4374 mon12-pool, #4375 parallel-unlimited, #4376 held-all, and #4373 lane-over-minutes: all failed in the v0.28.79 run and
  passed in v0.28.78 and v0.28.80. mon12, parallel and held-all decide whether a goal starts, and a start reads free memory
  (MON-16 floor, 3.5 GB of free commit); eight shards side by side on one runner drop under it for some runs. Reproduced on
  this 4 GB PC: mon12 fails 3 checks and test-settings fails the parallel checks until the machine is made up. The code is
  right; the toys leaked the real machine. Fix: `dev/toy/reap.sh` (every toy sources it) exports a made-up LOOP_MACHINE with room
  unless a toy set its own.
- #4373 lane-over-minutes: fails at v0.28.76, v0.28.77, v0.28.79, v0.28.81 and passes at v0.28.78 and v0.28.80, so it is
  flaky, not a regression of one release. Its toy section asks for a nightly row to be selected, and the lane answered REUSED
  with 6 reused rows; the cause is unproven.
- #4367 set8-local-setting-refused: FAIL at v0.28.78 and v0.28.80, SKIPPED in the other runs; first run with the row was
  v0.28.76's adoption release. The state comparison fails with no output saying what changed; passes on this PC.
  Fix here: the case prints a diff of what the refusal wrote, so the next Actions run names it.

## Approaches
1. Fix each toy (isolate the machine, give mon8 its process). Cost: small, no product code. Risk: none for the requirements.
2. Change the code so the board ignores memory under test or STALLED when no process is readable. Cost: product change under the
   19,000-byte caps; risk: weakens MON-16 and #4359.
Chosen: 1, since each requirement still holds and only the toys read the real machine or an older behaviour.

## #4379
Keys, evidence and titles go through `issues.posix` (forward slashes only), and `file.held_all` reads each issue's marker key
through it, so a Windows run and a Mac run name one finding one way. A toy (`test-health-key-posix.py`) is seen red first.
Existing duplicate pairs are closed once by hand after the merge, naming the issue kept.

## Done lines
1. Each row's first failing release is named above; the toy fixes and a seen-red row for the machine (`defect-4375-toys-fake-machine`)
   hold them; each issue is closed with the passing line from Actions after merge.
2. `defect-4379-health-key-posix` is seen red; duplicate pairs are closed once.
3. Files stay under 19,000 LF bytes; the package file count is unchanged; no reviewed requirement text changes.

## Open questions
- lane-over-minutes and set8-local-setting-refused cannot be reproduced on this PC; the Actions run on this branch decides them.
