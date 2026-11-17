# hotfix-4859 design

## Problem
v1.0.45 made `settings.py fill_private` also create `~/.workflow-loop/repos` (and health.json) from `~`. `dev/toy/test-defect.sh` sets `LOOP_FLOW` and `LOOP_HEALTH` through reap.sh but not HOME, so its `setup.py` call writes into the runner's real HOME and `homeguard.py` fails the toy at exit with LEAK. That turns defect-owed, pr-body-no-checks and worker-runs-release red on CI (#4859).

## Approaches
1. Sandbox HOME and USERPROFILE in the toy, after reap.sh is sourced, the way test-goal-release.sh and test-budget.sh do. One line, no product change. Risk: none; the guard remembers the real folder it snapshotted.
2. Make `fill_private` honour LOOP_FLOW's folder for `repos`. Changes product behaviour for a test's sake, and a toy that sets HOME is the repo's convention.

## Chosen
Approach 1, plus a `home-sandbox` case in the same toy and a defect row `home-sandbox-4859` (seen red on the old toy) as the issue's defect test. No new file.

## Done lines
1. The toy runs under a temp HOME and USERPROFILE: the export line.
2. The three rows pass, with a negative control: the new case fails on the old toy (HOME equals the real HOME) and homeguard reports `LEAK ... added repos` on the old toy against a non-temp HOME.
3. doc19-item-missing, judge-key-old and link-unread-never-pass do not share the cause: judge-key-old is a TypeError in file.py:108 (`IS.about` missing args), the other two are DOC-5 and DOC-19 page drift. They are named in the PR. None of the six rows is in `.loop/regression-known.tsv`, so nothing is removed.

## Open questions
None.
