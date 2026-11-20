# update.py stop() works on Windows, where os.killpg does not exist

- Slug: win-killpg
- Touches: skills/workflow-setup/scripts/update.py
- ETA: 190 active minutes (estimate 149m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. skills/workflow-setup/scripts/update.py stop() ends the process tree on Windows without calling os.killpg, keeps os.killpg on POSIX, and regression row win-posix-calls-gone passes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
