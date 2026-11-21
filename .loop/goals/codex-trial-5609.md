# machines.py no longer runs gh pr merge directly (Fixes #5609; TD519, the live Codex fallback trial): the batch path at machines.py:186 routes its merge through merge.py's own path at the recorded head, the way the tick does since #5608, so test-tree.sh's a script merges assert passes; machines.py stays under 19,000 bytes; it is a merge-path PR so it never batches

- Slug: codex-trial-5609
- Touches: skills, dev/toy
- ETA: 295 active minutes (estimate 233m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given test-tree.sh on this branch, then its assert that no script but the release step's merge.py calls gh pr merge passes, and the row that reads it was SEEN RED on main first
2. Given the pull request, then it says Fixes #5609 and that it was built by the Codex fallback, merge.py's st-no-bypass still holds (no --auto, exactly 2 --merge), and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
