# ci-small-groups plan

Checked: the 12 rows and their toys exist in .loop/regression.tsv and dev/toy (test-review-depth.sh, test-automation.sh, test-health-prd.sh, test-automation-email.sh, test-settings-table.sh, test-live-board.sh, test-milestone-wording.sh, test-budget.sh, test-health-on-windows.py); .github/workflows/regression.yml takes a `target` row id on workflow_dispatch and runs the rows from the ref's checkout.

## Build steps
1. For each toy, make the failing check print what it saw on failure only (board text, issue calls, the output compared). Commit and push the branch.
2. Dispatch regression.yml on this branch with each failing row as the target; read the cause from the CI log.
3. Fix each cause in the toy or in the code it guards; a cause that is real and cannot pass on CI (a Mac-only check, a runner without something) gets the row's CI behavior set the way the CI block already does (TOY_SKIP_FILE skips) and its cause written on the issue.
4. Re-dispatch until each row passes on CI; run the same rows on the PC with regression.py run.
5. Comment each issue with its cause and proof; the merge closes #4557 and #4558 only when all their rows pass or carry a written cause.

## Test per done line
Done 1: the dispatched CI runs for the 12 rows, then the next full run on main. Done 2: `regression.py run` for the rows on the PC and the lane's passing set.

## What could break
A fix to code the toys guard (live_board.py, health, automation) changing PC behavior; the toys that skip on Windows can only be proved on CI.

## Out of scope
The other CI groups (#4553 to #4556, ci-setup-rows) and rows outside these 12.

PENDING: none
