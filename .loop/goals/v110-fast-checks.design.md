# Design: v110-fast-checks (DEL-25), matching the plan revised after gate 5

Approach A, the one the plan builds. The plan is the authority; this file only records the shape so no older design text contradicts it.

## Shape

- One command, `skills/workflow-delivery/scripts/quick.py run`, runs the quick checks (lint, the docs check, the size limits) in one process on one clock with DEL-25.2's single 1-minute limit. It ships with the skills, so adopted repos get it.
- One pre-commit hook, `quick`, `language: system`, pre-push stage, installed by `quick.py install` where pre-commit is available. The git-native private-name stub stays as pre-commit's legacy hook. There is no `local_lane` setting, no `quick_limit_seconds` setting.
- New files under `skills/workflow-delivery/scripts/`: `skip.py` (the lane skip, the reader that lets record qa and ship accept a recorded skip, nothing written to `.ok`), `regen.py` (the generated-file check) and `quick.py`. A skipped lane is recorded apart (`.last` state skipped, `<step>-lane.skip`); `.ok` is a tested pass only; `lane-wait` exits 3 for a skip.
- At `goal.py pr` the generated files are checked, never rewritten; the writers are the existing commands named in the Fix line, run by the worker at ship.
- Rows, one per test script (REG-4), tier `land`, keyed to the feature id DEL-25: three (TD815 grant).
- No new setting, no change to `role.py`, `merge.py`, `guards.py` or `replan.py`.

## What is not in this design

The private-name stub is unchanged; DEL-17's text is not edited (the owner ruled DEL-25.3 over it, o830); a flow that opens a pull request before ship is a separate change.
