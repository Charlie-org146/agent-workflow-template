# Lane rows that die with Windows exit 0xC0000142 (process could not start, low memory or app restart) are rerun or reported as not-run, never FAIL, and never cost a try (#4639)

- Slug: lane-dll-init
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a lane where some rows exit 3221225794, when the lane reports, then those rows are rerun once and any still dying are listed as not run with the cause, not FAIL, and the try is not counted
2. Given a lane with one real FAIL and several 0xC0000142 rows, when it reports, then the real FAIL still fails the lane

## Verify by hand

1. Run `python3 dev/toy/test-lane-dll-init.py`.
   Expect: ten PASS lines, including "a row that could not start once, then passes, is PASS after one rerun" and "a row that dies twice is ENV (not run), never FAIL"; exit 0.
2. In that output, read the negative-control line for a real FAIL.
   Expect: "PASS: negative control: a real FAIL beside three dying rows still exits 1 (1)".
3. Run `python3 dev/toy/test-lane-env.py`.
   Expect: lane-memory's ENV checks still pass (nine PASS lines, exit 0).
