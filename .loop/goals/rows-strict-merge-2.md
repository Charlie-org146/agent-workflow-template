# Replaces rows-strict-merge, whose done line promised 22 fewer rows (Operation TD603): carries loop/rows-strict-merge's commits, which merge the 9 strict groups proven on the Mac (G1, G3, G4, G5, G6, G9, G12, G13, G16) and the PC's rows-600-e 4 cuts, so the table holds 17 fewer rows than main 48ac06e7d; groups G2 (proven by rows-600-e on the PC), G7, G8, G10, G11, G14 and G15 are listed with why they were not merged here. Each merged row runs every assertion its sources checked, no requirement loses its last row, and every removed id is cleaned out

- Slug: rows-strict-merge-2
- Touches: .loop/regression.tsv, .loop/regression-red.tsv, .loop/regression-runs.tsv, .loop/regression-issues.tsv, .loop/regression-known.tsv, docs/wiki, dev/toy
- ETA: 260 active minutes (estimate 207m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of the 9 merged groups, then its row runs every assertion its source rows checked (old to new in the pull request body), was seen failing by a recorded break, passes, and runs under 200 seconds; rows-600-e's cuts carry its own proof from the PC
2. Given the table, then it has 17 fewer rows than main 48ac06e7d, no requirement has fewer than one non-defect land or nightly row, no removed id is left in the regression records, the Tests pages or any toy, and the skipped groups are listed with their reasons
3. Given this goal's diff, then only .loop/regression*.tsv, the re-rendered pages, toys that named a removed id and the goal's own records change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
