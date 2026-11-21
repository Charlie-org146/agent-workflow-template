# Plan: lane-once

## Implementation plan

Checked against the code. `need_lane` (role.py:225) reads `<slug>.<step>-lane.ok` for the step being recorded (qa, ship; goal.py:262). `lane()` (lane.py:184) starts or polls a lane named qa, ship or pr; `finalize` (lane.py:~160) writes `<slug>.<name>-lane.ok` holding the head on a pass and `set_last` records `<name>-lane.last` (head, state, line). All three names run the same command (`lane_argv`: `regression.py run land --reuse --tier goal`), so a pass at a head by one proves the other two. Today `lane()` reuses only the same name's pass, so qa, ship and pr each rerun at one head. `goal.py pr` runs `role.lane(..., "pr", ...)` (goal.py:374) and `lane_part` (role.py:~310) reads `pr-lane.last` and `.txt` for the PR body.

The done lines are the five frozen lines in `.loop/goals/lane-once.md`. The steps below are authoritative.

Build steps, in order:

1. lane.py gains `passed(runs, slug, head, name)`: the lane name (own first, then the others in qa, ship, pr order) whose `.last` says state pass at that head, or empty. It gains `lane_ok(runs, slug, step, head)`: `head` when any of the three `.ok` files holds exactly `head`, else the step's own `.ok` text (empty when missing), so a refusal still names where a lane last passed.
2. `lane()` replaces its own-name-only reuse with `passed()`: with no job held, a clean tree and a pass at this head by any name, it returns pass. When the pass is another name's, it first copies that name's `.last` and `.txt` to this name and writes this name's `.ok` (head), so `lane_part`, `lane_note` and the gates read the same record; the copied line ends with `; reused: the <src> lane passed on this head` so a reader sees no second lane ran (the `N pass; M not runnable here` text `lane_note` matches is kept). Nothing else in `lane()` changes: a lane for any name still stops a job of another name on an older head, and returns running while another name's job at this head is live.
3. `lane_status()` (used by `lane-wait`) also answers pass from `passed()` when its own record has none.
4. role.py `need_lane` calls `lane_ok(...)` in place of reading the step's own `.ok`. The HEAD_MOVED and LANE_MISSING refusals, their fix lines and the `over_caps` check are unchanged. role.py gets shorter, not longer (19,997 bytes now).
5. Row selection is untouched: `lane_argv`, `prep`, the tests tables and the budgets are not edited, so the one lane selects exactly what today's qa lane selects.
6. New toy `dev/toy/test-lane-once.py` with a regression row in `.loop/regression.tsv` (the toy builds a fixture repo and runs the real `lane()`/`need_lane` with a fake regression command, as `dev/toy/test-lane-control.sh` does): (a) a pass by qa at head H: `lane ship` and `lane pr` return pass without starting a job (no `.job` file, the fake command's start counter stays at 1), their `.ok` hold H and `need_lane` returns None for qa and ship; (b) negative controls: HEAD moved by one commit: `need_lane` refuses HEAD_MOVED and `lane ship` starts a new job; a failed qa lane at H: `need_lane` refuses LANE_MISSING and `lane ship` does not return pass; a pass at another head: refused; a dirty tree: no reuse; (c) the copy carries `.txt` and `.last` so `lane_part` shows the rows; (d) with the reuse removed from lane.py (the toy is run against a copy with `passed()` limited to the own name) controls (a) fail.
7. One existing assertion changes with the behavior it described: `dev/toy/test-lanes.sh` line 234 ("ship reuses qa's run on unchanged content and runs no row") expects a `LANE ship REUSED 0/` line and a `.ship-lane.txt` with `REUSED n rows`; after this change ship runs no lane, so that check asserts the reused line and no second job instead. The row stays green, no check is dropped, and the regression row ids are unchanged. `dev/toy/test-lane-control.sh` lines 176 to 184 (`need_lane` for goal rs) hold as written: rs has no qa pass at HEAD.
8. Docs: `skills/loop-files.md` line 140 (the `loop/runs/<slug>.qa-lane.*` row) says one lane per head satisfies all three; docs, package and private-name checks pass; `docs.py audit` and `entry.py write` clean; re-stamp own pages if needed (stamp lines only).
9. No new file under skills/; only skills/workflow-delivery/scripts/lane.py and role.py, `skills/loop-files.md`, `dev/toy/test-lane-once.py`, `.loop/regression.tsv`, docs stamps and this goal's records change. lane.py stays under 19,000 bytes if the helper fits (18,716 now); if not, the helper goes to lanekit.py (19,548, under the 20,480 cap) and that is recorded.

Test for each done line (negative control seen failing on main):
- Done line 1: the toy's (a) and the head-moved control; on main `lane ship` after a qa pass starts a second job.
- Done line 2: `git diff` shows no edit to `lane_argv`, `prep`, `regression.py` or budgets; the toy asserts the shared pass is the qa lane's own record, row list and all.
- Done line 3: the toy's failed-lane, other-head and dirty-tree controls.
- Done line 4: docs, package and private checks; `git diff origin/main --stat` lists no new file under skills/.
- Done line 5: delivery.

What could break:
- A pass copied under a different name keeps the source attempt in `.last`; `lane-wait` and finalize read `.last` only for the name's own held job, so a copy never finalizes anything.
- `goal.py pr` merges the base first, so HEAD moves and a new lane runs; that is the stated rule, not a regression.
- Two names racing: the existing `.job` create-exclusive and the `other_held live` check are unchanged.

Out of scope: lane budgets, row selection, the flow file, `merge`, the lane child.

- `goal.py pr` first merges the base (HEAD moves when main moved) and `bump_version` is off in this repo (`pr_bumps_version` false), so the pr lane is satisfied only when the base merge and the goal-touches commit leave HEAD where the qa/ship lane passed. That is the stated rule ("any HEAD move needs a new lane"), recorded so the PR body does not promise more.

PENDING: none for the owner.


<!-- autoplan-accepted:ceo -->
- With no job held, a clean tree and a recorded pass at this exact HEAD by any of the qa, ship or pr lanes, `lane()` returns pass without starting a job; the other name's `.last` and `.txt` are copied to this name (the line ends `; reused: the <src> lane passed on this head`) and this name's `.ok` is written last. `lane_status()` answers the same.
- `need_lane` accepts an `.ok` equal to HEAD from any of the three names; LANE_MISSING and HEAD_MOVED refusals, their fix lines and `over_caps` are unchanged; a failed lane, a pass at another head or a dirty tree gets no reuse.
- Row selection, `lane_argv`, `prep`, budgets and the tests tables are not edited.
- New toy `dev/toy/test-lane-once.py` with one regression row: happy reuse (no second job), head moved, failed lane, other-head pass, dirty tree, copied record read by `lane_part`, and a control run against a copy with the reuse removed that fails.
- `dev/toy/test-lanes.sh` line 234 asserts the reused line and no second job instead of a `LANE ship REUSED` line; no other check is dropped or loosened.
- Only lane.py, role.py (smaller), `skills/loop-files.md`, the new toy, `.loop/regression.tsv`, docs stamps and this goal's records change; no new file under skills/; the helpers live in lanekit.py (under 20,480), lane.py keeps only the calls.
- Copy source when two names pass at HEAD: own name, then a record without a `; reused:` suffix (the lane that ran), then qa, ship, pr order; an existing `; reused: ...` suffix is replaced, never stacked.
- flow.py runs `lane` for qa and ship before `record` (flow.py:306), so `lane_note(ship)` finds `ship-lane.last`; the toy asserts it after a qa-only pass.
- `need_lane`/`lane_ok` do not check a dirty tree (as today); the dirty-tree control tests `lane()`.
- The helpers `passed()`, `lane_ok()` and the copy live in lanekit.py (under 20,480 bytes); lane.py keeps only the calls; role.py shrinks.
- Toy method: fixture from `dev/toy/make.sh`, real `role.py lane`, a land row that counts starts into a file; control (d) runs the same steps on a temp copy of the delivery scripts whose `passed()` loop is cut to the own name, and the happy case must fail there.
- Sweep: every toy that mentions `ship-lane`, `lane-wait`, `lane ship` or `lane pr` is run and those that change are listed; a base merge that moves HEAD runs a fresh pr lane (the HEAD-move rule prevails).
- Dual-voice fixes (supersede steps 1 and 9 where they differ): `passed()`, `lane_ok()` and the copy live in lanekit.py only (measure the bytes; if lanekit.py would pass 20,480 the copy alone stays in lane.py); the conditional in step 9 is deleted.
- Added controls: ship holds a reused copy of qa, then pr reuses: the suffix names qa once; with the reuse cut out (control d) `lane ship` starts a second job; the argv logged by the fixture's land row for qa, ship and pr starts (at different heads) is identical, so a later divergence fails the toy.
- `dev/toy/test-lanes.sh` line 234 asserts: the ship output holds `; reused:`, no `ship-lane.job` exists and the fixture's start count is still one; it fails if ship starts a job.
- `skills/loop-files.md` states: qa and ship share one pass at a head; pr shares it only if the base merge and the goal-touches commit leave HEAD unmoved. The PR body lists the known limits: `need_lane` does not check a dirty tree (as today) and a pass with not-runnable rows is reused with its `N pass; M not runnable here` note.
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:dx -->
- No new command, flag or lane name; the copied lane line carries `; reused: the <src> lane passed on this head`, and a second `role.py lane SLUG ship|pr` at a head with a pass returns it at once with no prompt.
- If the copy raises OSError, `lane()` returns fail with `LANE_REUSE_COPY: could not copy the <src> lane record (<cause>). Fix: run the same command again; nothing was changed.`, writes no `.ok`, and the toy covers it with an unwritable target.
- `skills/loop-files.md` carries the one-lane-per-head sentence and the pr caveat (HEAD moved means a new lane).
- Existing refusal texts (LANE_MISSING, HEAD_MOVED) and run file names are unchanged.
- `lane_ok` returns `(ok_text, source)`; a refusal names the lane that last passed and its head: HEAD_MOVED reads `HEAD moved since the <src> lane passed (lane on <h>, HEAD <h2>)` with the unchanged fix line and code (own-name text is byte-identical to today); LANE_MISSING and HEAD_MOVED keep their codes.
- Precedence for a shared pass: a pass by any name at HEAD, with a clean tree, wins in `lane()` and in `lane_status()` (so `lane` and `lane-wait` agree) over an own terminal fail at the same head; a live job of another name at this head still returns running; a dirty tree gets no reuse in either.
- `lane_note(runs, slug, step)` falls back to the passing name's `.last` when the step has none, so `goal.py record --in-session` keeps the `N pass; M not runnable here` qualification.
- The reuse string `; reused: the <src> lane passed on this head` is a documented, toy-asserted contract; `skills/loop-files.md` carries a short two-command transcript (qa lane, then ship lane) and the manual recovery for a pass that must be retested without a commit: remove the `<slug>.<name>-lane.last` and `.ok` files of the passing name and of the step, then run the lane command again. No new flag or command.
- The toy adds an interrupted-copy case (`.last` copied, no `.ok`): the next call completes the copy and passes; and a stale-head case where ship has no `.ok` and qa's `.ok` is older than HEAD: HEAD_MOVED names qa and both heads.
- Where earlier steps (1, 9) and these accepted bullets differ, the accepted bullets are authoritative.
<!-- /autoplan-accepted:dx -->

<!-- autoplan-accepted:eng -->
- lanekit.py gains `passed(runs, slug, head, name)`, `lane_ok(runs, slug, step, head)` and `reuse(runs, slug, src, dst, head)`; lane.py calls them in `lane()` and `lane_status()`; role.py `need_lane` and `lane_note` call them. If the measured lanekit.py size would pass 20,480 bytes, `reuse` stays in lane.py (18,716 bytes now); neither file passes 20,480.
- `reuse` copies `.last` and `.txt` to the step's names (suffix replaced, never stacked), then writes `.ok` last; a crash between leaves LANE_MISSING and the next call completes it; an OSError returns the LANE_REUSE_COPY failure and writes no `.ok`.
- `dev/toy/test-lane-once.py` (one regression row) asserts every gap in the test diagram: own and other-name pass, no pass or unreadable `.last`, dirty tree, copy ok, OSError, interrupted copy, `lane_ok` match and stale heads, `lane_note` fallback, `lane` and `lane-wait` agreement, chained suffix, identical argv for the three names, and the reuse-cut control that fails; value cards are in the on-disk test plan.
- The failure modes registry above has 0 critical gaps and stays so.
- A name's pass is complete only when its `.last` says pass at HEAD and its `.ok` equals HEAD; `passed()` returns only complete names, and an own `.last` pass without `.ok` is an incomplete alias that `lane()` repairs by redoing the copy from a complete source (if none exists, a lane starts). `reuse` writes `.txt` and `.last` through a temp name and `os.replace`, then `.ok`; the OSError text is `LANE_REUSE_COPY: could not copy the <src> lane record (<cause>); no .ok was written. Fix: run the same command again`.
- Before the copy replaces an own terminal fail at the same head, that record moves to `<name>-lane.last.prev`; the documented manual recovery moves the lane files aside (`.prev`) instead of deleting them and says that a rerun of rows needs `regression.py run <id>` (the row cache can still reuse passes).
- The origin is a structured field in the copied `.last` (`reused_from`), and the suffix is rendered from it on the first line of the line (before any newline), so the PR body's first-line cut keeps it; the source picker prefers a record with no `reused_from`.
- `lane_status()` also finalizes a sibling's ended job at this head (through that name's `finalize`) and reports running for a live sibling job, then re-reads `passed()`; `lane_note` reads the `.last` of the name whose `.ok` satisfies the gate (own first).
- Toy additions: a failure after each write of the copy (`.last` only; `.last` and `.txt`), `.last` copied with `.txt` missing, a table test of `lane` against `lane_status` over fixture states (own fail plus other pass, dirty tree, live sibling job, sibling ended but not finalized), a budget-limited multiline result, all three names missing, `need_lane` with a dirty tree (records today's behavior), the fixture counter as the only source of the start count, argv compared in full for the three names, and the reuse-cut control asserting that the cut changed the file and that the happy case fails because a second job started.
<!-- /autoplan-accepted:eng -->
## Review record


<!-- AUTONOMOUS DECISION LOG -->
## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|----------------|-----------|-----------|----------|
| 1 | CEO | Mode SELECTIVE EXPANSION; keep approach A (share the pass) | Mechanical | P5 | closest to the existing lane() sibling loop | B shared record, C skip the gate |
| 2 | CEO | Add the reused note to the copied line | Taste | P1 | reader sees no second lane ran | no note |
| 3 | CEO | Skip role.py lane-status and a shared .ok file | Mechanical | P3, P4 | no consumer; renames every reader | M-size additions |
| 4 | CEO | Helpers in lanekit.py only, byte overflow plan | Mechanical | P5 | lane.py has 284 bytes of room | helpers in lane.py |
| 5 | CEO | Runner identity stays out of the key | Taste | P3 | done line 1 fixes the key as the exact head | fingerprint in the key |
| 6 | CEO | Reuse a pass with not-runnable rows, with its note | Taste | P3 | done line 1; the note and recovery disclose it | ineligible for reuse |
| 7 | DX | No new flag or command; manual recovery documented | Mechanical | P5 | DX POLISH adds no capability | --fresh, an off switch |
| 8 | DX | lane_ok returns the source; refusals name it | Mechanical | P1 | agent-ready errors | own-text only |
| 9 | DX | One precedence rule for lane and lane-wait | Mechanical | P1 | polling must agree with the action | own fail wins |
| 10 | DX | lane_note from the satisfying pass; LANE_REUSE_COPY error | Mechanical | P1 | record route keeps the qualification | no fallback |
| 11 | Eng | Complete-alias rule, atomic copy, .ok last | Mechanical | P1 | a half copy must never read as complete | copy in place |
| 12 | Eng | Keep superseded own fail in .prev; manual recovery moves files aside | Mechanical | P1 | evidence kept | delete |
| 13 | Eng | reused_from field; suffix on the first line | Mechanical | P5 | PR body keeps only the first line | free-text match |
| 14 | Eng | lane_status finalizes a sibling's ended job | Mechanical | P1 | lane-wait must see the sibling's pass | none result |
| 15 | Eng | Dirty tree not checked in need_lane (today's behavior), toy control | Taste | P3 | outside this goal's lines | check in need_lane |

### CEO review (autoplan, SELECTIVE EXPANSION)

Mode: SELECTIVE EXPANSION (set by autoplan's override rules). 0D: no approach choice needed; the design doc already weighed A (share the pass), B (one shared file), C (skip the gate), and the plan keeps A.

Premise table (0A, 0B; unverified=0):

| premise | claim | file:line receipt | verdict |
|---|---|---|---|
| P1 | each step's gate reads its own `<slug>.<step>-lane.ok` | role.py:233 | true |
| P2 | `lane()` writes the `.ok` per name and reuses only its own name's pass | lane.py:177, lane.py:204 | true |
| P3 | all three names run the same command | lane.py:46 (`lane_argv`), lane.py:249 (single Popen argv) | true |
| P4 | a live lane of another name at this head already makes a new caller wait | lane.py:192-198 | true |
| P5 | `goal.py pr` runs `role.lane(..., "pr", ...)` | goal.py:374 | true |
| P6 | the PR body reads `pr-lane.last` and `.txt` | role.py:310-318 | true |
| P7 | role.py is 19,997 bytes, lane.py 18,716, lanekit.py 19,548 (warn 19,000, fail 20,480) | wc -c on the branch | true |
| P8 | `pr_bumps_version` is off, the base merge moves HEAD only when main moved | .loop/config.json:28, goal.py:350-356 | true |
| P9 | no existing toy needs a second lane at one head except test-lanes.sh:234 | grep of dev/toy for `lane ... ship|pr` | true |

REALITY: premise-table pass nine claims, each with a receipt, unverified=0 (skills/workflow-delivery/scripts/role.py:233)
REALITY: already-done pass `git fetch origin main`, `git log origin/main --since=2026-11-20 -- lane.py role.py` lists nothing for this symbol; no main commit mentions 5734 (977f4f067)
REALITY: surface-check pass the only named commands are `role.py lane SLUG qa|ship|pr` and `role.py lane-wait`, both in lane.py:358-366 (skills/workflow-delivery/scripts/lane.py:358)
REALITY: binding-decisions pass no Binding decisions section and no branch decision conflicts; Reviewed DEL-17 is the promise being kept (.loop/goals/lane-once.md:1)
REALITY: numbers pass 15-minute lane budget and the three sizes are measured from the branch files [measured: wc -c, skills/workflow-delivery/scripts/lane.py:1]; 365-minute ETA is [estimated] by the loop
REALITY: deferred-asks pass issue 5734 asks for one lane per head; the plan leaves out nothing it asks for, and the goal's out-of-scope list (budgets, selection, the flow file, merge) is the owner's own (.loop/goals/lane-once.md:5)
REALITY: pr-count pass one PR, a patch, as the done lines say (.loop/goals/lane-once.md:16)

0A Premise challenge: the real problem is wall-clock and slot cost, not correctness: qa, ship and pr each rerun a 15-minute lane at one head (`--reuse` makes the second and third cheap on rows, but each still pays prep, planning, slot wait and a full lane process). The plan solves it at the source (one pass per head), not a proxy (a faster lane). Do-nothing cost: two extra slot holds per goal on a Mac with three slots.
0B Existing code leverage: `lane()` already stops a lane of another name on an older head and waits on a live sibling (lane.py:192-198); the plan extends that same loop to pass reuse. `finalize` already writes `.ok`/`.last`; nothing is rebuilt.
0C Dream state: CURRENT three lanes per head -> THIS PLAN one lane per head, gates read any name -> 12-MONTH IDEAL a single `<slug>.lane` record per head that every step reads (rejected now: it renames every reader and loses existing run records; the plan's `passed()` is the seam a later rename would replace).
0F/0G proposals (SELECTIVE): (1) the copied line ends with `; reused: the <src> lane passed on this head` (S, low risk): ACCEPTED, a reader of the pr step output sees no second lane ran (taste, auto-decided P1); (2) a `role.py lane-status` listing of all three names (M): SKIPPED, not asked for, no consumer (P3); (3) one shared `<slug>.lane.ok` file (M): SKIPPED, see 0C (P5); the HOLD checks: eight files or fewer, no new classes, no deferral needed.
0I Temporal: hour 1, the implementer needs `lane()`, `need_lane`, `finalize` and `lane_status` together; hours 2-3, the ambiguity is whose `.last` to copy (the passing name's, whole line); hours 4-5, the surprise is test-lanes.sh:234 and the PR body's lane part; hour 6+, they will wish for a control that runs the toy against a copy with the reuse removed (plan step 6d). Effort: human ~half a day, CC ~40 minutes.

<!-- autoplan-accepted:ceo -->
- With no job held, a clean tree and a recorded pass at this exact HEAD by any of the qa, ship or pr lanes, `lane()` returns pass without starting a job; the other name's `.last` and `.txt` are copied to this name (the line ends `; reused: the <src> lane passed on this head`) and this name's `.ok` is written last. `lane_status()` answers the same.
- `need_lane` accepts an `.ok` equal to HEAD from any of the three names; LANE_MISSING and HEAD_MOVED refusals, their fix lines and `over_caps` are unchanged; a failed lane, a pass at another head or a dirty tree gets no reuse.
- Row selection, `lane_argv`, `prep`, budgets and the tests tables are not edited.
- New toy `dev/toy/test-lane-once.py` with one regression row: happy reuse (no second job), head moved, failed lane, other-head pass, dirty tree, copied record read by `lane_part`, and a control run against a copy with the reuse removed that fails.
- `dev/toy/test-lanes.sh` line 234 asserts the reused line and no second job instead of a `LANE ship REUSED` line; no other check is dropped or loosened.
- Only lane.py, role.py (smaller), `skills/loop-files.md`, the new toy, `.loop/regression.tsv`, docs stamps and this goal's records change; no new file under skills/; the helpers live in lanekit.py (under 20,480), lane.py keeps only the calls.
- Copy source when two names pass at HEAD: own name, then a record without a `; reused:` suffix (the lane that ran), then qa, ship, pr order; an existing `; reused: ...` suffix is replaced, never stacked.
- flow.py runs `lane` for qa and ship before `record` (flow.py:306), so `lane_note(ship)` finds `ship-lane.last`; the toy asserts it after a qa-only pass.
- `need_lane`/`lane_ok` do not check a dirty tree (as today); the dirty-tree control tests `lane()`.
- The helpers `passed()`, `lane_ok()` and the copy live in lanekit.py (under 20,480 bytes); lane.py keeps only the calls; role.py shrinks.
- Toy method: fixture from `dev/toy/make.sh`, real `role.py lane`, a land row that counts starts into a file; control (d) runs the same steps on a temp copy of the delivery scripts whose `passed()` loop is cut to the own name, and the happy case must fail there.
- Sweep: every toy that mentions `ship-lane`, `lane-wait`, `lane ship` or `lane pr` is run and those that change are listed; a base merge that moves HEAD runs a fresh pr lane (the HEAD-move rule prevails).
- Dual-voice fixes (supersede steps 1 and 9 where they differ): `passed()`, `lane_ok()` and the copy live in lanekit.py only (measure the bytes; if lanekit.py would pass 20,480 the copy alone stays in lane.py); the conditional in step 9 is deleted.
- Added controls: ship holds a reused copy of qa, then pr reuses: the suffix names qa once; with the reuse cut out (control d) `lane ship` starts a second job; the argv logged by the fixture's land row for qa, ship and pr starts (at different heads) is identical, so a later divergence fails the toy.
- `dev/toy/test-lanes.sh` line 234 asserts: the ship output holds `; reused:`, no `ship-lane.job` exists and the fixture's start count is still one; it fails if ship starts a job.
- `skills/loop-files.md` states: qa and ship share one pass at a head; pr shares it only if the base merge and the goal-touches commit leave HEAD unmoved. The PR body lists the known limits: `need_lane` does not check a dirty tree (as today) and a pass with not-runnable rows is reused with its `N pass; M not runnable here` note.
<!-- /autoplan-accepted:ceo -->

Spec review round 1 (independent reviewer, score 7/10) fixes, all accepted:
- flow.py calls `role.lane` for the qa and ship steps before it prints NEXT (flow.py:306), so the copy in `lane()` always happens before `record ship`; `lane_note` therefore finds `ship-lane.last`. The toy asserts `lane_note(ship)` after a qa-only pass and a flow-style `lane ship`.
- Copy source: when two names hold a pass at HEAD, own name first, then a record whose line has no `; reused:` suffix (the lane that actually ran), then qa, ship, pr order. A copied line's existing `; reused: ...` suffix is replaced, never stacked.
- `need_lane` and `lane_ok` do not check a dirty tree, exactly as today (`lane()` does); the dirty-tree control tests `lane()` only.
- Size: the helpers `passed()`, `lane_ok()` and the copy go in lanekit.py (19,548 bytes, room for about 930); lane.py keeps only the few lines that call them. Limit is 20,480 (dev/package.py:278), warning at 19,000 is acceptable but avoided where possible; role.py shrinks.
- Toy method: it builds a fixture with `dev/toy/make.sh` and runs the real `role.py lane` and `lanekit` as `test-lane-control.sh` does (its regression.py and a land row that counts starts into a file); control (d) copies the delivery scripts folder to a temp dir, replaces the any-name loop in `passed()` with the own name only (a sed on one marked line), and runs the same steps there: the happy case must then fail (a second job starts).
- Sweep: before build ends, run every toy that mentions `ship-lane`, `lane-wait`, `lane ship` or `lane pr` (test-lane-control.sh, test-lanes.sh, test-lane-died.sh, test-lane-tmpdir.sh, test-prep-budget.sh, test-pr-tries.sh, test-two-lanes.sh if present, test-tiers.sh, test-not-runnable.py, test-pr-body-cap.py, test-defects-a.py) and list any that change; the qa lane's own row selection also runs them.
- The HEAD-move rule prevails over reuse: a base merge by `goal.py pr` that moves HEAD runs a fresh pr lane, selecting affected rows as today.
- The CEO summary file's "Reviewer Concerns: None yet" is superseded by this list; the working plan is the plan file.

### CEO dual voices (native CEO subagent: approve with 7 medium; Codex plan-review model: FINDINGS P1, 3 high, 1 medium)

Native findings, all accepted (auto-decided P1, P5): (1) helper location contradiction: lanekit.py, fixed above; (2) copy-source rule stated twice: one rule plus the chained-copy control; (3) the pr step rarely reuses when main moved: the docs line says so; (4) the safety argument assumes one argv: the toy asserts it; (5) test-lanes.sh:234 new assertion stated exactly, sweep listed; (6) control (d) also asserts the second job; (7) dirty-tree gap recorded in the PR body.

Codex findings: (1) HIGH runner identity not in the key: TASTE, declined. Reason: done line 1 fixes the key as "that exact head"; the runner is the installed package that all three lanes of one goal share within minutes, and same-name reuse has had the same key since the gate was written (lane.py:204). Listed at the gate. (2) HIGH a pass with not-runnable rows satisfies every gate: TASTE, kept. The copied line keeps the `N pass; M not runnable here` text and the PR body shows it; excluding such passes would cancel most of the saving on this Mac and contradicts done line 1. Listed at the gate. (3) HIGH no supersession rule: examined, not a gap: a lane for any name returns its pass at once when one exists at HEAD (lane.py:204), so no failing lane can start at a head that already has a pass; a stale `.ok` of an older head never equals HEAD. No change. (4) MEDIUM business case unmeasured: declined: operation asked for the change by the owner's word ("first"); the saving is the second and third lane's prep, planning and slot wait per goal.

```
CEO DUAL VOICES — CONSENSUS TABLE:
  Dimension                            Claude  Codex     Consensus
  1. Premises valid?                   yes     partly    DISAGREE (runner identity: taste, listed)
  2. Right problem to solve?           yes     yes       CONFIRMED
  3. Scope calibration correct?        yes     yes       CONFIRMED
  4. Alternatives sufficiently explored? yes   partly    DISAGREE (accelerate the cache: taste, declined)
  5. Competitive/market risks covered? n/a     n/a       CONFIRMED (internal plumbing)
  6. 6-month trajectory sound?         yes     partly    DISAGREE (evidence contract: taste, listed)
```

Error and rescue registry: `passed()` JSON read: unreadable file, rescued (ignored, a lane starts); copy OSError: rescued (no `.ok`, LANE_MISSING, retried); `lane_ok` open: rescued by the existing OSError path. 3 rows, 0 critical gaps.
Failure modes registry: kill between `.last` copy and `.ok` write | rescued | toy asserts retry | user sees LANE_MISSING with the fix | logged by the lane line. Stale `.ok` at an older head | rescued | HEAD_MOVED control | HEAD_MOVED with the rerun command | logged. 0 critical gaps.
PLAN_REALITY: see the check line below.
Completion summary: mode SELECTIVE EXPANSION; 3 scope proposals, 1 accepted; 11 sections run (11 skipped: no UI); outside voice: codex completed, 4 findings, 2 accepted-as-taste listed, 1 examined, 1 declined; unresolved decisions 0; reality rows 7/7, unverified 0.

### CEO review sections (autoplan)

1 Architecture: one helper pair in lane.py, one call site change in role.py; dependency direction unchanged (role imports lane). Before: gate(name) reads ok(name). After: gate(name) reads ok(any). No new coupling.

```
  qa lane --pass--> qa.ok = H, qa.last{head H, pass}
  lane(ship) --passed(H)?--> copy qa.last/.txt -> ship.last/.txt, ship.ok = H  (no job, no process)
  need_lane(ship) --lane_ok--> any .ok == HEAD? yes -> None
  HEAD moves -> passed(H') none -> a new job starts as today
```

Data paths: happy (a pass at H reused); nil (no `.last` for any name: `passed` is empty, a lane starts); empty (a `.last` with no head: not equal, ignored); error (a `.last` that is unreadable: `read_json` returns None, ignored). Rollback: revert the commit; run records stay valid (same file names).
2 Error and rescue: `passed()` only reads JSON through `read_json`, which already returns None on a bad file (lane.py `read_json` import from lanekit); the copy uses `shutil.copyfile`; a failed copy (OSError) must not leave a half record: write `.ok` last, so a crash leaves LANE_MISSING and the next call retries. No catch-all. Gap: none; CRITICAL GAPS 0.
3 Security: no new input, path or command; the slug and names are the existing ones. N/A beyond that: no finding.
4 Data flow and edge cases: two callers racing to copy: both write identical bytes (the `.job` exclusive create is only on starting a lane); a dirty tree: no reuse (as today); qa lane fail at H then ship: no pass, a lane starts; ship lane live at H when qa is asked: existing sibling wait (lane.py:196). A copy while the source name is being re-finalized: `.last` is replaced atomically by `set_last`.
5 Code quality: about 20 added lines, none duplicated; role.py shrinks.
6 Test review: see the toy plan (step 6): happy, head moved, failed lane, other-head pass, dirty, copied `.txt`/`.last`, reuse-removed control, and the changed test-lanes.sh assertion. Test that makes shipping at 2am safe: step 6a. Hostile QA: a pass at another head with the same `.ok` text. Chaos: kill between `.last` copy and `.ok` write (a retry completes it).
7 Performance: saves a prep plus planning plus a lane process per later step; cost of `passed()` is three small file reads.
8 Observability: the copied LANE line says it was reused; the failure lines are unchanged.
9 Deployment: patch release, no migration; old run files keep working; the first lane after upgrade behaves as before.
10 Trajectory: reversibility 5/5; debt: none; the 1-year reader finds `passed()` beside `lane()` with a header line. Design/UX: SKIPPED (no UI scope).

NOT in scope: lane budgets, row selection, `prep`, the flow file, `merge`, the lane child (owner's list, goal file); a shared `<slug>.lane.ok` (rejected, see 0C); a `role.py lane-status` command (skipped).
What already exists: lane.py `lane()` sibling check, `finalize`'s `.ok`, `lane_status`; reused.
Dream state delta: moves from three records per head to one pass with three readers.

CEO consensus table is filled after the dual voices below.

### DX review (autoplan, DX POLISH)

Product type: CLI tool used by agents (`role.py lane SLUG qa|ship|pr`, `role.py lane-wait`, the `flow.py` and `goal.py` steps that call them). Mode: DX POLISH (enhancement to an existing product; no new commands or flags).

TARGET DEVELOPER PERSONA: Who: an AI worker session (primary) driving a goal, and the operation session that reads its lane lines. Context: runs `flow.py <slug> qa|ship` or `goal.py pr` unattended on a Mac with three lane slots. Tolerance: none for a hang or a second 15-minute wait; reads output literally. Expects: one pass at a head is enough, and a refusal that names the fix command.

Developer empathy narrative: I am a worker. My qa step finished: LANE qa AFFECTED 4/4 in 612s. I run `flow.py lane-once ship`. Today I wait for another lane process: prep, planning, a slot, and a second line `LANE ship REUSED 0/4`. At minute 1 I wonder whether it re-ran my tests; the REUSED word tells me the rows were skipped but I still held a slot. After this plan I run the same command and get one line, instantly, saying the qa lane passed on this head, then NEXT. I never open a file to learn why. (Observed: lane.py:204 and test-lanes.sh:234 today; predicted: the new line, not yet written.)

Competitive DX benchmark (evidence: reported, not measured): Bazel/remote caches and GitHub Actions `needs:` reuse one result per commit across downstream jobs; Buildkite "skip if the same commit passed" does the same. This tool's equivalent boundary: start `flow.py ship` to its NEXT line. Today ~prep+plan+slot wait seconds to minutes; after, under 2 seconds. [estimated; re-measure in the toy: the second command makes no job and returns in the fixture's seconds]. Tier: Champion (< 2 min) for ship and for pr when HEAD is unmoved.

Magical moment (0D, delivery vehicle chosen by P5, lowest effort): the existing lane output line itself, extended with `; reused: the qa lane passed on this head`. No new command.

Developer journey map:

```
STAGE           | DEVELOPER DOES                         | FRICTION POINTS                         | STATUS
1. Discover     | reads flow.py NEXT line                | none: unchanged                         | ok
2. Install      | none (same scripts)                    | none                                    | ok
3. Hello World  | role.py lane SLUG ship after qa pass   | second lane ran today                   | fixed (reuse)
4. Real Usage   | goal.py pr after a base merge          | HEAD moved: a new lane, as the rule says| ok (documented)
5. Debug        | reads the LANE line and .last          | a copy must say it is a copy            | fixed (reused note)
6. Upgrade      | next release with old run files        | old files keep their names              | ok
```

First-time developer report (grounded in the code): T+0:00 `role.py lane s ship` after qa passed. T+0:02 today: "RUNNING" then 10 minutes of waiting for a slot; after: the pass line in the same second. T+0:30 reads `ship-lane.last`: the line carries `; reused: the qa lane passed on this head`. T+1:00 runs `goal.py pr` after main moved: HEAD moved, so a fresh pr lane starts; the docs line says so. No confusion remains; the only prediction is the pr step, now documented.

Pass 1 Getting started 8/10 -> 9: one command, one line; the toy proves no job starts. Pass 2 CLI design 8/10: no new names or flags; the lane names stay qa, ship, pr (consistency over cleverness). Pass 3 Errors 8/10 -> 9: refusals LANE_MISSING and HEAD_MOVED already carry what, fix, code; the reuse path adds no error. ERROR PATH MATRIX (agent-ready-v1): usage (unknown lane name) | what pass, fix pass, code pass, redaction pass, channel pass (exit 2 usage text, lane.py:359-370) | no cap; reuse copy failure (OSError) | what: the OSError text, fix: run the same command again, recovery: retry, side effects none, code: the lane has a LANE_ code only for existing paths: GAP, add `LANE_REUSE_COPY` to the failure line if the copy raises | CAP6 context noted, accepted as a plan item below; unexpected failure (corrupt `.last`) | read_json returns None: a lane starts, nothing is hidden | pass. Pass 4 Docs 7/10 -> 9: `skills/loop-files.md` line 140 gains the one-lane-per-head sentence and the pr caveat. Pass 5 Upgrade 9/10: file names and refusal texts unchanged; old runs still read. Pass 6 Environment 8/10: no new platform surface; works with the existing fixtures on Linux CI. Pass 7 Community 7/10: internal repo; N/A beyond the PR body. Pass 8 Measurement 7/10 -> 8: the toy asserts the start count; the PR body states the measured fixture seconds; no telemetry is added (a target tier does not approve one).

### DX dual voices (native DX subagent: about 7/10, 5 required changes; Codex plan-review model: FINDINGS P1, 1 high, 4 medium, 2 low)

Accepted (auto-decided P1/P5): stable greppable reuse string and a transcript in the docs; `lane_ok` returns the source and refusals name it; one precedence rule so `lane` and `lane-wait` agree; `lane_note` falls back to the passing name so the in-session record route keeps the qualification; interrupted-copy and stale-head toy cases; the manual recovery path documented; superseded plan text resolved by the "accepted bullets are authoritative" rule.
Taste, kept and listed at the gate: runner identity in the reuse key (same as CEO Codex 1); reuse of a pass with not-runnable rows (same as CEO Codex 2, now with the documented manual recovery as the escape); a `--fresh` flag (native high) declined because DX POLISH adds no flags and the files to remove are named in the docs; a repo setting to turn reuse off (native medium) declined, no second consumer.
Declined: a dirty-tree check inside `need_lane` (unchanged from today, listed as a known limit); a measured before/after time (same as CEO Codex 4).

```
DX DUAL VOICES — CONSENSUS TABLE:
  Dimension                           Claude  Codex     Consensus
  1. Getting started < 5 min?          yes     yes       CONFIRMED
  2. API/CLI naming guessable?         yes     yes       CONFIRMED
  3. Error messages actionable?        partly  partly    CONFIRMED (both: name the source lane and heads; fixed above)
  4. Docs findable & complete?         partly  partly    CONFIRMED (both: add a transcript; fixed above)
  5. Upgrade path safe?                yes     partly    DISAGREE (runner identity: taste, listed)
  6. Dev environment friction-free?    partly  partly    CONFIRMED (both: recovery for repaired environments; documented)
```

DX Scorecard: Getting Started 9, API/CLI 8, Error Messages 9, Documentation 9, Upgrade Path 9, Dev Environment 8, Community 7 (N/A, internal), DX Measurement 8; TTHW: second command under 2 seconds; mode POLISH; Overall DX 8.4/10 (initial 7.6).

DX Implementation Checklist: [x] ship after qa returns without a second job; [x] first run output is the pass line with the reused note; [x] errors keep what/fix/code; [ ] `LANE_REUSE_COPY` named when the copy raises (plan item); [x] no new command or flag; [x] docs line 140 updated; [x] works without a terminal (no prompts); [x] changelog by delivery.

Plan item added by DX (accepted, auto-decided P1): if the copy raises OSError, `lane()` returns fail with `LANE_REUSE_COPY: could not copy the <src> lane record (<cause>). Fix: run the same command again; nothing was changed.` and writes no `.ok`; the toy covers it with an unwritable `.last` target.

<!-- autoplan-accepted:dx -->
- No new command, flag or lane name; the copied lane line carries `; reused: the <src> lane passed on this head`, and a second `role.py lane SLUG ship|pr` at a head with a pass returns it at once with no prompt.
- If the copy raises OSError, `lane()` returns fail with `LANE_REUSE_COPY: could not copy the <src> lane record (<cause>). Fix: run the same command again; nothing was changed.`, writes no `.ok`, and the toy covers it with an unwritable target.
- `skills/loop-files.md` carries the one-lane-per-head sentence and the pr caveat (HEAD moved means a new lane).
- Existing refusal texts (LANE_MISSING, HEAD_MOVED) and run file names are unchanged.
- `lane_ok` returns `(ok_text, source)`; a refusal names the lane that last passed and its head: HEAD_MOVED reads `HEAD moved since the <src> lane passed (lane on <h>, HEAD <h2>)` with the unchanged fix line and code (own-name text is byte-identical to today); LANE_MISSING and HEAD_MOVED keep their codes.
- Precedence for a shared pass: a pass by any name at HEAD, with a clean tree, wins in `lane()` and in `lane_status()` (so `lane` and `lane-wait` agree) over an own terminal fail at the same head; a live job of another name at this head still returns running; a dirty tree gets no reuse in either.
- `lane_note(runs, slug, step)` falls back to the passing name's `.last` when the step has none, so `goal.py record --in-session` keeps the `N pass; M not runnable here` qualification.
- The reuse string `; reused: the <src> lane passed on this head` is a documented, toy-asserted contract; `skills/loop-files.md` carries a short two-command transcript (qa lane, then ship lane) and the manual recovery for a pass that must be retested without a commit: remove the `<slug>.<name>-lane.last` and `.ok` files of the passing name and of the step, then run the lane command again. No new flag or command.
- The toy adds an interrupted-copy case (`.last` copied, no `.ok`): the next call completes the copy and passes; and a stale-head case where ship has no `.ok` and qa's `.ok` is older than HEAD: HEAD_MOVED names qa and both heads.
- Where earlier steps (1, 9) and these accepted bullets differ, the accepted bullets are authoritative.
<!-- /autoplan-accepted:dx -->

### Eng review (autoplan)

Step 0 Scope Challenge: scope accepted as-is. Counted work: 7 files (lane.py, lanekit.py, role.py, `skills/loop-files.md`, `dev/toy/test-lane-once.py`, `dev/toy/test-lanes.sh`, `.loop/regression.tsv`) plus goal records and stamps; 0 new classes or services; under the 8-file and 2-class gate, so the complexity selectors are skipped.

REALITY: premise-table pass nine claims re-checked against the code, unverified=0 (skills/workflow-delivery/scripts/lane.py:204)
REALITY: already-done pass `git log origin/main --since=2026-11-20` on lane.py and role.py shows no lane-once commit (977f4f067)
REALITY: surface-check pass the commands `role.py lane` and `lane-wait` exist with these arguments (skills/workflow-delivery/scripts/lane.py:358)
REALITY: binding-decisions pass no binding decision overrides the goal's done lines (.loop/goals/lane-once.md:12)
REALITY: numbers pass byte sizes lane.py 18,716, lanekit.py 19,548, role.py 19,997 are [measured: wc -c on the branch]; the helper size ~700 to 900 bytes is [estimated] and re-measured at build (skills/workflow-delivery/scripts/lanekit.py:1)
REALITY: deferred-asks pass issue 5734 asks for one lane per head; nothing it asks for is left out (.loop/goals/lane-once.md:1)
REALITY: pr-count pass one PR, a patch (.loop/goals/lane-once.md:16)

What already exists: lane.py `lane()` already stops a lane of another name on an older head and waits on a live sibling (lane.py:192-198); `finalize` writes `.ok` and `.last`; `read_json`, `set_last`, `dirty` are in lanekit.py (lanekit.py:175-183, 268). Reused, nothing rebuilt.

Section 1 Architecture (design twice): shape A, a `passed()` lookup plus copy-on-reuse (chosen); shape B, a single `<slug>.lane` record read by every step (rejected: renames every reader and loses old runs; the lookup is the seam B would replace). Eight red flags: no shallow module (two small helpers hiding the name loop and the copy), no leakage (the three file names stay in lanekit.py only), no temporal split, no pass-through, split ownership: `.last`/`.ok` for a name now has two writers (the lane's own finalize and the copy) but only one can win per head because the copy runs only when no job is held and no own pass exists: one owner per record at a time, recorded; no second way to do one task (need_lane and lane() both use `lane_ok`/`passed`); importable internals n/a; hand-synced list: the tuple NAMES is the one list.

```
  role.py need_lane --lane_ok(runs,slug,step,head)--> lanekit.lane_ok --reads--> <slug>.{qa,ship,pr}-lane.ok
  flow.py/goal.py pr --> role.lane --> lane.lane() --> lanekit.passed(...) --> <slug>.<name>-lane.last
                                         |                 | pass at HEAD, clean tree
                                         |                 +--> lanekit.reuse(src,dst): copy .last,.txt (+suffix), write .ok last
                                         +--> else: today's path: stop older-head sibling, wait on live sibling, start a job
```

Section 2 Code quality: ~25 added lines in lanekit.py, ~6 in lane.py, role.py shrinks; no duplicated behavior (the old own-name reuse line is replaced, not kept); naming follows the file (`passed`, `lane_ok`, `reuse`).
Section 3 Test review: diagram.

```
CODE PATHS                                              USER FLOWS
[+] lanekit.passed(runs,slug,head,name)                 [+] qa then ship then pr at one head
  ├── own pass at head          [GAP] toy (a)             ├── [GAP] one job, two reuses (toy a)
  ├── other name's pass         [GAP] toy (a)             ├── [GAP] chained copy suffix (toy)
  ├── no pass / bad .last       [GAP] toy (b)           [+] HEAD moved after qa
  └── dirty tree                [GAP] toy (b)             └── [GAP] HEAD_MOVED names qa; new job (toy b)
[+] lanekit.reuse(src,dst)                              [+] failed or interrupted
  ├── copy ok, .ok last         [GAP] toy (a)             ├── [GAP] failed qa lane: no reuse (toy b)
  ├── OSError                   [GAP] toy: LANE_REUSE_COPY └── [GAP] interrupted copy retried (toy)
  └── already copied            [GAP] toy
[+] lanekit.lane_ok / role.need_lane                    [+] lane-wait
  ├── any .ok == head           [GAP] toy                 └── [GAP] agrees with lane (toy)
  └── else own text + source    [★★ TESTED today] test-lane-control.sh:176-184 (own name)
[+] role.lane_note fallback     [GAP] toy
COVERAGE: 0/14 new paths tested today (the toy is the plan)  |  existing refusal paths ★★: 2
QUALITY: target ★★★ for the shared pass (behavior + edge + error)  |  GAPS: 14, 0 E2E, 0 eval
```

Each gap maps to one assertion in `dev/toy/test-lane-once.py` (a single row, the toy runs the real `role.py lane` on a fixture with a counting land row); value cards are in the on-disk review test plan. Tests made obsolete: none; `dev/toy/test-lanes.sh:234` is rewritten. Existing toys unaffected by reading: test-lane-control.sh:176-184 holds.
Section 4 Performance: three small file reads per `lane()` call; the saving is two lane processes per goal head. No hot loop, no budget needed.

Failure modes registry:

```
CODEPATH            | FAILURE MODE                    | RESCUED? | TEST? | USER SEES?                   | LOGGED?
lanekit.passed      | unreadable .last                | Y ignored| Y     | a lane starts, as before     | Y
lanekit.reuse       | OSError on copy                 | Y        | Y     | LANE_REUSE_COPY + fix        | Y
lanekit.reuse       | crash between copy and .ok      | Y retry  | Y     | LANE_MISSING then pass       | Y
lanekit.lane_ok     | stale .ok at older head         | Y        | Y     | HEAD_MOVED names source/heads| Y
role.lane_note      | no own .last                    | Y fallbk | Y     | note kept                    | Y
lane() vs wait      | ship failed, qa passed at H     | Y rule   | Y     | both say pass                | Y
```

0 critical gaps. NOT in scope: lane budgets, row selection, the flow file, `merge`, the lane child; a repo setting to disable reuse; a `--fresh` flag; a dirty-tree check in `need_lane`; a measured before/after timing; runner identity in the key (listed taste). Deferred to TODOS.md: none (the goal limits the diff to the listed files; the taste items are in the PR body and at the gate).
Parallelization: sequential implementation, no parallelization opportunity (one module, lanekit.py, with its two callers).

### Eng dual voices (native Eng subagent: sound, 9 findings, 4 to resolve before build; Codex plan-review model: FINDINGS P1, 3 high, 4 medium)

Accepted (auto-decided P1/P5): complete-alias rule and atomic copy with `.ok` last; the corrected error text; evidence kept in `.prev`; structured `reused_from`; sibling finalization in `lane_status`; `lane_note` from the satisfying pass; first-line placement of the suffix; the toy additions listed in the accepted block; the overflow plan for the byte budget (copy stays in lane.py if lanekit.py would pass 20,480; no new file under skills/).
Taste, kept and listed at the gate: runner fingerprint in the reuse key (Codex high, third phase it appears; done line 1 fixes the key as "that exact head"); whole-lane reuse over the planner's skipped and flaky row retry (Codex high; the copied note discloses it, the manual recovery retests); `need_lane` with a dirty tree (native medium; unchanged from today, a toy control records it).

```
ENG DUAL VOICES — CONSENSUS TABLE:
  Dimension                           Claude  Codex     Consensus
  1. Architecture sound?               yes     partly    DISAGREE (runner fingerprint in the key: taste)
  2. Test coverage sufficient?         partly  partly    CONFIRMED (both: interrupted copy and sibling cases; fixed above)
  3. Perf risks + budget/bench named?  yes     yes       CONFIRMED (no hot path)
  4. Security threats covered?         yes     yes       CONFIRMED (fixed tuple of names, no new input)
  5. Error paths handled?              partly  partly    CONFIRMED (both: partial copy; fixed above)
  6. Deployment risk manageable?       yes     partly    DISAGREE (row retry policy bypass: taste, documented)
```
Completion summary: Step 0 scope accepted as-is; reality rows 7/7, 0 unverified; Architecture 2 issues; Code quality 1; Test review diagram produced, 14 gaps (all in the one toy); Performance 0; NOT in scope written; What already exists written; TODOS.md updates: 0 items proposed (taste items go to the gate and PR body); failure modes: 0 critical gaps; unresolved decisions 0; outside voice: codex completed; parallelization: sequential; Lake Score 5/5 (every scored recommendation took the complete option).

<!-- autoplan-accepted:eng -->
- lanekit.py gains `passed(runs, slug, head, name)`, `lane_ok(runs, slug, step, head)` and `reuse(runs, slug, src, dst, head)`; lane.py calls them in `lane()` and `lane_status()`; role.py `need_lane` and `lane_note` call them. If the measured lanekit.py size would pass 20,480 bytes, `reuse` stays in lane.py (18,716 bytes now); neither file passes 20,480.
- `reuse` copies `.last` and `.txt` to the step's names (suffix replaced, never stacked), then writes `.ok` last; a crash between leaves LANE_MISSING and the next call completes it; an OSError returns the LANE_REUSE_COPY failure and writes no `.ok`.
- `dev/toy/test-lane-once.py` (one regression row) asserts every gap in the test diagram: own and other-name pass, no pass or unreadable `.last`, dirty tree, copy ok, OSError, interrupted copy, `lane_ok` match and stale heads, `lane_note` fallback, `lane` and `lane-wait` agreement, chained suffix, identical argv for the three names, and the reuse-cut control that fails; value cards are in the on-disk test plan.
- The failure modes registry above has 0 critical gaps and stays so.
- A name's pass is complete only when its `.last` says pass at HEAD and its `.ok` equals HEAD; `passed()` returns only complete names, and an own `.last` pass without `.ok` is an incomplete alias that `lane()` repairs by redoing the copy from a complete source (if none exists, a lane starts). `reuse` writes `.txt` and `.last` through a temp name and `os.replace`, then `.ok`; the OSError text is `LANE_REUSE_COPY: could not copy the <src> lane record (<cause>); no .ok was written. Fix: run the same command again`.
- Before the copy replaces an own terminal fail at the same head, that record moves to `<name>-lane.last.prev`; the documented manual recovery moves the lane files aside (`.prev`) instead of deleting them and says that a rerun of rows needs `regression.py run <id>` (the row cache can still reuse passes).
- The origin is a structured field in the copied `.last` (`reused_from`), and the suffix is rendered from it on the first line of the line (before any newline), so the PR body's first-line cut keeps it; the source picker prefers a record with no `reused_from`.
- `lane_status()` also finalizes a sibling's ended job at this head (through that name's `finalize`) and reports running for a live sibling job, then re-reads `passed()`; `lane_note` reads the `.last` of the name whose `.ok` satisfies the gate (own first).
- Toy additions: a failure after each write of the copy (`.last` only; `.last` and `.txt`), `.last` copied with `.txt` missing, a table test of `lane` against `lane_status` over fixture states (own fail plus other pass, dirty tree, live sibling job, sibling ended but not finalized), a budget-limited multiline result, all three names missing, `need_lane` with a dirty tree (records today's behavior), the fixture counter as the only source of the start count, argv compared in full for the three names, and the reuse-cut control asserting that the cut changed the file and that the happy case fails because a second job started.
<!-- /autoplan-accepted:eng -->

