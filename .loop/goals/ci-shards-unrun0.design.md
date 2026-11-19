# Design: ci-shards-unrun0

## Problem
Main's nightly-level run split the rows over 8 shards by row index modulo 8, 30 minute job limit. The load is lumpy: in run
44463859531 shard 4 finished in 7 minutes while shards 3 and 6 used the whole 28 minutes of job time and skipped 73 and 101 rows
(UNRUN 169), so `review.py gate --suite-from` correctly refuses it.

## Approaches
1. More shards (16): the matrix, the shard divisor and the summary job's SHARDS go from 8 to 16. Each shard gets half the rows,
   so the lumpy residues are halved. Cost: more free runner jobs on a public repo. Risk: a residue may still be too heavy.
2. Longer job timeout: conflicts with REG-7, AUT-7 and the budgets-agree row, which name the 30 minute budget and a suite
   sharded to fit it, and needs wiki edits.

## Chosen
1. Keep 30 minutes; SHARDS = 16 in skills/workflow-regression/scripts/actions.py (the generator's constant) and the three matching
   lines in .github/workflows/regression.yml (matrix, REGRESSION_SHARD divisor, summary SHARDS). regression.yml is not regenerated:
   the generator output carries ~190 lines of unrelated drift, which is another goal's. One toy row greps the old matrix text.
   If a dispatch still shows UNRUN > 0 the next step is more shards (up to 24), not a longer timeout.

## Done lines
1. Dispatch regression.yml on the PR head; its summary must end `SHARDS 16 of 16 reported. UNRUN 0`.
2. Negative control, no new row: test-regression.sh "a row skipped for job time is recorded as unrun" and test-gate-ci-suite.py
   (UNRUN 3 and 7-of-8 runs refuse) already prove a slow shard keeps UNRUN > 0 and the gate refuses it; run both.
3. No row added or removed; touched: regression.yml, actions.py (SHARDS), dev/toy/test-regression.sh (matrix grep).

## Open questions
None for the owner. The wiki says "eight parallel jobs" (Regression.md Steps); the release step's docs rewrite owns that.
