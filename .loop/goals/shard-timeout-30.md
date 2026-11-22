# Raise the pull-request shard job's time limit from 20 to 30 minutes at the workflow generator (TD847, o755's 30-minute code PR-checks limit)

- Slug: shard-timeout-30
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, dev/toy, .loop/regression.tsv, docs/wiki, .loop/regression-known.tsv
- ETA: 265 active minutes (estimate 210m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the workflow generator, then the pull-request shard job's timeout-minutes is 30, written by the generator (no hand edit of regression-pr.yml), and the committed regression-pr.yml equals the generator's output.
2. Given the toys that check the generated workflow, then they assert the new 30-minute shard limit, every row still runs, and no other job's limit changes.
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

Raises the pull-request shard job's time limit from 20 to 30 minutes at the generator. Basis: the owner's record o755 and TD847 (code PR-checks limit 30 minutes).

**The one-line workflow diff** (`.github/workflows/regression-pr.yml`, shard job, regenerated with `regression.py workflow --visibility public`, not hand-edited):

```
-    timeout-minutes: 20
+    timeout-minutes: 30
```

**Where it comes from.** `skills/workflow-regression/scripts/lanes_cli.py:187` (same byte length; the file stays 20,477 bytes). `regression.yml` is unchanged; the committed `regression-pr.yml` equals the generator's output (`test-tree-first.py` and `test-shard-balance.py` still pass).

| Job | Limit (minutes) |
|---|---|
| shard | 30 (was 20) |
| affected | 8 (unchanged) |
| small | 5 (unchanged) |
| regression.yml (scheduled) | unchanged |

**Red proof.** In `dev/toy/test-local-schedule.sh` the `triggers` case (row `ls-narrow-triggers`) gains a separate check that reads the generated file: shard 30, affected 8, small 5, and the shard matrix still runs shards 0 to 7 and tree. With the generator at 20 that check FAILS; at 30 the case prints ALL PASS.

**The stale clause fix (named, approved by operation).** The case's existing clause expected `shard: [0, 1, 2, 3, 4, 5, 6, 7]`, but the generated file has had the tree cell (`[0, 1, 2, 3, 4, 5, 6, 7, tree]`) since TD504, so `ls-narrow-triggers` was already red on main. The clause now expects the tree cell. This PR merges before fix-5727's PR (#5772), which needs this patch to go green, so no `ls-narrow-triggers` known row exists on main when this merges and nothing is removed here; fix-5727 removes the row itself after it merges main up and the row passes. #4061 is not closed by this PR.

**Depth.** The plan ran at condensed depth for this goal only (TD850): the change is one generator line plus one assertion, so a full multi-round review costs far more than it can find. The plan gate recorded one BREAK (principle 3: DEL-17's 5-minute clock against 30), accepted on the owner's record o759 (`plan-accept`).

**The plain limit.** Raising the limit does not make shard (1) faster. If it needs more than 30 minutes, the next fix is the shard balance, not the limit.

**Named follow-up.** Rebalance the PR shards so shard (1) fits well under 30 minutes.
