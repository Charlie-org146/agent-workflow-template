# The loop survives a restart (TD463 restart-safe items 3 to 5, TD509; MCH-1): (a) persistent scratch: scratch.py path GOAL gives ~/.workflow-loop/scratch/GOAL so no loop script hard-codes /tmp, plus a health row counting worktree entries whose folder is missing; (b) a folder-trust health row listing pool or worker sessions whose worktree has no trust entry in ~/.claude.json (read only), and sessions.py assign refuses such a folder with ask the owner to trust it; (c) after MERGED the root checkout is fast-forwarded only when clean and on main, else one line root is dirty, not advanced, plus a stale-root health row; (d) the merge watcher arm-clean runs from the repo or is covered by the tick after a restart, and the PR says which. Net-zero files: new code goes into existing scripts (TD489)

- Slug: restart-safe-3to5
- Touches: skills, dev/toy
- ETA: 390 active minutes (estimate 310m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of (a) to (d), then a toy proves it with a negative control, and each new health row is SEEN RED with its check removed
2. Given the pull request, then nothing writes ~/.claude.json or accepts any trust, the PR body says how the watcher survives a restart, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
