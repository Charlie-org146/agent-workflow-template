# Fixes #5700 and #5671 (Operation TD604): dev/toy/test-platform-limits.py and dev/toy/test-machine-log.py pick up the Mac's live session state (host and session variables, the real HOME, the real git common dir), so their rows platform-sends-counted and machine-status-live-workers fail in qa lanes on the Mac while passing on CI. Both toys run hermetically: the host and session variables unset, a throwaway HOME and git common dir, the #5671 hunk taken from hidden-red-fixes. No check removed or loosened

- Slug: toy-hermetic
- Touches: dev/toy/test-platform-limits.py, dev/toy/test-machine-log.py
- ETA: 270 active minutes (estimate 215m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each toy run with the Mac's real session state, then it fails as today; run hermetically by its own setup, then it passes, and its rows platform-sends-counted and machine-status-live-workers pass in a qa lane on the Mac
2. Given each changed toy, then every assertion is kept, no check is skipped, and a control proves the toy still fails when its own subject is broken
3. Given this goal's diff, then only the two toys and the goal's own records change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
