# The merge queue's check is a small FIXED smoke, not a selection by reach (REL-15, Operation TD348: the first queue run of results-render failed because the merge_group small job selects rows by reach and its 60-second per-row timeout killed a slow toy, tables-prep-151, run 44721306280). The merge_group job named small runs on the merged result: python3 skills/workflow-docs/scripts/docs.py check, python3 -m py_compile on every script under skills/, and python3 skills/workflow-docs/scripts/criteria.py render --check, within 2 minutes (job timeout 5 minutes), and nothing selected by reach. The change is made where regression-pr.yml is generated (NARROW in lanes_cli.py) and the file is regenerated; lanes_cli.py must not end larger than main's size (real trims if needed, no reformat); the job keeps the name small so the ruleset's required check still matches. The pull_request job named affected is unchanged. Lane prep (Tests-table render and restamp) and the red proof for any added row run before the push, no local lane

- Slug: queue-smoke
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, dev/toy/test-local-schedule.sh
- ETA: 345 active minutes (estimate 275m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the merge_group event, when the small job runs, then it runs docs.py check, py_compile on every script under skills/ and criteria.py render --check and nothing selected by reach, the job is named small, and its timeout is 5 minutes
2. Given lanes_cli.py and the generated regression-pr.yml, then the workflow is regenerated from NARROW, lanes_cli.py is no larger than on main, and the pull_request job named affected is unchanged
3. Given this goal's diff, then only lanes_cli.py, regression-pr.yml, the toy or row that guards the small job's steps and the goal's own record files change, any added row has its red proof recorded, and the docs check passes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
