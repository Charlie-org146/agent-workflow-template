# auto-approve-off: plan

Design: .loop/designs/auto-approve-off.md. Goal: .loop/goals/auto-approve-off.md (done lines frozen).

## Implementation plan
1. `.loop/config.json`: `"auto_approve": false`. Nothing else in the file changes (`auto_merge` stays true). The goal's worktree carries no local floor edit.
2. Regenerate, never hand-edit: `entry.py write` (workflow-docs) for `.loop/START.md`; the settings render (`docs.py`/`criteria.py render`, whichever owns `docs/wiki/How-to-use-Setup.md` row `auto_approve`) so the row reads default, not "overridden: true". Revert unrelated churn the render makes. Restamp the pages it touches (`audit.py restamp auto-approve-off`).
3. `docs/wiki/How-to-use-Delivery.md:48`: rewrite the sentence "This repo runs with no gates ..." to say `auto_merge` is on, `auto_approve` is off, and what a step leaves for the owner waits (WAITING, under Needs you) until the owner answers; review stays the only check step.
4. `dev/toy/test-goal.sh`: after the "No gates" block (its negative control, auto_approve true prints `AUTO-APPROVED`, stays unchanged), add a case that reads this repo's committed `.loop/config.json` from `$here`, asserts `auto_approve` is false, copies that value into the fixture config, runs a step replying `PENDING: <item>` and asserts `WAITING`, run record status `waiting` with `waiting.ask` set (guards.hold, guards.py:134-135), and no `AUTO-APPROVED` and no `auto-approved` in the goal log. One new PASS line.
5. `dev/toy/test-goal.sh` header: add `.loop/config.json` to its `# reads:` lines. The lane selects a row for a config change only when the script reads `.loop/config.json` and names the changed key (narrow.py:69-75), and the new case now depends on the committed value; without the header a later flip back to true would not rerun the row.
6. `.loop/regression.tsv`: extend the existing `auto-approved` row's command with a second grep for the new PASS line. No new row; `reads:` header of the row unchanged unless the row has one that must name `.loop/config.json`.

## Verification
- `settings.py show` reports auto_approve false; `docs.py check --own` clean.
- Sweep: every toy that renders settings/START or runs record, before and after, on a fresh clone; no assertion changed except one that reads the repo value (none expected: test-goal, test-review-depth, test-delivery-prd set their own config; test-defect.sh:255 quotes the generic commands.md line).
- Byte caps: no script changes, so every script's size is unchanged.

## NOT in scope
auto_merge; plan_ahead (an owner's "approve ahead" answer); any script or wording change in goal.py; the headless case.

## What already exists
`goal.py:280` already holds a PENDING step when auto_approve is not true; the "No gates" block in test-goal.sh already proves the true side. Only the committed value and the sentence that describes it are wrong.

## Failure modes
- A row that renders the repo value changes text: caught by the lane; fix only if it reads the repo value.
- Wiki pages turn stale after the render: restamp before the lane.
- With auto_approve still true on main, this goal's own plan/review record could auto-approve a PENDING item: keep PENDING empty or hold (TD1051).


## Review record

### CEO
## CEO review (HOLD SCOPE; owner decided the value, o806)

| premise | claim | receipt | verdict |
|---|---|---|---|
| P1 | .loop/config.json has auto_approve true | .loop/config.json:35 | verified |
| P2 | record holds a PENDING step unless auto_approve is true or plan_ahead | skills/workflow-delivery/scripts/goal.py:280, skills/workflow-delivery/scripts/fit.py:322-323 | verified |
| P3 | settings.py show lists the repo value | `settings.py show` line 8 prints `auto_approve | true | repo | .loop/config.json` | verified |
| P4 | the Setup row is rendered, not written by hand | skills/workflow-docs/scripts/render.py:271 (`overridden` or `default`) | verified |
| P5 | START.md is written by entry.py write | skills/workflow-docs/scripts/entry.py:282,336 | verified |
| P6 | restamp takes a slug | skills/workflow-docs/scripts/audit.py:378 | verified |
| P7 | full_auto stays true and is independent of auto_approve | .loop/config.json:52, skills/workflow-monitoring/scripts/auto.py:76 | verified |
| P8 | the line in test-defect.sh:255 quotes the generic reference, not the repo | dev/toy/test-defect.sh:255, skills/workflow-delivery/references/commands.md:580 | verified |
unverified=0

REALITY: premise-table pass 8 claims, each with a receipt, unverified=0 .loop/config.json:35
REALITY: already-done finding `git log origin/main -- .loop/config.json` shows auto_approve was set off by 1943c87a9 (o700, 2026-11-20) and reverted by ab4651036 the same day (the commit message gives no reason); no commit on main sets it false now, so the work is not done .loop/config.json:35
REALITY: surface-check pass settings.py show, entry.py write, audit.py restamp exist; the settings render owner is render.py skills/workflow-docs/scripts/render.py:271
REALITY: binding-decisions pass the branch decision search printed nothing; the binding words are o806 (off) and the goal's frozen done lines; o700's revert is history, o806 is later .loop/goals/auto-approve-off.md:9
REALITY: numbers pass no figures beyond line numbers, each read from the files [measured: grep] .loop/config.json:35
REALITY: deferred-asks pass no linked issue; nothing left out .loop/goals/auto-approve-off.md:1
REALITY: pr-count pass one PR, no split, no ship policy file .loop/goals/auto-approve-off.md:3

### Scope (HOLD SCOPE)
Accepted: the five plan items. Not expanded. Nothing deferred.
Finding C1 (WARNING, non-blocking): the same flip was made and reverted on 2026-11-20 (1943c87a9, ab4651036). Whoever reverted it did not leave a reason in the commit. o806 is the newer owner word and the frozen done line, so the plan stands; the PR notes should say the owner's o806 is the authority so a later revert is a visible choice.
Finding C2 (OK, informational): `full_auto` stays true (config.json:52). A step held for the owner can still be answered by the operation session under auto.py's rules, so "holds for the owner" means the item is held at record, not that no session can answer it. The owner said only auto_approve; the plan leaves full_auto alone and says so in NOT in scope.

### Sections 1-10 (examined; no issues unless named)
1 Architecture: one config read at goal.py:280; no new component. Rollback: revert the one key; time under a minute. No issues found.
2 Error and rescue: no new codepath or exception; the held path (WAITING, guards.hold) exists. 0 gaps.
3 Security: this turns a gate on, which narrows what is approved without the owner; no new input, secret or surface. No issues found.
4 Data flow: the shadow paths are PENDING empty or none (pending_items drops them, tested by the "ng" case) and a real item (held). Covered by the new case plus the existing ones. No issues found.
5 Code quality: no script changes; the toy case reuses the cfg and step helpers of the block above. No issues found.
6 Tests: new case holds; negative control stays (true gives AUTO-APPROVED). Assertion: PENDING item with the repo's committed value prints WAITING, status stays running, log has no auto-approved. It rejects a wrong result where the repo value were true. no_claim=real owner answer flow (fixture goal only).
7 Performance: none.
8 Observability: the hold prints WAITING and appears under Needs you on the board; no new log needed.
9 Deployment: config key only; no migration; old and new readers read the same key. The lane proves rows still pass.
10 Trajectory: reversibility 5/5. Debt: none added. One documentation debt removed (the "no gates" sentence goes).
11 Design/UX: SKIPPED (no UI scope).

### NOT in scope
auto_merge (owner named only auto_approve); full_auto; plan_ahead; goal.py wording; the headless-trust question (belongs to trust-fail-closed).
### What already exists
goal.py:280 hold logic; the "No gates" toy block; render.py and entry.py generators.
### Dream state delta
12-month ideal: the repo's gates are the owner's visible choice; this moves the committed value to the owner's word and ties the prose to the value.
### Failure modes
| codepath | failure mode | rescued | test | user sees | logged |
|---|---|---|---|---|---|
| record, PENDING item, auto_approve false | a revert of the key flips back | n/a | new toy case reads the committed value | WAITING | goal log |
| rendered rows | stale after the flip | restamp + docs check | docs.py check --own | clean check | audit log |
0 critical gaps.

### Completion
Mode HOLD SCOPE; findings 2 (C1 warning, C2 info); critical gaps 0; unresolved decisions 0; outside voice: not run in this step (Codex not asked; see the reply's VERDICT lines).

## Eng review (HOLD SCOPE; code read, not assumed)

REALITY: premise-table pass every claim below cites a line I read, unverified=0 skills/workflow-delivery/scripts/goal.py:280
REALITY: surface-check pass guards.hold sets status waiting; config() read at goal.py:278 skills/workflow-delivery/scripts/guards.py:134

### Scope challenge
Minimum change: one key plus the sentence that describes it. No script change, so no byte-cap exposure (operate.py and every capped script stay as they are). Complexity: 5 files (config.json, START.md, Setup page, Delivery page, test-goal.sh) plus regression.tsv; all in the done lines' Touches.

### Findings
E1 (CORRECTED in the plan): the plan said a held step leaves status running. guards.hold sets status "waiting" and waiting.ask (guards.py:134-135). The toy asserts waiting, not running (the "running" check at test-goal.sh:164 is the auto-approved side).
E2 (CORRECTED in the plan): the lane selects a row for a config change only if its script reads .loop/config.json and names the changed key (narrow.py:69-75). test-goal.sh reads neither in its header. The new case reads the committed value, so the header gets `.loop/config.json` (test-goal.sh names auto_approve already). Cost: this goal's config flip selects the 9 test-goal rows and test-defect.sh/test-auto-owner-words.py (already reading config.json) in the lane; the lane budget (15 min) is the thing to watch, so the lane note goes in the PR.
E3 (OK): test-auto-owner-words.py:57 asserts full_auto true in the repo config and never reads auto_approve; test-defect.sh:255 quotes the generic commands.md line. Neither changes.
E4 (OK): the fixture config comes from the fixture repo; the new case passes the repo's value through the existing cfg helper (cfg 'auto_approve=<value>'), so the case holds even if the fixture default changes.

### Architecture (ASCII)
    .loop/config.json --auto_approve--> goal.py:280 (wait and (true or plan_ahead))
         | false                              |
         v                                     v
    cfg.get(...) is True? no -> hold (WAITING)   yes -> AUTO-APPROVED + advance
    START.md/Setup rows <-- entry.py write / render.py:271 (generated)
    How-to-use-Delivery.md:48 (hand-written, rewritten)

### Test diagram
| codepath | test | happy | failure | edge |
|---|---|---|---|---|
| record PENDING item, repo value false | new case in test-goal.sh | WAITING, status waiting | n/a | PENDING none still records (existing "ng" case) |
| record PENDING item, auto_approve true | existing No-gates block (negative control) | AUTO-APPROVED | n/a | existing |
| rendered rows | docs.py check --own | clean | stale page fails the check | restamp |
| lane reach | test-config-lane.py semantics | row selected on key change | n/a | header present |
no_claim for the new case: real owner answer flow and the board (fixture goal only).

### Performance / failure modes / deploy
No hot path. Failure modes: a stale page after the render (caught by docs check), a revert of the key (caught by the new case via the reads header). Rollback: git revert, under a minute. 0 critical gaps.

### Completion
Eng findings 4 (2 corrected in the plan, 2 informational); critical gaps 0; unresolved decisions 0; outside voice not run (see VERDICT lines).

## DX review (adopter-facing docs only; the change adds no command, flag or API)

REALITY: surface-check pass no new command, flag or route; the setting already exists in settings.py:22 skills/workflow-setup/scripts/settings.py:22
Developer: an adopter reading How-to-use-Delivery or the Setup settings table.
Journey: (1) reads the Delivery page: line 48 says this repo runs with no gates, auto_approve and auto_merge on: false once the key flips; (2) reads the Setup row: shows "overridden: true": false after; (3) runs the board: held items show under Needs you.
D1 (FIX, in plan item 3): rewrite line 48 so it matches (auto_merge on, auto_approve off) and keeps the pointer that the release step merges after review.
D2 (OK): the Setup row is generated; "default" replaces "overridden: true" through render.py:271, no hand edit.
D3 (OK): START.md row regenerates through entry.py write.
Scores: getting-started n/a (no change), error messages n/a, docs accuracy 6/10 before (one false sentence), 10/10 after the rewrite. TTHW unchanged. DX checklist: [ ] sentence rewritten [ ] rows regenerated [ ] docs.py check --own clean.

## REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | CLEAR | HOLD SCOPE, 0 critical gaps; C1 (revert history of the same flip) and C2 (full_auto stays true) noted |
| Outside Review | none | Independent 2nd opinion | 0 | not run | no completed external or native fallback review; coverage missing |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR | 4 issues, 0 critical gaps; E1 (hold status is waiting) and E2 (reads header for the lane) corrected in the plan |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | skipped | no UI scope |
| DX Review | `/plan-devex-review` | Developer experience gaps | 1 | CLEAR | score 6/10 to 10/10 after the sentence rewrite; no TTHW change |

**OUTSIDE COVERAGE:** none ran (Codex not asked; the preflight and native fallback were skipped); reviews are native only.
**VERDICT:** CEO + ENG + DX CLEARED on the plan; outside voice missing, named so it is not read as clean.

NO UNRESOLVED DECISIONS
