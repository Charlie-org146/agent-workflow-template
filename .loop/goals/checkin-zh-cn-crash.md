# Fix checkin.py crashing on a zh-CN Windows PC: slug_busy (and other Windows tool-output reads) decode non-UTF-8 code-page bytes as UTF-8 (issue #4810)

- Slug: checkin-zh-cn-crash
- Touches: skills/workflow-monitoring/scripts/board_status.py, .loop/regression.tsv, dev/toy
- ETA: 205 active minutes (estimate 162m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a process list containing bytes that aren't valid UTF-8, when checkin.py runs with PYTHONUTF8=1, then it prints the check-in, and slug_busy treats the unreadable line as text instead of raising.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
