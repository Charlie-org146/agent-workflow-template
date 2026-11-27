# Task 18 goal 1, Lighter plans (owner o1095): the plan step runs the forms its row of the size table lists, in full for a large goal or one touching a safety class, with the round rule in REVW-5's words (REVW-5 and the size-table change).

- Slug: v110-plan-by-size
- Review: one
- Touches: skills/workflow-delivery, dev/toy, .loop/regression.tsv, skills/workflow-setup/scripts/settings.py, skills/loop-files.md, .loop/START.md, docs/wiki/How-to-use-Setup.md, .loop/regression-relevel.tsv
- ETA: 330 active minutes (estimate 264m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given `review_depth` as shipped, when a small goal's plan step starts, then it is told to run the forms its row of the size table lists; and when a large goal's starts, or any goal touching a safety class, then it is told to run them in full and a shorter run is refused.
2. The plan step's instructions state the round rule in REVW-5's words: the reviews once, at most `plan_fix_reads` reads of fixes on the changes only, and wording findings as build notes.
3. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

What it does: a plan step with no stored size starts from a provisional row (small; large for a goal frozen large, with no frozen size, or touching a safety class or risky path) and is told that row's forms; the plan step prints REVW-5's round rule with `plan_fix_reads` (new setting, default 2 in settings.py, read from the base branch's config when it sets one; .loop/config.json carries no key for it, owner o1110). Touches were widened through the tool to hold the setting and its generated references: settings.py, skills/loop-files.md, .loop/START.md, docs/wiki/How-to-use-Setup.md and .loop/regression-relevel.tsv.

Found outside this change (filed as deliver-first by the operation, WHAT only):
1. (v110-plan-by-size-later-goal-1) The shared safety-class word list misses the word "oauth", so a goal about oauth login is not detected as touching a safety class: a fail-open in safety-class detection, which the plan-start row also relies on.
2. (v110-plan-by-size-later-goal-2) An owner-edited checks table that gives the large row a one-pass plan review makes a large goal's plan step run condensed, because the depth follows the table.
3. (v110-plan-by-size-later-goal-3) A malformed stored `sized` record (not a dict, `checks` null, or a `passes` value that is not a number) raises in `sizing.depth`, which `guards._record` also calls. Four such crashes were found by the red team and left as out of scope.

Red team (form full, 2 passes):
- Pass 1 at 81f1fafda: 8 fail-open inputs inside this change, red 7db69f536 (10 failing checks), fix 0d4651050.
- Pass 2, the rerun, at 0d4651050: 6 further fail-open shapes, red d042e87f2 (8 failing checks), fix 5d2ee19ba. No third pass ran.

QA on the Mac lane: 12 passed, 2 known, 0 failed. The known rows are ls-judge-login and ls-size-budget, red on main (#5343).

Build red: the red for the first build commit 526d73dd2 was not its own commit. It was proved by hand on 89da3f874, where dev/toy/test-plan-by-size.py failed 10 checks.

Red on main too, not from this change: dev/toy/test-settings.sh (4 failures) and dev/toy/test-review-depth.sh (9 failures) under a clean environment, the same on a clean origin/main worktree.

Changed assertion (TD162), dev/toy/test-plan-by-size.py, owner o1110 (drop the plan_fix_reads key from .loop/config.json; the default 2 in settings.py stays):
- Old: `config.json holds plan_fix_reads 2 and its help line`. New: `config.json holds no plan_fix_reads key or help line (owner o1110)`, plus a new check `with the key absent the setting reads 2 by default`. Why: the owner dropped the key, so the file must match origin/main. Not weakened: the new assertion still pins the file's exact state, red first (it failed while the key was present), and the default is asserted by a check that sets no key. dev/toy/test-settings.sh needed no change: it checks the config setup writes into a toy repo, and its 4 failures are the same as on origin/main.
