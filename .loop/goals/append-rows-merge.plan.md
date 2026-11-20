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

## Build steps (after pc-w3's results-render design is fixed)
1. `.gitattributes`: `.loop/regression.tsv merge=union` and `.loop/regression-issues.tsv merge=union`.
2. `regression.py`: `cmd_sort`, registered as `sort`: read both tables line by line (header kept, comment lines kept first), key = first cell; refuse and exit 1
   naming every duplicate key (`REFUSED: duplicate id X in regression.tsv. Fix: keep one row`); otherwise write the rows sorted by key (byte order, LF), only if they changed.
3. `wiki.py`: in `rerender`, run `regression.py sort` in the publish tree first and include `.loop/regression.tsv` and `.loop/regression-issues.tsv` in the same commit;
   a refusal from sort stops the publish with its message.
4. Size: trim comments and docstrings in `regression.py` and `wiki.py` by at least what steps 2 and 3 add (room: 148 and 6 bytes), measured in LF bytes.
5. Toy `dev/toy/test-append-rows-merge.py` (python, so it runs on native Windows): temp git repo, the `.gitattributes`, three branches each adding one row to
   regression.tsv and one link to regression-issues.tsv; merge them into a base in all six orders; assert no conflict, then run `regression.py sort` and assert the six
   files are byte-identical; assert a duplicate id (a row both sides edit) makes sort refuse naming the id; negative control: the same merges without `.gitattributes` conflict.
6. Widen one existing Regression-feature row's command to also run the toy (no new row, net 0) and prove it red with `regression.py red ID --break`.
7. One-time: run `regression.py sort` on the two tables in this branch so the committed tables are already sorted (the only change to their rows' order).

## Tests per done line
- Done line 1: the toy in step 5 (six orders, byte-identical after sort, duplicate refused, control conflicts without the attributes), run by the widened row.
- Done line 2: the existing size and no-new-file rows, plus a check of the diff: touched scripts' LF bytes at or under 19,000 and not above main; row count unchanged.

## What could break
- Union keeps both sides of a row two PRs both edit: a duplicate id. Sort refuses loudly (and `read_rows` today would hide it); resolution is by hand.
- GitHub's server-side merge ignores `merge=union`: a PR must stay merged up to date with main (already the BASE_MOVED rule), or it shows a conflict there.
- CRLF working copies: the sort reads and writes lines without changing their endings; the toy runs with `core.autocrlf` unset.
- Reordering 1,300 rows once makes a large diff and a merge conflict for any open PR that touched the tables: land it when the queue is quiet.

## Out of scope
Changing readers of the tables, the towncrier design, results-render's own changes, `regression-runs.tsv` and the other tables, any requirement text.

## Decisions for the owner
None.
