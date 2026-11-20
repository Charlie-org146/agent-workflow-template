# The Codex fallback finishes a goal on its own (TD520): (a) test-tree.sh's REAP step has a sandbox-safe path when ps is not permitted, so it passes or skips with a named reason, never a silent pass; (b) worker.py loop drives the goal's flow steps around a Codex run and records success, so a good Codex run does not end as failed: ended without finishing; (c) the next Codex goal pushes its own branch, proving push works in the sandbox with network on

- Slug: codex-fallback-2
- Touches: skills, dev/toy
- ETA: 295 active minutes (estimate 234m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a toy where ps is refused, then the REAP step prints a named SKIP reason and the run does not silently pass; given a Codex run that commits and passes its checks, then the run record ends done with its flow steps recorded, and a failing one still ends failed (negative control)
2. Given the pull request, then each new row is SEEN RED, a live Codex goal pushed its own branch with the sandbox profile (o674), and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
