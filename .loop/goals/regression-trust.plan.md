# regression-trust plan

Checked against the code on origin/main (v0.28.61); every file and function named below exists.

## Build steps, in order
1. `skills/workflow-regression/scripts/tiers.py` (plan, line 277): replace the two-way sort with `todo.sort(key=lambda rid: rank(why[rid]))`; `rank` is 0 for "new row", 1 for "failure rerun" and "skipped last time", 3 for "root runner" and "names an unmapped path", else 2 ("reaches ..."). `list.sort` is stable, so the order inside a rank is unchanged. Done line 2 (#531).
2. `skills/workflow-regression/scripts/runs.py` (execute, about line 206): compute `tail` before the print, and under `if state == "FAIL" and reuse` print the last 20 lines of `tail` (the loud text) to stderr instead of the raw text. Done line 1 (#3911).
3. `runs.py` `owed_clear` takes `live`; when it removes a record that holds an issue URL, `gh issue close URL --comment ...` runs live, otherwise "WOULD close". `regression.py` (line 244) passes the live flag. Done line 3 (#3907).
4. Toys, shell-neutral Python: `dev/toy/test-lane-order.py` (rank), `dev/toy/test-lane-fail-text.py` (execute with reuse on a grep -q row; stderr holds the text), `dev/toy/test-owed-close.py` (gh stubbed; the issue is closed once the red proof is recorded). Rows in `.loop/regression.tsv` with `regression.py add`, then `red --break` for each. No new script in the package (file cap).
5. #3908 is closed with proof (both rows seen failing, no owed file, runs.owed_record refuses a seen row), after the merge.

## Test for each done line
1. rows lane-fail-text; 2. lane-order; 3. owed-close; #3908 by the proof lines in its closing comment. 4. toys are Python, no bash.

## What could break
- Order only: the run set is unchanged, so reuse and results are the same; the stable sort keeps ties.
- The lane re-runs a failing quiet row once more, as the issue body already did.
- Closing an issue: only live and only the one in the owed record.

## Out of scope
- #3944 (Mac and Linux runs) stays an off-machine to-do. The 3.0 GB free-memory start is operation's `min_free_memory_gb` setting.
