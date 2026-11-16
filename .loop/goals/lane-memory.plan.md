# lane-memory plan

Checked: `affected` on the main checkout walked 83,596 paths, 82,577 inside `.git`; the `.git` guard in `references` compared a `/`-split first part, so a Windows `normpath` path (`.git\loop\...`) slipped past it. Sizes by LF count: lanes 19,280, runs 19,997, regression 18,998, lane 18,978, guards 19,2xx, lanekit 18,799 (the 19,000 rows already fail for runs and lanes on main; the hard cap is 20,480).

## Build steps
1. lanes.py: `walk` skips `.git`; `references` normalizes its candidate to `/` before the `.git` guard. Measure `affected` before and after.
2. slots.py and lanekit.py: EXIT_ENV = 6 (copies kept equal). runs.py: START_CODES make a row ENV (SKIPPED with env, NOTRUN to-do excluded), with a rerun hint. regression.py: ENV line, exit 6 when more than half the rows are ENV and none failed.
3. lanes_cli.py: the memory wait gives up with a MEMORY_WAIT note and exit 6. lanekit.env_line and lane.py print it as the lane line's last line. guards.failed_try counts no try for a MEMORY_WAIT or LANE_ENV reason (own cap 10, then it counts).
4. Toys: test-lane-walk-git.py, test-lane-env.py, test-lane-memory.py; update test-budget-enforce.py (exit 6). Rows lane-walk-skips-git, lane-env-states, lane-env-exit, lane-memory-not-counted, each seen red; all linked to REG-7.

## Test per done line
Done 1: the walk toy, the memory-wait toy (exit 6, MEMORY_WAIT note), the guards toy, plus the measured numbers (1149 MB and 833 s before, 124 MB and 35 s after). Done 2: the ENV toy, with a row exiting 1 staying FAIL, and the exit-code cases (6, 0, 1).

## What could break
A narrower walk selects fewer rows (README.md loses five, all reached only through `.git`); the byte caps (runs.py and lanes.py were over 19,000 already); a stale `exit 4` reader of the memory wait (test-budget-enforce and its row, updated).

## Out of scope
lane.py's slot-wait LANE_BUG text (a slot wait still exits 4), the nightly memory floor, and the scripts-under-19,000 rows for runs.py and lanes.py.

PENDING: none
