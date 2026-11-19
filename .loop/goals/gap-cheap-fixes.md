# Three small README gaps close: the five leftover --body command-line calls become --body-file (MCH-1.7), goal_lane_minutes stops being a second lane limit beside the lane budget (REG-7.1), and criteria_max's default matches the README (TOP-DECISION 128, readme-conformance)

- Slug: gap-cheap-fixes
- Touches: skills/workflow-release/scripts/merge.py, skills/workflow-docs/scripts/milestones.py, skills/workflow-docs/scripts/prdcopy.py, skills/workflow-delivery/scripts/lane.py, skills/workflow-health/scripts/milestone.py, skills/workflow-health/scripts/rules.py, skills/workflow-setup/scripts/settings.py, skills/workflow-setup/scripts/survey.py, skills/workflow-setup/references/settings.md, skills/workflow-regression/references/commands.md, skills/workflow-health/references/commands.md, .loop/regression.tsv, .loop/config.json, .loop/START.md
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py, milestones.py and prdcopy.py pass no PR or issue body on the command line (each uses --body-file), and the pr-body-by-file row covers all of them, with a negative control
2. goal_lane_minutes no longer stops or fails a lane on its own; the lane budget is the only lane limit, proven by a row with a negative control
3. criteria_max's default equals the README's value, and the health rule reading it agrees
4. No requirement text changes, no new shipped file, every touched script stays under 19,000 bytes or does not grow, net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
