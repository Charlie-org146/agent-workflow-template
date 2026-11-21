# Fixes #5651 as one change (replaces the split goals hr-body-file and hr-body-file-mailbox-2, whose frozen scopes each held one file): gh calls in machines.py (line 168) and mailbox.py (line 201) pass their text through a temporary --body-file, removed afterwards, instead of --body, and dev/toy/test-checkin-view.py's fake gh reads the --body-file contents at call time with the same assertion. Built from commits 04b4cf373 (machines.py), 20b402903 (mailbox.py) and 4f13136bc (toy); both scripts stay under 19,000 bytes. A defect row linked to #5651 runs dev/toy/test-body-file.sh

- Slug: hr-body-file-pair
- Touches: skills/workflow-monitoring/scripts/machines.py, skills/workflow-monitoring/scripts/mailbox.py, dev/toy/test-checkin-view.py, .loop/regression.tsv
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given dev/toy/test-body-file.sh, then it exits 0 with no FAIL line on this branch and fails on main (a defect row linked to #5651, seen failing then passing)
2. Given the changed calls, then gh receives the same text byte for byte through --body-file, the temporary file is removed, and test-checkin-view.py, test-mailbox.py, test-restart-tick.py and test-three-level.py pass as on main
3. Given this goal's diff, then only machines.py and mailbox.py (each under 19,000 bytes), test-checkin-view.py, the row, re-rendered pages and the goal's own records change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
