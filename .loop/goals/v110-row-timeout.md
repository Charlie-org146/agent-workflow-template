# PR check row time limit: 300 seconds (owner o1019)

- Slug: v110-row-timeout
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, skills/workflow-delivery/scripts/cover.py, dev/toy/test-shard-budget.py, dev/toy/test-cut-complete.py, dev/toy/test-cover-lane.sh, docs/wiki/How-to-use-Regression.md
- ETA: 255 active minutes (estimate 203m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a pull-request check row, when it runs, then its time limit is 300 seconds, in the workflow template and the generated regression-pr.yml alike.
2. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `grep -c -- '--timeout 300' .github/workflows/regression-pr.yml`. Expect: 2 (the tree shard line and the numbered shard line).
2. Run `grep -c -- '--timeout 300' skills/workflow-regression/scripts/lanes_cli.py`. Expect: 2, and `grep -c -- '--timeout 200'` on both files gives 0.
3. Run `python3 skills/workflow-regression/scripts/regression.py workflow`, then `git status --porcelain .github/workflows/`. Expect: no change (the committed workflow matches the template).
4. Run `python3 dev/package.py --static`. Expect: a PASS line (the package rules hold).
