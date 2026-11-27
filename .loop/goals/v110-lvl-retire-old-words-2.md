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
