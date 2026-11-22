# Raise the pull-request shard job's time limit from 20 to 30 minutes at the workflow generator (TD847, o755's 30-minute code PR-checks limit)

- Slug: shard-timeout-30
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, dev/toy, .loop/regression.tsv, docs/wiki
- ETA: 265 active minutes (estimate 210m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the workflow generator, then the pull-request shard job's timeout-minutes is 30, written by the generator (no hand edit of regression-pr.yml), and the committed regression-pr.yml equals the generator's output.
2. Given the toys that check the generated workflow, then they assert the new 30-minute shard limit, every row still runs, and no other job's limit changes.
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
