# Plan: ops-findings

## Build steps

1. `skills/workflow-monitoring/scripts/mailbox.py`: add `file_finding` (with `gh`, `norm`, `ids_of`, `repeat_of`, `covered`) and the
   `finding` subcommand in `main`. Checked: `mailbox.main` exists and `auto.CLASSES`, `auto.owner_rows`, `auto.loop_dir`, `auto.stamp` exist.
2. `skills/workflow-monitoring/scripts/checkin.py`: in `render`, list `auto.since(root, stamp, "findings.log")` as
   "Findings filed (operation layer)". Checked: `auto.since` takes a log name.
3. `skills/workflow-monitoring/SKILL.md` (Command map row) and `references/commands.md`.
4. `docs/wiki/Operation.md` (OPS-25 and its Revisions table), `How-to-use-Operation.md`, Tests tables via `criteria.py render`.
5. `dev/toy/test-checkin-view.py`: the new cases. `.loop/regression.tsv`: add `ops25-findings-filed`, fold
   `mon5-for-cell-sentence` into `mon5-checkin-machine-line` (same goal CHK-2, same toy file): net 0.
6. Red proof for the new row, then the lane, then the pull request.

## Test for each done line

1. Filing and the duplicate negative controls: "a finding is filed on the feature", "the same normalised title is refused",
   "the same IDs and most of the words is refused" (row `ops25-findings-filed`, seen red with the repeat check broken).
2. "the check-in lists the findings filed since the last check-in" and the safety negative controls ("no owner's words",
   "owner's words that list other IDs").
3. Net rows: 1,299 before, 1,299 after; `mailbox.py` and `checkin.py` under 19,000 bytes; no new shipped file.

## What could break

The size rows (mailbox.py is 14.2 KB), the reply hook (the new section name is not read as a header: it has a parenthesis), and
the docs check (a new requirement needs a how-to item and a scenario row; both added).

## Out of scope

Filing the process findings of tonight by hand; moving old findings; any change to `goal.py finding` or `milestone.py`; the
requirement review (the owner's, after the v2.0 tag).
