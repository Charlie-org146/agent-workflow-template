# Row pool-reconcile-ghosts passes on main again (Fixes #5638): test-pool-reconcile.py expects the 5 ghosts to leave and 3 live ids to stay, but reconcile now reports 6 stay (3 not checked, not local_). Find which of today's pool or sessions changes (fde0f3d08, 7447083e8, a3c65f022, b89652301) made the count differ and fix the side that is wrong, with evidence; built by the Codex fallback, which pushes its own branch

- Slug: fix-pool-reconcile
- Touches: skills, dev/toy
- ETA: 295 active minutes (estimate 236m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main with this fix, then test-pool-reconcile.py has no FAIL and row pool-reconcile-ghosts passes; the 5 ghosts still leave and live ids still stay
2. Given the pull request, then it says Fixes #5635 is not reopened and Fixes #5638, names the commit that caused it and which side was wrong, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
