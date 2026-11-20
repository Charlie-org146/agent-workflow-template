# Design: results-render (part 0b of the merge queue, TD231/TD232)

## Problem
Every lane re-renders the Tests tables and appends `.loop/regression-runs.tsv`, and `goal.py pr` commits both (lanekit.prep, role.record, lanes_cli merge-runs). Two PRs that touch the same feature page therefore conflict on its Tests page and on runs.tsv, and each merge makes the others re-run their lanes. The release step on main should render the generated files instead (towncrier).

## Approaches
1. Fragments (chosen). Each lane writes its row results to `.loop/lane-results/<slug>.tsv` (id, status, date, head, flaky: runs.tsv's columns), a file no other PR touches. The release commit on main folds every fragment into runs.tsv, deletes them, then renders the Tests tables, START.md, Home and the settings rows. Cost: one fold function and a check rule. Risk: the docs check must not call the Tests tables stale on a PR head that has fragments.
2. Keep re-rendering in the lane, merge with a union driver on Tests.md. Cost: generated pages still diverge, and each merge reruns lanes. Rejected: it is today's behaviour with a patch.

## Chosen shape
- Lane side. `lanes_cli.py merge-runs` writes the fragment (name `<slug>.tsv`, slug from branch `loop/<slug>`, else the short head) instead of calling `runs.write` under the row lock. `lanekit.prep` stops running `criteria.py render --tables` and stops committing runs.tsv; `role.record` stops re-rendering the tables and commits the fragment with issues.tsv (`FILES`, BOOKKEEPING). `lanekit.mend` loses its Tests.md and runs.tsv union handling, since neither is touched by a lane any more.
- Fold, in `render.py` (fragments in, runs.tsv out; deterministic, per row id the entry with the greatest (date, head), so folding in any order gives the same file). `refresh` and the Tests-page check treat the tables as the release's job while any fragment is pending, and enforce them once none is, so `docs.py check` passes on a PR head and on main after the release.
- Release side. `autorelease.push_release_commit` calls the fold, then renders the tables, `entry.py write` and the front-page blocks, and adds them to the release commit with VERSION and CHANGELOG. `STAMPS` and the carried-pass test already allow runs.tsv; they also allow the fragment path.
- No shipped file is added: all code goes into existing scripts, with comments and dead code trimmed to pay for it.

## Size
lanekit.py (19,475), lanes_cli.py (20,348) and role.py (20,034, not in the touches list but it holds the second render) must each end at or under 19,000 and no larger than main. Savings: lanekit loses the render call, the runs.tsv commit and most of mend; lanes_cli loses merge_runs' lock code and about 1,000 bytes of docstring; role.py loses the render and `generated` use. autorelease.py (18,945) and wiki.py (18,994) must not grow, so the fold lives in render.py (18,853) and is paid for there.

## Done lines
1. Three fixture PRs that each run a lane and touch the same feature page merge in any order with no conflict, and after the release step the tree is byte-identical: a toy builds the three fragments plus three edits to one page, merges in all six orders, folds, and compares trees.
2. The release step renders every generated file, removes the fragments it rendered, and `docs.py check` passes afterwards: the same toy runs check on the result.
3. Size and rows: byte counts of each touched script against main and 19,000; regression rows net 0 by folding the toy into an existing row (test-lanes.sh); no requirement text is changed.

## Open questions
- Whether the fold belongs in the release commit or in a step before it on the base tree (the release commit is built in a detached worktree; the fold must run there). Chosen: in that worktree, before the commit.
