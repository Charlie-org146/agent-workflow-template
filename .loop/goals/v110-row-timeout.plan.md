# Plan: v110-row-timeout (owner words o1019), on origin/main af5cddd37

Goal: the pull-request check's per-row time limit is 300 seconds. Frozen done lines: (1) Given a pull-request check row, when it runs, then its time limit is 300 seconds, in the workflow template and the generated regression-pr.yml alike. (2) The standard package line.

Owner record: o1019 "Raise the pull-request check's per-row time limit from 200 to 300 seconds." Scope of the forced consequences: TD1935.

Size fields (for sizing.py; 6 hand-edited files):
Files: skills/workflow-regression/scripts/lanes_cli.py
Files: .github/workflows/regression-pr.yml
Files: skills/workflow-delivery/scripts/cover.py
Files: dev/toy/test-shard-budget.py
Files: dev/toy/test-cut-complete.py
Files: dev/toy/test-cover-lane.sh
Lines: ~10 (6 to 14)
Gates: none
Classes: none

## Steps (one commit)

1. lanes_cli.py, the regression-pr.yml template: the tree shard line's `--timeout 200` and the numbered shard line's `--timeout 200` become `--timeout 300` (same bytes; the file stays at 20,448).
2. Regenerate .github/workflows/regression-pr.yml with `python3 skills/workflow-regression/scripts/regression.py workflow`; the only change in the file is those two figures (checked by diff).
3. cover.py: WF_SHA becomes the sha1 of the regenerated regression-pr.yml (LF, stripped, as pinned() reads it), in the same commit, so the cover keeps holding on the new workflow.
4. Toys move their expected 200 to 300, each checking the same thing at the new figure: test-shard-budget.py (the limit sits on both shard lines), test-cut-complete.py (its replace now targets "--timeout 300"), test-cover-lane.sh (the narrowed-call variant).

## Tests

- Red first: each of the three toys and test-cover.sh's positive cover cases fail against the regenerated workflow before steps 3-4 (stale figure or pin), and pass after.
- The package's static rules pass (done line 2); the cheap rows run singly; the regression rows that read lanes_cli.py, regression-pr.yml and cover.py run in the qa lane (on the operation's go).

## Limits

- A slow row can hold its shard up to 300 s; the shard's own budget still bounds the shard.
- The cover pin moves with the workflow file (intended): any later edit of the workflow needs the same pin update.
