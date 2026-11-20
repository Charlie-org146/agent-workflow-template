<!-- workflow-docs -->
# Tests

## Automation

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-refuse-replace"></a>refuse-replace | requirement | AUT-5 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-19 |
| <a id="t-ci-summary"></a>ci-summary | requirement | AUT-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-schedule-setting"></a>schedule-setting | requirement | AUT-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-08 |
| <a id="t-bad-schedule-refused"></a>bad-schedule-refused | requirement | AUT-5 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-08 |
| <a id="t-aut-defect-issue"></a>aut-defect-issue | requirement | AUT-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-10 |
| <a id="t-aut-regression-off"></a>aut-regression-off | requirement | AUT-5 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-10 |
| <a id="t-ls-private-tick"></a>ls-private-tick | requirement | AUT-1 | not run | - | local | 2026-11-12 |
| <a id="t-st-pass"></a>st-pass | requirement | AUT-1 | not run | - | local | 2026-11-12 |
| <a id="t-aut-email-file"></a>aut-email-file | requirement | AUT-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-runbook-good"></a>runbook-good | requirement | AUT-1 | not run | - | local | 2026-11-12 |
| <a id="t-runbook-registry"></a>runbook-registry | requirement | AUT-1 | not run | - | local | 2026-11-12 |
| <a id="t-capture-row-ci"></a>capture-row-ci | defect | [#3789](https://github.com/jcl2018/agent-workflow-template/issues/3789) closed (2026-11-13) | FAIL | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-13 |
| <a id="t-runbook-output-names-row"></a>runbook-output-names-row | requirement | AUT-1 | not run | - | local | 2026-11-13 |
| <a id="t-publish-tables-regen"></a>publish-tables-regen | requirement | AUT-5 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-13 |
| <a id="t-aut-routine-block"></a>aut-routine-block | requirement | AUT-1 | not run | - | local | 2026-11-13 |
| <a id="t-automation-table-health"></a>automation-table-health | defect | [#3857](https://github.com/jcl2018/agent-workflow-template/issues/3857) closed (2026-11-13) | not run | - | local | 2026-11-13 |
| <a id="t-health-register-no-launchd"></a>health-register-no-launchd | requirement | AUT-1 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-perms-docs-check"></a>perms-docs-check | requirement | AUT-1 | not run | - | local | 2026-11-14 |

## Check-in and board

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-retired-leaves-waiting"></a>retired-leaves-waiting | requirement | CHK-1 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-stuck-stays-top"></a>stuck-stays-top | requirement | CHK-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-status-roadmap-features"></a>status-roadmap-features | requirement | CHK-1 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-09 |
| <a id="t-status-graph-order"></a>status-graph-order | requirement | CHK-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-status-graph-board"></a>status-graph-board | requirement | CHK-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-reply-hook-blocks"></a>reply-hook-blocks | requirement | CHK-1 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-09 |
| <a id="t-reply-hook-scope"></a>reply-hook-scope | requirement | CHK-1 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-09 |
| <a id="t-reply-hook-mon5-wording"></a>reply-hook-mon5-wording | requirement | CHK-1 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-18 |
| <a id="t-held-stale-next"></a>held-stale-next | defect | [#102](https://github.com/jcl2018/agent-workflow-template/issues/102) closed (2026-11-10) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-depth-on-board"></a>depth-on-board | requirement | CHK-1 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-held-all"></a>held-all | requirement | CHK-1 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-20 |
| <a id="t-reply-hook-checkin-123"></a>reply-hook-checkin-123 | defect | [#123](https://github.com/jcl2018/agent-workflow-template/issues/123) closed (2026-11-10) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-aut-digest-create"></a>aut-digest-create | requirement | CHK-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-10 |
| <a id="t-est-area"></a>est-area | requirement | CHK-1 | not run | - | local | 2026-11-10 |
| <a id="t-est-pace"></a>est-pace | requirement | CHK-1 | not run | - | local | 2026-11-10 |
| <a id="t-est-stalled"></a>est-stalled | defect | [#37](https://github.com/jcl2018/agent-workflow-template/issues/37) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-est-issue-96"></a>est-issue-96 | defect | [#96](https://github.com/jcl2018/agent-workflow-template/issues/96) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-est-big-goal"></a>est-big-goal | requirement | CHK-1 | not run | - | local | 2026-11-10 |
| <a id="t-mon4-checkin-no-board"></a>mon4-checkin-no-board | requirement | CHK-1 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-deps-graph-94"></a>deps-graph-94 | defect | [#94](https://github.com/jcl2018/agent-workflow-template/issues/94) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-issues-phone-97"></a>issues-phone-97 | defect | [#97](https://github.com/jcl2018/agent-workflow-template/issues/97) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-report-held-111"></a>report-held-111 | defect | [#111](https://github.com/jcl2018/agent-workflow-template/issues/111) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-state-shared-113"></a>state-shared-113 | defect | [#113](https://github.com/jcl2018/agent-workflow-template/issues/113) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-held-time-115"></a>held-time-115 | defect | [#115](https://github.com/jcl2018/agent-workflow-template/issues/115) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-aut-email-mail"></a>aut-email-mail | requirement | CHK-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-reply-checkin-321"></a>reply-checkin-321 | defect | [#321](https://github.com/jcl2018/agent-workflow-template/issues/321) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-est-backtest-loo"></a>est-backtest-loo | requirement | CHK-1 | not run | - | local | 2026-11-10 |
| <a id="t-est-backtest-speed"></a>est-backtest-speed | requirement | CHK-1 | not run | - | local | 2026-11-12 |
| <a id="t-mon14-repo-blocks"></a>mon14-repo-blocks | requirement | CHK-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-mon14-reply-repo-blocks"></a>mon14-reply-repo-blocks | requirement | CHK-1 | not run | - | local | 2026-11-13 |
| <a id="t-mon14-reply-deps-whole"></a>mon14-reply-deps-whole | requirement | CHK-1 | not run | - | local | 2026-11-13 |
| <a id="t-mon-stray-runs"></a>mon-stray-runs | requirement | CHK-1 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-13 |
| <a id="t-mon14-map-finish"></a>mon14-map-finish | requirement | CHK-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-15 |
| <a id="t-machine-local-checkin"></a>machine-local-checkin | requirement | CHK-1 | not run | - | local | 2026-11-13 |
| <a id="t-held-time-session-hold"></a>held-time-session-hold | requirement | CHK-1 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-15 |
| <a id="t-roadmap-closed-drops"></a>roadmap-closed-drops | requirement | CHK-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-monitor-stray-runs-3862"></a>monitor-stray-runs-3862 | defect | [#3862](https://github.com/jcl2018/agent-workflow-template/issues/3862) closed (2026-11-14) | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-13 |
| <a id="t-budget-fair-base-moved"></a>budget-fair-base-moved | requirement | CHK-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-mon17-this-pod-only"></a>mon17-this-pod-only | requirement | CHK-1 | not run | - | local | 2026-11-15 |
| <a id="t-review-board-shows-wait"></a>review-board-shows-wait | requirement | CHK-1 | not run | - | local | 2026-11-15 |
| <a id="t-machine-guide-monitoring"></a>machine-guide-monitoring | requirement | CHK-1 | not run | - | local | 2026-11-16 |
| <a id="t-mon5-checkin-machine-line"></a>mon5-checkin-machine-line | requirement | CHK-1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-eta-checkin-table"></a>eta-checkin-table | requirement | CHK-1 | not run | - | local | 2026-11-16 |
| <a id="t-held-charge-pauses"></a>held-charge-pauses | requirement | CHK-1 | not run | - | local | 2026-11-16 |
| <a id="t-notify-new-events"></a>notify-new-events | requirement | CHK-1 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-mailbox-two-mails"></a>mailbox-two-mails | requirement | CHK-1 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-mailbox-two-mails-4785"></a>mailbox-two-mails-4785 | defect | [#4785](https://github.com/jcl2018/agent-workflow-template/issues/4785) closed (2026-11-18) | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-mailbox-two-mails-4671"></a>mailbox-two-mails-4671 | defect | [#4671](https://github.com/jcl2018/agent-workflow-template/issues/4671) closed (2026-11-18) | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-queue-view-blocks"></a>queue-view-blocks | requirement | CHK-1 | not run | - | local | 2026-11-20 |
| <a id="t-board-tz-mixed-stamps"></a>board-tz-mixed-stamps | requirement | CHK-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-20 |
| <a id="t-release-progress-bars"></a>release-progress-bars | requirement | CHK-1 | not run | - | local | 2026-11-20 |

## Delivery

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-no-done-line-refused"></a>no-done-line-refused | requirement | DEL-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-no-flow-refused"></a>no-flow-refused | requirement | DEL-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-pending-waits"></a>pending-waits | requirement | DEL-3 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-frozen-done-lines"></a>frozen-done-lines | requirement | DEL-19 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-stop-after-3-tries"></a>stop-after-3-tries | requirement | DEL-1 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-auto-approved"></a>auto-approved | requirement | DEL-3 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-wiki-release"></a>wiki-release | requirement | DEL-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-08 |
| <a id="t-auto-release"></a>auto-release | requirement | DEL-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-11 |
| <a id="t-scripts-no-hang"></a>scripts-no-hang | defect | [#35](https://github.com/jcl2018/agent-workflow-template/issues/35) closed (2026-11-09) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-08 |
| <a id="t-wiki-release-pycache"></a>wiki-release-pycache | defect | [#58](https://github.com/jcl2018/agent-workflow-template/issues/58) closed (2026-11-09) | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-08 |
| <a id="t-worker-runs-release"></a>worker-runs-release | defect | [PR 61](https://github.com/jcl2018/agent-workflow-template/pull/61) merged (2026-11-09) | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-08 |
| <a id="t-pr-body-no-checks"></a>pr-body-no-checks | defect | [PR 62](https://github.com/jcl2018/agent-workflow-template/pull/62) merged (2026-11-09) | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-08 |
| <a id="t-defect-flow-steps"></a>defect-flow-steps | requirement | DEL-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-08 |
| <a id="t-wiki-unmapped-stale"></a>wiki-unmapped-stale | requirement | DEL-1 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-09 |
| <a id="t-depth-condensed-refused"></a>depth-condensed-refused | requirement | DEL-3 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-09 |
| <a id="t-depth-in-pr-body"></a>depth-in-pr-body | requirement | DEL-1 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-guards-rule-start"></a>guards-rule-start | defect | [#147](https://github.com/jcl2018/agent-workflow-template/issues/147) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-guards-no-try"></a>guards-no-try | defect | [#148](https://github.com/jcl2018/agent-workflow-template/issues/148) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-guards-touches-finding"></a>guards-touches-finding | defect | [#157](https://github.com/jcl2018/agent-workflow-template/issues/157) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-guards-extra"></a>guards-extra | requirement | DEL-1 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-mon11-full-auto"></a>mon11-full-auto | requirement | DEL-3 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-10 |
| <a id="t-aut-email-secrets"></a>aut-email-secrets | requirement | DEL-9 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-builtin-flow"></a>builtin-flow | defect | [#47](https://github.com/jcl2018/agent-workflow-template/issues/47) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-suite-time-recorded"></a>suite-time-recorded | requirement | DEL-17 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-health-timing"></a>health-timing | requirement | DEL-17 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-19 |
| <a id="t-lane-over-minutes"></a>lane-over-minutes | requirement | DEL-17 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-19 |
| <a id="t-reg7-floor-test"></a>reg7-floor-test | requirement | DEL-17 | not run | - | local | 2026-11-11 |
| <a id="t-reg7-unmapped-tier"></a>reg7-unmapped-tier | requirement | DEL-17 | not run | - | local | 2026-11-11 |
| <a id="t-reg7-prep-setting"></a>reg7-prep-setting | requirement | DEL-17 | not run | - | local | 2026-11-11 |
| <a id="t-del6-depth-by-size"></a>del6-depth-by-size | requirement | DEL-3 | not run | - | local | 2026-11-11 |
| <a id="t-del5-patch-default"></a>del5-patch-default | requirement | DEL-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-11 |
| <a id="t-del9-pr-refuses"></a>del9-pr-refuses | requirement | DEL-9 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-18 |
| <a id="t-del9-merge-refuses"></a>del9-merge-refuses | requirement | DEL-9 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-del9-scan-sites"></a>del9-scan-sites | requirement | DEL-9 | not run | - | local | 2026-11-10 |
| <a id="t-issue-38-verdicts"></a>issue-38-verdicts | defect | [#38](https://github.com/jcl2018/agent-workflow-template/issues/38) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-issue-117-github-touches"></a>issue-117-github-touches | defect | [#117](https://github.com/jcl2018/agent-workflow-template/issues/117) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-issue-129-docs-published"></a>issue-129-docs-published | defect | [#129](https://github.com/jcl2018/agent-workflow-template/issues/129) closed (2026-11-15) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-issue-134-protected-release"></a>issue-134-protected-release | defect | [#134](https://github.com/jcl2018/agent-workflow-template/issues/134) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-issue-154-release-pr-merge"></a>issue-154-release-pr-merge | defect | [#154](https://github.com/jcl2018/agent-workflow-template/issues/154) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-issue-170-patch-on-remove"></a>issue-170-patch-on-remove | defect | [#170](https://github.com/jcl2018/agent-workflow-template/issues/170) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-del9-lane-part-no-path"></a>del9-lane-part-no-path | requirement | DEL-9 | not run | - | local | 2026-11-11 |
| <a id="t-set8-hooks"></a>set8-hooks | requirement | DEL-9 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-12 |
| <a id="t-set8-local-setting-refused"></a>set8-local-setting-refused | requirement | DEL-9 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-12 |
| <a id="t-ptb-mend"></a>ptb-mend | requirement | DEL-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-tree-once-lock"></a>tree-once-lock | requirement | DEL-17 | not run | - | local | 2026-11-12 |
| <a id="t-machine-no-private"></a>machine-no-private | requirement | DEL-9 | PASS 2026-11-17 FLAKY | - | local | 2026-11-16 |
| <a id="t-grd7-round-cost"></a>grd7-round-cost | requirement | DEL-17 | not run | - | local | 2026-11-12 |
| <a id="t-grd8-silent-worker"></a>grd8-silent-worker | requirement | DEL-17 | not run | - | local | 2026-11-12 |
| <a id="t-budgets-agree"></a>budgets-agree | requirement | DEL-17 | not run | - | local | 2026-11-18 |
| <a id="t-pr-body-by-file"></a>pr-body-by-file | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-19 |
| <a id="t-del5-docs-bump-minor"></a>del5-docs-bump-minor | requirement | DEL-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-13 |
| <a id="t-resume-ask-worker-step"></a>resume-ask-worker-step | requirement | DEL-1 | not run | - | local | 2026-11-13 |
| <a id="t-package-gate-controls"></a>package-gate-controls | requirement | DEL-1 | not run | - | local | 2026-11-13 |
| <a id="t-del1-new-here-main-refused"></a>del1-new-here-main-refused | defect | 3468 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-13 |
| <a id="t-reg7-unrun-warn-cost"></a>reg7-unrun-warn-cost | requirement | DEL-17 | not run | - | local | 2026-11-13 |
| <a id="t-release-head-status"></a>release-head-status | defect | [#3870](https://github.com/jcl2018/agent-workflow-template/issues/3870) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-pr-moved-uncounted"></a>pr-moved-uncounted | requirement | DEL-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-13 |
| <a id="t-rerun-both-touched"></a>rerun-both-touched | requirement | DEL-17 | not run | - | local | 2026-11-13 |
| <a id="t-merge-batch-split"></a>merge-batch-split | requirement | DEL-17 | not run | - | local | 2026-11-20 |
| <a id="t-health-mail-env-named"></a>health-mail-env-named | requirement | DEL-9 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-merge-stale-other-passes"></a>merge-stale-other-passes | defect | [#3941](https://github.com/jcl2018/agent-workflow-template/issues/3941) closed (2026-11-13) | not run | - | local | 2026-11-14 |
| <a id="t-lane-walk-skips-node-modules"></a>lane-walk-skips-node-modules | requirement | DEL-17 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-unattended-loop-recreate"></a>unattended-loop-recreate | requirement | DEL-3 | not run | - | local | 2026-11-14 |
| <a id="t-unattended-checkin-line"></a>unattended-checkin-line | requirement | DEL-3 | not run | - | local | 2026-11-14 |
| <a id="t-merge-refused-failed"></a>merge-refused-failed | defect | [#4004](https://github.com/jcl2018/agent-workflow-template/issues/4004) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-perms-private-never-written"></a>perms-private-never-written | requirement | DEL-9 | not run | - | local | 2026-11-14 |
| <a id="t-merge-refuses-worktree"></a>merge-refuses-worktree | defect | [#4020](https://github.com/jcl2018/agent-workflow-template/issues/4020) closed (2026-11-14) | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-moved-exit-live-at-pr"></a>moved-exit-live-at-pr | defect | [#4004](https://github.com/jcl2018/agent-workflow-template/issues/4004) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-lane-affected-memory"></a>lane-affected-memory | defect | 4151 | not run | - | local | 2026-11-14 |
| <a id="t-merge-main-own-printed"></a>merge-main-own-printed | defect | [#4020](https://github.com/jcl2018/agent-workflow-template/issues/4020) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-skill-refusals-in-references"></a>skill-refusals-in-references | requirement | DEL-1 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-pr-body-no-home-3841"></a>pr-body-no-home-3841 | defect | [#3841](https://github.com/jcl2018/agent-workflow-template/issues/3841) closed (2026-11-14) | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-lane-order"></a>lane-order | defect | 531 | not run | - | local | 2026-11-15 |
| <a id="t-release-scripts-under-19000"></a>release-scripts-under-19000 | requirement | DEL-1 | not run | - | local | 2026-11-20 |
| <a id="t-private-names-scoped"></a>private-names-scoped | requirement | DEL-9 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-15 |
| <a id="t-pr-head-audit-passes-4208"></a>pr-head-audit-passes-4208 | defect | [#4208](https://github.com/jcl2018/agent-workflow-template/issues/4208) closed (2026-11-15) | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-14 |
| <a id="t-scripts-a-delivery-under-19000"></a>scripts-a-delivery-under-19000 | requirement | DEL-1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-20 |
| <a id="t-del5-merge-forwards-checkout"></a>del5-merge-forwards-checkout | requirement | DEL-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-auto-owner-words-wait"></a>auto-owner-words-wait | requirement | DEL-3 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-18 |
| <a id="t-start-from-head-passes-4340"></a>start-from-head-passes-4340 | requirement | DEL-1 | not run | - | local | 2026-11-15 |
| <a id="t-hook-count"></a>hook-count | defect | 4345 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-15 |
| <a id="t-merge-main-own-finding-4343"></a>merge-main-own-finding-4343 | requirement | DEL-1 | not run | - | local | 2026-11-15 |
| <a id="t-review-hold-blocks"></a>review-hold-blocks | requirement | DEL-3 | not run | - | local | 2026-11-15 |
| <a id="t-review-help-runs-alone"></a>review-help-runs-alone | requirement | DEL-3 | not run | - | local | 2026-11-15 |
| <a id="t-audit-head-judges-own-docs"></a>audit-head-judges-own-docs | requirement | DEL-1 | not run | - | local | 2026-11-15 |
| <a id="t-release-criteria-known-skip"></a>release-criteria-known-skip | requirement | DEL-1 | not run | - | local | 2026-11-16 |
| <a id="t-test-caps-consolidate-allowed"></a>test-caps-consolidate-allowed | requirement | DEL-17 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-eta-freeze"></a>eta-freeze | requirement | DEL-17 | not run | - | local | 2026-11-16 |
| <a id="t-cut-pass-current-commit"></a>cut-pass-current-commit | requirement | DEL-1 | not run | - | local | 2026-11-16 |
| <a id="t-private-checks-stop"></a>private-checks-stop | requirement | DEL-1 | not run | - | local | 2026-11-16 |
| <a id="t-lane-env-states"></a>lane-env-states | requirement | DEL-17 | not run | - | local | 2026-11-16 |
| <a id="t-lane-memory-not-counted"></a>lane-memory-not-counted | requirement | DEL-1 | not run | - | local | 2026-11-19 |
| <a id="t-lane-walk-skips-git"></a>lane-walk-skips-git | requirement | DEL-17 | not run | - | local | 2026-11-16 |
| <a id="t-rel-major-refused"></a>rel-major-refused | requirement | DEL-1 | not run | - | local | 2026-11-17 |
| <a id="t-rel-open-issue-refused"></a>rel-open-issue-refused | requirement | DEL-1 | not run | - | local | 2026-11-19 |
| <a id="t-rel-owner-only"></a>rel-owner-only | requirement | DEL-1 | not run | - | local | 2026-11-17 |
| <a id="t-gate-untouched-not-refused"></a>gate-untouched-not-refused | requirement | DEL-1 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-19 |
| <a id="t-depth-marker-rows-4557"></a>depth-marker-rows-4557 | defect | #4557 | not run | - | local | 2026-11-19 |
| <a id="t-rel-ci-release"></a>rel-ci-release | requirement | DEL-17 | not run | - | local | 2026-11-20 |
| <a id="t-rel-update-asset"></a>rel-update-asset | requirement | DEL-17 | not run | - | local | 2026-11-20 |
| <a id="t-queue-use"></a>queue-use | requirement | DEL-17 | not run | - | local | 2026-11-20 |
| <a id="t-follows-adoption"></a>follows-adoption | requirement | DEL-21 | not run | - | local | 2026-11-20 |

## Documentation

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-stale-found"></a>stale-found | requirement | DOC-25 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-09 |
| <a id="t-page-shape"></a>page-shape | requirement | DOC-25 | FAIL | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-10 |
| <a id="t-review-dated"></a>review-dated | requirement | DOC-2 | FAIL | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-10 |
| <a id="t-template-sheet"></a>template-sheet | requirement | DOC-25 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-08 |
| <a id="t-no-usage-passes"></a>no-usage-passes | requirement | DOC-25 | not run | - | local | 2026-11-09 |
| <a id="t-docs-counts-issue-39"></a>docs-counts-issue-39 | defect | [#39](https://github.com/jcl2018/agent-workflow-template/issues/39) closed (2026-11-09) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-prd-section-order"></a>prd-section-order | requirement | DOC-25 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-18 |
| <a id="t-prd-lock-four"></a>prd-lock-four | requirement | DOC-2 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-18 |
| <a id="t-prd-repo-green"></a>prd-repo-green | requirement | DOC-25 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-18 |
| <a id="t-docs-count-word-gap-issue-104"></a>docs-count-word-gap-issue-104 | defect | [#104](https://github.com/jcl2018/agent-workflow-template/issues/104) closed (2026-11-10) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-docs-count-indented-code-issue-105"></a>docs-count-indented-code-issue-105 | defect | [#105](https://github.com/jcl2018/agent-workflow-template/issues/105) closed (2026-11-10) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-docs-count-defect-tests-issue-106"></a>docs-count-defect-tests-issue-106 | defect | [#106](https://github.com/jcl2018/agent-workflow-template/issues/106) closed (2026-11-10) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-docs-count-other-id-issue-107"></a>docs-count-other-id-issue-107 | defect | [#107](https://github.com/jcl2018/agent-workflow-template/issues/107) closed (2026-11-10) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-format-home"></a>format-home | requirement | DOC-25 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-19 |
| <a id="t-format-frontdoor"></a>format-frontdoor | requirement | DOC-25 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-18 |
| <a id="t-docs-guide-page-issue-125"></a>docs-guide-page-issue-125 | defect | [#125](https://github.com/jcl2018/agent-workflow-template/issues/125) closed (2026-11-11) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-docs-locked-hint-issue-133"></a>docs-locked-hint-issue-133 | defect | [#133](https://github.com/jcl2018/agent-workflow-template/issues/133) closed (2026-11-13) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-docs-merged-base-issue-156"></a>docs-merged-base-issue-156 | defect | [#156](https://github.com/jcl2018/agent-workflow-template/issues/156) closed (2026-11-11) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-deploy-section-optional"></a>deploy-section-optional | requirement | DOC-25 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-settings-overridden"></a>settings-overridden | requirement | DOC-25 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-blocks-no-insert"></a>blocks-no-insert | requirement | DOC-25 | not run | - | local | 2026-11-18 |
| <a id="t-spec-decisions-wording"></a>spec-decisions-wording | requirement | DOC-25 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-spec-decisions-log"></a>spec-decisions-log | requirement | DOC-25 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-12 |
| <a id="t-command-reference-complete"></a>command-reference-complete | requirement | DOC-25 | not run | - | local | 2026-11-13 |
| <a id="t-automation-links-runbook"></a>automation-links-runbook | requirement | DOC-25 | not run | - | local | 2026-11-13 |
| <a id="t-owner-record-applies"></a>owner-record-applies | requirement | DOC-2 | not run | - | local | 2026-11-13 |
| <a id="t-link-page-passes"></a>link-page-passes | requirement | DOC-25 | FAIL | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-14 |
| <a id="t-stale-own-finding"></a>stale-own-finding | requirement | DOC-25 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-13 |
| <a id="t-page-relock"></a>page-relock | requirement | DOC-2 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-20 |
| <a id="t-home-topic-live"></a>home-topic-live | requirement | DOC-25 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-14 |
| <a id="t-launchctl-missing-unknown"></a>launchctl-missing-unknown | requirement | DOC-25 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-sync-not-connected"></a>sync-not-connected | requirement | DOC-2 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-17 |
| <a id="t-merge-main-own-finding"></a>merge-main-own-finding | defect | [#4020](https://github.com/jcl2018/agent-workflow-template/issues/4020) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-skill-criteria-in-references"></a>skill-criteria-in-references | requirement | DOC-25 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-skill-lines-release-4172"></a>skill-lines-release-4172 | defect | [#4172](https://github.com/jcl2018/agent-workflow-template/issues/4172) closed (2026-11-19) | not run | - | local | 2026-11-14 |
| <a id="t-skill-lines-docs-4171"></a>skill-lines-docs-4171 | defect | [#4171](https://github.com/jcl2018/agent-workflow-template/issues/4171) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-skill-lines-regression-3983"></a>skill-lines-regression-3983 | defect | [#3983](https://github.com/jcl2018/agent-workflow-template/issues/3983) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-skill-lines-regression-3815"></a>skill-lines-regression-3815 | defect | [#3815](https://github.com/jcl2018/agent-workflow-template/issues/3815) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-skill-lines-docs-1403"></a>skill-lines-docs-1403 | defect | [#1403](https://github.com/jcl2018/agent-workflow-template/issues/1403) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-lane-rows-judge-own-diff"></a>lane-rows-judge-own-diff | defect | [#3876](https://github.com/jcl2018/agent-workflow-template/issues/3876) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-docs-scripts-under-19000"></a>docs-scripts-under-19000 | requirement | DOC-25 | not run | - | local | 2026-11-20 |
| <a id="t-template-in-commands"></a>template-in-commands | requirement | DOC-25 | not run | - | local | 2026-11-15 |
| <a id="t-stale-comments-only-3122"></a>stale-comments-only-3122 | defect | [#3122](https://github.com/jcl2018/agent-workflow-template/issues/3122) closed (2026-11-15) | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-restamp-marks-3867"></a>restamp-marks-3867 | defect | [#3867](https://github.com/jcl2018/agent-workflow-template/issues/3867) closed (2026-11-15) | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-restamp-wording-locked-3867"></a>restamp-wording-locked-3867 | defect | [#3867](https://github.com/jcl2018/agent-workflow-template/issues/3867) closed (2026-11-15) | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-docs-scripts-import-by-name"></a>docs-scripts-import-by-name | requirement | DOC-25 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-milestone-sync-no-source"></a>milestone-sync-no-source | requirement | DOC-2 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-15 |
| <a id="t-prd-copy-no-reader"></a>prd-copy-no-reader | requirement | DOC-2 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-15 |
| <a id="t-doc18-howto-missing"></a>doc18-howto-missing | requirement | DOC-25 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-doc18-howto-restamp"></a>doc18-howto-restamp | requirement | DOC-25 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-home-stale-clears"></a>home-stale-clears | requirement | DOC-25 | not run | - | local | 2026-11-16 |
| <a id="t-apply-rerender-blocks"></a>apply-rerender-blocks | requirement | DOC-2 | not run | - | local | 2026-11-16 |
| <a id="t-apply-rerender-tables"></a>apply-rerender-tables | requirement | DOC-2 | not run | - | local | 2026-11-16 |
| <a id="t-stale-code-page-reviewed"></a>stale-code-page-reviewed | requirement | DOC-2 | not run | - | local | 2026-11-16 |
| <a id="t-stale-code-page-wording"></a>stale-code-page-wording | requirement | DOC-2 | not run | - | local | 2026-11-16 |
| <a id="t-doc19-kind-row"></a>doc19-kind-row | requirement | DOC-25 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-17 |
| <a id="t-doc19-readme-links"></a>doc19-readme-links | requirement | DOC-25 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-17 |
| <a id="t-doc-nongoal-milestone-sync"></a>doc-nongoal-milestone-sync | defect | [#4546](https://github.com/jcl2018/agent-workflow-template/issues/4546) closed (2026-11-16) | not run | - | local | 2026-11-16 |
| <a id="t-doc19-diagram-passes"></a>doc19-diagram-passes | requirement | DOC-25 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-17 |
| <a id="t-docs-v2-repo-passes"></a>docs-v2-repo-passes | requirement | DOC-25 | not run | - | local | 2026-11-17 |
| <a id="t-links-own-site-passes"></a>links-own-site-passes | requirement | DOC-25 | not run | - | local | 2026-11-18 |
| <a id="t-entry-committed-config"></a>entry-committed-config | requirement | DOC-25 | not run | - | local | 2026-11-19 |
| <a id="t-sections-controls"></a>sections-controls | requirement | DOC-25 | not run | - | local | 2026-11-20 |
| <a id="t-delegated-record-accepted"></a>delegated-record-accepted | requirement | DOC-2 | not run | - | local | 2026-11-20 |

## Guardrails

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-mon7-govern-blocks"></a>mon7-govern-blocks | requirement | GRD-4 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-pull-ff-only-passes"></a>pull-ff-only-passes | defect | [#495](https://github.com/jcl2018/agent-workflow-template/issues/495) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-machine-no-prompt-mode"></a>machine-no-prompt-mode | requirement | GRD-4 | not run | - | local | 2026-11-12 |
| <a id="t-grd4-touches"></a>grd4-touches | requirement | GRD-4 | not run | - | local | 2026-11-12 |
| <a id="t-grd4-budget"></a>grd4-budget | requirement | GRD-4 | not run | - | local | 2026-11-12 |
| <a id="t-grd4-govern"></a>grd4-govern | requirement | GRD-4 | not run | - | local | 2026-11-12 |
| <a id="t-grd5-regression-dry"></a>grd5-regression-dry | requirement | GRD-5 | not run | - | local | 2026-11-12 |
| <a id="t-grd5-health-close"></a>grd5-health-close | requirement | GRD-5 | not run | - | local | 2026-11-12 |
| <a id="t-grd6-head-moved"></a>grd6-head-moved | requirement | GRD-6 | not run | - | local | 2026-11-12 |
| <a id="t-mon16-notes-pass"></a>mon16-notes-pass | requirement | GRD-4 | not run | - | local | 2026-11-13 |
| <a id="t-issues-live-only-ci"></a>issues-live-only-ci | requirement | GRD-5 | not run | - | local | 2026-11-13 |
| <a id="t-package-caps-held"></a>package-caps-held | requirement | GRD-20 | PASS 2026-11-14 FLAKY | - | local | 2026-11-13 |
| <a id="t-perms-undeclared"></a>perms-undeclared | requirement | GRD-4 | not run | - | local | 2026-11-14 |
| <a id="t-perms-repo-ok"></a>perms-repo-ok | requirement | GRD-4 | not run | - | local | 2026-11-14 |
| <a id="t-perms-settings-tracked"></a>perms-settings-tracked | requirement | GRD-4 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-perms-no-repo-deny"></a>perms-no-repo-deny | requirement | GRD-4 | not run | - | local | 2026-11-15 |
| <a id="t-grd4-worker-commit-main-refused"></a>grd4-worker-commit-main-refused | requirement | GRD-4 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-issues-rest-fallback"></a>issues-rest-fallback | defect | [#4464](https://github.com/jcl2018/agent-workflow-template/issues/4464) closed (2026-11-16) | not run | - | local | 2026-11-16 |
| <a id="t-quiet-plain-import-4892"></a>quiet-plain-import-4892 | defect | [#4892](https://github.com/jcl2018/agent-workflow-template/issues/4892) closed (2026-11-17) | not run | - | local | 2026-11-17 |
| <a id="t-desk-lists"></a>desk-lists | requirement | GRD-4 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-desk-lists-4805"></a>desk-lists-4805 | defect | [#4805](https://github.com/jcl2018/agent-workflow-template/issues/4805) closed (2026-11-18) | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |

## Health

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-known-no-block"></a>known-no-block | requirement | HLT-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-13 |
| <a id="t-same-lines"></a>same-lines | requirement | HLT-2 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-no-token-would"></a>no-token-would | requirement | HLT-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-repeat-no-second"></a>repeat-no-second | requirement | HLT-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-13 |
| <a id="t-defect-health"></a>defect-health | requirement | HLT-2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-08 |
| <a id="t-cost-time-warn"></a>cost-time-warn | requirement | HLT-2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-20 |
| <a id="t-judge-section-format"></a>judge-section-format | requirement | HLT-4 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-08 |
| <a id="t-report-header"></a>report-header | requirement | HLT-2 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-09 |
| <a id="t-preview-writes-nothing"></a>preview-writes-nothing | requirement | HLT-4 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-hlt6-controls-fire"></a>hlt6-controls-fire | requirement | HLT-2 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-hlt6-refused"></a>hlt6-refused | requirement | HLT-2 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-known-recorded"></a>known-recorded | requirement | HLT-4 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-docs-check-speed"></a>docs-check-speed | requirement | HLT-7 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-docs-check-same"></a>docs-check-same | requirement | HLT-2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-reg-defect-label"></a>reg-defect-label | requirement | HLT-4 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-mon9-board-fast"></a>mon9-board-fast | requirement | HLT-7 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-aut-email-rounds"></a>aut-email-rounds | requirement | HLT-7 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-hlt2-twelve-groups"></a>hlt2-twelve-groups | requirement | HLT-2 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-18 |
| <a id="t-hlt4-feature-milestones"></a>hlt4-feature-milestones | requirement | HLT-4 | not run | - | local | 2026-11-12 |
| <a id="t-hlt1-same-answer"></a>hlt1-same-answer | requirement | HLT-2 | not run | - | local | 2026-11-10 |
| <a id="t-health-tokens-124"></a>health-tokens-124 | defect | [#124](https://github.com/jcl2018/agent-workflow-template/issues/124) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-judge-cause-158"></a>judge-cause-158 | defect | [#158](https://github.com/jcl2018/agent-workflow-template/issues/158) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-health-docs-159"></a>health-docs-159 | defect | [#159](https://github.com/jcl2018/agent-workflow-template/issues/159) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-health-not-enforced-warn"></a>health-not-enforced-warn | requirement | HLT-2 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-health-unreviewed-warn-issue-118"></a>health-unreviewed-warn-issue-118 | defect | [#118](https://github.com/jcl2018/agent-workflow-template/issues/118) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-hlt7-fast-check"></a>hlt7-fast-check | requirement | HLT-7 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-grd1-guardrail-list"></a>grd1-guardrail-list | requirement | HLT-2 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-13 |
| <a id="t-aut7-budget-agrees"></a>aut7-budget-agrees | requirement | HLT-7 | not run | - | local | 2026-11-18 |
| <a id="t-capture-row-mac"></a>capture-row-mac | defect | [#3789](https://github.com/jcl2018/agent-workflow-template/issues/3789) closed (2026-11-13) | not run | - | local | 2026-11-13 |
| <a id="t-issues-one-open-ci"></a>issues-one-open-ci | requirement | HLT-4 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-13 |
| <a id="t-backlog-milestones-made"></a>backlog-milestones-made | requirement | HLT-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-13 |
| <a id="t-repo-rules-run"></a>repo-rules-run | requirement | HLT-2 | not run | - | local | 2026-11-19 |
| <a id="t-hlt8-triage-one-issue"></a>hlt8-triage-one-issue | requirement | HLT-4 | not run | - | local | 2026-11-13 |
| <a id="t-hlt9-located-evidence"></a>hlt9-located-evidence | requirement | HLT-4 | not run | - | local | 2026-11-13 |
| <a id="t-hlt2-defect-exempt-health"></a>hlt2-defect-exempt-health | requirement | HLT-2 | not run | - | local | 2026-11-13 |
| <a id="t-aut-prompt-warns"></a>aut-prompt-warns | requirement | HLT-2 | not run | - | local | 2026-11-13 |
| <a id="t-machine-local-health-warn"></a>machine-local-health-warn | requirement | HLT-2 | not run | - | local | 2026-11-13 |
| <a id="t-config-holds-topics"></a>config-holds-topics | requirement | HLT-2 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-workers-setting-listed"></a>workers-setting-listed | defect | [#4040](https://github.com/jcl2018/agent-workflow-template/issues/4040) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-roadmap-page-passes-check"></a>roadmap-page-passes-check | requirement | HLT-2 | not run | - | local | 2026-11-15 |
| <a id="t-docs-release-scripts-under-19000"></a>docs-release-scripts-under-19000 | requirement | HLT-2 | not run | - | local | 2026-11-20 |
| <a id="t-lean-reads-commands-sheet"></a>lean-reads-commands-sheet | requirement | HLT-2 | not run | - | local | 2026-11-15 |
| <a id="t-sweep-health-record"></a>sweep-health-record | requirement | HLT-4 | not run | - | local | 2026-11-15 |
| <a id="t-file-close-no-crash"></a>file-close-no-crash | requirement | HLT-4 | not run | - | local | 2026-11-15 |
| <a id="t-defect-4379-health-key-posix"></a>defect-4379-health-key-posix | defect | [#4379](https://github.com/jcl2018/agent-workflow-template/issues/4379) closed (2026-11-15) | not run | - | local | 2026-11-15 |
| <a id="t-rowtail-block-in-workflow"></a>rowtail-block-in-workflow | requirement | HLT-4 | not run | - | local | 2026-11-15 |
| <a id="t-machine-health-rule"></a>machine-health-rule | requirement | HLT-2 | not run | - | local | 2026-11-16 |
| <a id="t-test-caps-health"></a>test-caps-health | requirement | HLT-2 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-test-caps-controls"></a>test-caps-controls | requirement | HLT-2 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-eta-health-rules"></a>eta-health-rules | requirement | HLT-2 | not run | - | local | 2026-11-16 |
| <a id="t-size-warn-band"></a>size-warn-band | requirement | HLT-2 | not run | - | local | 2026-11-16 |
| <a id="t-trim-monitoring-4-size"></a>trim-monitoring-4-size | requirement | HLT-2 | not run | - | local | 2026-11-16 |
| <a id="t-judge-key-savings"></a>judge-key-savings | requirement | HLT-4 | not run | - | local | 2026-11-16 |
| <a id="t-health-findings-table"></a>health-findings-table | requirement | HLT-2 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |
| <a id="t-health-feature-always"></a>health-feature-always | requirement | HLT-4 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |

## Machines

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-del8-floor-step"></a>del8-floor-step | requirement | MCH-1 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-12 |
| <a id="t-del8-prep-board"></a>del8-prep-board | requirement | MCH-1 | not run | - | local | 2026-11-11 |
| <a id="t-del7-kill-resume"></a>del7-kill-resume | requirement | MCH-1 | not run | - | local | 2026-11-13 |
| <a id="t-del8-board-over"></a>del8-board-over | requirement | MCH-1 | not run | - | local | 2026-11-12 |
| <a id="t-mon15-pod-owner"></a>mon15-pod-owner | requirement | MCH-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-stop-takes-tree"></a>stop-takes-tree | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-machine-apply-installs"></a>machine-apply-installs | requirement | MCH-1 | not run | - | local | 2026-11-12 |
| <a id="t-machine-task-layout"></a>machine-task-layout | requirement | MCH-1 | PASS 2026-11-17 FLAKY | - | local | 2026-11-17 |
| <a id="t-adopt-record-qa"></a>adopt-record-qa | requirement | MCH-1 | PASS 2026-11-16 FLAKY | - | local | 2026-11-12 |
| <a id="t-resume-ask-prompt"></a>resume-ask-prompt | requirement | MCH-1 | not run | - | local | 2026-11-13 |
| <a id="t-tokens-unread-shown"></a>tokens-unread-shown | requirement | MCH-1 | not run | - | local | 2026-11-13 |
| <a id="t-grd2-time-stop"></a>grd2-time-stop | requirement | MCH-1 | not run | - | local | 2026-11-15 |
| <a id="t-grd2-limits-in-settings"></a>grd2-limits-in-settings | requirement | MCH-1 | not run | - | local | 2026-11-13 |
| <a id="t-pr-queue-order"></a>pr-queue-order | requirement | MCH-1 | not run | - | local | 2026-11-13 |
| <a id="t-pr-parallel-disjoint"></a>pr-parallel-disjoint | requirement | MCH-1 | not run | - | local | 2026-11-13 |
| <a id="t-pr-order-one-queue"></a>pr-order-one-queue | defect | [#3922](https://github.com/jcl2018/agent-workflow-template/issues/3922) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-held-time-over-still-stops"></a>held-time-over-still-stops | requirement | MCH-1 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-held-time-3878"></a>held-time-3878 | defect | [#3878](https://github.com/jcl2018/agent-workflow-template/issues/3878) closed (2026-11-15) | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-windows-safe-posix-names"></a>windows-safe-posix-names | requirement | MCH-1 | not run | - | local | 2026-11-14 |
| <a id="t-prd-no-dunder-import-3800"></a>prd-no-dunder-import-3800 | defect | [#3800](https://github.com/jcl2018/agent-workflow-template/issues/3800) closed (2026-11-15) | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-14 |
| <a id="t-adopt-prerequisites"></a>adopt-prerequisites | requirement | MCH-1 | not run | - | local | 2026-11-15 |
| <a id="t-grd2-pr-lane-holds-merge-slot"></a>grd2-pr-lane-holds-merge-slot | requirement | MCH-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-queue-merged-free-4343"></a>queue-merged-free-4343 | requirement | MCH-1 | not run | - | local | 2026-11-15 |
| <a id="t-test-caps-qa-refused"></a>test-caps-qa-refused | requirement | MCH-1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-eta-budget-raise"></a>eta-budget-raise | requirement | MCH-1 | not run | - | local | 2026-11-16 |
| <a id="t-held-charge-idle"></a>held-charge-idle | requirement | MCH-1 | not run | - | local | 2026-11-16 |
| <a id="t-machines-handover"></a>machines-handover | requirement | MCH-1 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-machines-handover-4787"></a>machines-handover-4787 | defect | [#4787](https://github.com/jcl2018/agent-workflow-template/issues/4787) closed (2026-11-18) | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-routing-timeout-tree"></a>routing-timeout-tree | requirement | MCH-1 | not run | - | local | 2026-11-18 |
| <a id="t-restart-tick-agent"></a>restart-tick-agent | requirement | MCH-1 | not run | - | local | 2026-11-20 |

## Operation

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-dependency-held"></a>dependency-held | requirement | OPS-1 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-no-line-in-governor"></a>no-line-in-governor | requirement | OPS-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-13 |
| <a id="t-failed-waits-mender"></a>failed-waits-mender | requirement | OPS-1 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-worker-refuses"></a>worker-refuses | requirement | OPS-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-one-way-to-run"></a>one-way-to-run | requirement | OPS-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-operate-all"></a>operate-all | requirement | OPS-1 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-09 |
| <a id="t-worker-reports-live"></a>worker-reports-live | requirement | OPS-1 | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-08 |
| <a id="t-session-assign"></a>session-assign | requirement | OPS-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-09 |
| <a id="t-session-board-issue98"></a>session-board-issue98 | defect | [#98](https://github.com/jcl2018/agent-workflow-template/issues/98) closed (2026-11-09) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-report-done-final"></a>report-done-final | defect | [#108](https://github.com/jcl2018/agent-workflow-template/issues/108) closed (2026-11-10) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-guards-resume"></a>guards-resume | defect | [#149](https://github.com/jcl2018/agent-workflow-template/issues/149) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-guards-worker-role"></a>guards-worker-role | defect | [#121](https://github.com/jcl2018/agent-workflow-template/issues/121) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-guards-worktree"></a>guards-worktree | defect | [#160](https://github.com/jcl2018/agent-workflow-template/issues/160) closed (2026-11-13) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-mon6-merged-frees"></a>mon6-merged-frees | requirement | OPS-1 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-mon12-pool"></a>mon12-pool | requirement | OPS-16 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-slot-pool-112"></a>slot-pool-112 | defect | [#112](https://github.com/jcl2018/agent-workflow-template/issues/112) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-attempt-114"></a>attempt-114 | defect | [#114](https://github.com/jcl2018/agent-workflow-template/issues/114) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-pool-edges-122"></a>pool-edges-122 | defect | [#122](https://github.com/jcl2018/agent-workflow-template/issues/122) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-merged-frees-175"></a>merged-frees-175 | defect | [#175](https://github.com/jcl2018/agent-workflow-template/issues/175) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-worker-save-159"></a>worker-save-159 | defect | [#159](https://github.com/jcl2018/agent-workflow-template/issues/159) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-issue-117-bind-self"></a>issue-117-bind-self | defect | [#117](https://github.com/jcl2018/agent-workflow-template/issues/117) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-mon13-two-layers"></a>mon13-two-layers | requirement | OPS-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-guards-null-report-bind-mend"></a>guards-null-report-bind-mend | requirement | OPS-1 | not run | - | local | 2026-11-12 |
| <a id="t-stop-tree-session-tool"></a>stop-tree-session-tool | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | not run | - | local | 2026-11-12 |
| <a id="t-set13-hooks-once"></a>set13-hooks-once | defect | [#2880](https://github.com/jcl2018/agent-workflow-template/issues/2880) closed (2026-11-12) | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-13 |
| <a id="t-mon8-silent-worker"></a>mon8-silent-worker | requirement | OPS-1 | not run | - | local | 2026-11-15 |
| <a id="t-operation-checkout-ff"></a>operation-checkout-ff | requirement | OPS-1 | not run | - | local | 2026-11-13 |
| <a id="t-who-merges-report"></a>who-merges-report | defect | [#3868](https://github.com/jcl2018/agent-workflow-template/issues/3868) closed (2026-11-13) | not run | - | local | 2026-11-13 |
| <a id="t-operate-toy-no-check"></a>operate-toy-no-check | defect | [#3906](https://github.com/jcl2018/agent-workflow-template/issues/3906) closed (2026-11-13) | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-13 |
| <a id="t-unattended-sends-warn"></a>unattended-sends-warn | requirement | OPS-1 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-14 |
| <a id="t-blockers-first"></a>blockers-first | requirement | OPS-1 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-go-app-holds-goal"></a>go-app-holds-goal | defect | [#4040](https://github.com/jcl2018/agent-workflow-template/issues/4040) closed (2026-11-14) | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-14 |
| <a id="t-runs-skips-non-dict"></a>runs-skips-non-dict | defect | [#4040](https://github.com/jcl2018/agent-workflow-template/issues/4040) closed (2026-11-14) | not run | - | local | 2026-11-14 |
| <a id="t-app-refuses-headless-4184"></a>app-refuses-headless-4184 | defect | [#4184](https://github.com/jcl2018/agent-workflow-template/issues/4184) closed (2026-11-14) | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-new-binds-app-session-4257"></a>new-binds-app-session-4257 | defect | [#4257](https://github.com/jcl2018/agent-workflow-template/issues/4257) closed (2026-11-15) | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-14 |
| <a id="t-scripts-a-monitoring-under-19000"></a>scripts-a-monitoring-under-19000 | requirement | OPS-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-20 |
| <a id="t-config-memory-key-once"></a>config-memory-key-once | requirement | OPS-16 | not run | - | local | 2026-11-15 |
| <a id="t-set13-hooks-once-bullet"></a>set13-hooks-once-bullet | requirement | OPS-16 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-15 |
| <a id="t-mon16-machine-line"></a>mon16-machine-line | requirement | OPS-16 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-15 |
| <a id="t-defect-4375-toys-fake-machine"></a>defect-4375-toys-fake-machine | defect | [#4375](https://github.com/jcl2018/agent-workflow-template/issues/4375) closed (2026-11-15) | not run | - | local | 2026-11-15 |
| <a id="t-mon16-checkin-grouped"></a>mon16-checkin-grouped | requirement | OPS-16 | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-18 |
| <a id="t-ops-findings-filed"></a>ops-findings-filed | requirement | OPS-1 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-19 |
| <a id="t-platform-sends-counted"></a>platform-sends-counted | requirement | OPS-1 | not run | - | local | 2026-11-20 |
| <a id="t-machine-status-live-workers"></a>machine-status-live-workers | requirement | OPS-1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-20 |

## Regression

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-unproven-blocks"></a>unproven-blocks | requirement | REG-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-12 |
| <a id="t-one-link"></a>one-link | requirement | REG-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-07 |
| <a id="t-refused-unmet"></a>refused-unmet | requirement | REG-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-10 |
| <a id="t-milestones-once"></a>milestones-once | requirement | REG-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-12 |
| <a id="t-every-row-described"></a>every-row-described | requirement | REG-4 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-10 |
| <a id="t-untested-listed"></a>untested-listed | requirement | REG-4 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-08 |
| <a id="t-defect-categories"></a>defect-categories | requirement | REG-4 | FAIL | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-08 |
| <a id="t-lanes-reuse"></a>lanes-reuse | requirement | REG-4 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-lanes-pr-affected"></a>lanes-pr-affected | requirement | REG-4 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-prd-scenarios"></a>prd-scenarios | requirement | REG-4 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-09 |
| <a id="t-prd-readers"></a>prd-readers | requirement | REG-4 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-toy-no-leftovers"></a>toy-no-leftovers | defect | [#100](https://github.com/jcl2018/agent-workflow-template/issues/100) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-lanes-headers"></a>lanes-headers | requirement | REG-4 | FAIL | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-12 |
| <a id="t-lanes-declared"></a>lanes-declared | requirement | REG-4 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-11 |
| <a id="t-lanes-trace-check"></a>lanes-trace-check | requirement | REG-4 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-lanes-trace"></a>lanes-trace | requirement | REG-4 | FAIL | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-summary-only-real-rows"></a>summary-only-real-rows | defect | [#92](https://github.com/jcl2018/agent-workflow-template/issues/92) closed (2026-11-10) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-reg2-wording"></a>reg2-wording | requirement | REG-4 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-18 |
| <a id="t-local-row-env"></a>local-row-env | requirement | REG-4 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-10 |
| <a id="t-tests-page-stale"></a>tests-page-stale | requirement | REG-4 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-10 |
| <a id="t-runs-sha"></a>runs-sha | requirement | REG-4 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-reg-same-env"></a>reg-same-env | requirement | REG-4 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-docs-milestone-line-issue-130"></a>docs-milestone-line-issue-130 | defect | [#130](https://github.com/jcl2018/agent-workflow-template/issues/130) closed (2026-11-11) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-10 |
| <a id="t-tiers-unmapped-qa-pr"></a>tiers-unmapped-qa-pr | requirement | REG-4 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-11 |
| <a id="t-workflow-goal-to-release"></a>workflow-goal-to-release | workflow | REG-4: Every requirement has its tests, written and run one way, with honest results | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-workflow-kind-shown"></a>workflow-kind-shown | requirement | REG-4 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-defect-owed-branch-proved"></a>defect-owed-branch-proved | requirement | REG-4 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-flaky-marked"></a>flaky-marked | requirement | REG-4 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-ci-target-input"></a>ci-target-input | requirement | REG-4 | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-merge-guard-base-head"></a>merge-guard-base-head | requirement | REG-4 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-release-lists-fixes"></a>release-lists-fixes | requirement | REG-4 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-11 |
| <a id="t-reopened-shows-failing"></a>reopened-shows-failing | requirement | REG-4 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-lane-ports-tmpdir"></a>lane-ports-tmpdir | requirement | REG-4 | PASS 2026-11-16 FLAKY | - | local | 2026-11-11 |
| <a id="t-lane-messages-table"></a>lane-messages-table | requirement | REG-4 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-merge-reach-fail-closed"></a>merge-reach-fail-closed | requirement | REG-4 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-goal-levels-nightly"></a>goal-levels-nightly | requirement | REG-4 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-lane-tmpdir-outside-repo"></a>lane-tmpdir-outside-repo | requirement | REG-4 | not run | - | local | 2026-11-11 |
| <a id="t-port-base-windows"></a>port-base-windows | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | not run | - | local | 2026-11-12 |
| <a id="t-lanes-abs-not-walked"></a>lanes-abs-not-walked | requirement | REG-4 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-12 |
| <a id="t-reg10-owed-waits"></a>reg10-owed-waits | requirement | REG-4 | not run | - | local | 2026-11-13 |
| <a id="t-backlog-renames-old"></a>backlog-renames-old | requirement | REG-4 | not run | - | local | 2026-11-13 |
| <a id="t-mac-rows-skip-77"></a>mac-rows-skip-77 | requirement | REG-4 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-13 |
| <a id="t-machine-local-owed"></a>machine-local-owed | requirement | REG-4 | not run | - | local | 2026-11-13 |
| <a id="t-list-link-ids"></a>list-link-ids | requirement | REG-4 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-13 |
| <a id="t-tests-own-folder"></a>tests-own-folder | requirement | REG-4 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-13 |
| <a id="t-skill-workflow-in-references"></a>skill-workflow-in-references | requirement | REG-4 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-tests-links-workflow-3839"></a>tests-links-workflow-3839 | defect | [#3839](https://github.com/jcl2018/agent-workflow-template/issues/3839) closed (2026-11-14) | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-lane-fail-text"></a>lane-fail-text | defect | 3911 | not run | - | local | 2026-11-15 |
| <a id="t-owed-close"></a>owed-close | defect | 3907 | not run | - | local | 2026-11-15 |
| <a id="t-scripts-c-regression-under-19000"></a>scripts-c-regression-under-19000 | requirement | REG-4 | not run | - | local | 2026-11-20 |
| <a id="t-prd-copy-rows-list"></a>prd-copy-rows-list | requirement | REG-4 | not run | - | local | 2026-11-15 |
| <a id="t-toys-set-userprofile"></a>toys-set-userprofile | defect | [#4393](https://github.com/jcl2018/agent-workflow-template/issues/4393) closed (2026-11-15) | not run | - | local | 2026-11-15 |
| <a id="t-config-lane-duplicate-key"></a>config-lane-duplicate-key | requirement | REG-4 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-private-checks-classify"></a>private-checks-classify | requirement | REG-4 | not run | - | local | 2026-11-16 |
| <a id="t-toys-no-leak-schedule"></a>toys-no-leak-schedule | requirement | REG-4 | not run | - | local | 2026-11-17 |
| <a id="t-toys-no-leak-lane-pool"></a>toys-no-leak-lane-pool | requirement | REG-4 | not run | - | local | 2026-11-17 |
| <a id="t-budget-order-first"></a>budget-order-first | requirement | REG-4 | not run | - | local | 2026-11-20 |

## Setup

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-settings-reference"></a>settings-reference | requirement | SET-2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-adopt-set-1"></a>adopt-set-1 | requirement | SET-1 | FAIL | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-adopt-set-3"></a>adopt-set-3 | requirement | SET-10 | FAIL | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-08 |
| <a id="t-adopt-set-4"></a>adopt-set-4 | requirement | SET-1 | FAIL | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-adopt-set-5"></a>adopt-set-5 | requirement | SET-2 | FAIL | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-08 |
| <a id="t-setup-both-halves"></a>setup-both-halves | requirement | SET-1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-skill-size-116"></a>skill-size-116 | defect | [#116](https://github.com/jcl2018/agent-workflow-template/issues/116) closed (2026-11-10) | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-09 |
| <a id="t-skill-kept"></a>skill-kept | requirement | SET-10 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-13 |
| <a id="t-depth-setup"></a>depth-setup | requirement | SET-2 | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-migration-clean"></a>migration-clean | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-migration-base-config"></a>migration-base-config | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-migration-robustness"></a>migration-robustness | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-sync-check-preview"></a>sync-check-preview | requirement | SET-1 | not run | - | local | 2026-11-10 |
| <a id="t-sync-default-source"></a>sync-default-source | requirement | SET-1 | SKIPPED | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-10 |
| <a id="t-entry-stale"></a>entry-stale | requirement | SET-2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-entry-adopt"></a>entry-adopt | requirement | SET-2 | SKIPPED | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-10 |
| <a id="t-agents-wire"></a>agents-wire | requirement | SET-10 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-size-139"></a>size-139 | defect | [#139](https://github.com/jcl2018/agent-workflow-template/issues/139) closed (2026-11-19) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-size-140"></a>size-140 | defect | [#140](https://github.com/jcl2018/agent-workflow-template/issues/140) closed (2026-11-19) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-size-141"></a>size-141 | defect | [#141](https://github.com/jcl2018/agent-workflow-template/issues/141) closed (2026-11-19) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-11 |
| <a id="t-codex-ro-home"></a>codex-ro-home | requirement | SET-10 | not run | - | local | 2026-11-12 |
| <a id="t-codex-key-commands"></a>codex-key-commands | defect | [#38](https://github.com/jcl2018/agent-workflow-template/issues/38) closed (2026-11-11) | not run | - | local | 2026-11-12 |
| <a id="t-set1-health-bracket"></a>set1-health-bracket | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-set1-docs-format"></a>set1-docs-format | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-set2-layers-show"></a>set2-layers-show | requirement | SET-2 | not run | - | local | 2026-11-12 |
| <a id="t-adopt-fixture-existing-checks"></a>adopt-fixture-existing-checks | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-setup-fit"></a>setup-fit | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-set9-from-no-values"></a>set9-from-no-values | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-setup-zero-tests-119"></a>setup-zero-tests-119 | defect | [#119](https://github.com/jcl2018/agent-workflow-template/issues/119) closed (2026-11-13) | not run | - | local | 2026-11-12 |
| <a id="t-setup-tsv-guard-127"></a>setup-tsv-guard-127 | defect | [#127](https://github.com/jcl2018/agent-workflow-template/issues/127) closed (2026-11-13) | not run | - | local | 2026-11-12 |
| <a id="t-adoption-golden"></a>adoption-golden | requirement | SET-1 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-12 |
| <a id="t-grd10-install-hooks"></a>grd10-install-hooks | requirement | SET-1 | not run | - | local | 2026-11-12 |
| <a id="t-package-gate-head"></a>package-gate-head | requirement | SET-10 | FAIL | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-20 |
| <a id="t-migration-v1"></a>migration-v1 | requirement | SET-1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-13 |
| <a id="t-repo-rules-threshold"></a>repo-rules-threshold | requirement | SET-2 | not run | - | local | 2026-11-13 |
| <a id="t-repo-rules-setup"></a>repo-rules-setup | requirement | SET-1 | not run | - | local | 2026-11-13 |
| <a id="t-matrix-health-rule"></a>matrix-health-rule | requirement | SET-1 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-13 |
| <a id="t-package-headroom-held"></a>package-headroom-held | requirement | SET-10 | FAIL | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-13 |
| <a id="t-package-rows-tracked"></a>package-rows-tracked | requirement | SET-10 | FAIL | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-13 |
| <a id="t-topics-in-reference"></a>topics-in-reference | requirement | SET-2 | PASS | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-16 |
| <a id="t-package-passes-3800"></a>package-passes-3800 | defect | [#3800](https://github.com/jcl2018/agent-workflow-template/issues/3800) closed (2026-11-15) | not run | - | local | 2026-11-20 |
| <a id="t-pr-statuses-only-lane-3840"></a>pr-statuses-only-lane-3840 | defect | [#3840](https://github.com/jcl2018/agent-workflow-template/issues/3840) closed (2026-11-14) | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-14 |
| <a id="t-migration-runs"></a>migration-runs | defect | 3821 | not run | - | local | 2026-11-15 |
| <a id="t-adopt-stamps-version"></a>adopt-stamps-version | requirement | SET-1 | not run | - | local | 2026-11-15 |
| <a id="t-setup-owner-words-up-front"></a>setup-owner-words-up-front | requirement | SET-1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-15 |
| <a id="t-review-hold-setting-listed"></a>review-hold-setting-listed | requirement | SET-2 | not run | - | local | 2026-11-15 |
| <a id="t-test-caps-settings"></a>test-caps-settings | requirement | SET-1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-private-checks-run-local"></a>private-checks-run-local | requirement | SET-1 | not run | - | local | 2026-11-16 |
| <a id="t-agent-routing"></a>agent-routing | workflow | SET-10: One versioned package; every agent runs one loop | not run | - | local | 2026-11-20 |

## Other

| Test | Kind | Guards | Result | Date | Run | Seen failing |
|---|---|---|---|---|---|---|
| <a id="t-one-failure"></a>one-failure | requirement | - | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-breaking-asks"></a>breaking-asks | requirement | - | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-12 |
| <a id="t-landed-left-alone"></a>landed-left-alone | requirement | - | PASS | 2026-11-09 | [CI 2026-11-09](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-09) | 2026-11-07 |
| <a id="t-defect-wording"></a>defect-wording | requirement | - | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-08 |
| <a id="t-stale-groups-defect"></a>stale-groups-defect | defect | [#89](https://github.com/jcl2018/agent-workflow-template/issues/89) closed (2026-11-09) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-09 |
| <a id="t-board-estimates-overrun"></a>board-estimates-overrun | defect | [#93](https://github.com/jcl2018/agent-workflow-template/issues/93) closed (2026-11-11) | PASS | 2026-11-10 | [60def83](https://github.com/Charlie-org146/agent-workflow-template/commit/60def83dfbc8727d0307a13b77f5aad43479da6a) | 2026-11-09 |
| <a id="t-ls-plist"></a>ls-plist | requirement | done line local-schedule:1 | FAIL | 2026-11-13 | [CI 2026-11-13](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-13) | 2026-11-12 |
| <a id="t-ls-private-no-workflow"></a>ls-private-no-workflow | requirement | done line local-schedule:2 | not run | - | local | 2026-11-12 |
| <a id="t-ls-narrow-triggers"></a>ls-narrow-triggers | requirement | done line local-schedule:3 | not run | - | local | 2026-11-12 |
| <a id="t-ls-log-bounded"></a>ls-log-bounded | requirement | done line local-schedule:4 | not run | - | local | 2026-11-12 |
| <a id="t-ls-judge-login"></a>ls-judge-login | requirement | done line local-schedule:5 | not run | - | local | 2026-11-12 |
| <a id="t-ls-usage-steps"></a>ls-usage-steps | requirement | done line local-schedule:5 | not run | - | local | 2026-11-12 |
| <a id="t-ls-nothing-in-repo"></a>ls-nothing-in-repo | requirement | done line local-schedule:6 | not run | - | local | 2026-11-12 |
| <a id="t-ls-size-budget"></a>ls-size-budget | requirement | done line local-schedule:1 | not run | - | local | 2026-11-20 |
| <a id="t-st-public-zero"></a>st-public-zero | requirement | done line local-schedule:7 | not run | - | local | 2026-11-12 |
| <a id="t-st-union-contexts"></a>st-union-contexts | requirement | done line local-schedule:7 | not run | - | local | 2026-11-12 |
| <a id="t-st-setup-readonly"></a>st-setup-readonly | requirement | done line local-schedule:2 | not run | - | local | 2026-11-12 |
| <a id="t-two-lanes-toy-435"></a>two-lanes-toy-435 | defect | [#435](https://github.com/jcl2018/agent-workflow-template/issues/435) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-done-line-rows-128"></a>done-line-rows-128 | defect | [#128](https://github.com/jcl2018/agent-workflow-template/issues/128) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-lane-limit-150"></a>lane-limit-150 | defect | [#150](https://github.com/jcl2018/agent-workflow-template/issues/150) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-red-race-135"></a>red-race-135 | defect | [#135](https://github.com/jcl2018/agent-workflow-template/issues/135) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-lane-last-152"></a>lane-last-152 | defect | [#152](https://github.com/jcl2018/agent-workflow-template/issues/152) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-head-moved-168"></a>head-moved-168 | defect | [#168](https://github.com/jcl2018/agent-workflow-template/issues/168) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-tables-prep-151"></a>tables-prep-151 | defect | [#151](https://github.com/jcl2018/agent-workflow-template/issues/151) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-lane-control-all"></a>lane-control-all | requirement | done line lane-control:1 | not run | - | local | 2026-11-10 |
| <a id="t-operate-wait-99"></a>operate-wait-99 | defect | [#99](https://github.com/jcl2018/agent-workflow-template/issues/99) closed (2026-11-11) | not run | - | local | 2026-11-10 |
| <a id="t-operate-10-under-load"></a>operate-10-under-load | requirement | done line lane-control:6 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-done-lines-warning-143"></a>done-lines-warning-143 | defect | [#143](https://github.com/jcl2018/agent-workflow-template/issues/143) closed (2026-11-20) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-lanes-trace-hook-173"></a>lanes-trace-hook-173 | defect | [#173](https://github.com/jcl2018/agent-workflow-template/issues/173) closed (2026-11-14) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-narrow-root-172"></a>narrow-root-172 | defect | [#172](https://github.com/jcl2018/agent-workflow-template/issues/172) closed (2026-11-11) | PASS | 2026-11-10 | [CI 2026-11-10](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-10) | 2026-11-10 |
| <a id="t-repo-narrow-178"></a>repo-narrow-178 | defect | [#178](https://github.com/jcl2018/agent-workflow-template/issues/178) closed (2026-11-12) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-10 |
| <a id="t-size-budget"></a>size-budget | requirement | done line lane-control:7 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-row-timeout-holds"></a>row-timeout-holds | requirement | done line lane-control:2 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-lane-start-mark-once"></a>lane-start-mark-once | requirement | done line lane-control:3 | PASS | 2026-11-11 | [CI 2026-11-11](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-11) | 2026-11-11 |
| <a id="t-pr-commit-scope"></a>pr-commit-scope | requirement | done line lane-control:5 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-11 |
| <a id="t-no-milestone-issue-ok"></a>no-milestone-issue-ok | requirement | done line milestone-freeform:2 | not run | - | local | 2026-11-12 |
| <a id="t-no-milestone-page-ok"></a>no-milestone-page-ok | requirement | done line milestone-freeform:2 | not run | - | local | 2026-11-12 |
| <a id="t-home-milestone-optional"></a>home-milestone-optional | requirement | done line milestone-freeform:2 | not run | - | local | 2026-11-12 |
| <a id="t-pr-no-milestone"></a>pr-no-milestone | requirement | done line milestone-freeform:2 | not run | - | local | 2026-11-12 |
| <a id="t-regression-issue-no-milestone"></a>regression-issue-no-milestone | requirement | done line milestone-freeform:2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-digest-no-milestone"></a>digest-no-milestone | requirement | done line milestone-freeform:2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-setup-no-milestone-step"></a>setup-no-milestone-step | requirement | done line milestone-freeform:2 | not run | - | local | 2026-11-12 |
| <a id="t-milestone-v1-free-form"></a>milestone-v1-free-form | requirement | done line milestone-freeform:3 | not run | - | local | 2026-11-12 |
| <a id="t-milestone-wording-unreviewed"></a>milestone-wording-unreviewed | requirement | done line milestone-freeform:1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-milestone-rows-seen-red"></a>milestone-rows-seen-red | requirement | done line milestone-freeform:4 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-worker-push-guard-refuse"></a>worker-push-guard-refuse | requirement | done line worker-push-guard:1 | not run | - | local | 2026-11-12 |
| <a id="t-worker-push-guard-allow"></a>worker-push-guard-allow | requirement | done line worker-push-guard:3 | not run | - | local | 2026-11-12 |
| <a id="t-worker-push-guard-unaffected"></a>worker-push-guard-unaffected | requirement | done line worker-push-guard:2 | not run | - | local | 2026-11-12 |
| <a id="t-pods-docs"></a>pods-docs | requirement | done line pods:1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-pods-owner"></a>pods-owner | requirement | done line pods:2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-pods-lock"></a>pods-lock | requirement | done line pods:3 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-pods-independent"></a>pods-independent | requirement | done line pods:4 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-pods-blocks"></a>pods-blocks | requirement | done line pods:5 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-pods-size"></a>pods-size | requirement | done line pods:6 | not run | - | local | 2026-11-12 |
| <a id="t-setup-refusal-writes-120"></a>setup-refusal-writes-120 | defect | [#120](https://github.com/jcl2018/agent-workflow-template/issues/120); [#4858](https://github.com/jcl2018/agent-workflow-template/issues/4858); [#4683](https://github.com/jcl2018/agent-workflow-template/issues/4683); [#4772](https://github.com/jcl2018/agent-workflow-template/issues/4772) | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-guards-null-report-reset"></a>guards-null-report-reset | requirement | done line guards-null-report:1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-guards-null-report-writers"></a>guards-null-report-writers | requirement | done line guards-null-report:2 | not run | - | local | 2026-11-12 |
| <a id="t-guards-null-report-nofiles"></a>guards-null-report-nofiles | requirement | done line guards-null-report:3 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-settings-default-row"></a>settings-default-row | requirement | done line settings-table:1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-settings-template-line"></a>settings-template-line | requirement | done line settings-table:2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-settings-refresh"></a>settings-refresh | requirement | done line settings-table:3 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-settings-entry"></a>settings-entry | requirement | done line settings-table:4 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-automation-missing-workflow"></a>automation-missing-workflow | requirement | done line settings-table:5 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-plan-calls-flat"></a>plan-calls-flat | defect | [#710](https://github.com/jcl2018/agent-workflow-template/issues/710) closed (2026-11-11) | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-plan-identity"></a>plan-identity | requirement | done line lane-plan-cache:2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-plan-sizes"></a>plan-sizes | requirement | done line lane-plan-cache:5 | not run | - | local | 2026-11-20 |
| <a id="t-plan-cache-key"></a>plan-cache-key | requirement | done line lane-plan-cache:3 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-plan-seconds-nightly"></a>plan-seconds-nightly | requirement | done line lane-plan-cache:1 | not run | - | local | 2026-11-12 |
| <a id="t-pending-none-goes-on"></a>pending-none-goes-on | requirement | done line pending-none:1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-pending-real-waits"></a>pending-real-waits | requirement | done line pending-none:2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-package-win-parity-1397"></a>package-win-parity-1397 | defect | [#1397](https://github.com/jcl2018/agent-workflow-template/issues/1397) closed (2026-11-12) | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-12 |
| <a id="t-package-win-stdin-1397"></a>package-win-stdin-1397 | defect | [#1397](https://github.com/jcl2018/agent-workflow-template/issues/1397) closed (2026-11-12) | not run | - | local | 2026-11-12 |
| <a id="t-package-hang-stdin"></a>package-hang-stdin | requirement | done line package-hang:1 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-package-hang-bound"></a>package-hang-bound | requirement | done line package-hang:2 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-package-hang-slot"></a>package-hang-slot | requirement | done line package-hang:3 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-package-hang-no-skills-file"></a>package-hang-no-skills-file | requirement | done line package-hang:4 | PASS | 2026-11-12 | [CI 2026-11-12](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-12) | 2026-11-12 |
| <a id="t-est-time-order-selector"></a>est-time-order-selector | requirement | done line estimate-timeorder:3 | not run | - | local | 2026-11-12 |
| <a id="t-est-time-order-board"></a>est-time-order-board | requirement | done line estimate-timeorder:1 | not run | - | local | 2026-11-12 |
| <a id="t-est-loo-diagnostic"></a>est-loo-diagnostic | requirement | done line estimate-timeorder:2 | not run | - | local | 2026-11-12 |
| <a id="t-deployments-counts-pages"></a>deployments-counts-pages | requirement | done line docs-small-fixes:1 | not run | - | local | 2026-11-12 |
| <a id="t-readme-commands-in-command-map"></a>readme-commands-in-command-map | requirement | done line docs-small-fixes:2 | not run | - | local | 2026-11-12 |
| <a id="t-portlock-fallback"></a>portlock-fallback | requirement | done line package-cap-3:3 | not run | - | local | 2026-11-12 |
| <a id="t-package-passes"></a>package-passes | requirement | done line package-cap-3:1 | SKIPPED | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-12 |
| <a id="t-lane-stale-pid-safe"></a>lane-stale-pid-safe | requirement | done line lane-died:1 | not run | - | local | 2026-11-12 |
| <a id="t-lane-died-signal"></a>lane-died-signal | requirement | done line lane-died:2 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-3"></a>machine-done-3 | requirement | done line operator-setup:3 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-4"></a>machine-done-4 | requirement | done line operator-setup:4 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-5"></a>machine-done-5 | requirement | done line operator-setup:5 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-12 |
| <a id="t-machine-done-6"></a>machine-done-6 | requirement | done line operator-setup:6 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-7"></a>machine-done-7 | requirement | done line operator-setup:7 | PASS 2026-11-17 FLAKY | - | local | 2026-11-12 |
| <a id="t-machine-done-8"></a>machine-done-8 | requirement | done line operator-setup:8 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-9"></a>machine-done-9 | requirement | done line operator-setup:9 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-10"></a>machine-done-10 | requirement | done line operator-setup:10 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-11"></a>machine-done-11 | requirement | done line operator-setup:11 | not run | - | local | 2026-11-12 |
| <a id="t-machine-done-12"></a>machine-done-12 | requirement | done line operator-setup:12 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-12 |
| <a id="t-review-findings-wording"></a>review-findings-wording | requirement | done line review-findings:1 | not run | - | local | 2026-11-12 |
| <a id="t-review-findings-skill-lines"></a>review-findings-skill-lines | requirement | done line review-findings:2 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-13 |
| <a id="t-size-lf-crlf"></a>size-lf-crlf | defect | [#3125](https://github.com/jcl2018/agent-workflow-template/issues/3125) closed (2026-11-13) | not run | - | local | 2026-11-12 |
| <a id="t-findings-one-per-lesson"></a>findings-one-per-lesson | workflow | done line migration-lessons:1 | not run | - | local | 2026-11-12 |
| <a id="t-win-posix-calls-gone"></a>win-posix-calls-gone | requirement | done line win-posix-rest:1 | PASS | 2026-11-15 | [CI 2026-11-15](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-15) | 2026-11-12 |
| <a id="t-body-file-windows"></a>body-file-windows | defect | [#2879](https://github.com/jcl2018/agent-workflow-template/issues/2879) closed (2026-11-12) | not run | - | local | 2026-11-12 |
| <a id="t-docs-block-split"></a>docs-block-split | defect | [#1402](https://github.com/jcl2018/agent-workflow-template/issues/1402) closed (2026-11-19) | FAIL | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-20 |
| <a id="t-settings-render-tables"></a>settings-render-tables | requirement | done line settings-render-windows:1 | not run | - | local | 2026-11-12 |
| <a id="t-settings-render-fresh"></a>settings-render-fresh | requirement | done line settings-render-windows:1 | FAIL | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-13 |
| <a id="t-health-listing-filtered"></a>health-listing-filtered | defect | [#1402](https://github.com/jcl2018/agent-workflow-template/issues/1402) closed (2026-11-19) | not run | - | local | 2026-11-12 |
| <a id="t-migration-fix-sched-task"></a>migration-fix-sched-task | defect | [#3780](https://github.com/jcl2018/agent-workflow-template/issues/3780) closed (2026-11-13) | not run | - | local | 2026-11-13 |
| <a id="t-stale-net-diff-revert"></a>stale-net-diff-revert | requirement | done line stale-net-diff:1 | not run | - | local | 2026-11-13 |
| <a id="t-no-usage-section"></a>no-usage-section | requirement | done line drop-usage:1 | not run | - | local | 2026-11-13 |
| <a id="t-pr-queue-goal"></a>pr-queue-goal | requirement | done line pr-queue:1 | not run | - | local | 2026-11-13 |
| <a id="t-machine-status-line"></a>machine-status-line | requirement | done line machine-status:1 | not run | - | local | 2026-11-13 |
| <a id="t-held-time-pr-queue"></a>held-time-pr-queue | requirement | done line held-time-budget:1 | PASS | 2026-11-14 | [CI 2026-11-14](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-14) | 2026-11-13 |
| <a id="t-pods-caps-3919"></a>pods-caps-3919 | defect | [#3919](https://github.com/jcl2018/agent-workflow-template/issues/3919) open (2026-11-15) | not run | - | local | 2026-11-14 |
| <a id="t-defect-3854-long-pr-body"></a>defect-3854-long-pr-body | defect | [#3854](https://github.com/jcl2018/agent-workflow-template/issues/3854) closed (2026-11-15) | not run | - | local | 2026-11-15 |
| <a id="t-defect-3939-lane-skips-node-modules"></a>defect-3939-lane-skips-node-modules | defect | [#3939](https://github.com/jcl2018/agent-workflow-template/issues/3939) closed (2026-11-15) | not run | - | local | 2026-11-15 |
| <a id="t-home-guard-catches-leak"></a>home-guard-catches-leak | defect | [#4393](https://github.com/jcl2018/agent-workflow-template/issues/4393); [#4901](https://github.com/jcl2018/agent-workflow-template/issues/4901); [#4896](https://github.com/jcl2018/agent-workflow-template/issues/4896); [#4865](https://github.com/jcl2018/agent-workflow-template/issues/4865) | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-machine-hook-state"></a>machine-hook-state | defect | [#4506](https://github.com/jcl2018/agent-workflow-template/issues/4506); [#4660](https://github.com/jcl2018/agent-workflow-template/issues/4660); [#4695](https://github.com/jcl2018/agent-workflow-template/issues/4695); [#4758](https://github.com/jcl2018/agent-workflow-template/issues/4758) | PASS | 2026-11-18 | [CI 2026-11-18](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-18) | 2026-11-17 |
| <a id="t-listing-names-every-command"></a>listing-names-every-command | requirement | done line package-cap-3:1 | not run | - | local | 2026-11-15 |
| <a id="t-defect-4496-checkin-goal-lines"></a>defect-4496-checkin-goal-lines | defect | [#4496](https://github.com/jcl2018/agent-workflow-template/issues/4496) closed (2026-11-15) | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-not-runnable-lane"></a>not-runnable-lane | requirement | done line qa-not-runnable:1 | not run | - | local | 2026-11-16 |
| <a id="t-not-runnable-qa"></a>not-runnable-qa | requirement | done line qa-not-runnable:2 | not run | - | local | 2026-11-16 |
| <a id="t-not-runnable-todo"></a>not-runnable-todo | requirement | done line qa-not-runnable:3 | not run | - | local | 2026-11-16 |
| <a id="t-ci-summary-fail-output"></a>ci-summary-fail-output | requirement | done line ci-fail-output:1 | not run | - | local | 2026-11-16 |
| <a id="t-ci-summary-passing-left-out"></a>ci-summary-passing-left-out | requirement | done line ci-fail-output:2 | not run | - | local | 2026-11-16 |
| <a id="t-audit-cd-path-found"></a>audit-cd-path-found | requirement | done line audit-cd-path:1 | not run | - | local | 2026-11-16 |
| <a id="t-audit-cd-path-toy"></a>audit-cd-path-toy | requirement | done line audit-cd-path:2 | not run | - | local | 2026-11-16 |
| <a id="t-ci-block-skip-file"></a>ci-block-skip-file | requirement | done line ci-fail-causes:2 | not run | - | local | 2026-11-16 |
| <a id="t-ci-groups-complete"></a>ci-groups-complete | requirement | done line ci-fail-causes:1 | not run | - | local | 2026-11-16 |
| <a id="t-done-hard-eta-1"></a>done-hard-eta-1 | workflow | done line hard-eta:1 | not run | - | local | no |
| <a id="t-done-hard-eta-2"></a>done-hard-eta-2 | workflow | done line hard-eta:2 | not run | - | local | no |
| <a id="t-done-hard-eta-3"></a>done-hard-eta-3 | workflow | done line hard-eta:3 | not run | - | local | no |
| <a id="t-pr-queue-keeps-place"></a>pr-queue-keeps-place | requirement | done line pr-queue-step:1 | not run | - | local | 2026-11-16 |
| <a id="t-pr-queue-step-toy"></a>pr-queue-step-toy | requirement | done line pr-queue-step:2 | not run | - | local | 2026-11-16 |
| <a id="t-trim-setup-under-19000"></a>trim-setup-under-19000 | requirement | done line trim-scripts-98:1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-20 |
| <a id="t-trim-package-98"></a>trim-package-98 | requirement | done line trim-scripts-98:2 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-eta-preflight-asked"></a>eta-preflight-asked | requirement | done line eta-preflight:1 | not run | - | local | 2026-11-16 |
| <a id="t-eta-preflight-missed"></a>eta-preflight-missed | requirement | done line eta-preflight:2 | not run | - | local | 2026-11-16 |
| <a id="t-done-home-stale-1"></a>done-home-stale-1 | workflow | done line home-stale:1 | not run | - | local | no |
| <a id="t-done-home-stale-2"></a>done-home-stale-2 | workflow | done line home-stale:2 | not run | - | local | no |
| <a id="t-eta-header-margin-header"></a>eta-header-margin-header | requirement | done line eta-header-margin:1 | not run | - | local | 2026-11-16 |
| <a id="t-eta-header-margin-setting"></a>eta-header-margin-setting | requirement | done line eta-header-margin:2 | not run | - | local | 2026-11-16 |
| <a id="t-done-held-time-charge-1"></a>done-held-time-charge-1 | workflow | done line held-time-charge:1 | not run | - | local | no |
| <a id="t-done-held-time-charge-2"></a>done-held-time-charge-2 | workflow | done line held-time-charge:2 | not run | - | local | no |
| <a id="t-lane-closure-slashes"></a>lane-closure-slashes | defect | [#4457](https://github.com/jcl2018/agent-workflow-template/issues/4457) closed (2026-11-16) | not run | - | local | 2026-11-16 |
| <a id="t-lane-closure-posix-same"></a>lane-closure-posix-same | defect | [#4457](https://github.com/jcl2018/agent-workflow-template/issues/4457) closed (2026-11-16) | not run | - | local | 2026-11-16 |
| <a id="t-done-judge-stable-keys-1"></a>done-judge-stable-keys-1 | workflow | done line judge-stable-keys:1 | not run | - | local | no |
| <a id="t-done-judge-stable-keys-2"></a>done-judge-stable-keys-2 | workflow | done line judge-stable-keys:2 | not run | - | local | no |
| <a id="t-done-apply-rerender-1"></a>done-apply-rerender-1 | workflow | done line apply-rerender:1 | not run | - | local | no |
| <a id="t-done-apply-rerender-2"></a>done-apply-rerender-2 | workflow | done line apply-rerender:2 | not run | - | local | no |
| <a id="t-pr-body-cap-large"></a>pr-body-cap-large | requirement | done line pr-body-cap:1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-pr-body-cap-small"></a>pr-body-cap-small | requirement | done line pr-body-cap:2 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-docs-no-plain-dunder-import"></a>docs-no-plain-dunder-import | requirement | done line docs-import-render:1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-docs-import-rows-pass"></a>docs-import-rows-pass | requirement | done line docs-import-render:2 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-hook-stub-mark-own"></a>hook-stub-mark-own | requirement | done line hook-stub-mark:1 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-16 |
| <a id="t-hook-stub-mark-foreign"></a>hook-stub-mark-foreign | requirement | done line hook-stub-mark:2 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-16 |
| <a id="t-done-toys-no-leak-1"></a>done-toys-no-leak-1 | workflow | done line toys-no-leak:1 | not run | - | local | no |
| <a id="t-done-toys-no-leak-2"></a>done-toys-no-leak-2 | workflow | done line toys-no-leak:2 | not run | - | local | no |
| <a id="t-lane-dll-init-rerun"></a>lane-dll-init-rerun | requirement | done line lane-dll-init:1 | not run | - | local | 2026-11-16 |
| <a id="t-lane-dll-init-real-fail"></a>lane-dll-init-real-fail | requirement | done line lane-dll-init:2 | not run | - | local | 2026-11-16 |
| <a id="t-settings-reference-fresh"></a>settings-reference-fresh | requirement | done line settings-ref:2 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-settings-start-fresh"></a>settings-start-fresh | requirement | done line settings-ref:1 | PASS | 2026-11-16 | [CI 2026-11-16](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-16) | 2026-11-16 |
| <a id="t-done-homeguard-skills-main-1"></a>done-homeguard-skills-main-1 | workflow | done line homeguard-skills-main:1 | not run | - | local | no |
| <a id="t-done-homeguard-skills-main-2"></a>done-homeguard-skills-main-2 | workflow | done line homeguard-skills-main:2 | not run | - | local | no |
| <a id="t-affected-deleted-root-runner"></a>affected-deleted-root-runner | defect | [#4554](https://github.com/jcl2018/agent-workflow-template/issues/4554) closed (2026-11-18) | not run | - | local | 2026-11-17 |
| <a id="t-token-diet-step-tokens"></a>token-diet-step-tokens | requirement | done line token-diet:1 | not run | - | local | 2026-11-17 |
| <a id="t-token-diet-op-rows"></a>token-diet-op-rows | requirement | done line token-diet:2 | not run | - | local | 2026-11-17 |
| <a id="t-token-diet-budget"></a>token-diet-budget | requirement | done line token-diet:3 | not run | - | local | 2026-11-17 |
| <a id="t-token-diet-quiet"></a>token-diet-quiet | requirement | done line token-diet:4 | not run | - | local | 2026-11-17 |
| <a id="t-token-diet-layout"></a>token-diet-layout | requirement | done line token-diet:5 | not run | - | local | 2026-11-17 |
| <a id="t-token-diet-output-cap"></a>token-diet-output-cap | requirement | done line token-diet:6 | not run | - | local | 2026-11-17 |
| <a id="t-checkin-nonutf8-procs-4810"></a>checkin-nonutf8-procs-4810 | defect | [#4810](https://github.com/jcl2018/agent-workflow-template/issues/4810) closed (2026-11-17) | not run | - | local | 2026-11-17 |
| <a id="t-changelog-bracket-no-gh"></a>changelog-bracket-no-gh | requirement | done line changelog-v:1 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |
| <a id="t-changelog-no-heading-gh"></a>changelog-no-heading-gh | requirement | done line changelog-v:2 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |
| <a id="t-full-auto-all-answers"></a>full-auto-all-answers | requirement | done line full-auto-all:1 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |
| <a id="t-full-auto-safety-waits"></a>full-auto-safety-waits | requirement | done line full-auto-all:2 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |
| <a id="t-full-auto-record-carried"></a>full-auto-record-carried | requirement | done line full-auto-all:3 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |
| <a id="t-full-auto-no-new-file"></a>full-auto-no-new-file | requirement | done line full-auto-all:4 | PASS | 2026-11-17 | [CI 2026-11-17](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-17) | 2026-11-17 |
| <a id="t-done-docs-v2-1"></a>done-docs-v2-1 | workflow | done line docs-v2:1 | not run | - | local | no |
| <a id="t-done-docs-v2-2"></a>done-docs-v2-2 | workflow | done line docs-v2:2 | not run | - | local | no |
| <a id="t-done-docs-v2-3"></a>done-docs-v2-3 | workflow | done line docs-v2:3 | not run | - | local | no |
| <a id="t-done-docs-v2-4"></a>done-docs-v2-4 | workflow | done line docs-v2:4 | not run | - | local | no |
| <a id="t-done-docs-v2-5"></a>done-docs-v2-5 | workflow | done line docs-v2:5 | not run | - | local | no |
| <a id="t-done-docs-v2-6"></a>done-docs-v2-6 | workflow | done line docs-v2:6 | not run | - | local | no |
| <a id="t-hands-off-fallback"></a>hands-off-fallback | requirement | done line hands-off-operation:1 | not run | - | local | 2026-11-17 |
| <a id="t-hands-off-archive"></a>hands-off-archive | requirement | done line hands-off-operation:2 | not run | - | local | 2026-11-17 |
| <a id="t-hands-off-pressure"></a>hands-off-pressure | requirement | done line hands-off-operation:3 | not run | - | local | 2026-11-17 |
| <a id="t-hands-off-start"></a>hands-off-start | requirement | done line hands-off-operation:4 | not run | - | local | 2026-11-17 |
| <a id="t-hands-off-timer"></a>hands-off-timer | requirement | done line hands-off-operation:5 | not run | - | local | 2026-11-17 |
| <a id="t-hands-off-feature"></a>hands-off-feature | requirement | done line hands-off-operation:6 | not run | - | local | 2026-11-17 |
| <a id="t-hands-off-queued"></a>hands-off-queued | requirement | done line hands-off-operation:7 | not run | - | local | 2026-11-17 |
| <a id="t-hands-off-size"></a>hands-off-size | requirement | done line hands-off-operation:8 | not run | - | local | 2026-11-17 |
| <a id="t-auto-planning"></a>auto-planning | requirement | done line auto-planning:1 | not run | - | local | 2026-11-17 |
| <a id="t-auto-planning-approve"></a>auto-planning-approve | requirement | done line auto-planning:2 | not run | - | local | 2026-11-17 |
| <a id="t-auto-planning-machines"></a>auto-planning-machines | requirement | done line auto-planning:3 | not run | - | local | 2026-11-17 |
| <a id="t-auto-planning-started"></a>auto-planning-started | requirement | done line auto-planning:4 | not run | - | local | 2026-11-17 |
| <a id="t-auto-planning-check"></a>auto-planning-check | requirement | done line auto-planning:5 | not run | - | local | 2026-11-17 |
| <a id="t-home-sandbox-4859"></a>home-sandbox-4859 | defect | [#4859](https://github.com/jcl2018/agent-workflow-template/issues/4859) closed (2026-11-17) | not run | - | local | 2026-11-17 |
| <a id="t-done-agent-routing-1"></a>done-agent-routing-1 | workflow | done line agent-routing:1 | not run | - | local | no |
| <a id="t-del-16-on-page"></a>del-16-on-page | workflow | done line del-16:1 | PASS | 2026-11-19 | [CI 2026-11-19](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-19) | 2026-11-17 |
| <a id="t-del-16-linked"></a>del-16-linked | workflow | done line del-16:2 | not run | - | local | 2026-11-17 |
| <a id="t-gap-floor-default-3"></a>gap-floor-default-3 | requirement | done line gap-wave1-small:1 | not run | - | local | 2026-11-19 |
| <a id="t-gap-milestones-source-known"></a>gap-milestones-source-known | requirement | done line gap-wave1-small:2 | not run | - | local | 2026-11-19 |
| <a id="t-gap-token-needs-live"></a>gap-token-needs-live | requirement | done line gap-wave1-small:3 | not run | - | local | 2026-11-19 |
| <a id="t-done-gap-wave1-small-4"></a>done-gap-wave1-small-4 | workflow | done line gap-wave1-small:4 | not run | - | local | no |
| <a id="t-eta-ledger"></a>eta-ledger | requirement | done line eta-honesty:1 | not run | - | local | 2026-11-20 |
| <a id="t-eta-health"></a>eta-health | requirement | done line eta-honesty:2 | not run | - | local | 2026-11-20 |
| <a id="t-shard-balance"></a>shard-balance | requirement | done line shard-balance:3 | not run | - | local | 2026-11-20 |
| <a id="t-retired-id-exists"></a>retired-id-exists | requirement | done line retired-ids-check:1 | not run | - | local | 2026-11-20 |
| <a id="t-keep-what-this-is"></a>keep-what-this-is | requirement | done line keep-what-this-is:1 | not run | - | local | 2026-11-20 |
| <a id="t-operate-loop-under-load"></a>operate-loop-under-load | requirement | done line lane-control:6 | not run | - | local | 2026-11-20 |
| <a id="t-health-stale-checkout"></a>health-stale-checkout | requirement | done line health-guard:1 | PASS | 2026-11-20 | [CI 2026-11-20](https://github.com/Charlie-org146/agent-workflow-template/actions/workflows/regression.yml?query=created%3A2026-11-20) | 2026-11-20 |
| <a id="t-release-static-rules"></a>release-static-rules | requirement | done line fast-release-rules:1 | not run | - | local | 2026-11-20 |
| <a id="t-package-static-toy"></a>package-static-toy | requirement | done line fast-release-rules:1 | not run | - | local | 2026-11-20 |
| <a id="t-pool-reconcile-ghosts"></a>pool-reconcile-ghosts | requirement | done line pool-reconcile:1 | not run | - | local | 2026-11-20 |
| <a id="t-pool-ghost-health"></a>pool-ghost-health | requirement | done line pool-reconcile:2 | not run | - | local | 2026-11-20 |
