# Fix hidden red issue 5680 (TD567, corrected by TD568): dev/toy/test-who-merges.py still says only worker.py may start merge.py, but mailbox.py's tick starts merge.py on purpose (TD499, PR 5608) at a job's exact head, only for a job the operation session wrote. Update the test, not the product: it allows exactly two callers, worker.py and mailbox.py's tick-job path, and refuses any other caller, with negative controls for a third caller and for the tick without a job record. This widens what the test accepts, so the pull request body says so and cites TD499 and PR 5608. No product script, row, known list or setting changes

- Slug: hr-who-merges
- Touches: dev/toy/test-who-merges.py
- ETA: 270 active minutes (estimate 215m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given dev/toy/test-who-merges.py run on this branch, then it prints no FAIL line and exits 0 with worker.py and mailbox.py's tick-job path as the only allowed callers
2. Given a toy third script that starts merge.py, or mailbox.py's tick path without a job record, then the test fails on it (negative controls), proven red then green
3. Given this goal's diff, then only dev/toy/test-who-merges.py and the goal's own records change, the widening and its reason (TD499, PR 5608) are written for the pull request body, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
