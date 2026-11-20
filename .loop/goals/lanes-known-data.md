# Lane selection stops treating .loop/regression-known.tsv as a dependency of every row, so a goal that edits the known list runs only the rows whose status it changes (TOP-DECISION 46)

- Slug: lanes-known-data
- Touches: not declared
- ETA: 285 active minutes (estimate 228m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Lane selection (affected rows) no longer treats .loop/regression-known.tsv as a dependency of every row: an edit to it selects only the rows whose known status the edit actually changes
2. A negative control proves a row whose known status flips is still selected, and no test is skipped: the full suite at the gate and its row set are unchanged
3. Nothing else changes; net test rows grow by at most 1

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 skills/workflow-regression/scripts/lanes_cli.py affected --root . -- .loop/regression-known.tsv` on a branch that did not edit the known list.
   Expect: `AFFECTED 0 of N rows ()` (it used to name over a thousand rows).
2. Append a line for an existing row id to `.loop/regression-known.tsv` (do not commit), run the same command, then restore the file with `git checkout -- .loop/regression-known.tsv`.
   Expect: that row id is in the AFFECTED list.
