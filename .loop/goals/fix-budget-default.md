# Row grd2-time-stop passes on main again (Fixes #5635): dev/toy/test-budget-enforce.py expects min_free_memory_gb's default to be 4, but settings.py has said 3 since 55e0d2d25 (11-19); the toy reads the default from settings.TABLE (or uses 3) so it follows the code

- Slug: fix-budget-default
- Touches: dev/toy
- ETA: 270 active minutes (estimate 214m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main with this fix, then python3 dev/toy/test-budget-enforce.py has no FAIL and row grd2-time-stop passes
2. Given the pull request, then it says Fixes #5635, changes no setting's default, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
