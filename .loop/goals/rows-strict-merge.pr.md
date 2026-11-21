# rows-strict-merge: pull request notes

Row count against main 48ac06e7d: 694 before, 677 after (13 from the groups below, 4 from the rows-600-e cut picked in on the coordinator's word: goal-commands-page, goal-pr-push-retried and goal-pr-push-error into frozen-done-lines, and defect-4115-lane-control into lane-limit-150). rows-600-e head a7a74a541 holds the same final rows for those four cuts as this branch, so picking it added nothing further. The goal asked for 22 fewer rows; 17 fewer were reached, because the groups marked skipped could not be proven here (reasons after the table).

Wall times were measured on a loaded Mac (load average about 13), one row at a time. Every break below is a one-line edit of the named toy, run by `regression.py red ID --break` on a copy of HEAD; each ended SEEN RED, and the unbroken row passed.

| Group | Old ids | New id | Assertions kept | Wall time | Red break used |
|---|---|---|---|---|---|
| G1 test-estimates CHK-1 | est-area, est-pace, est-big-goal, est-backtest-loo, est-backtest-speed | est-area | one run of the whole toy: the PASS line of each of the 29 cases the old rows named (area to time_order_edges) and ALL PASS | 9 s | check_backtest_speed made to fail |
| G2 test-goal nightly DEL-19 | frozen-done-lines, goal-commands-page, goal-pr-push-retried, goal-pr-push-error | frozen-done-lines (from rows-600-e) | the 4 PASS lines, one run | not measured: test-goal.sh did not finish in 14 minutes here (its watch step waits) | none recorded here |
| G3 test-health-hygiene HLT-2 | hlt6-controls-fire, hlt6-refused, hlt6-branches | hlt6-controls-fire | the 12 PASS lines of the three rows, one run | 53 s | the old-branch check ("fresh" must not be listed) inverted |
| G4 test-machine MCH-1 | machine-apply-installs, machine-task-layout | machine-apply-installs | the toy run once with no argument: all 16 cases, which include the 12 the old rows named (exit status). The toy case machine-task-layout is renamed machine-task-schedule, and row machine-done-8 and the toy's row list follow | 26 s | the task-layout file check made to fail |
| G5 test-docs-format DOC-25 | format-home, format-key | format-home | the 13 PASS lines of both rows, one run | 68 s | the "format key without problem turns DOC-8 off" check inverted |
| G6 test-hard-eta DEL-17 | eta-freeze, eta-health-missing | eta-freeze | the 10 cases' PASS lines and the three controls.py runs, one run | 3 s | the goal.py join check ("pr_queue join") broken |
| G7 test-criteria REG-4 | one-link, refused-unmet | not merged | | | |
| G8 test-setup-adopt SET-1 | set1-health-bracket, set1-docs-format | not merged | | | |
| G9 test-tiers REG-4 | tiers-unmapped-qa-pr, goal-levels-nightly | tiers-unmapped-qa-pr | the 7 checks, one run (the two counted greps keep their counts) | 9 s | the goal-lane "SELECTED" check changed |
| G10 test-lanes REG-4 | lanes-reuse, lanes-pr-affected | not merged | | | |
| G11 test-budget MCH-1 | del8-floor-step, grd2-step-budget | not merged | | | |
| G12 test-roadmap CHK-1 | roadmap-closed-drops, roadmap-finished-not-queued | roadmap-closed-drops | the 10 PASS lines, one run | 2 s | the home-path check inverted |
| G13 test-narrow REG-4 | lanes-declared, lanes-wide-parity | lanes-declared | the 9 groups of PASS lines, one run | 8 s | the LANES_WIDE affected-set line changed |
| G14 test-migration SET-1 | migration-clean, migration-base-config | not merged | | | |
| G15 test-release-gate DEL-1 | rel-open-issue-refused, rel-owner-only | not merged | | | |
| G16 test-budget-enforce MCH-1 | grd2-time-stop, grd2-limits-in-settings | grd2-time-stop | the 12 PASS lines of both rows, one run | 2 s | the default time budget check (240) changed to 239 |

## Skipped groups and why

- G7, G10 and G11: a source row already fails in this environment on main (refused-unmet, lanes-pr-affected, del8-floor-step and grd2-step-budget exit 1 on the base commit here, apparently the real gh or push each needs), so the merged row can neither be measured nor proven here. They pass on the owner's machine; merge them there.
- G8 and G14: the old rows run 8 and 11 different arguments, over the 6-run limit, and the toy run with no argument fails here (test-migration.sh in its known-red part, test-setup-adopt.sh in a case that depends on order).
- G15: the no-argument run includes the major leg, which fails today (rel-major-refused is on the known list); the legs are 7 runs.
- G2: see the table; the merge comes from rows-600-e and is not proven by this goal.

No requirement has fewer non-defect land or nightly rows than one (173 requirements before and after). Removed ids are gone from regression-red, -runs, -issues, -known and the Tests pages; the only toy that named one (test-machine.sh) is updated. Dated notes (docs/triage-2026-11-14.md, .loop/readme-gap-table.md, past goal files) still name old ids as history.
