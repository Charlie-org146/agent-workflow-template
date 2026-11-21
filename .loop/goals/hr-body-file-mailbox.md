# Second half of hidden red issue 5651 (TD567): skills/workflow-monitoring/scripts/mailbox.py line 201 passes an issue text to gh issue create with --body, which dev/toy/test-body-file.sh forbids; pass it through a temporary file with --body-file, removed afterwards, the same way loop/hr-body-file fixed machines.py, no other behaviour change. mailbox.py is 18,994 bytes and must stay under 19,000 (prose trims only, never reformat code). Paired with hr-body-file: the test exits 0 only with both. Code only: no row, no known list, no setting changes

- Slug: hr-body-file-mailbox
- Touches: skills/workflow-monitoring/scripts/mailbox.py
- ETA: 270 active minutes (estimate 215m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given loop/hr-body-file's machines.py fix merged in and this fix, then dev/toy/test-body-file.sh prints no FAIL line and exits 0, and with this fix reverted it prints the mailbox.py FAIL again
2. Given mailbox.py's changed call, then the same text reaches gh through --body-file, an existing toy that covers the ops-finding issue proves the text and labels arrive unchanged, and the temporary file is removed afterwards
3. Given this goal's diff, then only mailbox.py (under 19,000 bytes) and the goal's own records change, the docs check passes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
