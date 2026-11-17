# REG-1: The review-depth marker rows and the automation, health and milestone rows pass on CI (#4557, #4558)

- Slug: ci-small-groups
- Touches: not declared
- ETA: 205 active minutes (estimate 163m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the 3 rows in #4557 and 9 rows in #4558, when the full suite runs on CI, then each passes or has its real cause written on its issue
2. The same rows still pass on the PC

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Open the regression workflow's runs on GitHub (Actions, regression) and open the first full run on main after this merges.
   Expect: depth-on-board, depth-in-pr-body, depth-reference, aut-defect-issue, aut-old-issue-relabel, aut-email-regression, hlt4-feature-milestones, live-board-leftouts, automation-live, milestone-rows-seen-red, reg7-suite-time and health-mail-env-windows all show PASS in the run summary.
2. On a machine with no `~/.workflow-loop` folder, run `python3 skills/workflow-setup/scripts/settings.py fill-private --file /tmp/flow.json`.
   Expect: it prints FILLED and creates `~/.workflow-loop/repos`, with no traceback.

