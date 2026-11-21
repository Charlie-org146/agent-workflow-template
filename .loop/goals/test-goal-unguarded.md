# Every assert a test script prints is read by a row (REG-4; v2.0 part 3, TD540): test-goal.sh has 4 FAILing asserts on clean main that no row reads (the page lists --owner-record; pr commits the regenerated START.md before the push; second push worked; final failure prints git's error). Give each its row, see it red, then fix it or put it on the known list with an issue; and add a check that names every FAIL line a dev/toy script can print that no row in regression.tsv reads, reporting how many scripts have unread asserts

- Slug: test-goal-unguarded
- Touches: skills, dev/toy
- ETA: 295 active minutes (estimate 235m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given test-goal.sh, then each of the 4 asserts has a row; each row is SEEN RED, and then passes with a fix or sits on the known list with its own issue
2. Given the new unread-assert check, then it lists every dev/toy script with an assert no row reads and the count, a fixture script with an unread assert is named and one fully read is not (negative control), and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
