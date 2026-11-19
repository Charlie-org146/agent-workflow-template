# Three small README gaps close: the five leftover --body command-line calls become --body-file (MCH-1.7), goal_lane_minutes stops being a second lane limit beside the lane budget (REG-7.1), and criteria_max's default matches the README (TOP-DECISION 128, readme-conformance)

- Slug: gap-cheap-fixes
- Touches: skills/workflow-release/scripts/merge.py, skills/workflow-docs/scripts/milestones.py, skills/workflow-docs/scripts/prdcopy.py, skills/workflow-delivery/scripts/lane.py, skills/workflow-health/scripts/milestone.py, skills/workflow-health/scripts/rules.py, skills/workflow-setup/scripts/settings.py, skills/workflow-setup/scripts/survey.py, skills/workflow-setup/references/settings.md, skills/workflow-regression/references/commands.md, skills/workflow-health/references/commands.md, .loop/regression.tsv, .loop/config.json, .loop/START.md, dev/toy/test-tiers.sh, dev/toy/test-timing.sh, dev/toy/test-docs-format.sh, docs/wiki/Home.md, docs/wiki/Delivery.md, docs/wiki/Documentation.md, docs/wiki/Regression.md, docs/wiki/Tests.md, skills/workflow-health/scripts/defects.py, dev/toy/test-migration.sh
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py, milestones.py and prdcopy.py pass no PR or issue body on the command line (each uses --body-file), and the pr-body-by-file row covers all of them, with a negative control
2. goal_lane_minutes no longer stops or fails a lane on its own; the lane budget is the only lane limit, proven by a row with a negative control
3. criteria_max's default equals the README's value, and the health rule reading it agrees
4. No requirement text changes, no new shipped file, every touched script stays under 19,000 bytes or does not grow, net regression rows 0 or fewer

## Verify by hand

1. Run `grep -rn '"--body",' skills` from the repo root.
   Expect: no output; merge.py, milestones.py and prdcopy.py pass the body with `--body-file`, `-`.
2. Run `grep -rn goal_lane_minutes skills .loop/config.json`.
   Expect: only references and docs text (health's commands.md); no code, no setting, no config key.
3. Open `skills/workflow-health/scripts/rules.py`, function `requirements_per_page`.
   Expect: both defaults are 10, the same as the settings default.
4. Run `wc -c` on the changed scripts (merge.py, milestones.py, prdcopy.py, defects.py, rules.py, lane.py).
   Expect: each is under 19,000 bytes, and the row table holds the same number of rows as main.
