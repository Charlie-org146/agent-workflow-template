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

## Worker evidence (2026-11-20)

- Changed only the batch PR body transport: UTF-8 temporary file, closed before gh reads it, passed with `--body-file`, removed in `finally`. Followed `autorelease.sh_text`; trimmed only introductory prose for size. machines.py: 18,927 bytes before, 18,907 after.
- `bash dev/toy/test-body-file.sh`: baseline exit 1 names machines.py:168 and the pre-existing mailbox.py:201. With the fix, exit 1 names only mailbox.py:201. Replaced machines.py temporarily with HEAD's original bytes: exit 1 names machines.py:168 again. Restored the fixed bytes: only mailbox.py:201 remains. Full green is blocked by that out-of-scope violation; it was not hidden or changed.
- Temporarily added assertions to existing `dev/toy/test-merge-batch.sh`'s driver: read the body file as bytes, compare with the unchanged body derived from the batch title, compare fake gh's saved body, and assert the path is absent after batch returns. The toy printed `PASS: body bytes reach gh unchanged and temporary file is removed`, all its other assertions passed, and it printed `ALL PASS`. Restored the toy byte for byte; no new row or test file.
- `docs.py check`: exit 0, DOCS OK (16 pages). `criteria.py render --check`: exit 0, TABLES OK. `dev/package.py --static`: exit 0, static rules hold (100 files).
- `bash dev/toy/test-pods.sh size`: all three assertions pass and ALL PASS. Both this and the batch toy exit 77 because sandbox permissions deny the cleanup helper's process listing (`ps`); leftover-process cleanup could not be checked.
- `private.py hook staged` and `git diff --check`: exit 0. Startup `entry.py lag` printed nothing. No config changes, publishing, or pull request.
