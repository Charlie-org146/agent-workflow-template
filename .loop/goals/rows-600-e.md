# Merge more .loop/regression.tsv rows toward REG-4's 600 by requirement, type and script, leaving known-red rows and package, listing and size-limit rows alone, with every old case kept

- Slug: rows-600-e
- Touches: .loop/regression.tsv, .loop/regression-known.tsv, .loop/regression-red.tsv, .loop/regression-runs.tsv, .loop/regression-issues.tsv, docs/wiki/Tests.md, dev/toy/
- ETA: 490 active minutes (estimate 391m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression.tsv before (689 rows) and after, then rows are merged under rows-600-d's rules (same requirement, type, script and Windows-skip state, defect links kept in the link cell, nightly into land) with no known-red row touched and no row whose only check is a package, listing.json or 19,000 or 20,480 byte limit merged, and the PR body shows the before and after counts and the reachable count
2. Given every old row, then each case it ran still runs in the merged row and nothing is dropped; a coverage output in the PR body lists every old row id with the merged row that runs it and counts zero uncovered
3. Given a merged row, then its command runs under dash, runs each distinct script call once, units that skip native Windows come last, and its description is 400 characters or fewer, starts Given, when, then and names every case in short form; a group that cannot fit is split, never truncated
4. Given the old row ids, then every toy, row command and doc check that names an old id or an old Tests#t- or id="t- anchor is pointed at the merged id before the push (scanned across dev/, skills/ and .github/), the Tests tables are re-rendered, and the full docs check prints DOCS OK
5. Given this goal's diff, then it is data only: no file under skills/ is added or changed, no script over 20,480 bytes is added, rows never rise, no requirement text changes, and the diff numbers with and without whitespace match

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
