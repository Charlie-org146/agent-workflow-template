# Fix hidden red issue 5651 (TD567): machines.py line 168 passes a pull request text with --body, which dev/toy/test-body-file.sh forbids (text goes through --body-file). Pass it through a temporary file with --body-file like the other callers, no other behaviour change; machines.py stays under 19,000 bytes (prose trims only, never reformat code). Code only: no row, no known list, no setting changes

- Slug: hr-body-file
- Touches: skills/workflow-monitoring/scripts/machines.py
- ETA: 270 active minutes (estimate 215m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given dev/toy/test-body-file.sh run on this branch, then it prints no FAIL line and exits 0, and with the fix reverted it prints the machines.py:168 FAIL again
2. Given machines.py's changed call, then the same text reaches gh through --body-file, a toy or existing test proves the text arrives unchanged, and the temporary file is removed afterwards
3. Given this goal's diff, then only machines.py (under 19,000 bytes) and the goal's own records change, the docs check passes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
