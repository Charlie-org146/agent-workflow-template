# Plan: record-commit-ci

Checked against the code: `role.record()` (role.py:336) makes the one bookkeeping commit "pr: record issue states and the
lane's results"; `goal.py cmd_pr` calls it at goal.py:381 and `fit.pr_open` (fit.py:305) is the first and only push, so lane
commit and record commit land in one push today. The workflow text is the `PR_WORKFLOW` template in `lanes_cli.py`
(rendered by `regression.py workflow`), committed as `.github/workflows/regression-pr.yml`. The job is named `affected`.

## Build steps

1. `skills/workflow-regression/scripts/recordonly.py` (new, under 19,000 LF bytes): `HEAD` checks exactly as the design
   lists; reads the parent's check runs through `gh api`, polls up to 25 minutes while queued or in progress, prints
   `RECORD-ONLY <parent>` (exit 0) or `FULL <why>` (exit 1). Pure functions for the file test and the check verdict so a
   toy can drive them without a network.
2. `lanes_cli.py`: the template gets `checks: read`, an `id: rec` step running recordonly.py with `continue-on-error`,
   `if: steps.rec.outcome == 'failure'` on the rows step, and a concurrency `cancel-in-progress` that is false for a push
   whose head commit message starts "pr: record". Trim comments/text in the file so it does not grow past its size.
3. `regression.py workflow` regenerates `.github/workflows/regression-pr.yml`; commit it.
4. `goal.py cmd_pr`: one best-effort `git push -u origin <branch>` before `role.record`, so the lane head is a pushed
   parent. goal.py is at 18,999 LF bytes: trim at least as many bytes of comments or text first so it ends at or under
   19,000.
5. `dev/toy/test-record-ci.py` with a temp git repo and a fake `gh`: RECORD-ONLY with a passing parent; FULL with a failing
   parent, no parent result, an extra file, an unlisted wiki line, two parents, a wrong subject. Rows `record-ci-skip` and
   `record-ci-full` added with `regression.py add` and seen failing with `red` before step 1 lands.
6. Delivery page: reword the DEL-1 "(v2.0 planned) A pr record commit..." line as the rule, with its Tests row; the new
   wording goes to the owner for review.

## Test per done line

1. Row `record-ci-skip` (toy cases above, RECORD-ONLY with a passing parent; the workflow text contains the step and the
   `if`), seen failing before step 1.
2. Row `record-ci-full`: every FULL case, so a head whose record commit touches anything else still gets the full round.

## What could break

- A parent check that never appears: bounded wait, then FULL, so CI never passes unproven.
- The extra push races the `pull_request` run; both are keyed on the head, and merge.py still reads the final head's checks.
- Script sizes: recordonly.py new; lanes_cli.py and goal.py must not exceed 19,000 LF bytes.
- The pr-lane `.ok` and `pr_head` records are unchanged.

## Out of scope

merge.py, the lane's own row selection, the scheduled full suite, and any change to which paths count as bookkeeping beyond
`.loop/regression-issues.tsv` and the generated result lines of the Tests and Documentation pages.
