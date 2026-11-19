# README conformance: the 38 issues moved to v2.0

Companion to `.loop/readme-gap-table.md` (bullet keys such as DEL-19.1 are rows there). Each issue is one of: **gap** (a README bullet is unmet; the closing cluster is named), **closed by** a goal the README already names, **close proposed** (needs the owner's words; nothing was closed here), or **README silent** (no bullet asks for it: the owner decides whether to add a requirement or move it to v2.1). Issue state is as read from the issue text; I did not re-measure CI or counts.

## Test-naming issues (#5219 to #5229)

Each says a requirement has no test row naming it. The tags below are the bullets that carry the ID; the audit reading says whether the behaviour exists. Where the behaviour is done the fix is only to name an existing row (net rows 0 or fewer); where it is not, a row naming it would be red, so the issue closes with the behaviour cluster.

| issue | IDs | bullets and status | reading | closes with |
|---|---|---|---|---|
| #5219 | AUT-10 | REL-12.2 done | behaviour done; naming gap only | naming goal (retag or name existing rows) |
| #5220 | CHK-3, CHK-4, CHK-9 | MCH-5.2 done, HLT-7.5 done, MCH-5.4 partial | naming gap plus behaviour gap (1 of 3 bullets) | naming goal after G05 |
| #5221 | DEL-18, DEL-19 | DEL-19.1 missing, DEL-19.2 missing, DEL-19.3 missing | naming gap plus behaviour gap (3 of 3 bullets) | naming goal after G06 |
| #5222 | DOC-20, DOC-21, DOC-22 | DOC-2.4 done, DOC-2.5 done, DOC-1.16 done, DOC-2.2 partial, DOC-2.3 done | naming gap plus behaviour gap (1 of 5 bullets) | naming goal after G18 |
| #5223 | GRD-15, GRD-16, GRD-17, GRD-18, GRD-19, GRD-20, GRD-22 | GRD-8.1 done, GRD-8.2 done, GRD-6.3 partial, GRD-7.2 partial, MCH-1.6 done, MCH-1.7 partial, HLT-11.3 done, GRD-20.1 partial, GRD-20.3 partial | naming gap plus behaviour gap (5 of 9 bullets) | naming goal after C01, G07, G14 |
| #5224 | HLT-11, HLT-12, HLT-13 | HLT-11.1 done, HLT-11.2 done, HLT-4.8 missing, HLT-2.16 partial | naming gap plus behaviour gap (2 of 4 bullets) | naming goal after G06 |
| #5225 | INT-1, INT-2, INT-4, INT-5, INT-6, INT-7, INT-8 | INT-1.1 partial, INT-2.1 done, GRD-5.2 partial, INT-1.3 partial, INT-1.2 missing, INT-7.1 done, INT-2.3 partial | naming gap plus behaviour gap (5 of 7 bullets) | naming goal after G02, G03, G17 |
| #5226 | OPS-20 | OPS-16.4 done | behaviour done; naming gap only | naming goal (retag or name existing rows) |
| #5227 | REG-11, REG-12, REG-13, REG-15, REG-16 | REG-7.2 done, REG-4.7 done, REG-4.8 missing, REG-9.4 missing, REG-9.5 missing | naming gap plus behaviour gap (3 of 5 bullets) | naming goal after G11 |
| #5228 | REL-11, REL-14 | DEL-1.7 partial, DEL-1.4 done | naming gap plus behaviour gap (1 of 2 bullets) | naming goal after G16 |
| #5229 | SET-21 | SET-4.1 partial | naming gap plus behaviour gap (1 of 1 bullets) | naming goal after G19 |

Name the existing rows in one goal (`tests-name-requirements`, net rows 0): the audits found the rows under other IDs (token-diet-*, notify-*, gate-*, del9-pr-refuses, stale-comments-only-3122).

## The other 27 issues

| issue | topic | README bullet(s) | state | goal or reason |
|---|---|---|---|---|
| #5239 | health checks the principles (HLT-14) | HLT-2.17, 2.18, 2.19, 2.20, 2.21, DEL-1.8 (all marked v2.0 planned) | gap | G08 health-principles and G09 plan-red-team. The title says v2.1 while the README says v2.0 planned: owner picks. |
| #5131 | restore the trimmed health explanation | none | README silent; close proposed | Debt from known-red-w8-size; the text is in git history and nothing requires a page. Propose defer to v2.1. |
| #5126 | confirm Agensi's size units | GRD-20.2 | gap (external fact) | G14 package-gate: read Agensi's page; the 30-day date rule and the owner-words gate are the code part. Title says v2.1. |
| #5124 | GRD-22: a goal added a file over the package cap | GRD-20.3 | gap | G14: qa says room left and what would free it. |
| #5123 | fold files to bring headroom to 98 | HLT-11.4, GRD-20.3 | gap | G13 size-trims-19000 and G14; every fold costs a script's bytes. |
| #5079 | declare milestones_source as a setting | INT-2.3 | gap | G02 adopter-upgrade-fixes (small; migration-check flags it MIG_SETTINGS today). |
| #5078 | DOC-19: own-repo GitHub image links count as inside | DOC-1.14 | gap | G02 adopter-upgrade-fixes. |
| #4914 | release gate for every major | REL-3.1 to REL-3.10 | closed by named goal | Gate, waivers, snapshot, promote, revert are done (REL-3.2 to 3.9); REL-3.1 partial and REL-3.10 release-readiness open: G16. Close when release-readiness lands. |
| #4904 | report-v2: one shared status view | CHK-1.2, CHK-1.6, MCH-5.4 | gap | G15 board-v2 (owner design question: the board skill) and G05 for reply commands. |
| #4830 | token-diet: wake accounting, 300k ceiling, 30% report | none (nearest GRD-8.1, HLT-7.5, both done) | README silent | Owner record o104 has no requirement bullet. Owner: add one, or move to v2.1. |
| #4829 | token-diet C6/C7: goal.py pr and flow qa/ship block until done | none | README silent | Same as #4830. |
| #4828 | token-diet C1/C5: restart operation session, fresh worker per goal | none (nearest OPS-1.9 done, DEL-7.4 partial) | README silent | Same as #4830. |
| #4788 | token-diet: 30% fewer tokens | none | README silent | Parent of #4828 to #4830; same decision. |
| #4813 | operation session sets up its own check-in timer and hook | OPS-1.4 | close proposed | OPS-1.4 done: notify.py:256 timer_lines, unattended.py loop RECREATE, rows unattended-loop-recreate and unattended-sends-warn. |
| #4784 | docs self-contained, with a system diagram | DOC-1.14, DOC-1.1 | gap (partly) | Home has the System diagram; the own-repo link rule is G02; the sweep of external links and machine paths has no bullet: owner decides. |
| #4783 | every open issue closed or placed in a v2.x release | HLT-4.7 (conflicts) | close proposed | Process task, finished when the close list from this goal is applied. HLT-4.7 keeps a standing Backlog milestone per feature while this issue retires them: owner picks. |
| #4781 | hands-off operation: rebind workers, one approval batch | DEL-7.4, MCH-5.4, OPS-2.3, DEL-3.4 | gap | G05 owner-decisions-by-action and G20 delivery-small-fixes. |
| #4778 | release-channels: staging branch, rc tags, promotion | SET-4.6 (develop-staging), REL-3.7 | closed by named goal | develop-staging is planned in the README; the design goes to the owner first: G16. |
| #4710 | Mac: turn on notify_email | MCH-5.2 (done on PC) | close proposed | Off-machine to-do; the PC owns all repos and the Mac runs only steward cleanup, so the Mac sends no operation mail. |
| #4702 | regression tidy-up near a cap | none (nearest REG-7.1, GRD-20.3) | README silent | Owner plan o90 has no bullet. Owner: add one, or move to v2.1. |
| #4701 | every open defect names its regression row | none (nearest HLT-4.3, REG-1.1) | README silent | Same as #4702. |
| #4700 | per-row time limit max_row_seconds | none (nearest REG-7.1, HLT-11.1) | README silent | Same as #4702. |
| #4682 | public-repo regression off GitHub Actions (o86) | AUT-1.1, AUT-1.2 | conflict: owner decides | README still says public regression runs in Actions and on every tag; REL-3.4 and ci-shards-unrun0 depend on CI runs; code follows the README. Amend AUT-1, or close as superseded. |
| #4653 | seven scripts over 19,000 bytes | HLT-11.4 | close proposed | The scripts the issue names (auto, checkin, pool, replan, controls, judge, runs, docs) are all under 19,000 now (known-red-w8-size and later trims). A different set of 12 delivery, monitoring and setup scripts is over the line: that is G13 size-trims-19000, not this issue. |
| #4556 | CI regression: cause not read for 29 rows | REG-4.9 (ci-shards-unrun0), REL-3.10 | closed by named goal | Folded into #4516; closes with ci-shards-unrun0 and release-readiness once the red-row count is zero. |
| #4516 | 100 rows fail on Linux CI, cause unknown | REG-4.9, REL-3.10 | closed by named goal | Same: G12 and G16. State is from the issue (baseline 2026-11-15), not re-measured. |
| #4507 | one clean prompt starts an operation session | OPS-1.4, MCH-1.1 | close proposed | OPS-1.4 and MCH-1.1 done: unattended.py:219 prerequisites, notify.py readiness, pool ask-to-fill. |

## Close list (for the owner, one message)

Nothing was closed. Closes need the owner's words:

- **Delivered, close:** #4813, #4507 (OPS-1.4, MCH-1.1 done). #4710 (the PC owns all repos). #4783 once this list is applied.
- **Defer or close:** #5131 (nothing requires the page).
- **Owner decision first (README silent):** #4788, #4828, #4829, #4830 (token-diet o104); #4700, #4701, #4702 (o90). Add a requirement each, or move to v2.1.
- **Owner decision first (README conflicts):** #4682 (AUT-1 versus o86); #5239 (v2.1 title versus v2.0 planned text).
- **Delivered, close:** also #4653 (its seven scripts are under 19,000 now).
- **Close when a named goal lands:** #4556 and #4516 (ci-shards-unrun0, release-readiness), #4914 (release-readiness), #4778 (develop-staging).
- **Stay open as gaps:** the 11 test-naming issues until the behaviour or the naming lands; #5126, #5124, #5123, #5079, #5078, #4904, #4784, #4781.
