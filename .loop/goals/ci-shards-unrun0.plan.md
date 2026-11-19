# Plan: ci-shards-unrun0

Checked against the code: `SHARDS` and `BUDGET_MINUTES` are module constants in skills/workflow-regression/scripts/actions.py;
`render()` fills @SHARDS@ and @MATRIX@ from them; slots.py SUMMARY_JOB carries `SHARDS: "@SHARDS@"`; the shard split is
`(seen - 1) % shards != mine` in the embedded runs.py rowtail.

## Build steps
1. actions.py: `SHARDS = 16` (done).
2. regression.yml: matrix 0..15, `REGRESSION_SHARD: .../16`, summary `SHARDS: "16"` (done, three lines, not regenerated).
3. dev/toy/test-regression.sh: the workflow-shape row greps the 16-shard matrix (done).
4. Commit, `goal.py pr`, then dispatch regression.yml on the branch; read the summary line.

## Tests per done line (no new rows)
1. The dispatch run itself: `SHARDS 16 of 16 reported. UNRUN 0`.
2. test-regression.sh unrun row and test-gate-ci-suite.py (UNRUN 3 refuses; 7 of 8 refuses); test-automation-budgets.sh derives the
   matrix from actions.SHARDS and still passes.
3. `git diff --stat main` lists only the three files and the goal's own .loop/goals files; regression.tsv untouched.

## Could break
A residue still too heavy for 30 minutes (then 24 shards); test-regression.sh is skipped on Windows (runs on Mac and CI);
wiki wording "eight" drifts until the release docs rewrite.

## Out of scope
A longer timeout, regenerating regression.yml, balancing rows by time, fixing red rows.
