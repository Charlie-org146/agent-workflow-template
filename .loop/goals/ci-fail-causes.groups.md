# Cause groups for the full regression run on main (#4516, #4515)

Run 43814023230 on loop/ci-fail-causes: 858 passed, 85 failed, 13 known, 95 skipped of 1051. The 22 macOS-only rows (ls-*) that failed in the earlier runs 43807419354 and 43810611039 are fixed in this goal: the CI block now reads TOY_SKIP_FILE, so they are SKIPPED, not FAIL (row ci-block-skip-file). Every one of the 85 failing rows below is in exactly one group.

## G1: Setup, hooks and agent-permission rows (SET-*, grd*, adopt fixture) (14 rows)

Shared error: These toys set up repos, hooks and a background agent. On the CI runner the agent has no allowed tools ('agent_command [claude, -p] grants no tools', 'a background agent stops at any permission prompt'), and the hook toys fail at the SET-8 step. Likely shared cause: the runner has no claude CLI or settings; unconfirmed.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4553

Rows: `set1-never-blocks`, `setup-fit`, `setup-refusal-writes-120`, `grd10-install-hooks`, `grd3-private-commit`, `set1-no-fit-filed`, `set8-health`, `set8-hooks`, `adopt-fixture-ci-gitignore`, `set9-from-borrows`, `grd3-hooks-health`, `set7-second-run-nothing`, `lanes-trace`, `sync-apply-keeps`

## G2: Affected-lane rows: a change only to NO_EFFECT files reaches no root runner (7 rows)

Shared error: All 7 print the same failed check from one toy: a change only to NO_EFFECT files (a release's VERSION) still reaches a root runner on CI.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4554

Rows: `affected-quiet-release`, `merge-wiki-rename-refused`, `merge-reach-fail-closed`, `merge-wiki-skill-refused`, `merge-base-undiffable`, `merge-wiki-head`, `pass3-symlink-page`

## G3: LEAK: toys change the real ~/.workflow-loop on the CI runner (4 rows)

Shared error: The home-guard LEAK line: the toy added lanes/port-0 or lanes/counter.lock under the runner's real ~/.workflow-loop, i.e. it did not point HOME at a temp dir.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4555

Rows: `worker-runs-release`, `pr-body-no-checks`, `defect-owed`, `suite-time-recorded`

## G4: Cause not yet read: the toy prints only its failure count in the last 20 lines (29 rows)

Shared error: The CI block keeps the last 20 lines, and for these toys that is only the count ('N FAILED') or a passing line. The failing check printed earlier. Cause not yet read.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4556

Rows: `no-token-dry-run`, `migration-gaps-pr`, `migration-major-refused`, `operate-wait-99`, `merge-guard-base-head`, `pods-owner`, `mon15-merge-lock`, `stale-found`, `st-union-contexts`, `deploy-not-locked`, `pods-lock`, `no-token-would`, `st-post-fails`, `lane-messages-table`, `publish-refused-stale`, `auto-release`, `migration-flags`, `st-merge-wiki-head`, `deploy-doc14-reviewed`, `pods-independent`, `lane-control-all`, `deploy-section-optional`, `health-file-no-milestone`, `mon15-pod-owner`, `toy-no-leftovers`, `format-frontdoor`, `migration-writes-nothing`, `st-release-pr`, `grd5-regression-dry`

## G5: Review-depth marker rows (3 rows)

Shared error: The same PASS line is the last output: 'a full review missing a configured marker fails, and the error never shows the marker', then the row exits non-zero. Cause not yet read.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4557

Rows: `depth-on-board`, `depth-in-pr-body`, `depth-reference`

## G6: Automation, health and milestone rows (9 rows)

Shared error: Automation, health and milestone rows that fail on the CI runner; each prints its own check (defect issue, a finding's group, the Mac's local-schedule status). Cause not yet read.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4558

Rows: `aut-old-issue-relabel`, `hlt4-feature-milestones`, `aut-email-regression`, `automation-live`, `live-board-leftouts`, `milestone-rows-seen-red`, `aut-defect-issue`, `reg7-suite-time`, `health-mail-env-windows`

## G7: Single-row causes (17 rows)

Shared error: One row each, each with its own first failing line (listed below). Cause not yet read unless the line says it.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4559

Rows: `landed-left-alone`, `deployments-counts-pages`, `entry-stale`, `operate-10-under-load`, `del9-scan-sites`, `codex-ro-home`, `repo-narrow-178`, `runbook-repo`, `review-recorded-merges`, `restamp-at-merge-3867`, `stale-page-row`, `plan-cache-key`, `skill-kept`, `lanes-trace-check`, `guards-resume`, `runbook-registry`, `lane-pass-dirty`

## G8: Size rows: the 19,000-byte script cap sits above health's 90% WARN line (18,432 bytes) (2 rows)

Shared error: runs.py (18,970 bytes) and regression.py (18,860) are 92% of the 20,480 cap, and health.py is over the same line, so the size toys report them. The 19,000-byte rule keeps scripts above health's 90% WARN line (18,432), so these rows fail by design until one of the two limits moves.

Outcome: filed, https://github.com/jcl2018/agent-workflow-template/issues/4560

Rows: `no-milestone-issue-ok`, `size-141`
