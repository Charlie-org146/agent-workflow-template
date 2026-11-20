# Health refuses to file or close issues from a checkout behind origin/main (TD451 (c)): it still prints its findings, but when HEAD is N commits behind origin/main it prints 'checkout is N commits behind origin/main: not filing' and files and closes nothing. This stops a stale checkout from filing false issues again, as the 09:03 run did (#5523 to #5556)

- Slug: health-guard
- Touches: skills, dev/toy
- ETA: 465 active minutes (estimate 369m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a checkout 3 commits behind origin/main, when health files, then it prints 'checkout is 3 commits behind origin/main: not filing' and files and closes no issue, and a toy proves it
2. Given a checkout level with origin/main, when health files, then it files as before, and the same toy proves that case
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
