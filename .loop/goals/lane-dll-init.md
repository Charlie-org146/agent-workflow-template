# Lane rows that die with Windows exit 0xC0000142 (process could not start, low memory or app restart) are rerun or reported as not-run, never FAIL, and never cost a try (#4639)

- Slug: lane-dll-init
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a lane where some rows exit 3221225794, when the lane reports, then those rows are rerun once and any still dying are listed as not run with the cause, not FAIL, and the try is not counted
2. Given a lane with one real FAIL and several 0xC0000142 rows, when it reports, then the real FAIL still fails the lane

## Verify by hand

<!-- Numbered steps a person can follow, each with an Expect: line. -->
