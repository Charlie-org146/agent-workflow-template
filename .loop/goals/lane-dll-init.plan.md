# lane-dll-init plan

I checked these against lane-memory's branch (`loop/lane-memory` at 57e67f0b, which merges first):
- `runs.execute`: lane-memory added `START_CODES`, the `nostart` state, the `ENV <id> (exit N: could not start; ...)` line and the `env` flag.
- `regression.py cmd_run`: lane-memory's version exits 1 on any FAIL, `slots.EXIT_ENV` (6) when ENV rows are over half the lane, else 0.
- `lane.py finalize` turns `EXIT_ENV` into `LANE_ENV`, and lane-memory's `guards.failed_try` doesn't count it.

This goal changes `runs.execute` only. `runs.py` stays at net zero bytes against lane-memory's version (19,997), because
trim-scripts-19k (#4653) owns trimming it.

## Build steps (after lane-memory merges; base the branch on that main)
1. In `runs.execute`, copy `keep` (`list(todo)`, so the caller's list is never extended). A row whose first exit is in `START_CODES` is held in
   `first` and appended to `keep` once, so it reruns after every other row. On its second turn it runs again. If the budget is already
   spent, it reuses the first result instead of going LEFT. Only a row that is still dying becomes ENV, exactly as lane-memory
   defines it. To pay for the added bytes, compact the same function: build the row env once and reuse it for `run_row` and
   `shown`, and fold the two `remaining is None` checks into `late`/`cap`. The output text doesn't change.
2. Add a toy, `dev/toy/test-lane-dll-init.py` (`# windows: ok`, with `# reads:` naming runs.py and regression.py). It stands in for
   `lanes.run_row` in-process, because a bash row can't exit 0xC0000142.
   - Done 1: a row that dies once and then passes is PASS after two runs. A row that always dies is ENV after two runs, never FAIL,
     and its line names the exit code. A row that dies with the budget spent keeps ENV and is not LEFT. A lane of only dying rows,
     run through `regression.py run`, exits `EXIT_ENV`: not a counted try.
   - Done 2: `regression.py run` over one row exiting 1 beside three dying rows exits 1, with the dying rows still ENV.
3. Add two rows: `regression.py add lane-dll-init-rerun --goal lane-dll-init:1` and `lane-dll-init-real-fail --goal lane-dll-init:2`,
   both category criterion, level land. Prove each red with `red --break` (one breaks the rerun, one makes a start code
   count as FAIL), then re-render the Tests tables.
4. Add one sentence to the Regression page where lane-memory describes ENV rows: the row is rerun once first.
   Fill in Verify by hand.

## Test per done line
The rows in step 3, each seen failing against the broken code and passing after the change. The toys `test-not-runnable.py`,
`test-lane-memory.py`, `test-row-output.py`, `test-lane-fail-text.py` and `test-budget.sh` must still pass.

## What could break
- A row whose first run left files behind (it couldn't start, so it can't have) would trip LANE_DIRTY. No risk is expected here.
- A lane of hundreds of dying rows takes about twice as long on them. A start failure returns in milliseconds, and the budget still caps the lane.
- Row order in the results changes for rerun rows. Nothing reads the order.

## Out of scope
- The runs.py split and trim (#4603, #4653).
- A whole lane process that can't start (rc 0xC0000142 from lane.py itself): lane-memory's LANE_ENV and LANE_DIED paths come
  first. If it's still seen after that, it gets filed as a backlog item at ship.
- Other Windows start codes beyond lane-memory's `START_CODES`.
