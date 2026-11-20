# Pilot slice of the regression-row cleanup (owner words 03:24: merge the test rows down to 600; Operation TD354, TD356; the plan is in operation-top/readme-drafts/v2-build-plan.md, section rows-600). Today 982 of the 1,299 rows each run a whole test script and grep one PASS line, so a script with N rows runs N times. This slice merges only the LARGEST groups of rows that share one test script invocation and one requirement (the goal column), where every row in the group passes on main, has a seen_red date, and has no id on .loop/regression-known.tsv, removing at least 100 rows (candidates: test-estimates.sh / CHK-1, test-stands-alone.py / DOC-1, test-summary.sh / REG-4, test-docs-sync.py / INT-2; check each against the known list first). A merged row runs the invocation once, checks EVERY PASS line its group's rows checked, and fails on any FAIL line; the surviving row keeps one id of the group and, if regression.py red checks id and date only, the LATEST seen_red date of the group (if red hashes the command, the worker reports the cost before running any proof). Rows merge only within the same level. The pull request carries an exact-set check that the PASS lines checked before and after are identical. The cap max_regression_rows stays 1300 in this slice. Lane prep (Tests-table render and restamp) and the caps guard run before the push; no local lane

- Slug: rows-600-a
- Touches: .loop/regression.tsv, docs/wiki
- ETA: 340 active minutes (estimate 271m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression.tsv on this branch, then at least 100 rows fewer than on main, each merged row covers one script invocation and one requirement, runs it once and checks every PASS line its old rows checked and fails on any FAIL line, and no row with an id on the known list was merged
2. Given the set of PASS lines checked by all rows on main and on this branch, then the two sets are identical, and a check in the pull request proves it
3. Given every merged row, then it has a seen_red date that regression.py accepts, and the Tests pages re-render and the docs check passes
4. Given .loop/config.json, then max_regression_rows is unchanged at 1300, and no script, workflow or test logic outside regression.tsv, the regenerated pages and the check changes

## Verify by hand

1. Run `python3 dev/check-row-merge.py origin/main`.
   Expect: "checks before 600, after 600; lost 0, added 0" and exit 0.
2. Run `grep -c . .loop/regression.tsv` on this branch and on origin/main.
   Expect: this branch has 116 lines fewer.
