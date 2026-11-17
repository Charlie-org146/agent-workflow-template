# REG-1: The home guard no longer reports a false LEAK when another session writes ~/.workflow-loop/skills-main, or the real schedule registry, during a toy run (#4760)

- Slug: homeguard-skills-main
- Touches: dev/toy/homeguard.py, dev/toy/test-home-guard.py
- ETA: 180 active minutes (estimate 141m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given another process writes ~/.workflow-loop/skills-main/.loop/START.md or schedule/repos.json during a toy run, when the guard checks, then it reports no LEAK
2. Given a toy itself writes into ~/.workflow-loop/skills-main or schedule/repos.json, when the guard checks, then it still reports the LEAK, with a negative control in test-home-guard.py

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
