# Plan: known-red-w4-docs-health

## Build steps

1. `skills/workflow-delivery/scripts/lanekit.py` `prep`: commit with `-c user.name -c user.email` when git has no author (stale-code-page-reviewed).
2. `dev/toy/test-runbook.sh`: ship `.claude/settings.json` in the copy, declare the registry routine's permissions (runbook-registry).
3. `dev/toy/test-stale-groups.sh` and its row description: Milestones stays removed, Release is a feature, How-to-use pages are not groups (stale-groups-defect).
4. `dev/toy/test-health-hygiene.sh`: skip list names the `repo` group; the broken-rule edit also breaks WARN (hlt6-cannot-fire).
5. `dev/toy/test-health-table.py`: unset GITHUB_ACTIONS (health-findings-table).
6. `dev/toy/test-milestones.sh`: fixture script over the limit so it is a FAIL (defect, no milestone), `as defect` and `--label defect` expectations (health-file-no-milestone).
7. `dev/toy/test-sync.sh`: final edit matches the Problem text (entry-stale).
8. `dev/toy/test-prd.sh`, `test-docs-issues.sh`, `test-criteria.sh`: How-to-use page with System diagram, Home diagram, in-repo milestone URLs, `criteria_trouble(...)[0]`, base push before the Usage check (prd-readers, docs-guide-page-issue-125, no-usage-passes).
9. `no-milestone-issue-ok`: no change here; needs known-red-w8-size's health script trim, then main merged in.

## Tests

Each done-line row is its own test, seen failing on main run 44463859531 and passing on this branch in CI (workflow_dispatch, target land).

## What could break

Other rows that source the same toys. The full land run on the branch shows it.

## Out of scope

The other red rows (w1 to w8 goals), trimming health scripts (w8).

PENDING: none
