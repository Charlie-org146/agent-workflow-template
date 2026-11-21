# Toward REG-4's 600 rows (Operation TD587, option a): merge the 22 strict groups of regression rows, rows that run the same script at the same level for the same goal, category and link and are not on the known list, into one row per group, as rows-600-c did. Each merged row runs every assertion its source rows checked, is re-proven with regression.py red --break, and every stale id is removed from the regression records, the Tests pages and any toy that names it. No assertion is dropped, no requirement loses its last row, and no cross-goal fold is made

- Slug: rows-strict-merge
- Touches: .loop/regression.tsv, .loop/regression-red.tsv, .loop/regression-runs.tsv, .loop/regression-issues.tsv, docs/wiki, dev/toy
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each merged group, then the merged row's command checks every assertion its source rows checked (listed old to new in the pull request body), it was seen failing by a recorded break and passes, and its wall time is measured and under 200 seconds
2. Given the table after the merge, then it has 22 fewer rows than main, no requirement has fewer non-defect land or nightly rows than one, and no removed id is left in regression-red, -runs, -issues, -known, the Tests pages or any toy
3. Given this goal's diff, then only .loop/regression*.tsv, the re-rendered pages, toys that named a removed id and the goal's own records change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
