# PR check row time limit: 300 seconds (owner o1019)

- Slug: v110-row-timeout
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, skills/workflow-delivery/scripts/cover.py, dev/toy/test-shard-budget.py, dev/toy/test-cut-complete.py, dev/toy/test-cover-lane.sh
- ETA: 255 active minutes (estimate 203m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a pull-request check row, when it runs, then its time limit is 300 seconds, in the workflow template and the generated regression-pr.yml alike.
2. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
