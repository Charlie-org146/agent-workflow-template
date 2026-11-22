# shard-timeout-30: plan

Goal: the pull-request shard job's `timeout-minutes` goes from 20 to 30 at the generator (TD847, o755's 30-minute code PR-checks limit). A one-value patch; every change below is named with its file and line, measured on origin/main f8118b117 at the goal's base e9cea93d8.

## Facts (read in the worktree)

- `skills/workflow-regression/scripts/lanes_cli.py:187` is `    timeout-minutes: 20` inside the `shard:` job; `:221` is 8 (the `affected` job), `:249` is 5 (the `small` job, merge_group), `:270` is 30 (the scheduled workflow). Only :187 changes. The file is 20,477 bytes and `20` to `30` is the same length, so it stays 20,477 (under the 20,480 cap; it was already over 19,000, so it does not newly cross).
- `.github/workflows/regression-pr.yml` is generated ("Written by workflow-regression (regression.py workflow)"); its limits are line 16 (shard, 20), line 50 (affected, 8), line 78 (small, 5). The generator is run as `python3 skills/workflow-regression/scripts/regression.py workflow --visibility public`.
- `dev/toy/test-tree-first.py:115-116` and `dev/toy/test-shard-balance.py:209-211` assert the committed regression-pr.yml equals the rendered one, so regenerating keeps them green and a hand edit would turn them red.
- No toy asserts the shard job's limit today. `dev/toy/test-local-schedule.sh` case `triggers` (row `ls-narrow-triggers`, line 259-262) asserts the generated regression-pr.yml's triggers and jobs and "a merge_group job with a 5 minute timeout", and builds the file with the generator into a temporary repo.
- `.github/workflows/regression.yml` (the scheduled workflow) has its own budget limits (test-automation-budgets.sh) and is not touched.

## Build steps (in order)

1. `lanes_cli.py:187`: `timeout-minutes: 20` to `timeout-minutes: 30` (one value, same byte length).
2. Regenerate `.github/workflows/regression-pr.yml` with the generator (no hand edit): its diff is exactly one line (line 16, 20 to 30). Check `regression.py workflow` again leaves it unchanged (committed == rendered), and run `test-tree-first.py` and `test-shard-balance.py`.
3. Extend the existing row `ls-narrow-triggers` by adding, to the `triggers` case in `dev/toy/test-local-schedule.sh`, one `check` that the generated regression-pr.yml has: the `shard` job's `timeout-minutes: 30`, the `affected` job's 8 and the `small` job's 5 (each read from its own job block with the same `sed -n "/^  <job>:/,/^  <next>:/p"` bounding the case already uses), and the unchanged matrix `shard: [0, 1, 2, 3, 4, 5, 6, 7, tree]`. No new row, no new file; no existing check is edited or loosened.
4. Red proof (seen failing first): run the new check against the unchanged generator output (20) and against a copy with another job's limit changed; both must fail; then the changed generator passes.
5. Check: `docs.py check` DOCS OK; the byte caps (lanes_cli.py 20,477); `regression.py` rows the change reaches pass; the other jobs' limits are 8 and 5 and the scheduled workflow is unchanged.
6. PR notes in the goal file before the lane: the one-line workflow diff, the red proof, the limits table (shard 30, affected 8, small 5, regression.yml unchanged), and the plain limit: raising the limit does not make shard (1) faster; if it needs more than 30 minutes the next fix is the shard balance, not the limit.

## Done-line mapping

Line 1: step 1, 2 (generator writes 30; committed == rendered). Line 2: steps 3-4 (the toy asserts 30, 8, 5 and the matrix, so every row still runs and no other limit changes). Line 3: the package rule: lanes_cli.py stays 20,477; no new file; no test loosened; nothing names the service repo.

## What could break

- A toy elsewhere that hard-codes the old 20 for the shard job: searched: none (grep of dev/toy for "timeout-minutes"); the build repeats the search before recording.
- The generator's other output: a public repo's regression.yml and regression-pr.yml are both rendered by `regression.py workflow`; only regression-pr.yml may change, and the build checks regression.yml is byte-identical.

## Out of scope

Balancing the shards, any other job's limit, the o755 limits table (fast-clock), the merge queue, v110-fast-ci-2's workflows.
