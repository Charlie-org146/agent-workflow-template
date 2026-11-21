# Clear known-red rows merge-guard-base-head (carrying the toy and row work kept on loop/v2fix-5306 at 8d5fd152) (Operation TD596): each row fails on main today for a reason this goal finds and fixes at its root, in the product or in the toy, without weakening any check; each row then passes on this branch run alone twice, and its known line is removed in this goal. Refs the issues the known list names for these rows

- Slug: merge-guard-toy-fix
- Touches: skills, dev/toy, .loop/regression.tsv, .loop/regression-known.tsv, docs/wiki
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of the rows merge-guard-base-head (carrying the toy and row work kept on loop/v2fix-5306 at 8d5fd152), then it passes on this branch run alone twice outside any sandbox, with its root cause named in the pull request body
2. Given each fix, then no assertion is weakened or skipped, any changed expectation is checked at least as strictly, and the nearest toys for every touched script pass as on main or better
3. Given this goal's diff, then the known lines for merge-guard-base-head (carrying the toy and row work kept on loop/v2fix-5306 at 8d5fd152) are removed from .loop/regression-known.tsv, only the scripts, toys, rows and pages the fixes need change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
