# lane-prep: plan

Fixes #5730, #5728 and #5735. Done lines are frozen in `.loop/goals/lane-prep.md`; touches now include `skills/workflow-release`
(operation session: "TOUCHES lane-prep +skills/workflow-release").

## Requirement served
DEL-17 (Reviewed 2026-11-20), the clause "then one local lane (5 minutes, only the tests the change reaches, reused by later
steps)". Done line 1 and 3: a lane that moves HEAD, or dies in a fresh clone before any row runs, is not one reusable lane.
Done line 2: the lane refusing LANE_DIRTY on the tool's own render means the pr step cannot reuse it. The issues name DEL-17.

## Build steps, in order
1. `skills/workflow-docs/scripts/audit.py`: `relock(root, slug="", only=None)` tests `only is not None`, so an empty set means no
   pages and `None` means every page; the DOC-18 loop reads `(only or ())`; `restamp_own` reads the `STALE <page>` lines of
   `docs.py check --own HEAD` (the form it already parses) and returns `[]` when there are none, so a lane start with nothing
   stale makes no Kept commit (#5730). The only callers are `restamp_own` (always a set) and `docs.py audit --relock` (passes none,
   every page); the `restamp` command line needs a page name.
2. `skills/workflow-release/scripts/wiki.py` (C1, replaces the earlier fit.py path, which is back to main's bytes): `cmd_prepare`
   reads `git status --porcelain -- README.md` before the audit; `commit()` takes `readme`, and the audit's mechanical-fix commit
   names `README.md` together with the wiki folder when README was clean before and no page is still stale and README now shows
   a change. README and the wiki pages are one commit, or neither; a hand-edited README (dirty before, staged or untracked) is
   never committed, so the pr lane still refuses it with LANE_DIRTY. A commit refused by a hook refuses the wiki pages and
   README together, as it did for the wiki pages before; README alone can no longer be left behind (B6).
3. `skills/workflow-delivery/scripts/lane.py` `lane()`: `os.makedirs(runs, exist_ok=True)` first (#5735).
4. Tests: `dev/toy/test-lane-prep.py` (throwaway git repos it builds itself) and one case in `dev/toy/test-merge-unblock.py`; three
   regression rows, one per issue; the Tests tables re-rendered in `docs/wiki/Delivery.md`, `Documentation.md`, `Tests.md`.

## Evidence (clean detached clone at head f4810250f, 2026-11-21 PST; `dev/toy` run there only, never in the real tree)
- B1a, existing expectations unchanged: `git diff 977f4f067 f4810250f -- dev/toy/test-merge-unblock.py` is exactly two added lines
  (a `head_before` read and one new `check(...)`); no existing line is changed or removed.
- B2, seen red, 11:39:03-04 PST, main's `audit.py`, `lane.py` and `wiki.py` with the new toys: `python3 dev/toy/test-merge-unblock.py
  restamp` prints `FAIL: an empty set of pages re-stamps nothing, makes no Kept commit and HEAD does not move (#5730)`;
  `python3 dev/toy/test-lane-prep.py` prints `FAIL: a lane start in a clone with no runs folder makes the folder and does not
  crash`, `FAIL: a README only the render changed is committed, and the tree is clean`, `FAIL: the wiki page and README land
  in one commit named for the wiki update`.
- New scripts, 11:39:04-14 PST: `test-merge-unblock.py` 25 PASS, no FAIL; `test-lane-prep.py` 8 PASS, `ALL PASS`, including the
  controls (stale page still re-kept earlier in the same case, hand-edited README stays dirty, a page still stale commits no
  README, a hook-refused commit leaves README and the wiki uncommitted together, `lane_status` makes no folder).
- B3a, runtime: `test-lane-prep.py` takes 0.97 s (`time -p`); no lane runs it twice.
- B4: `python3 skills/workflow-delivery/scripts/private.py scan --base 977f4f067` prints "Private-name scan: 8 patterns from
  ~/.workflow-loop/private-names, clean." The toys use fixture text only.
- Sizes: `wiki.py` 19,274 bytes (cap 20,480, warning 19,000), `audit.py` 19.1 KB, `lane.py` 18.8 KB, `fit.py` unchanged from main.

## What could break
Another caller of `relock` passing an empty set by accident now skips the re-stamp; today there is none. The three wiki pages a
Tests re-render touches are the declared `docs` touch. Left open: the Kept commit 26d68d824 (made by an accidental lane in the
worktree) is reverted in a16655246 and stays in history; the PR notes say so.
