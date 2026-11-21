# Take .loop/regression.tsv from 713 rows to REG-4's 600 under the extra merge rules the owner approves, keeping every old case and every defect link visible to the traceability check

- Slug: rows-600-d
- Touches: .loop/regression.tsv, .loop/regression-known.tsv, .loop/regression-red.tsv, .loop/regression-runs.tsv, .loop/regression-issues.tsv, docs/wiki/Tests.md, dev/toy/
- ETA: 335 active minutes (estimate 267m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression.tsv before (713 rows) and after, then rows are merged under the rules of rows-600-c plus only the extra rules the owner approved (recorded in the PR body), the count falls to the number those rules allow and to 600 or fewer when they allow it, and the PR body shows the before and after counts and why any row stays separate
2. Given every old row, then each case it ran (its script, arguments and checked output) still runs in the merged row, nothing is dropped and no case is hidden behind a known-red entry it did not have; a coverage output in the PR body lists every old row id with the merged row that runs it and counts zero uncovered
3. Given a merged row, then its command runs under dash (no bash-only syntax outside bash -c), runs each distinct script call once, and its description is 400 characters or fewer, starts Given, when, then and names every case in short form; a group that cannot fit is split into rows, never truncated
4. Given a defect row that merges, then every defect link it carried stays in its link cell, the traceability check still finds a defect test for each closed issue, and the Tests table still shows each link
5. Given the old row ids, then every toy, row command and doc check that names an old id, an old Tests#t- anchor or an id="t- anchor is pointed at the merged id before the push (scanned across dev/, skills/ and .github/), the Tests tables are re-rendered, the known, red and runs lists are updated, and the full docs check prints DOCS OK
6. Given this goal's diff, then it is data only: no file under skills/ is added or changed, no script over 20,480 bytes is added, rows never rise, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
