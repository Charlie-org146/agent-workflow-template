# The hidden reds stay in v2.0, each with a test that runs it (owner, TD581 and TD582): one change brings every hidden-red toy back to green. It carries the five reviewed toy batches (hrt-flow, hrt-docs, hrt-health, hrt-monitor and hrt-misc), fixes #5675 (the settings table), makes the four environment toys (#5657, #5663 with BSD sed portability, #5665 and #5671) and test-govern.sh hermetic so no real claude agent starts, and adds about 8 to 10 grouped defect rows that each run a group of these toys in under 200 seconds and link every issue they cover. The PR body says Fixes #N for every issue whose toy is green

- Slug: hidden-red-fixes
- Touches: dev/toy, .loop/regression.tsv, skills/workflow-setup/scripts/settings.py, README.md, docs/wiki
- ETA: 245 active minutes (estimate 196m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every toy listed in the hidden-red issues, then it exits 0 with no FAIL line on this branch outside any sandbox, and any toy still red is named with its reason in the pull request body
2. Given the grouped defect rows, then each runs its group in under 200 seconds, links every issue it covers, and was seen failing (on main or by a recorded break) and then passing
3. Given this goal's diff, then only toys and their fixtures, the settings table and its rendered pages, the new rows, re-rendered pages and the goal's own records change; no check is weakened, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
