# Plan: v110-lvl-retire-old-words-3 (G4 of Test levels), on origin/main d25f31e5d (G1 merged)

Carried from v110-lvl-retire-old-words-2 (TD2444, TD2446; o1096): this is -2's plan, unedited but for the slug. Its branch could not push because the pre-push guard reads the goal slug from the worktree folder. -2's plan sha256 is 74759ce735602b2e3160dd906f879ee2eaac3f49a2229e4fa5f00e7d3ffff708 (a887f81687e82db93f483f702439f6253d17d9a3). Base now: origin/main e2fa360a9 (G2 #5938 and G3 #5941 merged), where the line above names d25f31e5d; -2's code was built on the merged re-levelling.

Goal: one set of level words, L0, L1 and L2. Done lines (frozen, in the goal file): (1) the goal_levels setting, the PR workflow's level map and the Regression runbook's labels use L0, L1, L2 and none of land, nightly, covered, draft; (2) a draft row's mark is in its own state column, it carries the level it will have, every level lists it as "not run: draft", and a requirement held only by drafts shows "not enforced"; (3) a covered row takes the highest level of the rows its list names, is green when they all are, and a list that doesn't resolve to row IDs is refused; (4) every script stays under 20,480 bytes, no test is loosened, no row turns red, committed text never names the service repo.

This goal replaces v110-lvl-retire-old-words. That goal's line 5 (a release cut waits for a green full run, owner record o996) is split into its own later goal (TD2201, TD2098). Nothing here changes when or what a release publishes. Owner record for these four lines: o1008. Design source: the owner-approved Test levels text, LVL-1.1 and LVL-1.5 (o980, o985; not on main). The earlier plan stays in git as history only.

Size fields:
Files: skills/workflow-regression/scripts/levels.py, skills/workflow-regression/scripts/levels_read.py, skills/workflow-regression/scripts/levels_cli.py, skills/workflow-regression/scripts/levels_write.py, skills/workflow-regression/scripts/level_words.py, skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/runs.py, skills/workflow-regression/scripts/tiers.py, skills/workflow-regression/scripts/tests.py, skills/workflow-regression/scripts/lanes_cli.py, skills/workflow-regression/scripts/actions.py, skills/workflow-setup/scripts/settings.py, skills/workflow-setup/scripts/survey.py, skills/workflow-docs/scripts/criteria.py, skills/workflow-docs/scripts/render.py, skills/workflow-health/scripts/enforce.py, skills/workflow-release/scripts/review.py, skills/workflow-delivery/scripts/cover.py, skills/loop-files.md, skills/workflow-regression/SKILL.md, .github/workflows/regression-pr.yml, .github/workflows/regression.yml, .loop/config.json, .loop/START.md, .loop/regression.tsv, .loop/regression-relevel.tsv, docs/wiki/Regression.md, docs/wiki/How-to-use-Regression.md, docs/wiki/How-to-use-Setup.md, dev/toy/test-level-words.py, dev/toy/test-tiers.sh, dev/toy/test-regression.sh, dev/toy/test-cover.sh, dev/toy/test-cover-lane.sh, dev/toy/test-shard-balance.py, dev/toy/test-tree-first.py
Lines: about 600
Gates: a covered row whose list doesn't resolve to row IDs is refused, a goal_levels value that is neither a level nor an old word is refused on a levelled table
Classes: destructive (the release path: skills/workflow-release/scripts/review.py, whose major gate D4 makes stricter), security (workflow files), risky path ^\.github/

The two workflow files, .loop/START.md, .loop/regression-relevel.tsv and level_words.py are added to the goal's touches through goal.py; the workflow files rest on the owner's record below.

## What G1 already does (on d25f31e5d)
A table is levelled when .loop/regression-relevel.tsv exists or the table holds lvl-armed. The record's columns are id, old, level, risk, covers, seconds, cmdhash, reason, and parse_record (levels.py:96) refuses a line without exactly eight cells. The table's own level cell keeps the old words, which still select what runs. For line 3, G1 already refuses a covered row whose list is empty, names itself, an unknown row or a covered row, or (when tagged) an untagged cover (LEVELS_BAD_COVERS), and computes a covered row's level from its covers (covered_level; L1 at least when tagged). Two rows with no covers are excused by fixed entries bound to id, goal and command (levels.py EXCUSED: done-pkg-secret-print-3, which G1 records as operation decision TD2022 and the earlier G4 plan records as ruled by the owner by ID in o1034, and done-gap-wave1-small-4, owner record o988); each read prints EXCEPTED. G1 has no draft row to handle and leaves the draft state column, the goal_levels words, the PR level map and the runbook labels to this goal; it leaves "green when all its covers are" to G2.

## Order and dependencies
G1 and the size-limit removal are merged. The build waits for G2 (v110-lvl-l1: running by level, the L0 and L1 selection, a covered row green when its covers are) to be merged, and for G3 (v110-lvl-l2) as far as D2's scheduled-workflow edit needs its selection by level. Neither is on main. Before the build every name here is re-read on main; a changed interface stops the build for a plan amendment. Work G2 or G3 already did is not done again: this goal then adds only its own case for the done line.

## Design

D1. Where the level lives. In a levelled table the level is the record's level cell. Column 2 of regression.tsv keeps the old word: dropping it is its own goal. A table that is not levelled behaves as today, and nothing here changes what it runs.

D2. Line 1's three surfaces.
a. goal_levels. The documented values are L0 (the default) and L1 (settings.py:43). A repo set up before may hold "land" or "nightly", so old values are read, never silently:

| held value | levelled table | table not levelled |
|---|---|---|
| "land" | read as L0 | land, as today |
| "nightly" | read as L1 | nightly, as today |
| "L0" or "L1" | itself | L0 runs as land, L1 as nightly |
| anything else | refused | runs as today (tiers.py:49 reads it as land) and now prints a warning |

An old value on a levelled table prints one line each run: `SETTINGS (GOAL_LEVELS_OLD): goal_levels "land" in .loop/config.json is read as L0. Fix: set "goal_levels": "L0" and commit it.` Another value on a levelled table: `REFUSED (GOAL_LEVELS_BAD): goal_levels is <value, quoted, cut at 40 characters> in .loop/config.json; the values are L0 and L1. Fix: set one there and commit it. Nothing was run.` on stderr, non-zero, before any work; the local cover passes this code through. setup update rewrites "land" to "L0" and "nightly" to "L1" with a printed line; survey's enum (survey.py:213) accepts old and new while borrowing. "None uses the words" covers what is written and documented; code that reads an old value only to replace it, saying so, does not use it. This repo's config changes to the new word.
b. "The PR workflow's level map" names no single object in the code. This plan reads it as what lanes_cli.py writes into regression-pr.yml (the template's "run @LEVELS@" at :202, filled at :314): for a levelled repo the written target is L1. The template of a repo that is not levelled is unchanged. ci_levels (settings.py:49) stops steering the pull-request run of a levelled repo and keeps its values and its other uses.
Everywhere the runner branches on "land" or "nightly" as a target, L0 and L1 take the branches of the selection they stand for, from G2's level selection: regression.py:300 and :302 (memory wait and run slot) and runs.py:279-282 (row choice). If "run L1" skipped the memory wait and the slot, that gate would fail open, so its case is shown red before the fix.
Files that follow: cover.py's WF_SHA (:31) moves in the same commit as any change to regression-pr.yml; dev/toy/test-shard-balance.py and dev/toy/test-tree-first.py move to the rendered L1 line with checks just as strict; a G2 toy that asserts the shard command keeps "run @LEVELS@" is updated and named; the negative controls that replace "run nightly --reuse --tier goal" (dev/toy/test-cover.sh:117-118, dev/toy/test-cover-lane.sh:91) move their needle to the new word, each shown red with the old needle against the new workflow. regression.yml is regenerated from actions.py (:93-100 read "land|nightly") so it knows the level targets and drafts; its triggers and permissions don't change.
c. The Regression runbook: the "## Runbook" section of docs/wiki/Regression.md uses L0, L1 and L2, and none of the four old words appears in it. It names only targets that work. Every place an old word must still be typed is listed in one old-to-new table in How-to-use-Regression.md. A draft is described as a row whose state column says it is not ready.

D3. Line 2, drafts.
- The record gains a state column, appended last: blank or "draft"; anything else is refused (LEVELS_BAD_STATE). parse_record accepts eight cells (state blank) or nine, so records written before this goal still read; every writer writes nine.
- A draft row's level cell in the record is the level it will have. Column 2 of the table keeps "draft" on purpose: a reader this goal misses then still doesn't run it. State and column 2 must agree, checked both ways (LEVELS_STATE_MISMATCH).
- Make one: `regression.py add <id> --level draft --test-level L1 ...`. Without --test-level it is refused (LEVELS_NO_STAGE) with the accepted values and the whole command, before either table changes. sync --write drafts get L1 and state draft, and its message names the command that readies them.
- Ready one: `regression.py level <id> --ready` clears the state and sets column 2 from the level. It refuses a draft with no real command. `level` reads state without that check, validates before writing and prints what it changed; the two-file write uses G1's pending-mark path.
- Every reader of the record is listed in the build record and tested against an eight-cell line, G3's reader and the generated scheduled runner included.
- Every run at L0, L1 or L2 prints "not run: draft <id>" for every draft row, whatever its level, and the L2 summary lists drafts. A requirement held only by drafts shows "not enforced" on its page (criteria.py leaves drafts out before render.py, which a case asserts) and in health (enforce.py), and sync's DRAFT line says it.
- One existing assertion changes: dev/toy/test-regression.sh:117 fails today if a run names a draft at all. It becomes: the draft's id appears only in its "not run: draft" line and has no result line. It is as strict about running a draft.

D4. Line 3, covered rows. The level and the refusal are G1's (above) and are kept as they are; this goal adds a case for each part of the done line against them: highest level, empty list, unknown id, self, covered cover, and a second row with no covers refused. The excused entries stay as G1 holds them, and this goal adds none. A cover that is a draft makes its covered row not green.
Green, bound to a commit. For commit C a covered row is green only when every cover has PASS recorded for C; a result for another commit doesn't count. Shown state is the worst of its covers, in this order: FAIL, FLAKY, no result for C (LEFT and draft included), SKIPPED, KNOWN, PASS. KNOWN is shown as known, never as green. G2 builds this rule; if G2 merged without part of it, this goal builds that part. review.py's major gate, which skips covered rows today (:123), evaluates a covered row through its covers by the rule it uses for any row: a PASS on HEAD already proven, else it runs the cover's command; a cover on the known list is treated as the gate treats it today and is printed "via known cover <id>". That is stricter. A committed page can't hold a result for its own commit, so the Runs column and the wiki pages never print a bare "green": they print the worst state with its commit and date, or "no result recorded".

D5. Room under the package limit. On d25f31e5d, bytes left: regression.py 248, lanes_cli.py 85, survey.py 187, settings.py 696, criteria.py 705, actions.py 1,458, review.py 1,492, runs.py 1,571, tests.py 1,663, tiers.py 1,333, cover.py 3,301. G2 and G3 spend some. This plan asks for one new script, level_words.py (the goal_levels reading, the level targets and the draft lines). Where an edit would reach 20,480, whole functions move into it, bodies unchanged, and the move is named in the build record and the pull request body. No byte-shaving.

D6. Existing rows. goal-levels-nightly carries the old words, and del-16-linked tests for "covered" in column 2, which stays. A row line changes only if its meaning changes; each changed line gets its approved-row-changes line, stricter or equal, never looser.

## Safety items (approved: owner record o1062)
Owner record o1062 approves editing .github/workflows/regression-pr.yml and regenerating regression.yml for the level map. release.yml is not in this goal. The numbers are the ones already sent to the owner.
- S7 (.github/, security): regression-pr.yml, the pull request check, runs the L1 level under its new name, and ci_levels no longer changes it.
- S8 (.github/, security): regression.yml, the scheduled test workflow, is regenerated so it knows the new level names and drafts; this goal changes none of its triggers or permissions.
Any other new workflow permission or trigger the build finds it needs is added to this list and asked the same way. D4 makes review.py's major gate stricter and loosens nothing.

## Reviewed pages
A page holds a Reviewed requirement when a requirement line on it is marked "**Reviewed <date>**". The build checks every wiki page in its diff. None is expected to hold one; if one would change, the build stops and says so, and the pull request then also waits for the owner at merge.

## Tests (each red is the row's own assertion failing, quoted in the build record: TD2007)
New toy dev/toy/test-level-words.py, run in an isolated clone with its own home (TD1965), with fixtures because main has no draft row. New rows, one per done line 1, 2 and 3. It holds a named case for: each goal_levels table cell; the memory wait and run slot under L0 and L1; each draft refusal, the ready command, an eight-cell record line and the state mismatch both ways; "not run: draft" at each level; "not enforced" for a drafts-only requirement; each part of line 3 (D4); green only for the commit asked about, and a draft cover not green. Each new rule is shown red on a build without it; a case on a rule G1 or G2 already built is shown red by breaking that rule in the isolated clone.
Existing toys are edited only where behavior changes: test-tiers.sh (goal_levels), test-regression.sh (D3), test-cover.sh, test-cover-lane.sh, test-shard-balance.py and test-tree-first.py (D2 b). Toys that build tables that are not levelled keep the old words, which D1 leaves working. If another toy needs an edit not named here, the build stops and says why.
Line 4: dev/package.py --static passes on every code commit; no packaged script reaches 20,480 bytes; the sizes of edited toys are listed.

## Verify by hand (delivery fills this in the goal file)

## Behavior changes
- goal_levels: old values are read with a notice on a levelled table; another value is refused there and warned about elsewhere; setup update rewrites old values.
- A levelled repo's pull-request workflow runs "run L1"; ci_levels no longer steers it. L0 and L1 are run targets.
- Drafts print "not run: draft <id>"; adding one needs --test-level; the record gains a state column.
- Covered rows join the major gate and show a state.

## Not in scope
Line 5 and anything about releases waiting for a full run. Dropping the old level column. Changing ci_levels' values. Re-levelling any row. Changing the runs of repos that are not levelled. Reverting anything.

## Review record
The earlier goal's outside reviews ran models that are not the plan-review policy's, or read earlier text. This text is reviewed anew, with the outside reader on the policy model (TD2061).
