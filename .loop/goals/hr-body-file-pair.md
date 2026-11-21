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

## Deferred and skipped

Recorded by the autoplan step (run 20261120-190654); none of this is built here, each is a decision for the owner.

- S3 deferred: restore the usage docstrings that this goal shortened in machines.py (18,907 bytes) and mailbox.py (18,994 bytes), when the 19,000-byte limit has room.
- S2 skipped: no shared gh-text helper in this goal (two callers here, five older ones with different bodies).
- Follow-up 1: a Backlog issue for the 19,000-byte cap on machines.py and mailbox.py (restore the trimmed docstrings, or split).
- Follow-up 2: a shared gh-text helper, with `--body-file -` on stdin as an alternative to a temporary file.
- Follow-up 3: widen dev/toy/test-body-file.sh's grep to the `--body=`, `--notes=` and `-b` forms.
- Follow-up 4: a `--text-file` entry point for `mailbox.py finding`.
- Follow-up 5: a cleanup that never masks the gh result or the created URL (a failed `os.remove` after a successful create).
- Follow-up 6: a batch() body assertion in test-merge-batch.py or test-machines.py (the fake gh reads `--body-file`, checks the body and the removal).
- User challenge uc1, held for the owner: move the temporary-file write inside `try` and make the cleanup never mask the result in both calls (every Design, DX and Eng voice recommends it; about 40 bytes, and mailbox.py has 6 spare). The build keeps the original form until the owner decides.
- Only `file_finding` can approach a reachable failure: its only entry point is `mailbox.py finding --text`, whose own command line already carries the text once. `batch()` is changed for the lint invariant of issue 5651 and test-body-file.sh, not because of a past incident.
