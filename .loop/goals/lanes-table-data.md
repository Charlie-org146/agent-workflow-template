# Lane selection stops treating .loop/regression-known.tsv and .loop/regression.tsv as dependencies of every row, so a goal that edits a few table lines runs only the rows those lines change plus the rows that read the table's content (TOP-DECISION 46, widened); replaces lanes-known-data, carrying its commits

- Slug: lanes-table-data
- Touches: not declared
- ETA: 285 active minutes (estimate 226m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. In lane selection (lanes_cli.affected, tiers.hit and lanes.plan), an edit to .loop/regression-known.tsv selects only the rows whose known status changed, and an edit to .loop/regression.tsv selects only the rows whose lines differ from the base plus every row whose closure explicitly names .loop/regression.tsv (rows that parse the table keep running); when the base cannot be resolved, selection falls back to today's behaviour
2. Negative controls prove a row whose known status or table line changed is still selected and a row whose closure names regression.tsv is still selected; no test is skipped, and the gate's full suite and its row set are unchanged
3. Nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. On a branch that edited one line of `.loop/regression.tsv`, run `python3 skills/workflow-regression/scripts/lanes_cli.py affected --root . -- .loop/regression.tsv | head -1`.
   Expect: `AFFECTED n of m rows`, with n a few hundred at most (it was about 1,260 of 1,300).
2. Run `python3 skills/workflow-regression/scripts/lanes_cli.py affected --root . -- .loop/regression-known.tsv | head -1` on a branch that did not edit the known list.
   Expect: `AFFECTED 0 of m rows ()`.
