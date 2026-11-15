# regression-fix: plan

Checked against the code: `skills/workflow-monitoring/scripts/board_status.py` (`stalled_line`, `slug_busy`, `LOOP_PROCS`),
`checkin.py` (the silent and STALLED lines), `dev/toy/test-monitoring-prd.sh` (`case_mon8`), `dev/toy/reap.sh` (sourced first by
every toy), `board_status.py` (`memory`, `allowed`, `LOOP_MACHINE`), `skills/workflow-health/scripts/issues.py` (`key_of`,
`legacy`, `evidence_of`) and `file.py` (`held_all`, `plan`). All exist as the design says.

## Build steps
1. mon8: `case_mon8` sets LOOP_PROCS so both goals have a process (done, passes with the fake machine on this PC).
2. Machine: `reap.sh` exports LOOP_MACHINE "64,64,10,0,0" unless a toy set one (done); mon12 now passes on this 4 GB PC.
3. set8 and lane-over-minutes: both toys print what they cannot explain (a diff of what the refusal wrote; the t6 lane log).
   Run both rows on Actions from this branch, read the output, fix the code or toy it names, and repeat until both pass.
4. #4379: `issues.posix` in `key_of`, `legacy`, `evidence_of`; `file.held_all` and the issue title use it (done).
5. After the merge: close the existing duplicate pairs once, naming the issue kept; close each of the seven issues with the passing
   line from the Actions run on main.

## Tests, one per done line
- Rows mon8-silent-30, grd8-silent-worker, mon12-pool, parallel-unlimited, held-all, set8-local-setting-refused and
  lane-over-minutes pass on Actions on this branch (each was FAIL there).
- `defect-4375-toys-fake-machine`: seen red by removing the export (STILL GREEN is refused), green with it.
- `defect-4379-health-key-posix`: seen red by making `posix` return its text; 7 of 9 checks fail on the old code.

## What could break
- A toy that tests memory must set its own LOOP_MACHINE (test-machine-status.py does; it never sources reap.sh).
- Keys held by old issues read through `posix`, so an issue written with a backslash key is found, updated once, and its marker
  rewritten with the forward-slash key.
- Sizes: file.py 18,781 and issues.py 18,345 LF bytes, under 19,000. No file is added to the package.

## Out of scope
The 100+ older rows pool-09's sweep-regression owns; reviewed requirement text; the Documentation page staleness (#347, #3903).

VERDICT: self-check: the design meets the frozen done lines
DEPTH: full
