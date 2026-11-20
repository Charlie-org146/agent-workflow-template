# Design: append-rows-merge

## Problem
Two PRs that each add a row at the end of `.loop/regression.tsv` (or `.loop/regression-issues.tsv`) conflict in git's text merge, because
both edit the same hunk (the end of the file). Every goal adds rows, so every PR after the first needs a hand merge, and the order the PRs
merge in changes the file. The release should leave one table whatever the merge order was.

## Approaches
1. One file per goal, assembled at release (towncrier): each goal writes `.loop/rows/<slug>.tsv`; release concatenates them into the table.
   Cost: a new folder, every reader of the table (regression.py, tests.py, lanekit, criteria, health) must read both, and the 1,300 existing
   rows need a migration. Risk: a second source of truth between merges; regression.py and wiki.py are already over 19,000 bytes, so the
   readers cannot grow.
2. `merge=union` on both tables in `.gitattributes`, plus a stable sort at release. Git's built-in union driver keeps both sides' added lines
   instead of conflicting. Cost: a two-line `.gitattributes`, a `regression.py sort` command (sort rows by id, refuse duplicate ids) and one
   call to it where release already touches the tree (wiki.py). Risk: union also keeps both versions of a row two PRs both edit, which
   makes a duplicate id, so the sort refuses that loudly instead of silently picking one (read_rows keeps the last today).

## Chosen
Approach 2. It needs no new folder, no reader change and no migration beyond one sort of the existing rows; the table stays one file that
`regression.py add` already appends to. Union is order dependent only in where the added lines land, and the release sort removes that.

## Done lines
1. Toy (python, so it runs on native Windows): a temp git repo with the attributes and three branches that each add a row; merge them in
   all six orders: no conflict each time; after `regression.py sort` the table is byte-identical across the six; a seventh branch that
   edits an existing row on two sides gives a duplicate id and the sort refuses naming it. Negative control: the same merges without the
   `.gitattributes` conflict. Same for `regression-issues.tsv` (rows keyed by link).
2. Size: counted in LF bytes regression.py is 18,852 and wiki.py 18,994 on main (not over 19,000), so the new code must fit: regression.py has 148 bytes of room and wiki.py 6, so each trims comments and docstrings to stay at or under 19,000 and not above main; no new shipped file (`.gitattributes` is repo config, not a shipped skill file); net regression rows 0 (an existing row is widened); no requirement text changes.

## Open questions
- Limit: `merge=union` applies to git merges run locally (goal.py pr merging main, and workers); GitHub's server-side `gh pr merge` ignores it, but a PR already merged up to date with its base (BASE_MOVED discipline) merges clean there.
- pc-w3's results-render goal also edits regression.py and wiki.py: build only after its design is fixed, and merge main once through
  goal.py pr before the slot.
- Where release calls the sort: wiki.py `prepare` (it already commits table changes) is the plan; confirm against results-render.
