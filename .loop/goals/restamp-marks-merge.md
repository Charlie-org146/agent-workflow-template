# Known-red-zero group H: row restamp-marks-3867 passes on main and comes off the known list (Fixes #5386). dev/toy/test-merge-unblock.py restamp fails 2 asserts on main: after the merge step's re-stamp nothing is stale (it still prints REWRITE A: STALE 1 commits since the page), and the goal's branch gets a re-stamp commit. Find whether the merge step's re-stamp or the toy is wrong, with evidence (git history since v1.0.110, kept-fragments #5380, guide-page-stamp #5614), and fix the one that is wrong

- Slug: restamp-marks-merge
- Touches: skills, dev/toy
- ETA: 340 active minutes (estimate 270m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given test-merge-unblock.py restamp on this branch, then every assert passes, and a negative control with the fix reverted fails the same 2 asserts
2. Given the pull request, then it says Fixes #5386 and which side was wrong and why, restamp-marks-3867 comes off .loop/regression-known.tsv, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
