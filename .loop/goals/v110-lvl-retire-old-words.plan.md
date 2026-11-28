# Plan: v110-lvl-retire-old-words (G4 of Test levels), on origin/main 7c6d69ffd

The owner ruled the two open readings (o1034, "approve the G4 readings by ID"): line 5 holds minor and major releases only, and line 3's one record-proved row is excused by its ID. The build still waits for the owner's record on the safety items below and for A, G1, G2 and G3.

Goal: one set of level words, L0, L1 and L2. Done lines (frozen, in the goal file): (1) the goal_levels setting, the PR workflow's level map and the Regression runbook's labels use L0, L1, L2 and none of land, nightly, covered, draft; (2) a draft row's mark is in its own state column, it carries the level it will have, every level lists it as "not run: draft", and a requirement held only by drafts shows "not enforced"; (3) a covered row takes the highest level of the rows its list names, is green when they all are, and a list that doesn't resolve to row IDs is refused; (4) every script stays under 20,480 bytes, no test is loosened, no row turns red, committed text never names the service repo; (5) a release cut waits for a green full (L2) run.

Owner records: o1008 (freeze the drafted lines 1, 2, 3 and 5; the old line 4 becomes its own goal); o996, verbatim: "Add the release cut's wait for a green full run to v110-lvl-retire-old-words." Design source: the owner-approved Test levels text, LVL-1.1, LVL-1.2, LVL-1.5 (o980, o985; not on main).

Size fields:
Files: skills/workflow-regression/scripts/levels.py, skills/workflow-regression/scripts/level_words.py, skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/runs.py, skills/workflow-regression/scripts/tiers.py, skills/workflow-regression/scripts/tests.py, skills/workflow-regression/scripts/actions.py, skills/workflow-regression/scripts/lanes_cli.py, skills/workflow-setup/scripts/settings.py, skills/workflow-setup/scripts/survey.py, skills/workflow-setup/scripts/seed.py, skills/workflow-release/scripts/l2wait.py, skills/workflow-release/scripts/autorelease.py, skills/workflow-release/scripts/release.py, skills/workflow-release/scripts/review.py, skills/workflow-docs/scripts/criteria.py, skills/workflow-docs/scripts/render.py, skills/workflow-docs/scripts/prd.py, skills/workflow-health/scripts/rules.py, skills/workflow-health/scripts/lean.py, skills/workflow-health/scripts/enforce.py, skills/workflow-health/scripts/health.py, skills/workflow-health/scripts/milestone.py, skills/workflow-delivery/scripts/cover.py, skills/loop-files.md, skills/workflow-regression/SKILL.md, .github/workflows/regression-pr.yml, .github/workflows/regression.yml, .github/workflows/release.yml, .loop/config.json, .loop/START.md, .loop/regression.tsv, .loop/regression-relevel.tsv, docs/wiki/Regression.md, docs/wiki/How-to-use-Regression.md, docs/wiki/How-to-use-Setup.md, dev/toy/test-level-words.py, dev/toy/test-l2-wait.py, dev/toy/test-tiers.sh, dev/toy/test-regression.sh, dev/toy/test-cover.sh, dev/toy/test-cover-lane.sh, dev/toy/test-l1-pr.py, dev/toy/test-shard-balance.py, dev/toy/test-tree-first.py, dev/toy/test-release-ci.py, skills/workflow-release/SKILL.md
Lines: about 1150
Gates: a covered row whose list doesn't resolve to row IDs is refused, a goal_levels value that is neither a level nor an old word is refused on an armed table, a minor or major release is held without its own green L2 result, an unreadable release part or verdict fails the release job
Classes: security (workflow files, including a new read permission in release.yml), destructive (the release path, o996's tag)

.loop/START.md and .loop/regression-relevel.tsv were outside the frozen touches; the operation added them (TD2015).

## Readings and rulings

### Line 5, "a release cut": RULED (o1034)
LVL-1.2's reading: "A minor or major release cut waits for a green L2 on its commit or a later one. A per-push patch release shows the latest L2 result and doesn't wait." Minor and major releases wait; a patch release does not. D5 is the design.

### Line 3 STANDS (TD2014; TD2020)
A covered row takes the highest level of the rows its list names. A covered row tagged security or private may name only covers that carry the tag (D4, LEVELS_COVERS_RISK). Under G1's rule a tagged row is exactly L1, so the highest level of such a row's covers is L1: line 3 and G1's rule both hold, with no exception between them.

### The row done-pkg-secret-print-3: RULED, by ID (o1034)
The row is covered, and its proof is a run record, not a row: "proved by the 90-day search recorded in the goal's run record (ids kept in the git dir, not committed)". It names no row. D4 excuses that one row by its ID, bound to its goal and its command text.

### Line 4, "every script": TD2015's reading (under o1014)
"Every script stays under 20,480 bytes" means every PACKAGED script, checked by dev/package.py, which fails at 20,480 or more: the owner's package limit as A keeps it. No word changes. Top lists this reading so the owner can revert it. (Read literally over all scripts it is false on 7c6d69ffd and on A's head today: 27 scripts in dev/toy and dev/package.py are 20,480 bytes or more.)

Toys this goal edits or adds, with their size on 7c6d69ffd:
- dev/toy/test-tiers.sh: 14,312 bytes
- dev/toy/test-regression.sh: 25,383 bytes
- dev/toy/test-cover.sh: 18,027 bytes
- dev/toy/test-cover-lane.sh: 19,068 bytes
- dev/toy/test-l1-pr.py: G2's, not on main yet
- dev/toy/test-shard-balance.py: 16,850 bytes
- dev/toy/test-tree-first.py: 8,394 bytes
- dev/toy/test-release-ci.py: 5,370 bytes
- dev/toy/test-level-words.py and dev/toy/test-l2-wait.py: new

## Safety items for the owner: the owner's own words before the build
Staged when the plan is recorded (TD2066); relayed words do not count (TD2002). No build before that owner record exists. One line each:
- S1 (.github/, security): release.yml gets a new permission, "actions: read", to read the full test run's result.
- S2 (.github/, security): release.yml also starts when a regression run completes on main, scheduled or dispatched, and in that run it can create a release with the write permission it already has (D5.5 a).
- S3 (.github/, destructive): release.yml changes when it publishes: a minor or major waits for its own green full run, the release's size comes from every pull request merged since the last release, and the job fails if it can't read them.
- S4 (destructive): the merge step's own release (autorelease.py) creates a minor or major at a commit with its own green full run, or stops without publishing.
- S5 (destructive): release.py cut refuses a minor from a goal branch.
- S6 (destructive): review.py promote refuses a major whose commit has no green full run of its own.
- S7 (.github/, security): regression-pr.yml, the pull request check, runs the L1 level under its new name, and ci_levels no longer changes it.
- S8 (.github/, security): regression.yml, the scheduled test workflow, is regenerated so it knows the new level names and drafts; this goal changes none of its triggers or permissions.
Any other new workflow permission, trigger or release behavior the build finds it needs is added to this list and asked the same way.

## Reviewed pages
A page holds a Reviewed requirement when a requirement line on it is marked "**Reviewed <date>**". On 7c6d69ffd none of the wiki pages in Files has one: Regression.md, How-to-use-Regression.md and How-to-use-Setup.md; the generated Tests page, which new rows change, has none either. The new rows name this goal's own done lines, so no requirement page's tests table gains a row; the changed row goal-levels-nightly is shown on Regression.md, and del-16-linked on no requirement page. So no Reviewed page is expected in the diff. If the diff would change one, the build stops and says so, and the pull request then also waits for the owner at merge.

## Order and dependencies
The build waits for no-size-cap A and comes after G1 (the record file and levels.py), G2 and G3 (the L2 run and its verdict) (TD2015). The G2 dependency is real: G2 owns the L0 and L1 selection that goal_levels maps to, and its golden toy asserts that the PR template keeps "run @LEVELS@", which D2 changes. This plan is written against those three PLANS; before the build, every name below is re-read on main, and a changed interface stops the build for a plan amendment.
Taken from them: G1's record .loop/regression-relevel.tsv (id, old word, stage, risk, covers, seconds, reason, and a command hash), levels.py (join, check, STAGES) and the armed-table marker (G2's "lvl-armed"); G3's one line "L2_VERDICT <sha> red|incomplete|green" in the artifact l2-verdict, on main only, where no line means incomplete.

## Design

D1. Where the level lives. In an armed table the level is the record's stage column. Column 2 of regression.tsv keeps the old word, because dropping it is not in this goal (o1008). An UNARMED table (a repo with no record) behaves as today, and nothing in this plan changes what it runs or releases.

D2. Line 1's three surfaces.
a. goal_levels and adopters. The documented values are L0 (the default for new repos) and L1. setup has written the default "land" into adopters' configs (settings.py:44, :274-289), so old values are read, never silently:

| held value | armed table | unarmed table |
|---|---|---|
| "land" | read as L0 (G2's land to L0 pick) | land, as today |
| "nightly" | read as L1 | nightly, as today |
| "L0" or "L1" | itself | L0 runs as land, L1 as nightly |
| anything else | refused | runs as today (tiers.py:49 reads it as land), and now prints a warning |

An old value on an armed table prints one line each run: `SETTINGS (GOAL_LEVELS_OLD): goal_levels "land" in .loop/config.json is read as L0. Fix: set "goal_levels": "L0" and commit it.` Another value on an armed table: `REFUSED (GOAL_LEVELS_BAD): goal_levels is <value, quoted, cut at 40 characters> in .loop/config.json; the values are L0 and L1. Fix: set one there and commit it. Nothing was run.` on stderr, non-zero, before any work; cover.py passes this code through instead of reporting PLAN. setup update rewrites "land" to "L0" and "nightly" to "L1" with a printed line; survey's enum accepts old and new while borrowing. This reading of line 1 (TD2020, under o1014): "none uses the words" covers what is written and documented; code that reads an old value only to replace it, saying so, does not use it. Tests: a config written by today's setup goes through fill_repo, sync, borrow and a run, unarmed and armed. This repo's config changes "land" to "L0".

b. "The PR workflow's level map" names no single object in the code. This plan reads it as what lanes_cli.py writes into regression-pr.yml (the template's "run @LEVELS@" at :209, filled at :321): on an armed repo the written target is L1. An unarmed repo's template is unchanged. ci_levels stops steering the pull-request run on an armed repo and keeps steering the scheduled workflow only.
Everywhere the runner branches on "land" or "nightly" as a TARGET, L0, L1 and L2 take the same branches. The first is regression.py:308-310: the memory wait and the run slot apply only to "land", "nightly" or named ids, so "run L1" alone would skip both. That gate would fail open, so its case is shown red before the fix.
Files that follow: cover.py's WF_SHA moves in the same commit as any change to regression-pr.yml; dev/toy/test-shard-balance.py (:173, :226) and dev/toy/test-tree-first.py move to the rendered L1 line with checks just as strict; G2's golden toy dev/toy/test-l1-pr.py asserts the shard command keeps "run @LEVELS@", and that assertion is updated and named; the two negative controls that replace "run nightly --reuse --tier goal" (dev/toy/test-cover.sh:117-118, dev/toy/test-cover-lane.sh:91) move their needle to the new word, and each is shown red with the old needle against the new workflow.

c. The Regression runbook: the "## Runbook" section of docs/wiki/Regression.md uses L0, L1 and L2, and none of the four old words appears in it. It names only targets that work. Every place an old word must still be typed is listed in one old-to-new table in How-to-use-Regression.md. A draft is described as a row whose state column says it is not ready.

D3. Line 2, drafts.
- The record gains a state column, appended LAST. A missing cell reads as blank, so G1's records still read. Only blank or "draft"; anything else is refused (LEVELS_BAD_STATE).
- A draft row's record stage is the level it will have. Column 2 keeps "draft" ON PURPOSE: a reader this goal misses then still does not run it. The two must agree, checked both ways (LEVELS_STATE_MISMATCH).
- Make one: `regression.py add <id> --draft --stage L1 ...`. No --stage is refused (LEVELS_NO_STAGE) with the accepted values and the whole command to paste, before either table changes.
- Ready one: `regression.py level <id> --ready` clears the state and writes column 2 itself from the stage. It refuses a draft with no command. sync --write drafts get stage L1 and state draft, and its message names this command.
- `level` reads state and covers without the checks, validates before writing and prints what it changed. If one table write succeeds and the other fails, the next read's mismatch refusal names the one command that reconciles them.
- Every reader of the record is listed in the build record and tested against a line WITHOUT the new column: levels.py, G3's reader, the embedded scheduled runner. Union-merged duplicate lines stay G1's LEVELS_DUPLICATE.
- Every run at L0, L1 or L2 prints "not run: draft <id>" for every draft row, whatever its stage, and the L2 summary lists drafts. A requirement held only by drafts shows "not enforced": the requirement page's table already does (criteria.py drops drafts before render.py), which a case now asserts; health's DRAFT line says it too.
- One existing assertion changes: dev/toy/test-regression.sh:117 fails today if a run names a draft at all. It becomes: the draft's id appears only in its "not run: draft" line and has no result line. It is as strict about running a draft.

D4. Line 3, covered rows. The list is the record's covers column. In an armed table, reading refuses:
- LEVELS_BAD_COVERS: the list is empty, or an entry is not a row ID of the table (names the row and the entry);
- LEVELS_COVERS_COVERED: an entry is itself a covered row, a self-link included, so there is no chain or cycle (main has none today);
- LEVELS_COVERS_RISK: a covered row tagged security or private names a cover without that tag. An existing case is fixed by tagging the cover (a tightening) or goes to the owner.
Each refusal prints on stderr, exits non-zero, says nothing was changed and ends `Fix: regression.py level <id> --covers <row ids>`. `level` is never blocked by what it repairs. When no row can prove the claim: stop and ask the owner; never guess a cover.

The one excused row (o1034): one fixed entry in levels.py names done-pkg-secret-print-3 and its owner record. It applies only when all three match exactly: the id, the goal (v110-pkg-secret-print:3) and the command text (by hash). The row is then not refused for naming no row, takes no level from a list, and keeps today's five behaviors: never run (regression.py:274), no description needed (:183), never unmet in criteria (:205), shown as "by a person" (tests.py:35), skipped by the major gate (review.py:123). Each time it applies a line prints: `EXCEPTED <id>: covered with no row list, by <record id>`. All three are bound because a row ID is free text: bound to the ID alone, any row given that ID would be excused. Limits: a pull request run executes the branch's own scripts, so a branch that adds an entry excuses itself in that run and only review of that code change catches it; GitHub cannot check the owner record, because the ledger is never committed; a packaged script carries one repo's row, and adopters cannot declare their own. G1 creates levels.py and its build meets this row first (it has no hand mapping for it), so the same entry goes in with G1 and G4 reuses it.

Green, bound to a commit. For commit C a covered row is green only when every cover has PASS recorded FOR C. A result for another commit does not count. Shown state is the worst of its covers, in this order: FAIL, FLAKY, no result for C (LEFT included), SKIPPED, KNOWN, PASS. KNOWN is shown as known, never as green. review.py's major gate, which skips covered rows today, evaluates a covered row through its covers by the rule it uses for any row: PASS on HEAD from proven(), else it runs the cover's command; a cover on the known list is treated as the gate treats it today and is printed "via known cover <id>". That is stricter. A committed page cannot hold a result for its own commit, so the Runs column and the wiki pages never print a bare "green": they print the worst state with its commit and date, or "no result recorded".

D5. Line 5, the release wait. New module skills/workflow-release/scripts/l2wait.py. It applies only to an armed table; an unarmed repo releases as today.

D5.1 What waits. A release's changes are everything between the last release tag and the commit being released. Its part is the highest mark among them. A release of patch changes only is a patch release: it never waits. A release holding any minor or major change is a minor or major release: it waits.
CONSEQUENCE, stated for the owner: while a minor is held, a later patch is released on top of it, so that release holds the minor's code and waits with it. The other choice would ship the held code under a patch number, with no full run.

D5.2 What is published. Only a commit that has its OWN green L2 result: the tag, the package and the notes are made from that commit. A held minor is published at a green commit that contains it. This is the strict form of "on its commit or a later one": a later green commit is released as itself and never certifies an earlier one that is then shipped.

D5.3 What counts as green. Only: a run of this repository's regression workflow, started by schedule or by dispatch, on the base branch, from this repository, whose l2-verdict artifact holds G3's one line "L2_VERDICT <sha> green" with <sha> equal to that run's head commit. Everything else is not green. States, each with its own code, message and next step: L2_PENDING (no such run for the commit yet); L2_RUNNING (one is in progress: it prints the run's address and says wait, and prints NO start command, because the workflow's group cancels a run in progress, regression.yml:22-24); L2_RED; L2_INCOMPLETE; L2_UNREADABLE (a gh, permission, transport, artifact or parse failure, with the cause cleaned of secrets). The command that starts a full run is printed only when none is running.

D5.4 Marks. A change's mark is the release:minor or release:major label on its merged pull request. Today autorelease.label_part adds it only when merge_queue is true (:355), and this repo has merge_queue false while release.yml reads the label: a minor is read as a patch here. The label is now added whenever the part is minor or major, and a failure to add it stops merge.py before the merge. release.yml reads the labels of every pull request merged in the release's changes, page by page. A failed or cut-short lookup FAILS the job (L2_PARTS_UNREADABLE). The "|| true" that turns a failed lookup into a patch is removed. One existing assertion changes: dev/toy/test-release-ci.py:83 expects no label without merge_queue; it becomes a label for minor and major and none for patch. Limit: a pull request merged by hand with no label counts as a patch.

D5.5 Each route.
a. release.yml, the publisher this repo's recent tags come from. It runs on push to main as today, and ALSO when a regression run completes on main (new trigger, owner-pending). The main-red hold stays first and unchanged. The candidate is the pushed commit, or on a completed run that run's head commit; it is checked out by that id, and the package is built from it. A candidate the latest tag already contains is skipped. A patch release publishes as today and prints the latest L2 result, on a completed run too, whatever that run's result. A minor or major publishes only with its own green result. Held for L2_PENDING, L2_RUNNING, L2_RED or L2_INCOMPLETE, the job ends green, as the main-red hold does (o672), with a warning annotation and a job summary that start "NOT RELEASED", naming the code and the commit; nothing is tagged or created. L2_UNREADABLE and L2_PARTS_UNREADABLE FAIL the job: they are faults, not waits. A held release resumes by itself: the next qualifying run publishes it (the schedule is every four hours). The release job's concurrency stays (no cancel).
b. merge.py with merge_queue false (autorelease.finish). For a minor or major, the check comes BEFORE the release commit is pushed. With a green commit that contains the merge, it creates the release at that commit, with the next version from the latest tag and no VERSION commit (as the merge_queue path already does). A release release.yml already made at that commit is adopted. How the two publishers share patch releases today is not changed. Otherwise it stops through the existing fail() path with RELEASE_L2_HELD: non-zero, nothing pushed or created, the pull request already merged (it says so), the wiki not published, and the next step "run merge.py <slug> again after a green run". The batch path calls finish() before it records "released" (machines.py:202-207), so a stop there leaves the batch unreleased. A patch is unchanged and prints the latest L2 result.
c. release.py cut (a draft from a goal branch, before the merge). L2 runs on the base only, so a goal branch has no result. On an armed table, a minor cut is refused before any write (L2_CUT_ON_BRANCH): "Nothing changed. L2 runs on main only. Merge the goal; its minor is released from main when L2 is green. If this repo has no automatic release path, ask the owner." It does not offer a patch cut. A patch cut is unchanged and prints the latest L2 result. A major is already refused (MAJOR_GATE).
d. review.py promote (a major). The promoted commit must itself have a green result, which only a base commit can have. A release candidate or staging commit that is not on the base is refused (L2_NOT_ON_MAIN): merge it, wait for L2, promote that commit. This is added to today's local suite run.
e. An armed repo with no workflow that produces L2 results: every minor and major stays held as L2_PENDING, saying no qualifying run exists.

D5.6 No override. No flag or setting releases a minor or major without its own green result. A different need goes to the owner.

D6. Room under the package limit. On 7c6d69ffd: regression.py has 45 bytes, lanes_cli.py 32, criteria.py 25 (705 on A's head), milestone.py 87, survey.py 109, settings.py 194, review.py 1,492, autorelease.py 1,554, release.py 2,141; G1 to G3 spend some. The release check itself lives in l2wait.py. Where an edit would reach 20,480, whole functions move, bodies unchanged, into a sibling module (level_words.py in regression). These moves are consequences of the package rule (TD1987) and are named that way in the build record and the PR body. There is no byte-shaving (TD1246).

D7. Existing rows. goal-levels-nightly carries the old words, and del-16-linked tests for "covered" in column 2. A row line changes only if its meaning changes; each changed line gets its approved-row-changes line, stricter or equal, never looser.

## Tests (each red is the row's OWN assertion failing, quoted in the build record: TD2007)
New toys, run in an isolated clone with its own home (TD1965): dev/toy/test-level-words.py (lines 1, 2, 3; fixtures, because main has no draft row) and dev/toy/test-l2-wait.py (line 5, GitHub stubbed). New rows, one per done line 1, 2, 3 and 5.
test-level-words.py holds a named case for: each goal_levels table cell; the memory wait and run slot under L0, L1 and L2; each draft refusal, the ready command and a record line with no state column; each covers refusal; a second prose-covered row refused; the excused id with another goal or another command refused (red with an ID-only match); green only for the commit asked about.
test-l2-wait.py holds a named case for: each D5.3 state; each way a run does not qualify (other event, branch, repository, or commit mismatch); a patch after a held minor waits with it; a green later commit is published as itself; a failed or cut-short label lookup fails and never reads patch; finish() held pushes and creates nothing and exits non-zero, and the batch is not recorded released; a minor cut refused with nothing written; promote refusing a commit with no result; an unarmed repo unchanged. Each rule is shown red on a build without it.
Existing toys edited only where behavior changes: test-tiers.sh (goal_levels), test-regression.sh (D3), test-cover.sh, test-cover-lane.sh, test-shard-balance.py, test-tree-first.py and G2's test-l1-pr.py (D2 b), test-release-ci.py (D5.4). dev/toy/test-release-hold.py must pass unchanged: every release.yml step after the main-red hold keeps its hold condition. About 65 toys use the old words; they build unarmed fixtures, which D1 leaves unchanged. If one needs an edit not named here, the build stops and says why.
Line 4: dev/package.py passes; the sizes of edited toys are listed.

## Verify by hand (delivery fills this in the goal file)

## Behavior changes
- goal_levels: old values are read with a notice on an armed table; another value is refused there, and warned about on an unarmed one; setup update rewrites old values.
- An armed repo's pull-request workflow runs "run L1"; ci_levels no longer steers it. L0, L1 and L2 are run targets.
- Drafts print "not run: draft <id>"; adding one needs --stage; the record gains a state column.
- A bad covers list stops reads of an armed table (add, level and sync still repair it); covered rows join the major gate and show a state instead of "by a person".
- A minor or major release can be held; a later patch waits with a held minor. release.yml gains "actions: read", also runs when a regression run completes on main, reads every merged pull request's label since the last tag, and fails if it can't.
- merge.py releases a minor or major at a green commit without a VERSION commit; a minor cut from a goal branch is refused; promote needs a commit with its own green result.

## Not in scope
Dropping the old level column (its own goal, o1008). Changing ci_levels' values. Re-levelling any row. Changing unarmed repos' runs or releases. An override of the release wait. A machine-readable hold status. Reverting anything.

## Review record
The earlier outside reviews of the previous text ran gpt-6.1-sol, which is not the plan-review policy's model. Both were rerun on gpt-6-astra; all replies are kept in the goal's review notes, and every one of them rejected that text. This text is reviewed anew.
