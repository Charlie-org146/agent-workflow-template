# ci-small-groups design

## Problem
Twelve regression rows fail on the Linux CI runner but not on the PC: the 3 review-depth marker rows (#4557: depth-on-board, depth-in-pr-body, depth-reference, all from test-review-depth.sh) and 9 automation, health and milestone rows (#4558, from 8 toys). The issues say "cause not yet read". CI run 43994068499 (v1.0.32, the latest completed full run on main) still fails all 12, so none is fixed yet; later runs (v1.0.33, v1.0.34) were still running when this was written.

## Approaches
1. Read each toy and guess the cause. Cheap, but the PC cannot run these bash toys (they skip on Windows) and the CI log keeps only the last 20 lines of a failing row, so a guess cannot be checked.
2. Make each failing check print what it saw (the board text, the issue calls it made, the command output), then dispatch the regression workflow (workflow_dispatch, target one row, ref this branch) to read the cause from the CI log; fix the toy or the code it guards, or write the real cause on the issue when the row cannot pass on CI (for example, a row about the Mac's local schedule).

## Chosen
Approach 2: each failure becomes a read cause or a fix, never a guess. Diagnostics stay in the toys only where they print on failure, so they cost nothing on a pass.

## What each done line needs
1. Each of the 12 rows passes on CI, or the issue carries its real cause. Check: a dispatched CI run on this branch for each row, then the full run after merge.
2. The same rows still pass on the PC: the lane and `regression.py run ROW` here (rows that skip on Windows are run by the dispatched CI run).

## Open questions
None for the owner. A row whose cause is real and not fixable on CI (a Mac-only check) gets its cause written on the issue and is marked in the row, not deleted.
