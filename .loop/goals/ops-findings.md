# The operation layer (top and machine sessions) files every process finding it makes while scheduling, merging or deciding as an issue on the owning feature's Backlog milestone, by default, without asking, deduped against open issues, linking the decision or record that found it, and the check-in lists what was filed; separate from the delivery loop's own findings

- Slug: ops-findings
- Touches: skills/workflow-monitoring/scripts/layers.py, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/SKILL.md, skills/workflow-monitoring/references/commands.md, docs/wiki/Operation.md, docs/wiki/Tests.md, docs/wiki/How-to-use-Operation.md, .loop/regression.tsv, dev/toy/test-checkin-view.py
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A finding command files an issue on the owning feature's Backlog milestone with a link to the TOP-DECISION or record, refusing a duplicate of an open issue (dedupe by normalised title and IDs), with a negative control
2. The check-in shows the findings filed since the last check-in; nothing is filed for a safety-class item without the owner's words
3. Requirement wording goes to the operation for the owner before merge; it merges only after the v2.0 tag; no new shipped file unless a fold pays for it; net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 skills/workflow-monitoring/scripts/layers.py finding "Slot hand-out order was guessed" --feature Operation --found "TOP-DECISION 88" --dry-run`.
   Expect: it prints `WOULD file on Backlog: Operation: Slot hand-out order was guessed (found by TOP-DECISION 88; dry run)` and files nothing.
2. Run the same command with the title of an open issue (for example the title of #5170) and no `--dry-run`.
   Expect: it prints `REFUSED: repeats open issue #5170 (...)` and exits 1; no issue is created.
3. Run it with the title `Delete the old worktrees by hand` and no `--owner-words`.
   Expect: it prints `REFUSED: safety class destructive needs the owner's words` and exits 2.
4. Run `python3 skills/workflow-monitoring/scripts/checkin.py` after a finding was filed.
   Expect: a `Findings filed (operation layer):` section lists it, and a later check-in lists none.
