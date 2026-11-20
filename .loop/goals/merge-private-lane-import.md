# merge.py no longer crashes after a private-repo merge: private.py pr_result finds the lane module from a template checkout and from an installed skills folder without an extra PYTHONPATH (#5306)

- Slug: merge-private-lane-import
- Touches: skills/workflow-delivery/scripts/private.py, dev/toy/test-merge-guard.sh, .loop/regression.tsv
- ETA: 250 active minutes (estimate 198m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a toy private repo that uses the private-names list, when merge.py merges its PR with no PYTHONPATH set, then pr_result imports lane, the release step finishes and no ModuleNotFoundError is printed, from both a template checkout and an installed skills folder
2. Given the fix removed, when the same toy runs, then it fails with the ModuleNotFoundError, so the row is seen red
3. Given this goal's diff, then no shipped file is added, private.py is not larger than on main (it is over 19,000, so net zero or smaller), net regression rows are 0 or fewer (an assertion added to an existing merge-guard row), and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
