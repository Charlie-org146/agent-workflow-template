# Plan: four known toy leaks fixed

Goal file: .loop/goals/v110-toy-leak-fixes.md (done lines 1-5, frozen; line 5 is the literal words "The standard package line.").
Base measured: origin/main 7c6d69ffd.

Files: skills/workflow-regression/scripts/actions.py, dev/toy/test-budget-order.py, dev/toy/test-merge-where.py, dev/toy/test-platform-limits.py, dev/toy/test-entry-config.sh, .loop/regression.tsv, docs/wiki/Tests.md
Lines: 80
Gates: none
Classes: none

## When the build can start: after v110-no-size-cap-a is on main (path (b) of TD2039)

Measured on a scratch copy: line 2's change adds 120 bytes to actions.py (18,997 to 19,117). Two rules on main stop that: row package-headroom-held (actions.py at most 19,000) and `dev/toy/test-pods.sh size` (rows pods-size, make-room-3-package, make-room-b-3-package: no skill script newly reaches 19,000). v110-no-size-cap-a (70cabc292) changes both checkers and removes both rules.

The change stays in actions.py: `actions.row_env` is the one function that builds the row environment for the three row-start paths cited here (runs.py:202-203; regression.py:205-206 and :232); the remaining row-start paths are deferred; the list is kept privately. No text in actions.py is trimmed.

The whole build waits, line 4 included. At the build start: merge origin/main into the branch with a merge commit, then measure actions.py and re-read every line number below. If either rule still applies, stop and tell operation-mac.

## Line 1: dev/toy/test-merge-where.py

Cause: the toy changes back to the caller's folder (:121-122) before it calls autorelease.reopen (:128). reopen saves the run record where git finds the common folder of the current directory (release.py:44-49, :61).

Change, toy only:
- At the start, create a stand-in caller repo in the toy's own temp folder and change into it. Resolve every path the toy needs from `__file__` before that.
- Change back only after the last in-process call has returned.
- At the end assert, as one line: `no run record lands in the checkout the toy was started from`. It passes only if both hold: the stand-in holds no file under .git/loop; and the fixture's own record on disk (`runs/g.json` in the toy's temp repo, the file the toy writes at :89 and reads at :123), re-read after `reopen`, has reopen's `merge refused (exit 2)` note in its log (autorelease.py:104-108 passes the note to release.save). The second half fails whenever `reopen` runs outside the temp repo, even if the toy never changed into the stand-in. On failure the line says which half failed. Neither half reads the real checkout's .git/loop.

No product code changes: saving state where the command runs is intended.

## Line 4: dev/toy/test-entry-config.sh

Cause: the toy adds worktrees to the checkout it runs from (:12, :29) and sets user.name and user.email in them (:14, :30). Linked worktrees share that config. Its fixture commits (:32-33) go into that repo's object store. On this Mac the sed command at :15 fails after those writes, so a failing sed after the shared-config write leaves the name changed (probed with that command on a throwaway file; the toy was not run).

Change, toy only:
- `git clone -q --no-hardlinks "$here" "$t/repo"`. Every worktree, config write and fixture commit happens in the clone. The cleanup trap removes only `$t`.
- The read of origin/main that remains after v110-no-size-cap-a (the skills archive) stays on `$here`: the clone's origin/main comes from the source's local main. Do not restore the size comparison that goal removes.
- The fixtures' user name and email are built from the temp folder's own name, so only this run writes them.
- At the end, before `ALL PASS`, two assertions, each its own line: `the checkout's config holds neither name nor email of this run` (read with `git -C "$here" config --local --get-all`, which reads the shared file even when a worktree-level identity hides it) and `no worktree of this run is registered in the checkout` (search `git -C "$here" worktree list --porcelain` for the temp folder's leaf name, which does not depend on how the path is spelled).
- Make line 15 portable (part of the cause above). `/usr/bin/sed -i 's/…/…/' FILE` exits 1 on this Mac, so the toy would stop at `FAIL: setup`. Write to a new file and move it into place. Without this the toy cannot reach its checks on a Mac.

Measured: a clone made from this goal's worktree takes under 1 s and 87 MiB, and `entry.py check` prints ENTRY OK on it. `entry.py write` and the merge cases in clone worktrees have not been run.

Line 4 is proved by the new row toy-leak-entry-config, which requires the two new PASS lines and not `ALL PASS`. The toy's old negative control (:41) is expected to fail on main: it expects main's entry.py to print the whole list on one line, and main prints a count (entry.py:74). So row entry-committed-config, which requires `ALL PASS`, is on the known list (.loop/regression-known.tsv:29, "fixed by kept-reds-5; see #5352"). This goal changes neither that control nor that entry.

Stop rule: if either new assertion fails with the fix in place, if any other check in the toy besides that negative control fails, or if the control fails for another reason than the one above, stop and tell operation-mac. No check is loosened or removed.

## Line 3: dev/toy/test-platform-limits.py

Cause: case d runs `sessions.py assign`, which asks operate.untrusted about the toy's folder (sessions.py:234, operate.py:127-135). It reads the home's .claude.json and refuses unless a listed, trusted project holds the folder.

Change, toy only, both steps before the first child process:
1. Stand in for the stated caller: set HOME and USERPROFILE to a temp home whose .claude.json is `{"projects": {}}`. That home trusts no folder, so the call refuses (operate.py:133). Use exactly this stand-in. This makes every machine, CI included, test the case.
2. The fix: set HOME and USERPROFILE to a second temp home, a new empty folder of the toy's own, for the toy and its children.

The existing case d assertions are the check.

Issue #5671 records three FAIL lines and quotes only the first (`FAIL: d: with no free session a new one is refused with the reason`). The build runs the old toy in an isolated clone behind the step 1 home and lists every FAIL line. The pull request references #5671 and does not close it.

If a session check still fails after step 2, or needs a change outside the one planned here, stop and tell operation-mac.

## Line 2: actions.py and dev/toy/test-budget-order.py

Cause: lane.py:168-169 sets _LOOP_LANE_NOTE, _LOOP_LANE_QUEUED and _LOOP_LANE_STARTED for the lane's runner. row_env copies the environment minus ROW_DROP, so rows get them. slots.py is their only reader (:48, :239, :259).

Change in actions.py: a second tuple `LANE_DROP` with the three names, and `if k not in ROW_DROP + LANE_DROP` in row_env. It stays apart from ROW_DROP because the generated workflow embeds ROW_DROP (dev/toy/test-automation.sh:189). lane.py and slots.py do not change: the runner keeps its own environment. A row that starts a nested run no longer hands it the outer lane's note, queue or start paths.

Check, beside the LOOP_ROW_TIMES check (:57-58): set the three names and _LOOP_LANE_LABEL, then assert `a row never inherits a lane's note, queued or started path` and, as the control, that _LOOP_LANE_LABEL is kept. Restore the environment afterwards.

Build check: search the toys once more for any that expects to inherit one of the three; those read so far set or unset their own.

## Rows

No existing row changes, its seen-red date included (row tasks-rows-only-added rejects any changed or removed line).

New entries at the end of .loop/regression.tsv. Each has a description of at most 400 bytes (row every-row-described fails on any row without one) and a category:

| id | level | goal field | category | description | command or note |
|---|---|---|---|---|---|
| toy-leak-merge-where | land | v110-toy-leak-fixes:1 | criterion | Given test-merge-where.py started from a checkout, when it ends, then it has written no run record into that checkout. | `out=$(python3 dev/toy/test-merge-where.py 2>&1) && printf '%s\n' "$out" \| grep -qF "PASS: no run record lands in the checkout the toy was started from"` (exit 0 and the new line) |
| done-toy-leak-fixes-2 | covered | v110-toy-leak-fixes:2 | workflow | A row started while a lane's handoff variables are set holds none of the lane's note, queued or started paths. | proved by the budget-order-first row (REG-4) |
| done-toy-leak-fixes-3 | covered | v110-toy-leak-fixes:3 | workflow | test-platform-limits.py passes its session checks when its caller's home trusts no folder. | proved by the platform-sends-counted row (OPS-1) |
| toy-leak-entry-config | land | v110-toy-leak-fixes:4 | criterion | Given test-entry-config.sh run from a worktree, when it ends, then it has not changed that repo's user name or email and has registered no worktree in it. | `out=$(bash dev/toy/test-entry-config.sh 2>&1); printf '%s\n' "$out" \| grep -qF "PASS: the checkout's config holds neither name nor email of this run" && printf '%s\n' "$out" \| grep -qF "PASS: no worktree of this run is registered in the checkout"` (both new lines) |
| done-toy-leak-fixes-5 | covered | v110-toy-leak-fixes:5 | workflow | The standard package line for this goal. | proved by the release-static-rules row, the goal's lane and the build review |

docs/wiki/Tests.md is re-rendered with the tool the lane uses. The build runs row every-row-described after adding the rows.

Line 5 here means: packaged scripts stay within the package's size limit, no test is loosened, no row turns red, and committed text never names the service repo. `python3 dev/package.py --static` runs after every code commit.

## Red proofs

All red and green runs of these toys by hand happen in an isolated clone with its own .git and its own HOME. Each red is quoted as the toy's OWN FAIL line, with the toy's other checks shown running and no refusal, traceback, setup failure, timeout or missing tool behind it. The evidence for each red is that quoted FAIL line.

| Line | Break | Expected FAIL line |
|---|---|---|
| 1a | change back to the caller's folder before reopen, as today, keeping the stand-in | `no run record lands in the checkout the toy was started from` (the record lands in the stand-in) |
| 1b | both halves lost: no change into the stand-in, and the early change back before reopen | the same line, failed by its second half: the temp record lacks reopen's note (the leaked record lands in the isolated clone) |
| 2 | drop `+ LANE_DROP` from the filter | `a row never inherits a lane's note, queued or started path` |
| 3 | remove step 2, keep step 1 | `d: with no free session a new one is refused with the reason` |
| 4 | point the worktrees back at `$here`, keeping this run's identity values | both line 4 assertions, so row toy-leak-entry-config fails on its own two required lines |

Recording: only the two new runnable rows get a seen-red date. In the isolated clone, with the fixes and both rows committed, run `regression.py red <id> --break …` for toy-leak-merge-where and for toy-leak-entry-config; the tool writes each date into the clone's table. Each red is that row's own assertion: the quoted FAIL lines are the toy's, and the row fails only because its required PASS lines are missing. Commit those table changes in the clone as one commit (give the clone a local identity so it can commit; that commit only carries the change), fetch it into the goal worktree, apply it with `git cherry-pick -n` and commit it there, so no date is typed by hand and the author comes from this worktree's config. Before that commit, user.name reads Charlie from the worktree's config.worktree and user.email reads the same value there as for the goal's earlier commits; after it, check the commit's author name and email. The reds for lines 2 and 3 are recorded in the build record, not in existing rows.

## Build order

Line 4 first (it ends the shared-config writes), then 1, 3, 2, then the rows and Tests.md. One commit each, each with its check. Before every commit, user.name must read Charlie from this worktree's config.

## Running the restricted tests (operation-mac TD2041)

- Before lines 1 and 4 are both committed on the branch, test-merge-where.py and the rows that run test-entry-config.sh (entry-committed-config and toy-leak-entry-config) run only in an isolated clone with its own .git and HOME.
- After both are committed, each fix is proved red and green in an isolated clone first; then this goal's own lane may run them in this worktree. The author watcher stays on. Any user.name change during that lane stops it, and the change is reported to operation-mac.
- The budget preflight is recorded by operation-mac (keep). The ETA, 460 active minutes, exceeds the 240-minute budget.

## Overlaps and merge order

- v110-no-size-cap-a (70cabc292, not on main): the prerequisite. It also edits test-entry-config.sh (it removes the size comparison at :42) and test-platform-limits.py (case e). This build starts from a main that holds it.
- lane-scrub-2 (42a919cac, unmerged): edits actions.py. Whichever merges second takes main by a merge commit, keeps both changes to row_env and re-runs the affected rows. The same for .loop/regression.tsv and Tests.md.
- kept-reds-5 (6e911f592, local, not on main): changes test-entry-config.sh its own way and is named by the known entry as that row's fix. This goal does not take its changes. Whichever merges second takes main by a merge commit, keeps this goal's clone isolation and its two assertions, and re-proves line 4.
- toy-merge-where-isolation (823a27017; goal and plan only, no code): its plan changes test-merge-where.py and row merge-refuses-worktree, and its done line asks for a control on the real checkout's .git/loop. Line 1 stays here (o1029). This goal does not write or adopt that control as its own proof. Whichever merges second takes main by a merge commit and keeps both rows' conditions. If the control is on main first, this goal keeps it unchanged and re-proves its own line; a concurrent-writer failure from that control goes to operation-mac. operation-mac has raised the duplication with top; this goal does not touch that goal or its branch.

## Issues the lines touch

| line | issue | what the pull request does |
|---|---|---|
| 1 | #5858 | references it; it stays open (see Not in scope) |
| 2 | none claimed | - |
| 3 | #5671 | references it only; it does not close it |
| 4 | none claimed; #5352 stays with kept-reds-5 | - |

## Not in scope

A guard or writer log for test runs, a slot policy, a shared toy launcher, a change to `red`'s test for a failing run, and any change to where release state is saved or how folder trust is read.

Issue #5858 also asks for a check that fails if any file under the real checkout's .git/loop is created or changed during the toy's run. This goal does not build it: other sessions write there during any run, so it would fail innocent runs. The stand-in check proves the same leak for the checkout the toy was started from.

The old negative control in test-entry-config.sh (:41) and the known entry for row entry-committed-config in .loop/regression-known.tsv stay with kept-reds-5 and #5352. This goal changes neither and does not touch that file.

Named deferral: the docstring of slots.started() (slots.py:238) says a row's nested run sees the outer lane's marker. With line 2 the row no longer receives it; the lane's clock is still left alone. slots.py is not in the touches, so the sentence is not changed here.

<!-- autoplan-accepted:ceo -->
- Issue #5858 stays open, and its real-checkout check is named as not built, with the reason.
- Line 3 stops for operation-mac if a session check still fails after step 2; #5671 is referenced only; the clean home is a new empty folder of the toy's own.
- Line 4 keeps only the origin/main read that remains after v110-no-size-cap-a; its cause includes the sed failure after the shared-config write.
- The other goal's real-checkout control is neither written nor adopted here; if it is on main, it stays unchanged.
- The slots.started() docstring is a named deferral.
- All five new rows carry a description and a category, and the build runs every-row-described.
- The restricted tests run as TD2041 says, the new line 4 row included.
- Line 1's one assertion needs both halves (the stand-in holds nothing, and the temp record holds reopen's note), says which half failed, and is seen red with both halves lost as well as with the order alone.
- The seen-red date is applied with git cherry-pick -n and committed in the goal worktree, with the author name and email checked.
- Line 4 is proved by the new runnable row toy-leak-entry-config, which requires the two new PASS lines and is seen red as its own assertion.
- The old negative control and the known entry are not changed, .loop/regression-known.tsv is not touched, and kept-reds-5 is a named overlap.
- Line 4 follows its stop rule; no check is loosened or removed.
<!-- /autoplan-accepted:ceo -->
