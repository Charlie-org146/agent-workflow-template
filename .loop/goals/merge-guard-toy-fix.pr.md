# merge-guard-toy-fix: known-red row merge-guard-base-head cleared

Refs #4113 (the issue the known list names for merge-guard-base-head) and #5306.

This file was written with the file tool, as the goal's instruction note o685 allows.

The row runs `dev/toy/test-merge-guard.sh` and needs its last line to be ALL PASS plus four named PASS lines. On main the toy had 6 failures. All six were the toy's, and every one is fixed here with no assertion changed or skipped; the product (`merge.py`, `autorelease.py`, `private.py`) is untouched.

## Root cause 1 (toy): five cases reused a goal that a refused merge now leaves failed

Since #4004, a refused or failed `merge.py` leaves the goal `failed`, and `autorelease.mergeable` only lets a failed goal merge when it carries a `release_error`. The toy wrote the goal's state file once and then ran `merge.py g` five times in a row. The first refusal (HEAD_MOVED) flipped the state to failed, so the next four runs printed `REFUSED: g has no finished pull request` instead of the refusal under test. That is why these five lines failed:
- a head moved only by a wiki page commit is not HEAD_MOVED,
- a file moved into the wiki folder is no wiki-only move,
- a SKILL.md, even in the wiki folder, is no wiki-only move,
- a symlink named like a wiki page is no wiki-only move,
- a head moved by any other commit still refuses HEAD_MOVED.

Fix: a `reopen` helper, written like the toy's existing `go()` helper (which already reopens a refused goal for the later parts), rewrites the finished-goal state before each of those five runs. Each case still asserts the same exit code and message.

## Root cause 2 (toy): the #5306 lane-import check counted one line instead of two

`lane_import` prints `LANE OK` without a trailing newline, so `out=$(lane_import A)$(lane_import B)` gave `LANE OKLANE OK` on one line, and the check `grep -c "^LANE OK" = 2` saw 1. The product is fine: both imports succeed. Fix: the two calls are joined with an `echo`, so each result is a line. The check is unchanged (two imports, one from a checkout and one from an installed skills copy, both must print LANE OK and neither may print ModuleNotFoundError). This is the same one-line change that loop/v2fix-5306 holds at 8d5fd152.

## Proof
- `test-merge-guard.sh` ALL PASS (6 FAIL lines before; the five reopen cases and the lane-import case).
- `regression.py run merge-guard-base-head` passed twice, outside any sandbox, with the session's CLAUDE, ANTHROPIC and LOOP variables unset. The two other rows that run this toy, `merge-reach-fail-closed` and `grd6-head-moved`, pass too.
- The known line for merge-guard-base-head is removed.
- Nearest toys: test-merge-batch.sh (the guard toy calls it), test-merge-unblock.py and test-merge-main-own.py pass.
- docs.py check --own: DOCS OK, 16 pages. criteria.py render --check: TABLES OK. dev/package.py --static: PASS, 100 files.

## Rows
Net rows: 0. No row was added, removed or changed.

## Not carried from loop/v2fix-5306
That branch also holds a new toy, `dev/toy/test-private-lane.py`, and a new defect row for #5306 (`private-merge-finds-lane`). Carrying it adds one row and a toy that repeats the #5306 check `test-merge-guard.sh` already makes (it is part of that toy's ALL PASS, which this row requires), so it is left for the operation session to decide, under the rows rule of net 0 or fewer. #5306 has no defect row on main today.
