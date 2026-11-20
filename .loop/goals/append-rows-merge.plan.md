# Plan: append-rows-merge

Design: `.loop/goals/append-rows-merge.design.md` (merge=union plus a stable sort and duplicate refusal at release).

## Claims checked against the code
- `regression.py` exists (18,852 LF bytes); rows are `FIELDS = id, level, command, ...`, header `HEADER`, written by `slots.write_table(path, header, lines)`;
  `edit_rows` and `read_rows` key rows by id in a dict, so a duplicate id is silently collapsed (last wins) today. `cmd_add` appends at the end.
- `.loop/regression-issues.tsv` (link, state, date, reopened_at) is written whole by `tests.py` (`sorted(out.items())`), so it is already sorted on write;
  a union merge can still leave it unsorted or with a duplicated link until the next write.
- `wiki.py` exists (18,994 LF bytes); `rerender(tree, cfg)` runs at publish in the base tree and commits regenerated pages ("Wiki: re-render generated tables");
  `TESTS` points at the workflow-regression scripts folder. `merge.py` merges with `gh pr merge --merge` (server side, no union), and `goal.py pr` merges main locally.
- No `.gitattributes` exists in the repo today.

## Build steps (after pc-w3's results-render design is fixed; pc-w3 confirmed it does not touch wiki.py or regression.py)
Review finding folded in: wiki.py's `rerender` runs in a throwaway detached worktree whose commit is never pushed, so a sort there never reaches main.
The sort belongs where release really commits to the base: `autorelease.push_release_commit` (the release commit, or the release PR branch).
1. `.gitattributes`: `.loop/regression.tsv merge=union` and `.loop/regression-issues.tsv merge=union`. It sits beside `lanekit.mend`, which already
   unions regression.tsv and regression-runs.tsv rows on a conflict but not regression-issues.tsv, and returns False when any other file conflicts;
   with the attribute git itself merges both tables without a conflict, so `mend` sees only the other files.
2. `regression.py`: `cmd_sort` (`sort`, run in the repo given by cwd): read both tables with `newline=""`, normalise to LF, keep `#` header lines first, key = first cell,
   refuse and exit 1 naming every duplicate key, else write the rows sorted by (key, line) in byte order with LF endings, only when they changed.
   Run before any `add`, since `read_rows` collapses a duplicate id silently today.
3. `autorelease.py` `push_release_commit`: inside the `PUSH_TRIES` loop, after the `worktree add` and before `files = [...]` (each retry re-checks out the base), import
   `regression` and call a short `regression.sort_tables(tree)` (the logic lives in regression.py); put both tables into `files` before `git add`, and only when the sort changed
   them (the commit is path-limited); a refusal calls `fail` with its message. Do NOT add regression.tsv to `STAMPS` (it would let `carried` pass a stale lane for a row-only PR head):
   pass it through the existing `extra`/`allow` argument of the tree-equal check for the release-PR path only. The sort writes LF and compares normalised text, so no spurious diff.
   autorelease.py is pc-w3's file and outside this goal's declared touches: agree the hook line with pc-w3, and ask operation-pc to amend the Touches (see the owner decision).
   A release happens only on `cut` (done line 1 says "after release"); a goal that is left or has no release step leaves its table as merged.
   A duplicate id found at release blocks that release and every later one, because the base is shared: the fix is by hand on main (keep one row), then `merge.py SLUG`.
   Preferred, if merge.py may be touched: `regression.py sort --check` (refuse duplicates, write nothing) before `gh pr merge`, so a duplicate never merges.
4. Size, counted in LF bytes: trim FIRST, then add. regression.py has 148 bytes of room and autorelease.py 55 (18,945; pc-w3 targets 18,915); the hook needs about 150 to 200 bytes in
   autorelease.py, so trim at least that in comments and docstrings of the same file, never end above main, and remeasure after each step. wiki.py is no longer touched.
5. Toy `dev/toy/test-append-rows-merge.py` (python, runs on native Windows): a temp git repo with the attributes and three branches each adding a row to
   regression.tsv and a link to regression-issues.tsv; merge in all six orders: no conflict; after `sort` the six files are byte-identical, run once with
   `core.autocrlf=true`; a row both sides edit makes a duplicate id and sort refuses naming it; negative control: without `.gitattributes` the merge conflicts.
6. Widen one existing Regression-feature row's command to also run the toy (no new row, net 0) and prove it red with `regression.py red ID --break`.
7. One-time: run `sort` on the two tables so the committed tables are sorted and LF (the only change to their rows' order).

## Tests per done line
- Done line 1: the toy in step 5 (six orders, byte-identical after sort, duplicate refused, control conflicts without the attributes), run by the widened row.
- Done line 2: the existing size and no-new-file rows, plus a check of the diff: touched scripts' LF bytes at or under 19,000 and not above main; row count unchanged.

## What could break
- Union keeps both sides of a row two PRs both edit: a duplicate id. Sort refuses loudly (and `read_rows` today would hide it); resolution is by hand.
- GitHub's server-side merge ignores `merge=union`: a PR must stay merged up to date with main (already the BASE_MOVED rule), or it shows a conflict there.
- CRLF: `slots.write_table` and `tests.py` write in text mode (CRLF on Windows); the sort normalises both tables to LF so the bytes match across machines, and the toy runs with autocrlf on.
- `merge.py` diffs regression.tsv with -U0: the one-time sort in step 7 makes that diff large for open PRs.
- Reordering 1,300 rows once makes a large diff and a merge conflict for any open PR that touched the tables: land it when the queue is quiet.

## Out of scope
Changing readers of the tables, the towncrier design, results-render's own changes, `regression-runs.tsv` and the other tables, any requirement text.

## Decisions for the owner
Amend this goal's Touches to add skills/workflow-release/scripts/autorelease.py (and merge.py for the early duplicate check); the frozen goal file lists neither.
