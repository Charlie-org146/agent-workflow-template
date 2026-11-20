# The check-in's waiting count is honest (TD502; Honest machines, v2.0 part 1): today checkin.py line 1 says 26 waiting on you while the owner's real list has 2. A waiting record whose goal cannot be proved to still be waiting (no live session, no open question in its run record, or superseded or merged) shows as old, never as waiting on the owner; old records are counted apart and listed with their slugs, and nothing is deleted

- Slug: waiting-record-cleanup
- Touches: skills, dev/toy
- ETA: 390 active minutes (estimate 310m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given today's records, then checkin.py line 1 counts as waiting on you only goals with a provable open owner question (2 now), and the rest show under old with their slugs; a toy with a stale waiting record shows it as old and a real open question as waiting (negative control: the old rule counts both)
2. Given the pull request, then its toy row is SEEN RED with the change reverted, no run record or goal file is deleted or rewritten, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
