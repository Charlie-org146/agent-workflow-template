# Plan: v110-lvl-retire-old-words (G4 of Test levels), on origin/main 7c6d69ffd

TD2014 and TD2015 ruled the readings below. One item is STOPPED under TD2014's own condition (the record-proved row). The build does not start before it is ruled and the owner-pending safety items are answered.

Goal: one set of level words, L0, L1 and L2. Done lines (frozen, in the goal file): (1) the goal_levels setting, the PR workflow's level map and the Regression runbook's labels use L0, L1, L2 and none of land, nightly, covered, draft; (2) a draft row's mark is in its own state column, it carries the level it will have, every level lists it as "not run: draft", and a requirement held only by drafts shows "not enforced"; (3) a covered row takes the highest level of the rows its list names, is green when they all are, and a list that doesn't resolve to row IDs is refused; (4) every script stays under 20,480 bytes, no test is loosened, no row turns red, committed text never names the service repo; (5) a release cut waits for a green full (L2) run.

Owner records: o1008 (freeze the drafted lines 1, 2, 3 and 5; the old line 4 becomes its own goal); o996, verbatim: "Add the release cut's wait for a green full run to v110-lvl-retire-old-words." Design source: the owner-approved Test levels text, LVL-1.1, LVL-1.2, LVL-1.5 (o980, o985; not on main).

Size fields:
Files: skills/workflow-regression/scripts/levels.py, skills/workflow-regression/scripts/level_words.py, skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/runs.py, skills/workflow-regression/scripts/tiers.py, skills/workflow-regression/scripts/tests.py, skills/workflow-regression/scripts/actions.py, skills/workflow-regression/scripts/lanes_cli.py, skills/workflow-setup/scripts/settings.py, skills/workflow-setup/scripts/survey.py, skills/workflow-setup/scripts/seed.py, skills/workflow-release/scripts/l2wait.py, skills/workflow-release/scripts/autorelease.py, skills/workflow-release/scripts/release.py, skills/workflow-release/scripts/review.py, skills/workflow-docs/scripts/criteria.py, skills/workflow-docs/scripts/render.py, skills/workflow-docs/scripts/prd.py, skills/workflow-health/scripts/rules.py, skills/workflow-health/scripts/lean.py, skills/workflow-health/scripts/enforce.py, skills/workflow-health/scripts/health.py, skills/workflow-health/scripts/milestone.py, skills/workflow-delivery/scripts/cover.py, skills/loop-files.md, skills/workflow-regression/SKILL.md, .github/workflows/regression-pr.yml, .github/workflows/regression.yml, .github/workflows/release.yml, .loop/config.json, .loop/START.md, .loop/regression.tsv, .loop/regression-relevel.tsv, docs/wiki/Regression.md, docs/wiki/How-to-use-Regression.md, docs/wiki/How-to-use-Setup.md, dev/toy/test-level-words.py, dev/toy/test-l2-wait.py, dev/toy/test-tiers.sh, dev/toy/test-regression.sh, dev/toy/test-cover.sh, dev/toy/test-cover-lane.sh, dev/toy/test-l1-pr.py
Lines: about 900
Gates: a covered row whose list doesn't resolve to row IDs is refused, an old goal_levels value is refused, a release cut is held without a green L2 result
Classes: security (workflow files, including a new read permission in release.yml), destructive (the release path, o996's tag)

.loop/START.md and .loop/regression-relevel.tsv were outside the frozen touches; the operation added them (TD2015).

## Rulings and open items

### Line 5: TD2014's reading (under o1014)
"Release cut" is read in the vocabulary of the owner-approved LVL-1.2: the cuts that wait are the minor and major ones; a per-push patch release is not one. LVL-1.2, verbatim: "A minor or major release cut waits for a green L2 on its commit or a later one. A per-push patch release shows the latest L2 result and doesn't wait." So a minor or major waits, and a patch shows the latest L2 result and does not wait. Top lists this reading in its next check-in so the owner can revert it. Design D5 builds this reading.

### Line 3 STANDS (TD2014)
A covered row takes the highest level of the rows its list names. G1's plan (its line 79) forces a covered row tagged security or private to L1 and checks its covers only to resolve: a plan-wrong item for G1's build record. One edge remains for the reviewers: LVL-1.3 gives tagged rows a MINIMUM of L1, so this plan takes the highest level of the covers and never goes below that minimum; the two differ only when every cover of a tagged covered row is L0.

### The record-proved row done-pkg-secret-print-3: STOPPED under TD2014's condition
TD2014: it is plan-wrong for G4, fixed in G4's build under o1074 by giving the row its proper proof kind in place of "covered", with an approved-row-changes line citing TD2014, ON CONDITION that its proof stays checked exactly as strictly as now; if no proof kind keeps it that strict, the worker stops.
No such kind exists on 7c6d69ffd: the level values are land, nightly, draft and covered (regression.py:51) and the categories are criterion, workflow and defect. What checks this row today: it is never run (regression.py:274), exempt from the description rule (regression.py:183), never unmet in criteria (regression.py:205), shown as "by a person" (tests.py:35) and skipped by the major gate (review.py:123). Nothing in code reads its proof. Its command is prose: "proved by the 90-day search recorded in the goal's run record (ids kept in the git dir, not committed)". As land or nightly, no command can check a record that is not committed: it would be red or skipped on GitHub. This part of the plan is stopped, as TD2014 says, and waits for a new ruling (reported to the operation, 19:46).

### Line 4, "every script": TD2015's reading (under o1014)
"Every script stays under 20,480 bytes" means every PACKAGED script, checked by dev/package.py, which fails at 20,480 or more: the owner's package limit as A keeps it. No word changes. Top lists this reading so the owner can revert it. (Read literally over all scripts it is false on 7c6d69ffd and on A's head today: 27 scripts in dev/toy and dev/package.py are 20,480 bytes or more.)

Toys this goal edits or adds, with their size on 7c6d69ffd:
- dev/toy/test-tiers.sh: 14,312 bytes
- dev/toy/test-regression.sh: 25,383 bytes
- dev/toy/test-cover.sh: 18,027 bytes
- dev/toy/test-cover-lane.sh: 19,068 bytes
- dev/toy/test-l1-pr.py: G2's, not on main yet
- dev/toy/test-level-words.py and dev/toy/test-l2-wait.py: new

## Owner-pending safety items: the owner's own words before the build
Relayed words do not count (TD2002). All of these are pending:
- release.yml's new permission "actions: read" (a NEW workflow permission);
- release.yml's new trigger: it also runs when a scheduled regression run completes on main;
- this goal's DESTRUCTIVE class (the release path; o996 is tagged destructive);
- this goal's SECURITY class (workflow files).
Any other new workflow permission the build finds it needs is added to this list and asked the same way.

## Order and dependencies
The build waits for no-size-cap A and comes after G1 (the record file and levels.py), G2 and G3 (the L2 run and its verdict) (TD2015). The G2 dependency is real: G2 owns the L0 and L1 selection that goal_levels maps to, and its golden toy asserts that the PR template keeps "run @LEVELS@", which D2 changes. This plan is written against those three PLANS; before the build, every name below is re-read on main, and a changed interface stops the build for a plan amendment.
Taken from them: G1's record .loop/regression-relevel.tsv (id, old word, stage, risk, covers, seconds, reason, and a command hash), levels.py (join, check, STAGES) and the armed-table marker (G2's "lvl-armed"); G3's one line "L2_VERDICT <sha> red|incomplete|green" in the artifact l2-verdict, on main only, where no line means incomplete.

## Design

D1. Where the level lives. In an armed table the level is the record's stage column. Column 2 of regression.tsv keeps the old word, because dropping it is not in this goal (o1008). An UNARMED table (a repo with no record) behaves as today.

D2. Line 1's three surfaces.
a. goal_levels: the allowed values become L0 (default) and L1, selecting G2's L0 or L1 pick. An old value is refused with a code that names the file, the old value and the new one; nothing falls back silently (tiers.py:49 today treats any other value as land). settings.py, survey.py (its enum), tiers.py, .loop/config.json ("land" becomes "L0") and the setting's text in loop-files.md, START.md and How-to-use-Setup.md change.
b. "The PR workflow's level map" names no single object in the code. This plan reads it as what lanes_cli.py writes into regression-pr.yml (the template's "run @LEVELS@" at :209, filled at :321): on an armed repo the written target is L1. An unarmed repo's template is unchanged. ci_levels is named by no done line; it keeps its values and keeps driving the scheduled workflow. Any change to regression-pr.yml moves cover.py's WF_SHA in the same commit, as row-timeout did; G2's golden toy dev/toy/test-l1-pr.py asserts the shard command keeps "run @LEVELS@"; that assertion is updated and named. Two existing negative controls replace the text "run nightly --reuse --tier goal" in regression-pr.yml to prove the cover turns off (dev/toy/test-cover.sh:117-118, dev/toy/test-cover-lane.sh:91); their needle moves to the new word, so each still edits the file and still proves the same thing, and each is shown red with the old needle against the new workflow.
c. The Regression runbook: the "## Runbook" section of docs/wiki/Regression.md uses L0, L1 and L2, and none of the four old words appears in that section. A draft is described as a row whose state column says it is not ready.

D3. Line 2, drafts. The record gains a state column (blank or draft). A draft row's record stage is the level it will have ("add" of a draft requires --stage). Column 2 keeps "draft" for it ON PURPOSE: a reader this goal misses then still does not run it (fail closed). Every run at L0, L1 or L2 prints "not run: draft <id>" for every draft row, whatever the draft's stage, and the L2 summary lists drafts. A requirement held only by drafts shows "not enforced": the requirement page's tests table already does (criteria.py drops drafts before render.py), which a case now asserts; health's DRAFT line says "not enforced" too.
One existing assertion changes: dev/toy/test-regression.sh:117 fails today if a run names a draft at all. It becomes: the draft's id appears only in a "not run: draft" line and has no result line. It stays as strict about running a draft, and the PR body names it.

D4. Line 3, covered rows. The list is the record's covers column. In an armed table, reading refuses a covered row whose list is empty, or holds anything that is not a row ID of the table, naming the row and the entry. Its level is the highest stage among the covers (see Ruled). It is green only when every cover's latest recorded result is a pass (or known); otherwise it shows the worst of them. That result replaces "by a person" wherever covered rows are shown (tests.py's Runs column, criteria.py, render.py) and review.py's major gate, which today skips covered rows. An unreadable or missing result is not green.

D5. Line 5, the release wait (TD2014's reading). A new module l2wait.py answers one question: is there a green L2_VERDICT for this commit or a later one on the base branch? It reads the scheduled workflow's runs and their l2-verdict artifact. No verdict, red, incomplete or unreadable all mean "wait": it fails closed and prints the commit, what it found and the command that starts a full run.
- merge.py's path (autorelease.finish): a minor waits; a patch prints the latest L2 result.
- release.py cut: a minor waits.
- review.py promote (major): requires it in addition to today's local suite run.
- release.yml (push to main): it gains the permission "actions: read". For a minor or major it ends green, publishes nothing and says "held: waiting for L2 (sha)". So that a held minor is not lost on the next push, the part becomes the highest release label among the pull requests merged since the last release tag, not only the pushed commit's. So that a held release is not stuck when no further push comes, release.yml also runs when a scheduled regression run completes on main.
The permission and the new trigger are listed under SECURITY class above.

D6. Room under the package limit. On 7c6d69ffd: regression.py has 45 bytes, lanes_cli.py 32, criteria.py 25 (705 on A's head), milestone.py 87, survey.py 109, settings.py 194; G1 to G3 spend some. Where an edit would reach 20,480, whole functions move, bodies unchanged, into a sibling module (level_words.py in regression). These moves are consequences of the package rule (TD1987) and are named that way in the build record and the PR body. There is no byte-shaving (TD1246): no file is reformatted or trimmed to fit.

D7. Existing rows. goal-levels-nightly carries the old words, and del-16-linked tests for "covered" in column 2. A row line changes only if its meaning changes; each changed line gets its approved-row-changes line (the tasks-rows-only-added guard), stricter or equal, never looser.

## Tests (each red is the row's OWN assertion failing, quoted in the build record: TD2007)
New toys: dev/toy/test-level-words.py (lines 1, 2, 3; one named case each, on fixtures: main has 0 draft rows, so line 2 is testable ONLY on fixtures) and dev/toy/test-l2-wait.py (line 5, with gh stubbed: green on the commit, green later, red, incomplete, no verdict, unreadable). New rows, one per done line 1, 2, 3 and 5. Existing toys edited only where behaviour changes: test-tiers.sh (goal_levels), test-regression.sh (D3), test-cover.sh, test-cover-lane.sh and G2's golden toy test-l1-pr.py (D2 b). About 65 toys use the old words; they build unarmed fixtures, which D1 leaves unchanged. If one needs an edit that is not named here, the build stops and says why.
Line 4: dev/package.py passes; the sizes of edited toys are listed (O4).

## Verify by hand (delivery fills this in the goal file)

## Behavior changes
goal_levels refuses "land" and "nightly"; an armed repo's pull-request workflow runs "run L1"; a draft is printed as "not run: draft" at every level; a covered row shows a result instead of "by a person"; a minor or major release can be held; release.yml reads Actions runs, takes the part from every merge since the last tag, and also runs after a scheduled regression run.

## Not in scope
Dropping the old level column (its own goal, o1008). Changing ci_levels' values. Re-levelling any row. Changing unarmed repos. Reverting anything.
