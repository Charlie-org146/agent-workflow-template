# lane-dll-init design

## Problem
On a Windows machine near its commit-memory floor, a lane row can die with exit 3221225794 (0xC0000142, STATUS_DLL_INIT_FAILED):
Windows couldn't start the row's process at all (#4639). Goal `lane-memory` (merging first, by operation-pc's decision) already
counts such a row as ENV, a SKIPPED state, rather than FAIL. A lane made mostly of ENV rows exits `EXIT_ENV`, which costs no
counted try. What's left is that a row which hit a passing memory squeeze is never tried again, so one bad second turns a row
the lane could have run into "not run".

## Approaches
1. **Rerun once at the end of the lane, inside `runs.execute`.** A row whose first exit is a start code goes to the back of the
   queue. When it comes up again it runs once more within the lane's budget, after the other rows have freed their memory. If
   it now passes or fails for real, that result stands. If it dies again, it is ENV as lane-memory defines it: listed as not
   run, with its exit code. Cost: a few lines in one function. Risk: a lane with hundreds of dead rows spends about twice as
   long on them, but a dead start returns at once, and the budget still caps the lane.
2. **Rerun the whole lane from `lane.py` when it ends with ENV rows.** Cost: a second lane run, changes in lane.py and guards.py
   (both near the size cap), and overlap with lane-memory's free-try logic. Risk: it repeats every passing row.

## Chosen
Approach 1. It is local to the function that sees the exit code, and it touches no file but `runs.py`, the toy and the rows.
Operation-pc's rule: `runs.py` must not grow (net zero bytes against lane-memory's version), because goal trim-scripts-19k
(#4653) owns trimming it. The rerun is paid for by compacting that same function. If the budget runs out before a row's
rerun, the row keeps its first result (ENV), never LEFT, so it is still listed with its cause.

## What each done line needs
1. `runs.execute`: start-code rows rerun once, and only rows still dying get `env` with the exit code on their `ENV` line.
   `regression.py run` (lane-memory) then exits 0, or `EXIT_ENV` when they are most of the lane, so no counted try. A toy shows
   a row that dies once and then passes as PASS, run twice. A row that always dies shows as ENV, run twice, never FAIL.
2. Negative control: one row exiting 1 beside several start-code rows makes `regression.py run` exit 1 (FAIL), with the start-code rows
   still ENV.
Toy: `dev/toy/test-lane-dll-init.py`, which stands in for `lanes.run_row` in-process, because a bash row can't really exit
0xC0000142. It has two criterion rows, `lane-dll-init:1` and `lane-dll-init:2`, each seen red.

## Open questions
None for the owner. The build starts only after lane-memory merges (operation-pc sends its sha).
