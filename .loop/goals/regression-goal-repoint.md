# Regression rows that guard a folded requirement name its survivor (TD384, operation-top under owner delegation; the approved README draft o514, record o647, folds 17 IDs that readme-six retires). 195 rows of .loop/regression.tsv have a goal cell naming a retired ID, so docs.py check prints LINK lines once readme-six lands, while the folded requirements keep their tests. The change edits only the goal column of those rows, each to the survivor named in the absorbs lists of operation-top/readme-drafts/README-final-draft.md (the draft wins over any other list, and a difference is reported): AUT-9 to GRD-4, DEL-7 to MCH-1, REG-1 and REG-9 to REG-4, SET-4 and SET-6 to SET-1, REL-3 to DEL-1, MCH-4 to MCH-1, MCH-5 to CHK-1, REL-12 to DEL-3, REL-13, GRD-7, GRD-8 and REG-7 to DEL-17, INT-2 to DOC-2. No row is added or removed and no command, description or other column changes. It builds now and pushes after rows-600-b lands; it merges before readme-six, or as a stack on top of readme-six's branch if the docs check needs readme-six's retires first

- Slug: regression-goal-repoint
- Touches: .loop/regression.tsv
- ETA: 345 active minutes (estimate 273m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression.tsv after this goal, then no goal cell names any of the 17 folded IDs, each repointed row names the survivor that the draft's absorbs list gives for its old ID, and a column-by-column diff against main shows only goal cells changed
2. Given the diff, then the row count is unchanged, no command or description changes, role.py over_caps passes, criteria.py render --check and docs.py check pass on the merged result, and the pull request lists the count per old ID to survivor

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
