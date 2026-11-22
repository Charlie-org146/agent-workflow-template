# Make the machines, desk and restart-tick toys pass on Windows by fixing only their fixtures and setup: stop child processes before the tempdir is removed, and give the tick toy a Windows-runnable fake gh and PATH

- Slug: windows-toy-cleanup
- Touches: dev/toy/test-machines.py, dev/toy/test-desk.py, dev/toy/test-restart-tick.py
- ETA: 235 active minutes (estimate 185m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the toy has started child processes, when it ends, then they are stopped before the tempdir is removed and cleanup raises no WinError 32.
2. Given a fake gh and a stub merge.py, when the tick runs on Windows, then merge.log exists with the expected calls.
3. Given the same toys on macOS, then their PASS lines are unchanged (the control).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
