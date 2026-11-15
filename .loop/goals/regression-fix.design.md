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
- #4373 lane-over-minutes (and #4380 goal-levels-nightly, the same toy): found by logging every Popen of every python process in an Actions run. The toy's t4 case starts a lane with `lane.lane(..., 0)` and never waits for it; that lane's regression run goes on in the toy repo while the t6 case switches branch, commits its rows and starts its own lane. The t4 run executes rows m, a and c in the new working tree and saves a record for the branch t6 at its HEAD, so the t6 lane reuses it (REUSED, no row selected). Whether it finishes before t6 sets up depends on the runner's speed, which is why it passed at v0.28.78 and v0.28.80 and failed at the other releases. The code is right; the toy raced itself. Fix: t4 polls its lane to the end before the next case.
- #4367 set8-local-setting-refused: the toy's state hash covers the home folder, and the real gh (version 2.10x) writes its own `.local/state/gh/device-id` there on a first run (the case runs no stand-in gh). The refusal wrote nothing; gh did. Fix: the state hash leaves gh's own state folder out, and a failing case now prints a diff of what changed (seen on Actions).

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
