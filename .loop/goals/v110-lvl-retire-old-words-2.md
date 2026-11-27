# One set of level words: L0, L1, L2

- Slug: v110-lvl-retire-old-words-2
- Touches: skills/workflow-regression, skills/workflow-setup, skills/workflow-delivery, skills/workflow-health, skills/workflow-docs, skills/workflow-release, skills/loop-files.md, dev/toy, .loop/regression.tsv, .loop/config.json, docs/wiki, .github/workflows/regression-pr.yml, .github/workflows/regression.yml, .loop/START.md, .loop/regression-relevel.tsv, skills/workflow-regression/scripts/level_words.py
- ETA: 1060 active minutes (estimate 848m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the goal_levels setting, the PR workflow's level map and the Regression runbook's labels, when they are read, then each uses the levels L0, L1 and L2 and none uses the words land, nightly, covered or draft.
2. Given a draft row, when the table is read, then its draft mark is in its own state column, it carries the level it will have, every level lists it as "not run: draft", and a requirement held only by drafts shows "not enforced".
3. Given a covered row, when the table is read, then it takes the highest level of the rows its list names and is green when they all are, and a covered row whose list doesn't resolve to row IDs is refused.
4. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Notes

- NOTE, line (4): "every script stays under 20,480 bytes" means every packaged script, checked by dev/package.py (TD2015's reading, carried over by TD2209).
- Line (3) is met with the two covered rows excused on record (o988, TD2022) named in the pull request as exceptions (TD2209).
- Line (5) of the earlier goal v110-lvl-retire-old-words (the release cut's wait for a green full run, o996) is split into its own later goal (TD2201).

## Later work

- Build: give the covered rows done-gap-wave1-small-4 and done-pkg-secret-print-3 real covers lists, and then drop their two fixed entries in levels.py (deliver-first; TD2209).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

- After the upgrade, every row is re-picked once by entry_moved (the 9th state cell makes each line differ); this runs more rows, never fewer.
- This repo ran land (720 rows) before; L1 plans from 778 rows, a superset. nightly = L2 (747, the same set). D2a's reviewed table (land -> L0) was corrected under TD2334 because it planned from 3 rows.
- test-level-words.py, the settings case: its expected config word is changed to match (L0 to L1), not weakened; that one assertion edit was not seen red on its own.
- Departure: `setup update` does not rewrite an old goal_levels word yet; the sync commit's only seams are sync.py (private-scans A's file, TD1609) and settings.py (no room, TD1987). The run-time GOAL_LEVELS_OLD line names the value to set. Filed as a deliver-first line.
- skills/workflow-regression/scripts/tiers.py is 19,163 B after this goal: over the 19,000 B warning, under the 20,480 B limit.
- dev/toy/test-regression.sh line 117 (TD162): it was `$reg run nightly | grep -q add-median && bad "ran a draft"` and is now: no line naming add-median other than `not run: draft add-median-[12]` may appear, and `not run: draft add-median-1` is required. It is as strict about running a draft; the not-run line names the id, so the old "no line at all" could not stay.
- R6: "not run: draft <id>" repeats once per shard in the scheduled runner's log (cosmetic).
- R6: not_run is also copied into the summary job's l2 text (regression.yml, second copy) without a call there; it is dead text from the shared copied block. It is called once, in the run step, before the row loop.
- R6: actions.py is 20,466 B, 14 B under the 20,480 B cap.
- Hand-running dev/toy/test-regression.sh prints FAIL lines ("FAIL flag" four times, "labels on", "label create fails", "label on issue fails", "hostile: label create ..."). They are harness-only and the same on main e2fa360a9, run by hand in a clone with its own HOME (env -i, no --live); the rows that call the toy pass through the tool. Main's clone run shows three more, on main only: "shard split", "cron setting", "bad cron written".
- regression.py is 20,471 B after this goal, 9 B under the 20,480 B cap (actions.py 20,466 B, 14 B under).
- R5 need_stage keys on levelled(), not armed(): it is input validation, not what runs. levels_write.edit accepts --test-level exactly on a levelled table (LEVELS_NOT_LEVELLED otherwise), so the stage may be required exactly there; on armed() a levelled-but-unarmed table would take --test-level yet not require it. G1 has no existing stage rule for add (grep of the scripts finds none).
- R8/R13: regression-runs.tsv gains a sixth cell, the commit a result ran at; every reader indexes cells 0 to 4 or by name (runs.py, tests.py, render.py, audit.py, rules.py, board_lines.py, autorelease.py), file-level users (lanes.py, lanekit.py, operate.py, role.py) read no cell, and mend_tables.py unions 5-cell and 6-cell lines by id and keeps the later date (case mixedruns, a guard that passed first time). Limit: two lines of one id with the same date that differ (old and new format, or two commits) are left to the person merging, as already happens when the run cell differs.
- R8 (3): in CI tests.py runs without level_words, so a covered row shows its own recorded state. That state CAN be greener than the local worst-of-covers: a covered row with a stale own PASS in regression-runs.tsv shows PASS in CI while its cover fails and the local page shows FAIL (case swallow, both lines asserted). A covered row never runs, so it has such a record only from before this goal.
- R17: dev/toy/test-regression.sh:117 now requires the exact "not run: draft" line (and no other line naming the draft) and a following assertion shows the draft's command did not execute (a marker file stays absent), by level and by row id. Red: with regression.py changed so a draft is run by row id, the toy printed "FAIL: a draft's command executed"; the change was reverted.
- unarmed tables: a covered row now shows no result instead of its stale own record
- R11: on an armed table a row called L0, L1 or L2 is picked by the level and not by its id in the scheduled runner, as regression.py run has done since G2 (runs.py:265, "a row named like a level never replaces the run"); on an unarmed table the runner keeps the row-id reading (L1 is only the row called L1; L0 is refused). A row with no record entry runs at L1, not L0 (the safe side), in completion.pick and in the runner's level_pick (compared as functions in test-l2.py; a valid table has no such row, every run refuses LEVELS_NO_ENTRY).
- Deliver-first: one queued item stays stuck in runs/v110-lvl-retire-old-words-2.dlf.json (rel ".loop/goals/v110-lvl-retire-old-words-2.md": the label "deliver-first:" plus that path is 56 characters, over GitHub's 50-character limit, so it can never be created; each retry fails one call and posts nothing). It was left and the runs file not edited (TD2352). Its text was filed again under rel "default" as choice-2 (https://github.com/Charlie-org146/agent-workflow-template/issues/5917#issuecomment-7223264939); the three lines about dlf itself are choice-3, -4 and -5 on the same issue.
- R8 (CI display) and the runbook: the local Tests page shows a covered row as the worst state of its covers; CI shows no result (deliver-first choice-2).
- R11 and local/CI: a missing levels record is refused by the CI runner (NO_RECORD) while locally completion.entries returns {} and every row reads as L1, so CI is stricter; on unarmed tables a target named L1 is the row called L1 in CI and the level locally (runs.py:265).
- dev/toy/test-runbook.sh (repo part), old assertion: the Regression runbook, anywhere in the routine's text, contains 'draft and covered' (with 'exits 77', 'not a full run', 'feature_labels'). New assertion: the same three needles stay, and the Full run field line itself must contain both 'not ready' and 'proved by' (one line, asserted: "the Full run field does not say which rows a full run leaves out"); the page without that parenthetical fails it. The runbook sentence it matches: "(a row whose state says it is not ready is named in a `not run` line and never run, and a row proved by its covers is not run itself; a by-hand run at L0 or L1 runs fewer rows and is not a full run)". It is changed to match, not weakened: done line 1 takes the four old words out of the runbook. It failed first on the new page: "FAIL: Regression's regression-round runbook says a full run is live and a fixture never stands in".
- S7: regression-pr.yml changes one line, `run nightly --reuse --tier goal` to `run L1 --reuse --tier goal`, written by lanes_cli.py through level_words.pr_target (L1 on an armed table, else ci_levels or nightly as before); triggers, permissions, concurrency, jobs and steps are unchanged (case prlevel asserts the armed and unarmed files differ only in that line). R12 on this repo's table: the pull request run's row set is 778 ids before (nightly resolved to L1 by tiers.py when armed) and 778 after, 0 dropped, 0 added; a non-pull-request run of the old text would have been 747 ids, no job runs that path.
- S7/R14: cover.py's WF_SHA is a tuple of exactly two reviewed shas, 533fbed6... (the nightly-line text, kept so a table that is not armed stays covered) and 19b5c86b... (the L1-line text); a third edited text is still COVER OFF (case wfpin). COVER OFF: WF now prints the fix (regression.py workflow, then commit regression-pr.yml and merge it); update.py reports an old generated workflow on an armed table (WORKFLOW line, saying ci_levels is ignored there).
- S7 toy needles, changed to match and not weakened (TD162), each red first (the old needle against the new workflow: `assert a in t` fails, rows cover-claim and cover-lane FAIL; with the cover's sha check forced True both still FAIL): dev/toy/test-cover.sh:117 `wf "run nightly --reuse --tier goal" "run nightly --tier goal"` -> `wf "run L1 --reuse --tier goal" "run L1 --tier goal"`; :118 `... "run nightly --reuse --tier goal --ids example-row"` -> `"run L1 --reuse --tier goal --ids example-row"`; dev/toy/test-cover-lane.sh:91 `... --kind defect` the same; dev/toy/test-shard-balance.py:173,226 and dev/toy/test-tree-first.py:107 render the template with "L1" where they rendered "nightly".
- shard-balance red only in its docs step (11 REWRITE pages, STALE; Tests tables), cleared by the pr step's docs refresh; main shows DOCS OK; already red at db52af842, S7 makes it less red. Its full output in a clone of HEAD plus S7 has exactly two FAIL lines, both the docs step ("a pull request whose docs pass passes the docs step", "the fixture's Reviewed requirement passes the docs step before it is changed"), and 25 PASS lines. At the pr step shard-balance must be green after the refresh. The UNTESTED lines docs.py audit prints (CHP-1, CBS-1, DEL-17, DEL-22, DEL-23, DEL-27, DEL-28, DOC-28) are other goals' and pre-existing.
