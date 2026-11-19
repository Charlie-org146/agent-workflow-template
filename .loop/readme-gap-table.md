# README conformance: gap table

Built for goal `readme-conformance`. Source of truth: the consolidated README (requirements-consolidate, #5268; now README.md on main, text of tip a82f5669): 43 requirements, 228 distinct bullets (each bullet shows under up to four features; counted once here). Checked against main `d3c935a9` (v1.0.90; the passes read v1.0.87 and v1.0.88; v1.0.89 and v1.0.90 changed fit.py, narrow.py, merge.py, pageformat.py, render.py, prdcopy.py, judge.py, defects.py, commands.md and test rows only) by reading code, tests, settings and pages.

**Result:** 140 done, 61 partial, 26 missing, 1 n/a (a definition with nothing to build). 87 gaps in 21 clusters; the 4 DOC-1 bullets the consolidation left open closed with requirements-consolidate (#5268, v1.0.90); MCH-1.7 closes when gap-cheap-fixes merges; G09, G10, G12, G13 and part of G16 are goals the README already names.

This table changes no requirement text and adds no shipped file. Re-run it as a delta when the README or the code moves; requirements-consolidate (#5268) is already in.

## How the table was made

- Six read-only passes by feature (Delivery and Check-in; Operation, Automation, Integrations; Regression and Health; Guardrails; Setup, Machines, Release; Documentation) each read the code a bullet asks for. A bullet is `done` only with code (file:line) plus a test row or a page; a row that is red, known-red or `not run` on its page counts as no passing test.
- I re-checked by grep the rows I quote in the cluster list (DEL-19.1/19.2, DEL-3.4, DEL-9.3 with two mail secrets files, MCH-1.5, MCH-1.7 with five `--body` calls, DEL-1.2, DEL-7.3, AUT-1.2, GRD-5.1) and the changes below. Of the 19 rows where two passes disagreed, those decided by grep are above; the rest take the stricter reading.
- The first pass ran on README tip 1eb62f15; the first table was on fc691448. Between those two tips the README differs in: OPS-11 (a merge is no longer a safety class), OPS-16.3, CHK-1.2 (new board layout), HLT-2.20 and HLT-2.21 (plan-red-team and the hourly reviewer), OPS-1.10 to OPS-1.12 and HLT-4.9 (ops-findings), DOC-2.6 (delegated approvals). Those rows were re-audited by hand here.
- The README moved while I worked: fc691448 (first audit), a82f5669, then merged to main in #5268 (v1.0.90; main's README is a82f5669's text, no later change). The table is on main v1.0.90. The delta is small: the steward-merge safety class is now named in DEL-3.2, CHK-1.2 names a frozen board template, two planned bullets were added (DEL-1.9, REL-13.5) and a few tags and wordings changed. The commit 2f27d9ea that operation-top named is not on origin; if it differs from a82f5669, re-run as a delta.
- A pass could not run toys on Windows (one hit a temp-folder PermissionError); for rows without a run record it read the toy the row runs. Pages show 'not run' for most land rows: that is a missing run record, not a red row.

## What the consolidation PR (#5268, merged in v1.0.90) closed

- DOC-1.3, DOC-1.8, DOC-1.9, DOC-1.12: the two-part README and Home, the Flow-link and requirement-coverage checks (`pageformat.py` HEAD1/HEAD2, `frontdoor`) were on the branch only and are now on main (checked on the merged tree: DOCS OK).
- The eight-versus-six principles mismatch (HLT-2.4, the README principle list read by `pageformat.py`): `commands.md` is six on main. The Attention group (principle 6) still reads UNREAD afterwards: that stays HLT-2.3.
- OPS-11 wording (a merge is not a safety class; caps are operation-top's): the README now matches main's Operation page. The code still has the steward-merge class: DEL-3.2 in G05.
- MCH-1.7 (five command-line `--body` calls) is in flight in goal `gap-cheap-fixes` (PC); it stays partial here until that merges.
- DOC-1.17 (an adopter's README shows the template principles) is NOT closed: the branch checks only where a repo ships the principle list.

## Gap clusters (each could be one goal)

Order: PC-friendly and small first. `>19,000` says whether the fix grows a script already within 1,000 bytes of the 19,000-byte line; 12 shipped scripts are over it now (G13). PC: yes = pure Python and runnable on Windows (proof toys that are .sh still run on Linux CI).

| cluster | PC | scripts at the line | >19,000? | bullets | issues | note |
|---|---|---|---|---|---|---|
| G01 memory-floor-one-default | yes | settings.py 18,993 loses constants, replan/lanes_cli/file.py/board_status.py read one value; net shrink | no | OPS-16.6 (code defaults 4 and 3.5, README says 3 GB) (1) | - | tiny; first |
| G02 adopter-upgrade-fixes | yes | settings.py (18,993) needs ~200 B for the key: trim a docstring in the same file; prdcopy.py 18,897 regex only | no | INT-2.3 (declare milestones_source, validate mcp:notion plus 32 hex), DOC-1.14 (own-repo blob/raw URLs count as inside) (2) | 5079, 5078 | adopter migration path; both found in the v2.0 adopter-upgrade prep |
| G03 body-file-and-live | yes | merge.py 18,996, milestones.py 18,964, prdcopy.py 18,897, regression.py 18,992, runs.py 18,931, automation.py 18,878 | no | GRD-5.1 (GH_TOKEN turns writing on in automation.py:225, regression.py:242/309, runs.py:389; docs sync and release have no --live), GRD-5.2 (INT-4 rows) (2) | 5225 (INT-4 rows) | MCH-1.7 (five --body calls) moved out: gap-cheap-fixes has it in flight. GRD-5.1 needs one shared live() helper in a script with room: each edited script is within 1,000 bytes of the line |
| G04 one-mail-file | yes | mail.py 18,377 (about 600 B room); machine.py is dev, not shipped | no | DEL-9.3 (rounds/notify read schedule/mail.env with DIGEST_*; send-mail.py reads ~/.workflow-loop/mail.env with SMTP_* and mail-to) (1) | - | README says one file shared by both mailers |
| G05 owner-decisions-by-action | yes | auto.py 18,906 (removal shrinks); guards.py 19,252, sessions.py 20,000, fit.py 19,827 are over; mailbox.py 8,737 has room | yes (after G13) | DEL-3.2 (judge by action, add contradicts-my-words (the steward-merge class now matches the README)), DEL-3.4 (merge.py never reads the standing record), OPS-16.3, OPS-1.6 (merge/split only proposed), OPS-2.3 (ASK/PRIORITY/MERGE-REQUEST/MERGE-GO have no code), GRD-4.1 (own-goal scope is the LOOP_ROLE env var), MCH-5.4 (no sender check, no start/stop/reorder by mail) (7) | 5220, 4781 | put new code in mailbox.py or layers.py (room); do after G13 |
| G06 traceability-rules | yes | goal.py 18,952, fit.py 19,827 (over), defects.py 18,895 | yes (after G13) | DEL-19.1/19.2/19.3 (no health rule for a main commit no goal accounts for; goal.py new does not require a Reviewed requirement), HLT-2.5 (issue to feature, PR to goal to done lines, release to issues), HLT-2.16 (script or goal naming no requirement), HLT-4.8 (plan goals from filed issues) (6) | 5221, 5224 | health Traceability group; each rule needs a negative control |
| G07 guardrail-table-and-rules | partly | rules.py 18,206 (800 B room), actions.py 18,995, report.py 18,930, defects.py 18,895; Guardrails table is a wiki page | yes (after G13) | HLT-2.15 (the guardrail table; row grd1-guardrail-list greps for it), HLT-2.14, HLT-2.3 (Attention group, rules on the How-to page), HLT-2.6 (flaky rule), HLT-2.7 (built-in email/key scan), GRD-6.1/6.2/6.3 (read branch protection, flag --no-verify), GRD-7.1/7.2 (docs-only skip, daily minutes limit), GRD-8.3, SET-1.6 (setup lists guardrails installed) (11) | 5223 | write the table first; the other rules hang off it |
| G08 health-principles | yes | judge.py 18,599 (400 B room), controls.py 18,988 | yes (after G13) | HLT-2.17 (principle red for no enforcing requirement, no rule that can fail; requirement with no principle fails), HLT-2.18 (health reads the README list), HLT-2.19 (health review per principle); marked (v2.0 planned) in the README (3) | 5239 | README principles regroup (eight to six) is closed by the consolidation PR; Principle 6 stays UNREAD until the Attention group exists |
| G09 plan-red-team (named, planned) | partly | fit.py/flow.py near cap | unknown | DEL-1.8, HLT-2.20 (red-team each plan, record, build waits), HLT-2.21 (hourly and pre-ETA reviewer) (3) | 5239 | README names the goal; PR #5263 (plan-red-team-core) is open; nothing in main |
| G10 ops-findings (named, planned) | yes | mailbox.py 8,737 has room for a finding command | no | OPS-1.10/1.11/1.12 (file an ops-finding issue by default, refuse duplicates, safety class needs owner words), HLT-4.9 (4) | - | README names the goal; PR #5262 (ops-findings-v20) is open; nothing in main |
| G21 flaky-rows | yes | runs.py 18,931 (shown()), rules.py 18,206 (800 B room) | yes | HLT-2.1 (hlt1-same-answer flakes red: first run fails, the rerun passes, the cause is not kept; not a timeout), HLT-2.6 (no flaky-row rule in health) (2) | 5252 | owned by the PC (TOP-DECISION 134); the fix may be to keep the first run's output and make the toy line stable, not new code |
| G11 regression-coverage | partly | runs.py 18,931, regression.py 18,992, lanes.py 18,966, role.py 20,034 (over) | yes | REG-4.8 (local failure that passes on CI is filed and not counted), REG-9.4 (coverage steps from main's latest full run), REG-9.5 (coverage-drop refusal at qa and release), REG-7.1 (goal_lane_minutes is a second limit), REG-7.3, REG-1.1, REG-4.1 (7) | 5227, 4700, 4701, 4702 | most of the work is rendering and a qa check; toys are .sh so Linux CI proves them |
| G12 ci-regression (named, in progress) | no | actions.py 18,995 | yes | REG-4.9 (ci-shards-unrun0), REG-4.10 (lanes-table-data), SET-6.3 (ci-trace-matrix) (3) | 4516, 4556 | CI-only proof; README marks all three in progress; PRs #5189 (ci-shards-unrun0) and #5117 (lanes-table-data) are open |
| G13 size-trims-19000 (named, in progress) | yes | 12 scripts at or over 19,000 LF bytes now: fit 19,827, guards 19,252, lanekit 19,475, private 20,297, role 20,034, routing 19,066, operate 19,860, reply_hook 19,866, sessions 20,000, agents 19,380, seed 19,345, update 19,413 | - | HLT-11.4; rows scripts-a-delivery-under-19000 and scripts-a-monitoring-under-19000 are red on main; no row covers the three setup scripts (1) | 4653, 5123 | blocks G05, G06, G07, G08, G11, G14, G19, G20: every fix there costs bytes |
| G14 package-gate | partly | release.py 18,994, merge.py 18,996; dev/package.py (22,239) is not shipped | yes | GRD-20.1 (release cut and merge run package.py), GRD-20.2 (30-day date warn, owner words to raise a cap), GRD-20.3 (qa message with room left), SET-10.1 (no real Codex run recorded) (4) | 5124, 5126, 5123, 5223 | 5126 is an external fact (Agensi units) |
| G15 board-v2 | partly | live_board.py, board_lines.py 18,846, checkin.py 18,096, board.py 18,771; no new shipped file possible | yes | CHK-1.2 (Your move, Release goals, Critical path, Workers), CHK-1.6 (one row per peer goal) (2) | 4904 | README names a frozen board template until a board skill exists; none is in main, and a new skill would add shipped files at the 100-file cap: owner design question |
| G16 release-and-staging | partly | merge.py 18,996, release.py 18,994, review.py 18,988, pool.py 18,806, replan.py 18,818 | yes | SET-4.6 (develop-staging), REL-13.4 (merge-queue), REL-13.5 (a stamp-only commit carries a pass), REL-3.10 (release-readiness), REL-3.1 (minor tied to a milestone), REL-13.2 (batch merge is manual), DEL-1.7 (merged, release owed state), DEL-1.9 (a pr record commit never sends a goal back to pr) (8) | 4778, 4914, 5228 | README says the branch-flow design goes to the owner before any protection change; three named planned goals live here |
| G17 integrations-registry | yes | docs.py 18,470, health.py 18,956, board.py 18,771 | yes | INT-1.1/1.2/1.3 (one registry, adapters without loop code, board state); the How-to page itself says it is not built (3) | 5225 | largest single missing mechanism; #5225 asks only for tests |
| G18 docs-model | yes | pageformat.py 18,942, milestones.py 18,964 | yes | DOC-2.6 (delegated approvals by operation-top: new text), DOC-2.2 (one writer per page), DOC-1.15 (every command in the map), DOC-1.17 (adopter README principles rule) (4) | 5222 | DOC-1.17 waits for the consolidation PR |
| G19 adopt-completeness | partly | agents.py 19,380, seed.py 19,345, update.py 19,413 (over); setup.py 18,991, unattended.py 18,967, settings.py 18,993 | yes | SET-1.1 (adopted README with template principles; byte-exact install), SET-1.3 (Windows schedule), SET-1.5 (borrow milestone layout), SET-1.8 (default read-only connector probe), SET-1.9, SET-2.1 (local override), SET-4.1 (prove an adopter holds no skill code), SET-6.1 (fixture per adoption defect) (8) | 5229 | adopter migration; setup scripts are over 19,000 and no row guards them |
| G20 delivery-small-fixes | yes | fit.py 19,827 (over): put plan-in-body code in a roomy script; mend.py 18,331; machine_ops.py 6,754 | yes | DEL-1.2 (plan text in the PR body, Verify by hand required), DEL-7.3 (budget stop sets waiting under Needs you), DEL-7.4 (unusable session restarts in a fresh one), MCH-1.5 (behind-origin gap line) (4) | 4781 | after G13 |

Suggested order: **wave 1** (no size room needed): G01, G02, G04, G03, G10. **Wave 2** (after G13, one writer per script): G13, then G06, G08, G07, G20, G05, G11, G14. **Wave 3** (owner design or large): G15 (board skill does not exist), G16 (staging design goes to the owner), G17, G18, G19, G09. G12 is CI-only and already in progress.

## Needs the owner (README versus decisions, not code)

- AUT-1.1 and AUT-1.2 still say regression runs in GitHub Actions for a public repo and on every release tag; owner record o86 (#4682) says move off. REL-3.4 and ci-shards-unrun0 depend on CI runs. The code follows the README. Needs the owner's words: amend AUT-1 or close #4682 as superseded.
- CHK-1.2 names 'the skillset board skill'. There is no board skill; a new skill adds shipped files and the package is at the 100-file cap.
- Owner plans with no README bullet: token-diet (o104, 30% fewer tokens: #4788, #4828, #4829, #4830) and the regression plans of o90 (#4700 per-row time limit, #4701 defect issues carry a row, #4702 regression tidy-up). If they are v2.0 scope the README needs requirements first; otherwise they move to v2.1. See `.loop/readme-issues-map.md`.
- HLT-4.7 keeps one standing Backlog milestone per feature while #4783 retires the Backlog milestones.

## Red rows in main's full run 44504723066 (aa27754b)

The run: 1,055 passed, 81 failed, 30 known, 106 skipped of 1,273 rows (28m 29s; the log shows the 81 as the FAIL rows of its summary table). Each FAIL row is named in a goal's done lines (read from the pushed goal files) except the four marked NO OWNER. State is as read from git and `gh pr list` after v1.0.89 landed.

| owner goal | state | rows | row ids |
|---|---|---|---|
| known-red-waves-batch | MERGED #5248 (v1.0.89); the 29 rows need the next full run to show green | 29 | del-16-on-page, deploy-doc14-reviewed, deploy-not-locked, deploy-section-optional, deploy-table-refused, deployments-counts-pages, doc19-readme-links, home-guard-catches-leak, home-howto-linksonly, home-topic-column, link-unread-never-pass, machine-apply-installs, machine-done-7, migration-blocks-inserted, migration-clean, migration-flags, migration-gaps-pr, migration-gaps-state, migration-major-refused, migration-robustness, migration-v1, migration-writes-nothing, mon15-merge-lock, mon15-pod-owner, plan-cache-key, plan-identity, pods-independent, pods-lock, pods-owner |
| known-red-w5-merge-st | branch pushed, no PR open | 10 | merge-guard-base-head, merge-wiki-head, merge-wiki-rename-refused, merge-wiki-skill-refused, package-gate-head, pass3-symlink-page, st-merge-wiki-head, st-post-fails, st-release-pr, st-union-contexts |
| known-red-w2-adopt-setup | branch pushed, no PR open | 9 | adopt-fixture-bare-agent, adopt-fixture-ci-gitignore, adopt-fixture-existing-checks, adopt-fixture-feature-milestones, agent-routing, entry-adopt, set1-docs-format, settings-reference-fresh, setup-fit |
| known-red-w7-ops-checkin | branch pushed, no PR open | 9 | del9-scan-sites, guards-resume, landed-left-alone, lane-control-all, lane-messages-table, reply-hook-all, reply-hook-blocks, reply-hook-checkin-123, toy-no-leftovers |
| known-red-w4-docs-health | PR #5216 open | 9 | docs-guide-page-issue-125, entry-stale, health-file-no-milestone, hlt6-cannot-fire, no-usage-passes, prd-readers, runbook-registry, stale-code-page-reviewed, stale-groups-defect |
| known-red-w10-sync-apply | branch pushed, no PR open | 8 | apply-rerender-accepted, apply-rerender-hand-edit, docs-import-rows-pass, listing-names-every-command, stale-code-page-unreviewed, sync-apply-keeps, sync-default-source, sync-template-redirect |
| known-red-w4b-docs-wording | PR #5243 open | 2 | doc1-sync-pointer, milestone-wording-unreviewed |
| known-red-w9-trace | branch pushed, no PR open | 1 | lanes-trace |
| NO OWNER | none names these rows | 4 | hlt1-same-answer, lanes-trace-check, package-caps-held, repo-narrow-178 |

- **hlt1-same-answer** (HLT-2.1; owned by the PC, TOP-DECISION 134; cluster G21): not a timeout (no `timed out` text in its block; the one 900 s timeout in this run is another shard's row). Its FAIL block shows `ALL PASS` because `runs.py` `shown()` reruns the row without the `| grep -qx` filter for the report, and that rerun passed; the first run, the one that failed, is not kept. The row has failed in this run and in five earlier filings (#4489, #4536, #4550, #5080, #5252), each closed 'Passing again': it flakes. Unverified candidate (I cannot run the toy on Windows): its second check compares `ls -la .git | cksum` before and after `health check`, and that listing carries modification times to the minute, so a minute rollover with any write under .git changes the sum. The fix is a toy line that ignores times, plus keeping the first run's output when the rerun passes: not a faster row.
- **lanes-trace-check** sits next to lanes-trace (w9-trace, `ci-trace-matrix`, SET-6.3); **repo-narrow-178** next to lanes-repo-narrow (known-red-lanes); **package-caps-held** next to the package-100 rows. No goal names them: each needs an owner or an explicit add to the sibling goal's done lines.
- The 37 rows owned by wave branches with no PR open (as of v1.0.89) (w2, w5, w7, w9, w10) stay red until those branches get a PR and merge; w8-size and w11 already merged and are not in this list.

## Table

`tags` are the requirement IDs the bullet carries. Gap rows name their cluster; a `*` after done means a caveat in the evidence cell.

| bullet | tags | status | evidence | what is missing | issues | cluster |
|---|---|---|---|---|---|---|
| DOC-2.1 | DOC-2 | done | criteria.py:368-374 review/unreview need --user or owner record; rows review-owner-only, owner-re... | - | - | - |
| DOC-2.2 | DOC-22 | partial | milestones.py:329-342 guard, role.py:392 requirement_gate; row del9-pr-refuses (guard modes of test-delivery-prd.sh) | no mechanism for "a page has one writer at a time on any machine" (no page write lock) | 5222 | G18 |
| DOC-2.3 | DOC-22 | done* | goal.py:14,428 finding --requirement, private.py:389 files on Backlog milestone, milestones.py:32... | no row names DOC-22 | 5222 | - |
| DOC-2.4 | DOC-20 | done* | milestones.py:259-293 revise (date, why, owner record, older rows kept, only that ID Unreviewed);... | no row names DOC-20 | 5222 | - |
| DOC-2.5 | DOC-20 | done* | criteria.py:272 and pageformat.py:349 IDS-REUSE, :342-359 IDS-MISSING, retire in milestones.py:25... | no row names DOC-20 | 5222 | - |
| DOC-2.6 | DOC-2 | missing | git grep 'owner delegation' over skills, docs, .loop/goals: no hit; criteria.py review/unreview take only --user or an owner record | no delegation record kind, no list of operation-top approvals in the check-in, no revert | - | G18 |
| DEL-19.1 | DEL-18 | missing | grep "no goal accounts", rev-list, first-parent, direct commit in skills/workflow-health: nothing; Principles.md:15 says planned | no health rule flags a commit on main no goal accounts for; nothing blocks other writes | 5221 | G06 |
| DEL-19.2 | DEL-19 | missing | goal.py:191-227 / fit.py:278 freeze checks only done lines; milestones.py:340 guard is for changed Reviewed text only | no refusal at freeze for a goal naming no Reviewed requirement; no health flag | 5221 | G06 |
| DEL-19.3 | DEL-19 | missing | no code path or doc check; DEL-19 page row "not enforced" | no mechanism makes PRD-change goal first, build second | 5221 | G06 |
| DEL-19.4 | DEL-2 | done | goal.py:154-156 frozen(); guards.py:345 DONE_LINES_CHANGED; row frozen-done-lines (nightly) | - | - | - |
| INT-7.1 | INT-7 | done* | docs.tsv PRD source opt-in, .loop/prd copy, prdcopy.py:151 DOC-1 line; rows prd-copy-no-source, p... | no row names INT-7 | 5225 | - |
| REG-1.1 | REG-1 | partial | Requirement: health/scripts/enforce.py:44-53 (FAIL after 7 days); defect: delivery/goal.py:367, fit.py:430; workflow kind exists, but one workflow... | no rule that every whole flow has an end-to-end workflow row | - | G11 |
| REG-1.2 | REG-1 | done | docs/scripts/render.py:179 writes "no passing test / not enforced"; enforce.py:3; row tests-not-e... | - | - | - |
| HLT-2.1 | HLT-1 | partial | health.py check writes nothing; rows same-lines, check-writes-nothing; hlt1-same-answer is red in main run 44504723066 and in 5 nightly filings (#4... | the row flakes: its first run fails, the diagnostic rerun (runs.py shown) passes and prints ALL PASS, so the real failure text is never kept; not a timeout | 5252 | G21 |
| HLT-2.2 | DOC-13 | done | docs/scripts/audit.py and docs.py call no model (searched for claude, judge_command: none); row d... | - | - | - |
| HLT-2.3 | HLT-2 | partial | report.py:10-34 twelve groups with angles, MAX_GROUPS; judge.py:369 maps groups to principles; row hlt2-twelve-groups ran | rules are listed in skills/workflow-health/references/commands.md, not in How-to-use-Health; the Attention principle has no group, so no rule can fail | - | G07 |
| HLT-2.4 | HLT-2 | done | health/scripts/judge.py:369-379 PRINCIPLE line per principle, RED on FAIL, UNREAD if no rows; hea... | - | - | - |
| HLT-2.5 | HLT-2 | partial | Requirements: enforce.py:20,44-53; consistency: defects.py:128,151,166; docs: health.py:223. Traceability has only defect-tests and row-requirement... | traceability lacks issue to feature, pull request to goal to done lines, release to issues fixed; no rule for contradicting requirements | - | G06 |
| HLT-2.6 | HLT-2 | partial | Freshness nightly/unreleased/finding-age; Tests seen-red/skipped/network; Performance cost/test-time/suite-cap/check-time (report.py:17-21, command... | no "no flaky rows" rule in the Tests group (flaky is only marked in regression/tiers.py) | - | G21 |
| HLT-2.7 | HLT-2 | partial | rules.py:247 private, scan-hook, workflow-permissions (top-level permissions: only), scripts, skill-lines, requirements-per-page (rules.py:303); hy... | `private` reads only owner leak_patterns (INFO when none); no built-in email or key scan; permissions not checked as least; regression "firing" not read | - | G07 |
| HLT-2.8 | HLT-2 | done | health/scripts/report.py:33-34 MAX_GROUPS assert "retire one before adding another"; test-health-... | - | - | - |
| HLT-2.9 | HLT-2 | done | health/scripts/health.py:113-117 WARN after 7 days, never FAIL; regression/runs.py:344 PENDING; r... | - | - | - |
| HLT-2.10 | HLT-2 | done | health/scripts/file.py:316-361 limit_rows (rounds, active, memory waits, plan_pause_percent), WAR... | - | - | - |
| HLT-2.11 | HLT-2 | done | health/scripts/health.py:223-230 FAIL docs row for each DELTA from docs.py sync --open; How-to-us... | - | 5225 | - |
| HLT-2.12 | HLT-3 | done | health/scripts/report.py (groups header, findings table by feature, rule states, verdict); rows r... | - | - | - |
| HLT-2.13 | HLT-6 | done | health/scripts/controls.py (a control per rule); health.py refuses a rule with none; rows hlt6-co... | - | - | - |
| HLT-2.14 | GRD-9 | partial | Rules exist for some guardrails (scan-hook, hooks, workflow-permissions, rows-cap, suite-cap, cost); enforce.py:114 repo rules need a break; repo-r... | no mapping that every guardrail has a rule; GRD-9 shows "not enforced"; branch protection (GRD-6) has no health rule; grd9-controls SKIPPED | 5223 | G07 |
| HLT-2.15 | GRD-1 | missing | docs/wiki/Guardrails.md has requirements only; known-red row grd1-guardrail-list says "not built: the page is a definition only" | the table of guardrail, protection, enforcement point, setting, health rule | - | G07 |
| HLT-2.16 | HLT-13 | partial | rows with no requirement: docs/scripts/criteria.py:143, defects.py:122 row-requirement; conflicts: only the AI review (judge.py:219) | no deterministic rule for conflicting or repeated requirements, or for a script or goal naming no requirement | 5224 | G06 |
| HLT-2.17 | HLT-2 | partial | v2.0 planned: judge.py:369-379 prints PRINCIPLE lines red only on a failing group | no red for a principle with no enforcing requirement or no rule that can fail; no failure for a requirement with no principle; no controls | 5239 | G08 |
| HLT-2.18 | HLT-2 | partial | v2.0 planned: docs/scripts/pageformat.py:160 (docs check) fails a README principle sentence differing by a word from commands.md "## The eight prin... | the check is in docs, not health; the list has eight principles, README six | 5239 | G08 |
| HLT-2.19 | HLT-2 | missing | v2.0 planned: searched judge.py and health.py review for per-principle output: none | review per principle: enforcing requirements, tests, where weak | 5239 | G08 |
| HLT-2.20 | HLT-2 | missing | v2.0 planned: searched red-team in skills: none | plan-red-team check of each plan against every principle, with build waiting on owner words | 5239 | G09 |
| HLT-2.21 | HLT-2 | missing | git grep red-team / hourly reviewer in skills and dev: no hit | everything (named by plan-red-team) | 5239 | G09 |
| HLT-4.1 | HLT-4 | done | file.py:1-20 (group+feature tags, preview has no write path, repeat updates, fix closes, return r... | - | - | - |
| HLT-4.2 | REG-5 | done | runs.py:109 sync_issues (close/reopen), regression.py:27 dry-run unless --live; rows one-issue, k... | - | - | - |
| HLT-4.3 | DEL-14 | done | milestone.py:12 leftovers (FILE defect/backlog), private.py:398; rows backlog-leftovers-filed, ba... | - | - | - |
| HLT-4.4 | HLT-5 | done | judge.py:195-209,346 (review section, ranked next steps per feature); rows judge-verdict-unchange... | - | - | - |
| HLT-4.5 | HLT-9 | done | judge.py citation check; rows hlt9-evidence-or-nothing, hlt9-located-evidence, hlt9-review-rechec... | - | - | - |
| HLT-4.6 | HLT-10 | done | milestone.py:backlog (creates all), setup makes them; rows backlog-milestones-made, backlog-setup... | - | - | - |
| HLT-4.7 | HLT-8 | done | health.py:8 triage, issues.py:355-359 close with words + health:closed, file.py:176 stays closed;... | - | - | - |
| HLT-4.8 | HLT-12 | missing | Searched backlog/defect/issue list in monitoring and delivery scripts: only batch.py:217 roadmap page lists open issues; no planner proposes goals... | nothing reads defect/backlog issues per feature to propose goals, most blocking first | - | G06 |
| HLT-4.9 | OPS-1 | missing | git grep ops-finding, 'mailbox.py finding': no hit | everything (named only: ops-findings) | - | G10 |
| AUT-1.1 | AUT-1 | done* | workflows.py:178 due(), :316-333 REGRESSION runs on the Mac/Actions + DRIFT; automation.py:204 MI... | owner o86 (#4682) says public repos leave Actions; code still follows README | 4682 | - |
| AUT-1.2 | AUT-2 | done | actions.py:31-32 (tags v*, workflow_dispatch), :204-226 SKIPPED with reason, runs.py:75; loop-fil... | - | - | - |
| AUT-1.3 | AUT-3 | done | workflows.py:267-361 tick (probe, health, judge, regression, digest), :325 judge_skipped; automat... | - | - | - |
| AUT-1.4 | DOC-16 | done | criteria.py:203-267, deployments.py:94-179, counting.py:299; docs.py prompts; rows runbook-good,... | - | - | - |
| DEL-1.1 | DEL-1 | done | flow.py:92 (no flow refused), flow.py:33 STEPS, goal.py:191; rows no-done-line-refused, no-flow-r... | - | - | - |
| DEL-1.2 | DEL-4 | partial | fit.py:354-367 pr_body: goal file (done lines, Verify by hand), per-step result and verdicts, lane rows; PR 5186 body checked | plan text not in the body (only plan verdict); Verify by hand stays an empty comment unless authored | - | G20 |
| DEL-1.3 | REL-10 | done | merge.py:272,344 (auto_merge), release.py:367 (--draft), autorelease.py:105 release_error, live_b... | - | - | - |
| DEL-1.4 | REL-14 | done* | autorelease.py:73,153 notes; wiki.py:210 fixes_lines; row release-lists-fixes (REG-6, PASS) | no row names REL-14 (page: not enforced) | 5228 | - |
| DEL-1.5 | REL-9 | done | release.py:222 untouched(), release.py:224 re-render spans, wiki.py:56 pending(), merge.py:291; r... | - | - | - |
| DEL-1.6 | REL-9 | done | merge.py:36 file_issue (Backlog: <Feature>/Documentation, milestone made, open title checked, gh... | - | - | - |
| DEL-1.7 | REL-11 | partial | merge.py:291 stale check; second run skips merge if PR MERGED (merge.py:288, autorelease.py:129); test-autorelease.sh:65,122 | literal "merged, release owed" state absent; no row names REL-11; PR-check-before-slot not shown | 5228 | G16 |
| DEL-1.8 | - | missing | v2.0 planned; no plan-red-team in code or docs (git grep) | everything (named only) | 5239 | G09 |
| DEL-1.9 | DEL-1 | missing | merge.py:297 exempts only a wiki-only head move (operate.py wiki-only); a pr record commit (run records, issue records) is not exempt | a pr record commit still moves the head and can send the goal back to pr (v2.0 planned) | - | G16 |
| REL-3.1 | REL-1 | partial | release.py:182 bump refuses a major (MAJOR_GATE); patch default, minor from the goal's bump (fit.py:184 reads the goal text); row rel-major-refused... | minor is not tied to a milestone; only the word minor in the goal | - | G16 |
| REL-3.2 | REL-2 | done | review.py:215 gate_refusals lists open issues of milestone vX.0 unless waivers() (:147) names the... | - | - | - |
| REL-3.3 | REL-3 | done | review.py:196 check_suite runs the nightly suite on the candidate; FAIL, KNOWN, NOTRUN, ENV, LEFT... | - | - | - |
| REL-3.4 | REL-3 | done | review.py:186 ci_text (same sha, regression workflow, all shards, UNRUN 0, every row logged), ref... | - | - | - |
| REL-3.5 | REL-4 | done | review.py:161 check_reviews, :209 check_health, whole-wiki docs_trouble; each failure named; row... | - | - | - |
| REL-3.6 | REL-5 | done | review.py:241 frozen; merge.py:~312 calls it from the rc tag until the major is tagged; row rel-f... | - | - | - |
| REL-3.7 | REL-6 | done | review.py:282 promote: owner record must name the tag, gate must pass, tag -a, branch release/vX,... | - | - | - |
| REL-3.8 | REL-8 | done | review.py:332 non-gate verbs refused for workers (REVIEW_ROLE); :147 a waiver counts only with an... | - | - | - |
| REL-3.9 | REL-7 | done | review.py:310 revert pushes revert/vX-time and opens a pr, never pushes the base; worker refused;... | - | - | - |
| REL-3.10 | - | missing | v2.0 planned; no release-readiness check before the gate (git grep) | everything (named only) | - | G16 |
| REG-4.1 | DOC-3 | partial | docs/scripts/audit.py:70 UNTESTED (no test, test no longer matches) and :127 untested.tsv; regression.py sync --write drafts rows | nothing consumes untested.tsv to write Given/When/Then tests on PRD review; rows are not auto-written | - | G11 |
| REG-4.2 | REG-2 | done | regression/scripts/tests.py (list, summary grouped by feature, fixed columns); rows summary-group... | - | - | - |
| REG-4.3 | DOC-10 | done | docs/scripts/render.py:127 and :197 full_page writes docs/wiki/Tests.md; row tests-row-shape ran | - | - | - |
| REG-4.4 | REG-3 | done | regression/scripts/regression.py run; rows workflow-same-as-run, reg-same-env, local-row-env ran | - | - | - |
| REG-4.5 | REG-4 | done | regression/scripts/tiers.py (affected plus new rows, merge-base record); goal.py pr reruns after... | - | - | - |
| REG-4.6 | REG-8 | done | setup/scripts/settings.py:33,47-49,61-64,97 (regression_cron, goal_levels, regression_runs, caps,... | - | - | - |
| REG-4.7 | REG-12 | done | delivery/scripts/lanekit.py:103 and regression/scripts/slots.py:143 port leases; per-lane TMPDIR;... | - | 5227 | - |
| REG-4.8 | REG-13 | missing | Searched "passes on CI", REG-13, machine-specific in skills and dev/toy: none; How-to-use-Regression.md:72 says "Planned, not built yet" | whole behaviour: a machine-only failure is filed and not counted against the goal | 5227 | G11 |
| REG-4.9 | - | partial | v2.0: ci-shards-unrun0. regression.yml:30-34 has 8 shards and a 30-minute limit; health/scripts/lean.py:147 WARNs when a full run left rows unrun | no guarantee that nothing is left unrun; a shard that times out still leaves rows | - | G12 |
| REG-4.10 | - | partial | v2.0: lanes-table-data. regression/scripts/lanes.py:305,374 and tiers.py:212 rerun a changed row plus every row that reads the table; row lanes-tab... | rows that only read the table as data still rerun on a one-row edit | - | G12 |
| REG-9.1 | REG-9 | done | regression/scripts/tiers.py:13,359 flaky_apply (FLAKY mark, never reused); regression.py:285; row... | - | - | - |
| REG-9.2 | REG-6 | done | delivery/goal.py:367 refuses a pr with no defect test seen failing; fit.py:430 OWED; regression/t... | - | - | - |
| REG-9.3 | REG-10 | done | regression/runs.py:317-344 owed file, PENDING "never blocks"; SKILL.md:57; rows reg10-off-platfor... | - | - | - |
| REG-9.4 | REG-15 | missing | Searched coverage, Stated, Fresh in skills/*/scripts: nothing computes a coverage step; How-to-use-Regression.md:74 "Planned, not built yet" | whole behaviour: coverage step computed from main's latest full run and shown by each requirement | 5227 | G11 |
| REG-9.5 | REG-16 | missing | Searched role.py, goal.py, release scripts: qa refuses only on test caps (role.py:253); nothing checks the only proof of a Reviewed requirement or... | qa refusal for removing the only proof; release gate on lowered coverage | 5227 | G11 |
| DOC-1.1 | DOC-1 | done | criteria.py section order, pageformat.py problem()/bullets(); rows prd-section-order, prd-nongoal... | - | - | - |
| DOC-1.2 | DOC-14 | done | deployments.py:19 EMAIL, :83 recipients group-not-address; rows deploy-table-refused, deploy-sect... | - | - | - |
| DOC-1.3 | DOC-4 | done | main README.md and docs/wiki/Home.md carry 'Requirements by feature' (two parts); pageformat.py:1... | - | - | - |
| DOC-1.4 | DOC-15 | done | render.py:274 overridden marker; rows settings-overridden, settings-stale, settings-publish-refresh | - | - | - |
| DOC-1.5 | DOC-15 | done | counting.py:278-334 automation_block, audit.live via docs.py automation; rows automation-cron-wor... | - | - | - |
| DOC-1.6 | DOC-15 | done* | render.py:281-287 template_line, setup settings.py:74 template_repo; rows settings-template-line,... | "adoption entry points to all three" not checkable (no definition of the three) | - | - |
| DOC-1.7 | DOC-15 | done | counting.py (18,916 B) holds automation_block, render.py (18,928 B) the rest; rows docs-block-spl... | - | - | - |
| DOC-1.8 | DOC-23 | done | main README.md is the title, the wiki Home link and six principles in two parts (v1.0.90, #5268);... | - | - | - |
| DOC-1.9 | DOC-23 | done | pageformat.py:140-180 frontdoor: grid columns, Flow link target, requirement coverage, Home How-t... | - | - | - |
| DOC-1.10 | DOC-18 | done | deployments.py:326 PARTS, criteria.py:203-215; rows doc18-howto-skeleton, doc18-review-link-line,... | - | - | - |
| DOC-1.11 | DOC-18 | done | deployments.py:337 mapped() (How-to has no docs.tsv row), audit.py:258,376 restamp; rows doc18-ho... | - | - | - |
| DOC-1.12 | DOC-18 | done | Home links each How-to page (pageformat.py:136; rows home-howto-linksonly, home-howto-linksonly-c... | - | - | - |
| DOC-1.13 | DOC-19 | done | deployments.py howto()/prdcopy.py checks; rows doc19-item-missing, doc19-item-unknown, doc19-kind... | - | - | - |
| DOC-1.14 | DOC-19 | partial | counting.py:269-278 origins() (public-origins.json, public_origins), prdcopy.py:346-363 NEAR allows milestones, releases, wiki, README blob; rows d... | the repo's own GitHub blob/raw image URLs are reported "outside this repo" | 5078 | G02 |
| DOC-1.15 | DOC-6 | partial | test-command-reference.py (row command-reference-complete) checks each map verb appears in SKILL.md or commands.md; row ls-usage-steps (health only) | no check that every real command is in the map, nor that each has success output, refusals and exit codes | - | G18 |
| DOC-1.16 | DOC-21 | done* | counting.py:215-219 AST compare (comments and docstrings ignored), audit.py:258 restamp_own; rows... | rows are tagged DOC-2, none names DOC-21 | 5222 | - |
| DOC-1.17 | DOC-23 | missing | README check runs only where the template ships the list (pageformat.py:160); migration (defects.py:264) only checks the README template line | an adopter's README is not required to show the template principles byte for byte | - | G18 |
| OPS-1.1 | OPS-1 | done | operate.py:1-27 one command (`run`, `start`), no model in loop; rows no-line-in-governor, worker-... | - | 4507 | - |
| OPS-1.2 | OPS-1 | done* | layers.py:1-12 roles, operate.py:146 top publishes board every TOP_GAP=300 s, machine one line; r... | "top the only reader of the owner" is policy, not enforced | - | - |
| OPS-1.3 | OPS-13 | done | graph.py pods, operate.py claim in every followed repo; rows mon13-two-layers, pods-independent,... | - | - | - |
| OPS-1.4 | OPS-23 | done | unattended.py:selfcheck/loop RECREATE/sends warn at 16th; rows unattended-loop-recreate, unattend... | - | 4813 | - |
| OPS-1.5 | OPS-23 | done | layers.py:check_allowed (two-token form FIX), repo config.json has one token; row unattended-send... | - | - | - |
| OPS-1.6 | OPS-10 | partial | replan.py:1-20 re-reads progress each pass, logs each change once with reason; row mon10-replan | merges/splits are proposals only, never applied | - | G05 |
| OPS-1.7 | OPS-8 | done | board silent_minutes 30 -> Needs you (checkin.py:177); rows mon8-silent-30, mon8-silent-worker, s... | - | - | - |
| OPS-1.8 | CHK-7 | done | checkin.py needs list with holds-up and critical path; row blockers-first (PASS) | - | - | - |
| OPS-1.9 | OPS-6 | done | pool.py:147 worktree remove, :158 branch -D, return/archive; rows mon6-merged-frees, merged-frees... | - | - | - |
| OPS-1.10 | OPS-1 | missing | git grep ops-finding: no hit; mailbox.py has no finding command | no ops-finding label, no default filing | - | G10 |
| OPS-1.11 | OPS-1 | missing | no ops-finding filer, so no duplicate check | no normalised-title duplicate refusal, no check-in list | - | G10 |
| OPS-1.12 | OPS-1 | missing | no ops-finding filer | safety-class findings not separated | - | G10 |
| INT-2.1 | INT-2 | done | prdcopy.py:228 sync, milestones.py; rows sync-not-connected, sync-no-gh, prd-sync-no-reader, prd-... | - | - | - |
| INT-2.2 | INT-3 | done* | prdcopy.py:228-342 (baseline, DELTA/CONFLICT with side), milestones.py:139-150 post on Backlog mi... | Backlog milestones are being retired by #4783 | 4783 | - |
| INT-2.3 | INT-8 | partial | milestones.py:70 reads `milestones_source`; rows milestone-sync-* (14 rows, incl. no-overwrite, not-connected) | `milestones_source` is not in the settings table, so migration-check flags it MIG_SETTINGS "unknown" (defects.py:257) and update.py may drop it | 5079 | G02 |
| DEL-17.1 | DEL-17 | done | auto.py:225 eta_new, fit.py:283 frozen_fields, goal.py:217 ETA line; rows eta-freeze, eta-legacy-... | - | 5221 | - |
| DEL-17.2 | DEL-17 | done* | fit.py:131-137 budget_stop (ETA_PAST), auto.py:269 eta_over, :282 eta_wait, :311 eta_set (ship/de... | extend is not capped at one use (each needs a fresh owner record) | - | - |
| DEL-17.3 | DEL-17 | done | fit.py:283 preflight_new; commands.md:395-409; rows eta-preflight-asked, eta-preflight-missed | - | - | - |
| DEL-17.4 | DEL-17 | done | fit.py:123 active_minutes -> board_log.active_minutes (held time excluded); rows held-time-3878,... | - | - | - |
| REG-7.1 | REG-7 | partial | 15-minute floor: delivery/lanekit.py:353-369, lane.py:227; fit and defer: regression/runs.py (fit, execute); rows reg7-floor-test, reg7-budget-fit... | "the only time limit" is false: goal_lane_minutes (default 10, lane.py:138, milestone.py:335) is a second, lower lane limit | - | G11 |
| REG-7.2 | REG-11 | done | delivery/lanekit.py:223 LANE_PREP_BUDGET naming the part, :353-369 15-minute floor; How-to-use-Re... | - | 5227 | - |
| REG-7.3 | REG-14 | partial | Caps: settings.py:61-62; refusal at qa: delivery/role.py:253-275 (net rows, base branch cap); rows test-caps-own-cap, test-caps-consolidate-allowed... | suite time is the slowest recorded full run (role.py:268, lean.py:141), not the latest full run on main | - | G11 |
| HLT-7.1 | HLT-7 | done | rules.py:314-316 check-time (60 s); row hlt7-fast-check | - | - | - |
| HLT-7.2 | DOC-12 | done | row docs-check-speed (DOC-12, under 30 s on this repo) | - | - | - |
| HLT-7.3 | CHK-8 | done | row mon9-board-fast (CHK-8); toy of 12 goals and a slow gh, not this repo's own board | - | - | - |
| HLT-7.4 | AUT-7 | done | rounds.py:27 BUDGET_MINUTES=45, over flag rounds.py:220; rows aut-email-rounds, aut7-budget-agrees | - | - | - |
| HLT-7.5 | CHK-4 | done* | govern_hook.py:284 quiet_decide (QUIET_MINUTES 120, no model turn), checkin.py:311 op_append to o... | no row names CHK-4 (page: not enforced) | 5220 | - |
| GRD-8.1 | GRD-15 | done | guards.py:131 add_tokens; proctree.py:289 add reads the session transcript; row token-diet-step-t... | - | 5223 | - |
| GRD-8.2 | GRD-15 | done | fit.py:109 "tokens unread"; board_lines.py:332; rows tokens-unread-shown, grd2-tokens-unknown (pa... | - | 5223 | - |
| GRD-8.3 | GRD-8 | partial | time: board_model.py:16,342 stalled (3x estimate, 15 min floor) shown on the live board (live_board.py:231); silent worker: board_status.py:189 | no per-step token-multiple flag (only goal OVER tokens, board_lines.py:331); stall not in the check-in text; page "not enforced" | - | G07 |
| GRD-7.1 | GRD-7 | partial | concurrency cancel-in-progress in regression.yml:24-26, regression-pr.yml:10-12, generated by actions.py:48 and lanes_cli.py:177 | no paths-ignore or no-code skip: regression-pr.yml runs on every pull request; GRD-7 row "not enforced" | - | G07 |
| GRD-7.2 | GRD-17 | partial | rounds.py:259-270 shows Actions minutes per round, OVER 45 min flag; row aut-email-rounds, grd7-round-cost (nightly, Mac only) | no runs-or-minutes-per-day limit and no single alarm; only a per-round job-time flag | - | G07 |
| OPS-16.1 | OPS-16 | done | watch.py:296-330 start_round, graph.py:156 ready (every goal with deps met starts); rows mon16-me... | - | - | - |
| OPS-16.2 | OPS-16 | done | replan.py:160 active_limit, :176 plan_pause (PLAN_PAUSE), :182 memory_hold (LOW_MEMORY), graph.py... | - | - | - |
| OPS-16.3 | OPS-16 | partial | layers.py:184 check_budgets reports a budget over the cap; auto.py:295 budget raise by record; row mon16-machine-line | goal.py set does not refuse a raise past the cap; a package-limit raise has no owner-words gate (see GRD-20.2) | - | G05 |
| OPS-16.4 | OPS-20 | done* | graph.py:156-175 ready waits only on unmet deps, slots, memory; pr-lane waits only on overlapping... | OPS-20 itself has no test row (#5226) | 5226 | - |
| OPS-16.5 | OPS-12 | done | pool.py (pool_size, ask to fill); watch.py app_only waits; rows mon12-pool, go-app-holds-goal | - | - | - |
| OPS-16.6 | GRD-12 | partial | replan.py:182, lanes_cli.py:333 (lane waits, running lane never stopped), board_status.py:161; row config-memory-key-once | code default is 4 (replan.py:184, lanes_cli.py:337) and 3.5 (board_status.py:161), not 3 GB; default stated in several places | - | G01 |
| GRD-20.1 | GRD-20 | partial | dev/package.py check_files/check_scripts/check_safety/check_disclosure/check_listing print "FAIL <rule>: file"; land rows package-passes, package-g... | not wired into release: no release.py/autorelease.py/merge.py call; only land rows; no test names GRD-20 | 5223 | G14 |
| GRD-20.2 | GRD-21 | partial | table on How-to-use-Guardrails.md (Agensi figure, ours, date read); row package-caps-held (test-package-caps.py); package.py:41 caps | health does not warn when last read over 30 days; "raising ours needs my words" not enforced; table is on the How-to page, not Guardrails | 5126 | G14 |
| GRD-20.3 | GRD-22 | partial | package-gate-head land row fails the lane at qa if a script is 20,480+ bytes or files over 100; role.py:245 over_caps is for test caps only | no "unless it frees as much room" rule; the refusal does not say room left or what would free it | 5124, 5123 | G14 |
| HLT-11.1 | HLT-11 | done | health/scripts/lean.py:4,185 test-time names slowest rows; worktrees, local-branches print remova... | - | 5224 | - |
| HLT-11.2 | HLT-11 | done | health/scripts/health.py:50 WARN=19000; FAIL over 20,480; rows size-fail ran 2026-11-19, size-war... | - | 5126 | - |
| HLT-11.3 | GRD-19 | done | health/scripts/rules.py:303-307 requirements-per-page vs criteria_max (settings.py:43); rows crit... | - | 5224 | - |
| HLT-11.4 | - | partial | v2.0: docs, health, regression scripts are all at or under 18,999 LF bytes; monitoring still has sessions.py 20,000, reply_hook.py 19,866, operate.... | those three monitoring scripts are over 19,000 | 4653, 5123 | G13 |
| REL-13.1 | REL-13 | done | graph.py:391 merge_lock (one merge per repo); machines.py:87 turn across machines when machine_sy... | - | - | - |
| REL-13.2 | REL-13 | partial | pool.py:286 pr_turn waits only behind overlapping touches; wiki.py:252 group and :295 cmd_batch verify and merge disjoint goals; rows pr-parallel-d... | merge slot (replan.py:238) waits on any earlier lane; a goal waiting on me keeps its place; batch is manual | - | G16 |
| REL-13.3 | REL-13 | done | merge.py:91 base_moved refuses only when moved paths reach the goal's rows; goal.py:343-365 turn,... | - | - | - |
| REL-13.4 | - | missing | v2.0 planned; no merge queue use (git grep) | everything (named only) | - | G16 |
| REL-13.5 | REL-13 | missing | merge.py:91 base_moved compares paths; no tree-equal-modulo-stamps check, no carry of a pass to a stamp-only commit | v2.0 planned: a stamp-only commit carries the recorded pass with no fresh CI run | - | G16 |
| DEL-9.1 | DEL-9,GRD-3 | done | seed.py:27 GUARD hooks (commit, commit-msg, pre-push); private.py scan; machine.py LEAKS; rows de... | - | - | - |
| DEL-9.2 | DEL-9,GRD-3 | done | private.py:9,53 @public / @repos= scope; row private-names-scoped | - | - | - |
| DEL-9.3 | AUT-6 | partial | notify.py:71 and rounds.py:367 share schedule/mail.env; rows aut-email-secrets, health-mail-env-windows | machine send-mail.py uses ~/.workflow-loop/mail.env + mail-to (machine-templates.md:26): two files and two paths | - | G04 |
| DEL-9.4 | MCH-9 | done | machine.py:189 empty private-names (mode 600), machine_ops.py:90 restore skips mail/private-names... | - | - | - |
| GRD-4.1 | GRD-4 | partial | guards.py:321 operation_only, :402 touches, fit.py:194 set, guards.py:325 WORKER_SELF_REPAIR; rows grd4-touches, grd4-resume, grd4-budget | widen/resume/budget refused only by the LOOP_ROLE env var; sessions.py:292 report takes any slug, so "own goal only" is not enforced | - | G05 |
| GRD-4.2 | OPS-7 | done | govern_hook.py:137-223 (refuses edit/commit/push in the operation session); rows mon7-govern-bloc... | - | - | - |
| GRD-5.1 | GRD-5 | partial | --live in milestone.py:7-15, regression.py:19/27, automation.py:316; rows issues-live-only-ci, issues-live-only-local, grd5-health-close | no --live on docs.py sync (posts delta issues by default: milestones.py:144, prdcopy.py:326), health file.py, release/autorelease `gh release create`, sync.py:357 | - | G03 |
| GRD-5.2 | INT-4 | partial | docs.py sync reads by default; writes outside only for --accept (prdcopy.py:228-342); unattended.py:239 read-only probe; setup never attaches | no test row for INT-4 ("not enforced"); delta issues are posted without a switch (opt-out --dry-run); no narrowest-access check | 5225 | G03 |
| GRD-6.1 | GRD-6 | partial | merge.py HEAD_MOVED (row grd6-head-moved, page: not run); private.py:285 required_checks and post_statuses | platform rule is the owner's; nothing in the repo reads that force-push and direct-push are refused; page row "not enforced" | - | G07 |
| GRD-6.2 | GRD-6 | partial | setup writes no ruleset: test-statuses.sh:134 asserts no PUT/POST; setup.py/seed.py:198 only names BLOCKS | health does not read protection: defects.py:301 lists "branch protection (no gh read)" as NOT CHECKED | - | G07 |
| GRD-6.3 | GRD-16 | partial | health hooks rule lean.py:318 hook_rows, rules.py:264 scan_hook flag missing hooks; private.py scan runs on pr/push anyway; no loop code uses --no-... | no check that refuses or flags a commit made with --no-verify or empty hooksPath; no test (GRD-16 not enforced) | 5223 | G07 |
| AUT-9.1 | AUT-9 | done* | audit.py:305-356 permissions write/check; entry.py:365; setup SKILL.md:93; rows perms-undeclared,... | setup.py itself does not write them (separate `/workflow-setup permissions`);... | - | - |
| AUT-9.2 | MCH-11 | done* | dev/machine.py:34 NO_PROMPT, :146-154 routine file holds the prompt, :282-284 GAP mode; row machi... | machine.py lives in dev/, not shipped to adopters | - | - |
| AUT-9.3 | MCH-6 | done | machines.py:147 start_worker (one function; app-only waits); desk.py:80 phone_start; rows desk-li... | - | - | - |
| AUT-9.4 | MCH-6 | done | setup.py:327 -> desk.py list/run/done/check (DESK OK, phone_start); rows desk-lists, desk-lists-4805 | - | - | - |
| DEL-7.1 | DEL-7 | done | goal.py:49 MAX_TRIES=3, guards.py:245-259 failed_try; rows stop-after-3-tries, pr-moved-uncounted | - | - | - |
| DEL-7.2 | DEL-7 | done | fit.py:resume_at; rows del7-kill-resume, del7-recorded-refused (page: not run) | - | - | - |
| DEL-7.3 | DEL-7 | partial | fit.py:128-141 budget_stop (BUDGET_MINUTES/TOKENS), board_lines.py:331 OVER; eta-budget-raise needs owner record; rows del8-session-tokens, held-ti... | budget refusal only exits; goal is not set waiting, so no Needs-you entry (ETA has one) | - | G20 |
| DEL-7.4 | DEL-7 | partial | mend.py:6,42,283 gives a failed goal a fresh agent with the cause | no check that the failure was an unusable session/tool; no row for the planning-tool case | - | G20 |
| DEL-7.5 | MCH-3 | done | dev/machine.py backup/restore, machine_ops.py backup_set/vault/backup/restore, OWNER_ONLY; row ma... | - | - | - |
| SET-10.1 | SET-3 | partial | dev/package.py builds one ZIP; flow.py:37 BUILTIN default flow; test-codex.sh fake harness (codex-harness); matrix-smoke.py | matrix-runs.tsv holds one run (claude-cli, windows); no real Codex run; package-gate-head FAIL 2026-11-16 | 5123, 5124 | G14 |
| SET-10.2 | SET-10 | done | agents.py wire writes CLAUDE.md/AGENTS.md block (seen in this repo's CLAUDE.md); row agents-wire... | - | - | - |
| SET-10.3 | DEL-16 | done | routing.py:1-20 agents.json profiles/routes, AGENT_FALLBACK warning, `show` names agent/model/tok... | - | - | - |
| MCH-1.1 | MCH-7 | done | unattended.py:219 prerequisites (git, python3, gh, signed in, symlinks, platform, fixes); setup.p... | - | - | - |
| MCH-1.2 | MCH-1 | done | dev/machine.py plan (dry run) / apply (skill links, hooks, empty private-names); rows machine-app... | - | - | - |
| MCH-1.3 | MCH-2 | done | machine.py:189-230 operation-session, peer-link items; machine_ops.py hook_gap/peer_gap; row mach... | - | - | - |
| MCH-1.4 | MCH-2 | done | machine_ops.py OWNER_ONLY, checklist(); machine.py gaps():277 names mail files; rows machine-appl... | - | - | - |
| MCH-1.5 | MCH-10 | partial | machine.py:gaps() prints one GAP line per item (hooks, skills, tasks, mail files, check-in pointer); row machine-check-gaps | no "skills checkout behind" gap (skills only checked as linked) | - | G20 |
| MCH-1.6 | DEL-12,GRD-18 | done | dev/toy/test-windows-safe.py; row windows-safe-posix-names (land, GRD-18 lane) | - | - | - |
| MCH-1.7 | DEL-12,GRD-18 | partial | --body-file in fit.py:309, file.py:76, rounds.py:38, runs.py:87, autorelease.py:94; row pr-body-by-file greps only fit.py and goal.py | `--body` on the command line remains: merge.py:40, milestones.py:148,151, prdcopy.py:320,326 | - | C01 |
| MCH-4.1 | MCH-4,OPS-15 | done | graph.py:350-380 stamp/foreign/refuse; goal.py:403, operate.py:277, sessions.py:212, merge.py:281... | - | - | - |
| MCH-4.2 | MCH-4 | done | machines.py:164 handover (push, copy record to refs/loop/handover, status moved, no worker), :186... | - | - | - |
| MCH-4.3 | MCH-4 | done | settings.py:101 machine_sync private/off; machines.py:48 shared(), :84 stale (1800 s), :87 turn;... | - | - | - |
| MCH-4.4 | MCH-4 | done | machines.py:105 snapshot (JSON), :128 lines (one Machine line per peer from its SNAPSHOT), checki... | - | - | - |
| MCH-4.5 | MCH-8 | done | batch.py:312-340 cmd_adopt: needs pushed branch, done lines and OPEN PR, else refuses; flow = qa/... | - | - | - |
| INT-1.1 | INT-1 | partial | declared two ways: PRD source in .loop/docs.tsv and `milestones_source` in config; How-to-use-Integrations.md:39 "single registry is not built yet" | no registry (carries, direction, secrets, health rule per integration); mail, chat, agent, deploy not declared | 5225 (tests only) | G17 |
| INT-1.2 | INT-6 | missing | How-to-use-Integrations.md:44 "Planned ... not built yet"; searched skills/ for registry, adapter | no registry row path; a new system still needs loop code | 5225 (tests only) | G17 |
| INT-1.3 | INT-5 | partial | board.py:247 open_deltas (words --accept ...=repo/source); health.py:224 FAIL row per delta; rows sync-board-delta, sync-health-delta | no per-integration connection state on the board; an unreachable source is "not connected", not a finding (except UNREAD with no copy) | 5225 (tests only) | G17 |
| SET-1.1 | SET-1 | partial | update.py:296-315 sha256 per file, exact install, local fixes kept; sync.py generated files; set7 rows keep own files | adopted README principles not installed; DOC-23 says an adopting repo "keeps its own README" (contradicts o192) | - | G19 |
| SET-1.2 | SET-7 | n/a | records an owner decision (o192) resolving SET-1 vs SET-7; nothing to implement | - | - | - |
| SET-1.3 | SET-1 | partial | setup.py:139 adopt, seed.py:145 decide (config, pages, Home, Tests, regression.yml), health before/after; rows setup-both-halves PASS, set1-docs-fo... | scheduled regression only for public (workflow) or macOS launch agent (seed.py:196); Windows private repo needs machine.py apply | - | G19 |
| SET-1.4 | SET-7 | done | setup.py:195 dry run, :214 NO CHANGE; rows set7-dry-run-lists-all, set7-second-run-nothing | - | - | - |
| SET-1.5 | SET-9 | partial | survey.py:235 borrow(): settings and page shape; rows set9-from-borrows, set9-from-no-values | milestone layout skipped ("none made"); private rules and flow not borrowed ("no private file was read") | - | G19 |
| SET-1.6 | GRD-10 | partial | seed.py git_hooks installs the three private-name hooks on adopt; row grd10-install-hooks; defaults written to config | no listing of each guardrail installed; setup/health code never names "guardrail"; GRD-10 "not enforced" | - | G07 |
| SET-1.7 | SET-18 | done | setup.py:177 HEALTH START, :127 ADOPTION VERDICT; rows set1-health-bracket, set1-never-blocks, se... | - | - | - |
| SET-1.8 | SET-14 | partial | unattended.py:239 connectors reads wiki pages, prints OK or MISSING with fix, enables nothing; row adopt-connectors-probed (no run record) | no built-in read-only probe: state comes only from $LOOP_CONNECTOR_PROBE, unset reads as missing | - | G19 |
| SET-1.9 | SET-12 | partial | unattended.py:315 adopt(): --recent lists by pushedAt, named repos cloned, followed, set up or updated; row adopt-many-one-pass | no final board of exactly the chosen repos; repos file not reconciled to the choice | - | G19 |
| SET-4.1 | SET-21 | partial | SKILL.md rule: no skill code in repo; setup writes only .loop data, START.md, agent block, hooks calling installed private.py | no test or check names SET-21 (page "no passing test"); public regression.yml embeds script text (actions.py:60-80) | 5229 | G19 |
| SET-4.2 | SET-4 | done | update.py:275 check, :296 apply_skills; sync.py:197 apply_repo keeps config, pages, local setting... | - | - | - |
| SET-4.3 | SET-20 | done | setup.py:161 stamps template_version; entry.py:234 lag (none counts as 0), fit.py:258 refuses a n... | - | - | - |
| SET-4.4 | SET-16 | done | defects.py:267 migration_gaps, :314 main (exit 0 only with none, 1 gaps), :345 health Adoption ru... | - | - | - |
| SET-4.5 | SET-19 | done | sync.py:302-368 draft and run: update --propose --file-issue files a scrubbed issue on the templa... | - | - | - |
| SET-4.6 | - | missing | v2.0 planned; no staging or develop branch flow (git grep develop-staging: no hit) | everything (named only) | 4778 | G16 |
| SET-6.1 | SET-6 | partial | dev/toy/test-adopt-fixtures.sh (rows adopt-fixture-*), test-setup-fit.sh, dev/toy/repo; rows nightly, no run record | nothing forces a new fixture repo per adoption defect found | - | G19 |
| SET-6.2 | SET-11 | done | unattended.py:291 replay stops at first MISMATCH, step 8 never observed (exit 2); dev/toy/adoptio... | - | - | - |
| SET-6.3 | - | missing | v2.0 planned; no ci-trace-matrix, no CI replay of the 1,188 commands (git grep: no hit) | everything | - | G12 |
| SET-2.1 | SET-2 | partial | settings.py:230 resolve and :248 show print value, layer, home; settings-reference PASS; set2-layers-show (no run record) | each setting has one home, so a local value never overrides a repo value (survey.py:267 note) | - | G19 |
| SET-2.2 | SET-5 | done | entry.py:154 render, :282 write, :248 problems (pages and committed config only, no private read)... | - | - | - |
| DEL-3.1 | DEL-3 | done | fit.py depth_for; flow.py depth markers; rows pending-waits, auto-approved, depth-condensed-refus... | - | - | - |
| DEL-3.2 | OPS-11 | partial | auto.py:36-39 CLASSES; :77-91 why_not; row mon11-full-auto | classes are keyword regexes on the question text, not what the action does; no contradicts-my-words check (the steward-merge class now matches the README) | - | G05 |
| DEL-3.3 | OPS-11 | done | layers.py:194 relay, :206 defaults, sessions.py:243 OWNER-WORDS; toy test-three-level.py; caps: l... | - | - | - |
| DEL-3.4 | OPS-18 | partial | unattended.py:123-160 standing add/check/revoke (worker refused, per-goal IDs); auto.py:295 eta_record (record covers only its IDs); rows unattende... | nothing consults a standing merge instruction: merge.py and worker prompts never call `standing check`; page row "OPS-18 no passing test" | - | G05 |
| MCH-5.1 | MCH-5 | done* | notify.py:1-15 events, mailbox.py:70-110 numbered options, claim() shared ledger + notify_budget... | Mac notify_email still off (to-do) | 4710 | - |
| MCH-5.2 | CHK-3 | done* | notify.py (Needs you, stopped, past ETA, merged) via operate.py run; rows notify-new-events, noti... | rows are tagged CHK-2, none names CHK-3 | 5220 | - |
| MCH-5.3 | MCH-5 | done* | mailbox.py:cmd_reply BARE match, RISKY refuses bare number, operate.py send --source owner; row m... | RISKY is a keyword regex | - | - |
| MCH-5.4 | CHK-9 | partial | mailbox.py cmd_reply records text as owner words; mail carries question id | no sender check (own address or session); no start/stop/reorder by mail or phone; only mailed questions | 5220 | G05 |
| MCH-5.5 | AUT-4 | done | automation.py:5,286 pinned digest issue, mail.py digest by feature; rows aut-digest-create, aut-d... | - | - | - |
| CHK-1.1 | CHK-1 | done | live_board.py:1-12 (Issues, Running, Queued, Dependencies, Finish; no merged work; stuck first);... | - | - | - |
| CHK-1.2 | CHK-1 | missing | live_board.py:270-307 prints Issues, Running goals, Queued goals, Finish; no Your move, Release goals, Critical path, Workers | README layout (Your move, Release goals with progress, Critical path with clock ETAs, Workers) is not built; the README names a frozen board template until a board ski... | 4904 | G15 |
| CHK-1.3 | CHK-2 | done | board.py:133 cadence default 30, operate.py wakes on report, reply_hook.py:51,302-310 layout bloc... | - | - | - |
| CHK-1.4 | CHK-2 | done | layers.py:machine_reply (one line, STATUS within 30m), reply_hook.py:398,451 machine mode only; r... | - | - | - |
| CHK-1.5 | CHK-5 | done | board_status.py:277-282 release ETA and "not started" count; graph repo blocks; rows mon14-repo-b... | - | - | - |
| CHK-1.6 | CHK-6 | partial | checkin.py:168,219 other-machine questions read-only; machines.py:126-146 peer line from SNAPSHOT; row mon17-this-pod-only | other machines show one Machine line with slugs, not one row per goal with agent, step, status | - | G15 |
| OPS-2.1 | OPS-2 | done | sessions.py:292 cmd_report; operate.py send --source; rows session-reports, session-answer, worke... | - | - | - |
| OPS-2.2 | OPS-2 | done | watch.py/machines.py:147 start_worker (session first, else agent_command, app-only waits); rows s... | - | - | - |
| OPS-2.3 | OPS-2 | partial | layers.py:1-25, test-three-level.py (STATUS fields, 30 min, stale call-out); sessions.py:260 OWNER-WORDS | ASK, PRIORITY, MERGE-REQUEST, MERGE-GO have no code (merge order is the pr-turn ref); no check that a worker never messages top | - | G05 |
| REL-12.1 | REL-12 | done | review.py:38-43 REVIEW_HOLD, board_lines.py:366 "merge waiting on review"; rows review-hold-block... | - | - | - |
| REL-12.2 | AUT-10 | done | private.py statuses (commit statuses from the pr lane); rows st-pass, st-no-bypass, st-public-zer... | - | - | - |
| AUT-5.1 | AUT-5 | done | settings regression_cron/health_cron off; rows aut-regression-off, aut-off-by-hand, bad-schedule-... | - | - | - |
| AUT-5.2 | DOC-11 | done | docs.py:17-21 (publish never deletes, refuses unwritten page), :386 cmd_restore; rows refuse-repl... | - | - | - |

## Notes

- Evidence cells are cut to fit; the long form of every cell is in the six audit files kept with the goal's session notes.
- A done row with a caveat (`*`) means the behaviour exists and a test or page names it under another ID, or a limit is only reported, not enforced.
- `scripts-a-delivery-under-19000` and `scripts-a-monitoring-under-19000` are red on main today; nothing guards the three setup scripts over 19,000.
- Health's fallback `criteria_max` is 6 (rules.py:303) while the setting default is 10: a defect found on the way, not a README bullet.
- Only 708 of about 1,300 regression rows have a run record; I did not count a missing record as red.
