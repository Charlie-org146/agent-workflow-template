# Clear the known-red rows guards-resume, lane-messages-table, lanes-trace-check, repo-narrow-178, st-union-contexts and toy-no-leftovers (Operation TD596, TD609; supersedes kr-lanes, carrying its commits): each row fails on main today for a reason this goal finds and fixes at its root, in the product or in the toy, without weakening any check; each row then passes on this branch run alone twice, and its known line is removed in this goal. The rows lanes-trace (#5693) and the narrow.py rerun-fraction check behind lanes-headers (#5694) are not fixed here: each needs a redesign, which the pull request body names with its findings; their known lines stay exactly as on main, and the body says whether they stay known for v2.0 is the owner's open decision. Refs the issues the known list names for these rows

- Slug: kr-lanes-2
- Touches: skills, dev/toy, .loop/regression.tsv, .loop/regression-known.tsv, docs/wiki
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of the rows guards-resume, lane-messages-table, lanes-trace-check, repo-narrow-178, st-union-contexts and toy-no-leftovers, then it passes on this branch run alone twice outside any sandbox, with its root cause named in the pull request body
2. Given each fix, then no assertion is weakened or skipped, any changed expectation is checked at least as strictly, and the nearest toys for every touched script pass as on main or better
3. Given this goal's diff, then the known lines for exactly the rows guards-resume, lane-messages-table, lanes-trace-check, repo-narrow-178, st-union-contexts and toy-no-leftovers are removed from .loop/regression-known.tsv, the known lines for lanes-trace and the rerun-fraction check are unchanged from main, the pull request body names both redesigns (#5693, #5694) and says the owner's v2.0 decision on them is pending, only the scripts, toys, rows and pages the fixes need change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
