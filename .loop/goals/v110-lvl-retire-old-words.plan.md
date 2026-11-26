# Plan: v110-lvl-retire-old-words (G4 of Test levels), on origin/main 7c6d69ffd

DRAFT. Not yet reviewed. It carries OPEN items that wait for a ruling; no review or red team starts before top answers, and the build does not start before every open item is ruled.

Goal: one set of level words, L0, L1 and L2. Done lines (frozen, in the goal file): (1) the goal_levels setting, the PR workflow's level map and the Regression runbook's labels use L0, L1, L2 and none of land, nightly, covered, draft; (2) a draft row's mark is in its own state column, it carries the level it will have, every level lists it as "not run: draft", and a requirement held only by drafts shows "not enforced"; (3) a covered row takes the highest level of the rows its list names, is green when they all are, and a list that doesn't resolve to row IDs is refused; (4) every script stays under 20,480 bytes, no test is loosened, no row turns red, committed text never names the service repo; (5) a release cut waits for a green full (L2) run.

Owner records: o1008 (freeze the drafted lines 1, 2, 3 and 5; the old line 4 becomes its own goal); o996, verbatim: "Add the release cut's wait for a green full run to v110-lvl-retire-old-words." Design source: the owner-approved Test levels text, LVL-1.1, LVL-1.2, LVL-1.5 (o980, o985; not on main).

Size fields:
Files: skills/workflow-regression/scripts/levels.py, skills/workflow-regression/scripts/level_words.py, skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/runs.py, skills/workflow-regression/scripts/tiers.py, skills/workflow-regression/scripts/tests.py, skills/workflow-regression/scripts/actions.py, skills/workflow-regression/scripts/lanes_cli.py, skills/workflow-setup/scripts/settings.py, skills/workflow-setup/scripts/survey.py, skills/workflow-setup/scripts/seed.py, skills/workflow-release/scripts/l2wait.py, skills/workflow-release/scripts/autorelease.py, skills/workflow-release/scripts/release.py, skills/workflow-release/scripts/review.py, skills/workflow-docs/scripts/criteria.py, skills/workflow-docs/scripts/render.py, skills/workflow-docs/scripts/prd.py, skills/workflow-health/scripts/rules.py, skills/workflow-health/scripts/lean.py, skills/workflow-health/scripts/enforce.py, skills/workflow-health/scripts/health.py, skills/workflow-health/scripts/milestone.py, skills/workflow-delivery/scripts/cover.py, skills/loop-files.md, skills/workflow-regression/SKILL.md, .github/workflows/regression-pr.yml, .github/workflows/regression.yml, .github/workflows/release.yml, .loop/config.json, .loop/START.md, .loop/regression.tsv, .loop/regression-relevel.tsv, docs/wiki/Regression.md, docs/wiki/How-to-use-Regression.md, docs/wiki/How-to-use-Setup.md, dev/toy/test-level-words.py, dev/toy/test-l2-wait.py, dev/toy/test-tiers.sh, dev/toy/test-regression.sh
Lines: about 900
Gates: a covered row whose list doesn't resolve to row IDs is refused, an old goal_levels value is refused, a release cut is held without a green L2 result
Classes: security (workflow files, including a new read permission in release.yml), destructive (the release path, o996's tag)

.loop/START.md and .loop/regression-relevel.tsv are outside the frozen touches; the operation widens them before the build.

## OPEN items (a ruling is pending; each reading states what the build does)

### O1, owner ruling pending: done line 5, "a release cut"
The line is unqualified. LVL-1.2, verbatim: "A minor or major release cut waits for a green L2 on its commit or a later one. A per-push patch release shows the latest L2 result and doesn't wait." release.yml releases on every push to main.
- Reading A (recommended, LVL-1.2): minor and major cuts wait; a patch release prints the latest L2 result and does not wait. It narrows the line's words.
- Reading B (the line's words alone): every cut waits, patches too; each merge's release then waits for a later L2 run.
Design D5 is written for A. Under B the same check also gates every patch path.

### O3, owner ruling pending: done line 3 and the row done-pkg-secret-print-3
It is covered, and its proof is a run record, not a row: "proved by the 90-day search recorded in the goal's run record (ids kept in the git dir, not committed)". It has no list of row IDs, so line 3 refuses it, while line 4 allows no row to turn red. main has 24 covered rows; G1's plan assumes 23. No recommendation: every fix changes the row or reads line 3 around it. Choices: (a) the owner rules how a row proved by a record is marked; (b) a new row that really proves it, which the covered row then lists; (c) the row is retired with the owner's words.

### O4, ruling pending: done line 4, "every script"
Read as written it is false on main today and on no-size-cap A's head: 27 scripts in dev/toy and dev/package.py are 20,480 bytes or more. No packaged script (skills/) is.
- Reading A (recommended; the rule A keeps, "20 KB per packaged script"): every packaged script is under 20,480 bytes, checked by dev/package.py, which fails at 20,480 or more. The build record lists every toy this goal edits with its size.
- Reading B (the words, literally, all scripts): the line cannot be met without splitting 28 files that this goal has no reason to touch.

## Ruled: done line 3 stands (operation-mac 19:39)
A covered row takes the highest level of the rows its list names. G1's plan (its line 79) forces a covered row tagged security or private to L1 and checks its covers only to resolve; this is flagged for G1's build record. One edge remains for the reviewers: LVL-1.3 gives tagged rows a MINIMUM of L1, so this plan takes the highest level of the covers and never goes below that minimum; the two differ only when every cover of a tagged covered row is L0.

## Order and dependencies
The build waits for: no-size-cap A; G1 (the record file and levels.py); G3 (the L2 run and its verdict); and G2 too. The G2 dependency is real: G2 owns the L0 and L1 selection that goal_levels maps to, and its golden toy asserts that the PR template keeps "run @LEVELS@", which D2 changes. This plan is written against those three PLANS; before the build, every name below is re-read on main, and a changed interface stops the build for a plan amendment.
Taken from them: G1's record .loop/regression-relevel.tsv (id, old word, stage, risk, covers, seconds, reason, and a command hash), levels.py (join, check, STAGES) and the armed-table marker (G2's "lvl-armed"); G3's one line "L2_VERDICT <sha> red|incomplete|green" in the artifact l2-verdict, on main only, where no line means incomplete.

## Design

D1. Where the level lives. In an armed table the level is the record's stage column. Column 2 of regression.tsv keeps the old word, because dropping it is not in this goal (o1008). An UNARMED table (a repo with no record) behaves as today.

D2. Line 1's three surfaces.
a. goal_levels: the allowed values become L0 (default) and L1, selecting G2's L0 or L1 pick. An old value is refused with a code that names the file, the old value and the new one; nothing falls back silently (tiers.py:49 today treats any other value as land). settings.py, survey.py (its enum), tiers.py, .loop/config.json ("land" becomes "L0") and the setting's text in loop-files.md, START.md and How-to-use-Setup.md change.
b. "The PR workflow's level map" names no single object in the code. This plan reads it as what lanes_cli.py writes into regression-pr.yml (the template's "run @LEVELS@" at :209, filled at :321): on an armed repo the written target is L1. An unarmed repo's template is unchanged. ci_levels is named by no done line; it keeps its values and keeps driving the scheduled workflow. Any change to regression-pr.yml moves cover.py's WF_SHA in the same commit, as row-timeout did; G2's golden toy assertion for "run @LEVELS@" is updated and named.
c. The Regression runbook: the "## Runbook" section of docs/wiki/Regression.md uses L0, L1 and L2, and none of the four old words appears in that section. A draft is described as a row whose state column says it is not ready.

D3. Line 2, drafts. The record gains a state column (blank or draft). A draft row's record stage is the level it will have ("add" of a draft requires --stage). Column 2 keeps "draft" for it ON PURPOSE: a reader this goal misses then still does not run it (fail closed). Every run at L0, L1 or L2 prints "not run: draft <id>" for every draft row, whatever the draft's stage, and the L2 summary lists drafts. A requirement held only by drafts shows "not enforced": the requirement page's tests table already does (criteria.py drops drafts before render.py), which a case now asserts; health's DRAFT line says "not enforced" too.
One existing assertion changes: dev/toy/test-regression.sh:117 fails today if a run names a draft at all. It becomes: the draft's id appears only in a "not run: draft" line and has no result line. It stays as strict about running a draft, and the PR body names it.

D4. Line 3, covered rows. The list is the record's covers column. In an armed table, reading refuses a covered row whose list is empty, or holds anything that is not a row ID of the table, naming the row and the entry. Its level is the highest stage among the covers (see Ruled). It is green only when every cover's latest recorded result is a pass (or known); otherwise it shows the worst of them. That result replaces "by a person" wherever covered rows are shown (tests.py's Runs column, criteria.py, render.py) and review.py's major gate, which today skips covered rows. An unreadable or missing result is not green.

D5. Line 5, the release wait (reading O1-A). A new module l2wait.py answers one question: is there a green L2_VERDICT for this commit or a later one on the base branch? It reads the scheduled workflow's runs and their l2-verdict artifact. No verdict, red, incomplete or unreadable all mean "wait": it fails closed and prints the commit, what it found and the command that starts a full run.
- merge.py's path (autorelease.finish): a minor waits; a patch prints the latest L2 result.
- release.py cut: a minor waits.
- review.py promote (major): requires it in addition to today's local suite run.
- release.yml (push to main): it gains the permission "actions: read". For a minor or major it ends green, publishes nothing and says "held: waiting for L2 (sha)". So that a held minor is not lost on the next push, the part becomes the highest release label among the pull requests merged since the last release tag, not only the pushed commit's. So that a held release is not stuck when no further push comes, release.yml also runs when a scheduled regression run completes on main.
The permission and the new trigger are safety changes: they need the owner's own words before the build.

D6. Room under the package limit. On 7c6d69ffd: regression.py has 45 bytes, lanes_cli.py 32, criteria.py 25 (705 on A's head), milestone.py 87, survey.py 109, settings.py 194; G1 to G3 spend some. Where an edit would reach 20,480, whole functions move, bodies unchanged, into a sibling module (level_words.py in regression). These moves are consequences of the package rule (TD1987) and are named that way in the build record and the PR body. No file is reformatted to fit.

D7. Existing rows. goal-levels-nightly carries the old words, and del-16-linked tests for "covered" in column 2. A row line changes only if its meaning changes; each changed line gets its approved-row-changes line (the tasks-rows-only-added guard), stricter or equal, never looser.

## Tests (each red is the row's OWN assertion failing, quoted in the build record: TD2007)
New toys: dev/toy/test-level-words.py (lines 1, 2, 3; one named case each, on fixtures: main has 0 draft rows, so line 2 is testable ONLY on fixtures) and dev/toy/test-l2-wait.py (line 5, with gh stubbed: green on the commit, green later, red, incomplete, no verdict, unreadable). New rows, one per done line 1, 2, 3 and 5. Existing toys edited only where behaviour changes: test-tiers.sh (goal_levels), test-regression.sh (D3), G2's golden toy (D2 b). About 65 toys use the old words; they build unarmed fixtures, which D1 leaves unchanged. If one needs an edit that is not named here, the build stops and says why.
Line 4: dev/package.py passes; the sizes of edited toys are listed (O4).

## Verify by hand (delivery fills this in the goal file)

## Behavior changes
goal_levels refuses "land" and "nightly"; an armed repo's pull-request workflow runs "run L1"; a draft is printed as "not run: draft" at every level; a covered row shows a result instead of "by a person"; a minor or major release can be held; release.yml reads Actions runs, takes the part from every merge since the last tag, and also runs after a scheduled regression run.

## Not in scope
Dropping the old level column (its own goal, o1008). Changing ci_levels' values. Re-levelling any row. Changing unarmed repos. Reverting anything.
