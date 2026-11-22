<!-- /autoplan restore point: kept outside the repo (a git-excluded scratch folder) -->
# Plan: restamp-own-idempotent

Design: reproduced in a scratch clone of main. `audit.restamp_own` passes the STALE page set from `docs.py check --own HEAD` to `relock(root, slug, only)`. `relock` reads an empty `only` as "no filter, every page" (the slug-less auto-relock needs that), so with nothing stale every Reviewed page whose text is unchanged is written to `.loop/kept/<slug>.tsv` and a "Kept: <slug>" commit is made, on every run. With one really stale page, run 1 restamps that page and its How-to page (right) and run 2 restamps all 13 pages.

## Implementation plan

Source: issue #5797 (Operation TD969). The done lines are frozen in `.loop/goals/restamp-own-idempotent.md`.

1. `skills/workflow-docs/scripts/audit.py`: `restamp_own` takes its stale set from `docs.py check --own HEAD` (the STALE lines, the same predicate the docs check uses; audit.py:267-269) and returns `[]` before `relock` when that set is empty; the final lines are `only = {...}` and `return relock(root, slug, only) if only else []`. Callers of restamp-own: `audit.py restamp-own` (audit.py:384) prints one RESTAMPED line per returned page, so `[]` prints nothing; `lanekit.prep` (lanekit.py:340) runs it and then commits only dirty page files ("Lane: re-render the Tests tables"), so with nothing written there is no commit; `keep()` commits only its own `.loop/kept/<slug>.tsv`, and with `[]` it is never reached. `relock(root, slug, only)` is called with a slug and a page list by the CLI `audit.py restamp SLUG PAGE...` (audit.py:386) and the toys; it keeps its empty-set meaning, and `docs.py audit --relock` (docs.py:304) calls it with no slug. The file stays under 19,000 bytes: measured 18,991 with `wc -c` on the committed change (dc3872db0) (9 bytes of headroom, so any later edit to audit.py re-measures; a breach is a stop, not a trim elsewhere).
2. `dev/toy/test-restamp-idempotent.py`: a two-page fixture repo. Nothing stale: two runs print nothing, make no commit, append no kept rows. One real code change to a.py: the first run restamps exactly A in one commit, the second restamps nothing. The toy runs `audit.py restamp-own my-goal` as a subprocess in a temp repo (not through lanekit.prep), counts commits with `git rev-list --count HEAD` after each run, and a stale page is restamped by a kept row that `keep()` commits, so nothing is left uncommitted between runs (`check --own HEAD` is clean after run 1). Assertions: with nothing stale both runs print no RESTAMPED, the commit count is unchanged and no kept file exists; after one real change run 1 prints exactly `RESTAMPED A`, adds one commit and the kept rows are exactly [A]; run 2 prints nothing and the commit count and kept rows are unchanged. Negative control: the same check against a copy of `skills/workflow-docs` (scripts and references, so the rules block loads) whose audit.py has the text `if only else []` removed by string replace must fail, and the toy first asserts that the replace changed the file, so a drifted fix fails the control for a clear reason.
3. One regression row `restamp-own-idempotent-5797` under DOC-2 (the requirement that a re-stamp is a line in `.loop/kept/<slug>.tsv`), its own row, then `criteria.py render`. Rule: top's TD970 lets a new script carry its own row (net-zero exception), and TD815 allows folding only into a row for the same feature and the same script; `stale-comments-only-3122` runs test-merge-unblock.py, so it is not folded. docs/wiki changes only by that render (the Tests tables in Tests.md and Documentation.md).
4. Checks: `docs.py check --own`, `criteria.py render --check`, `dev/package.py --static` (observed PASS: 100 files before and after; dev/toy is not in the shipped listing), the private-name scan; sizes measured with `wc -c`: audit.py 18,991, the new toy 4,898, none newly over 19,000 (Tests.md and Documentation.md were already over). The goal stops at a pull request by the delivery flow, not by this change; Verify by hand stays empty because a patch has no release step of its own.

## NOT in scope

`relock` itself, `lanekit.prep`, `goal.py pr`, any change to when a page counts as stale, any loosened check or trimmed file.

## Failure modes

| step | failure | handled | the owner sees |
|---|---|---|---|
| 1 | a page really is stale but `check --own` prints nothing | nothing restamps; the docs check still reports it | STALE line from the docs check |
| 2 | fixture drifts from real page format | the toy builds pages with the repo's own `prd` functions | FAIL line |
| 3 | row text not Given/When/Then | docs check refuses it | REWRITE line |
| 1 | an unknown slug or an unwritable `.loop/kept/<slug>.tsv` | with nothing stale nothing is written; with a stale page `keep` raises as before, out of scope | the traceback, as today |
| 1 | `docs.py check --own HEAD` crashes (`seen` is its stdout string, audit.py:267) | stdout is empty, so nothing is restamped or committed; raising on a non-zero exit is skipped (9 bytes of headroom in audit.py; the goal's own docs check reports the crash) | no RESTAMPED line, the docs check output |


<!-- autoplan-accepted:ceo -->
- (accepted obligations, canonical list) restamp_own returns [] when the stale set is empty, before relock is called; relock keeps its empty-set meaning for the slug-less auto-relock and the CLI restamp. audit.py stays under 19,000 bytes. A two-page toy shows: nothing stale makes no commit and appends no rows in two runs; one real change restamps exactly that page once and a second run makes no commit; the negative control (the fix undone in a copy of skills/workflow-docs) must fail. One regression row restamp-own-idempotent-5797 under DOC-2, not folded into another row.
- Also accepted, from frozen done lines 3 and 4: no existing row or check is loosened and nothing is trimmed; no file newly crosses 19,000 bytes (audit.py 18,991 and the new toy 4,898 measured; growth of Tests.md, Documentation.md and regression.tsv, which were already over, is accepted); the docs, package and private-name checks pass; the goal stops at a pull request. A crash of `docs.py check --own HEAD` inside restamp-own restamps nothing and is surfaced by the goal's own docs check, an accepted risk with 9 bytes of headroom.
- Also accepted (CEO outside voices): the toy adds one assertion that `audit.relock(repo, slug, ())` with an empty set still restamps every Reviewed page, so the overload the fix leans on is pinned by a test.
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:eng -->
- The toy (T1): every restamp-own subprocess must exit 0 (stderr shown on failure); after each call it snapshots HEAD, the kept file's text and `git status --porcelain`; with nothing stale all snapshots are identical across both runs and the kept file is absent; after one real change run 1 prints exactly `RESTAMPED A` and adds one commit and run 2 changes none of the snapshots; the fixture's two pages are named A and AB (files a.py and ab.py) so a prefix-matching parse would restamp AB; git runs with commit.gpgsign=false and no hooks; the relock empty-set assertion runs in a subprocess with cwd the fixture repo; no sleeps. After the last merge from main, `wc -c` on audit.py is re-measured and a result of 19,000 or more stops the goal. The silent crash of `docs.py check` stays an accepted, owned risk with no toy case.
<!-- /autoplan-accepted:eng -->
## Review record

<!-- autoplan-baseline-edits:ceo {"sourceSha256":"2df72b6e901786ac6a5ee86115f5ffba9b29f3207e2bf4a92a64de22ffa92493","replacements":[{"oldText":"1. `skills/workflow-docs/scripts/audit.py`: `restamp_own` returns `[]` before `relock` when the stale set is empty. `relock`'s empty-set meaning stays (auto-relock calls it with no slug). The file stays under 19,000 bytes (18,991 after the change).","newText":"1. `skills/workflow-docs/scripts/audit.py`: `restamp_own` takes its stale set from `docs.py check --own HEAD` (the STALE lines, the same predicate the docs check uses; audit.py:267-269) and returns `[]` before `relock` when that set is empty; the final lines are `only = {...}` and `return relock(root, slug, only) if only else []`. Callers of restamp-own: `audit.py restamp-own` (audit.py:384) prints one RESTAMPED line per returned page, so `[]` prints nothing; `lanekit.prep` (lanekit.py:340) runs it and then commits only dirty page files (\"Lane: re-render the Tests tables\"), so with nothing written there is no commit; `keep()` commits only its own `.loop/kept/<slug>.tsv`, and with `[]` it is never reached. `relock(root, slug, only)` is called with a slug and a page list by the CLI `audit.py restamp SLUG PAGE...` (audit.py:386) and the toys; it keeps its empty-set meaning, and `docs.py audit --relock` (docs.py:304) calls it with no slug. The file stays under 19,000 bytes: measured 18,991 with `wc -c` on the committed change (dc3872db0) (9 bytes of headroom, so any later edit to audit.py re-measures; a breach is a stop, not a trim elsewhere)."},{"oldText":"Negative control: the same check against a copy of `skills/workflow-docs` with the fix undone must fail.","newText":"The toy runs `audit.py restamp-own my-goal` as a subprocess in a temp repo (not through lanekit.prep), counts commits with `git rev-list --count HEAD` after each run, and a stale page is restamped by a kept row that `keep()` commits, so nothing is left uncommitted between runs (`check --own HEAD` is clean after run 1). Assertions: with nothing stale both runs print no RESTAMPED, the commit count is unchanged and no kept file exists; after one real change run 1 prints exactly `RESTAMPED A`, adds one commit and the kept rows are exactly [A]; run 2 prints nothing and the commit count and kept rows are unchanged. Negative control: the same check against a copy of `skills/workflow-docs` (scripts and references, so the rules block loads) whose audit.py has the text `if only else []` removed by string replace must fail, and the toy first asserts that the replace changed the file, so a drifted fix fails the control for a clear reason."},{"oldText":"3. One regression row `restamp-own-idempotent-5797` under DOC-2 (the requirement that a re-stamp is a line in `.loop/kept/<slug>.tsv`), then `criteria.py render` for the Tests tables. The row is the net-zero exception logged by top (TD970); it is not folded into the 3122 row, which runs a different script (TD815).","newText":"3. One regression row `restamp-own-idempotent-5797` under DOC-2 (the requirement that a re-stamp is a line in `.loop/kept/<slug>.tsv`), its own row, then `criteria.py render`. Rule: top's TD970 lets a new script carry its own row (net-zero exception), and TD815 allows folding only into a row for the same feature and the same script; `stale-comments-only-3122` runs test-merge-unblock.py, so it is not folded. docs/wiki changes only by that render (the Tests tables in Tests.md and Documentation.md)."},{"oldText":"4. Checks: `docs.py check --own`, `criteria.py render --check`, `dev/package.py --static` (100 files), the private-name scan; no file newly crosses 19,000 bytes.","newText":"4. Checks: `docs.py check --own`, `criteria.py render --check`, `dev/package.py --static` (observed PASS: 100 files before and after; dev/toy is not in the shipped listing), the private-name scan; sizes measured with `wc -c`: audit.py 18,991, the new toy 4,898, none newly over 19,000 (Tests.md and Documentation.md were already over). The goal stops at a pull request by the delivery flow, not by this change; Verify by hand stays empty because a patch has no release step of its own."},{"oldText":"| 3 | row text not Given/When/Then | docs check refuses it | REWRITE line |","newText":"| 3 | row text not Given/When/Then | docs check refuses it | REWRITE line |\n| 1 | an unknown slug or an unwritable `.loop/kept/<slug>.tsv` | with nothing stale nothing is written; with a stale page `keep` raises as before, out of scope | the traceback, as today |\n| 1 | `docs.py check --own HEAD` crashes (`seen` is its stdout string, audit.py:267) | stdout is empty, so nothing is restamped or committed; raising on a non-zero exit is skipped (9 bytes of headroom in audit.py; the goal's own docs check reports the crash) | no RESTAMPED line, the docs check output |"}]} -->

### CEO Step 0 (autoplan, SELECTIVE EXPANSION by the autoplan override)

Mode: SELECTIVE EXPANSION (autoplan override; 0E rule would say HOLD SCOPE for a fix). Review depth: implementation-ready.

| ID and owner | Contract and evidence | Current | Proposed | Status | Exact approval and scope |
|---|---|---|---|---|---|
| S1 CEO | restamp_own must restamp nothing when nothing is stale (done lines 1, 2) | relock(root, slug, set()) restamps every page (audit.py:226, 266) | restamp_own returns [] on an empty stale set | approved | autoplan auto-decision P5, the goal's frozen done lines 1 and 2 |
| S2 CEO | relock has one slug caller with a possibly empty set: restamp_own (audit.py:270); docs.py:304 calls it with no slug; the CLI `restamp SLUG` (audit.py:386) passes its own page list | empty set = every page | make relock treat slug + empty set as nothing | declined | autoplan P3 and P5: the CLI `restamp SLUG` with no pages may rely on it, and the goal scope is restamp-own; Skip |
| S3 CEO | goal.py pr runs restamp-own before lane reuse (issue 5797) | each run moves HEAD | a second guard in goal.py pr | declined | out of the goal's Touches (skills/workflow-docs only) and unneeded once S1 holds; Skip |
| S4 CEO | new toy, one regression row under DOC-2 (net-zero exception, TD970; folding into 3122 refused, TD815) | row present | keep | approved | done line 3 and top's TD970 |

Premise table (REALITY):
- premise 1: "restamp-own restamps every Reviewed page when nothing is stale" | skills/workflow-docs/scripts/audit.py:226-270, reproduced in a scratch clone (run 2 printed 13 RESTAMPED) | verified
- premise 2: "an empty `only` means every page in relock" | audit.py:229 (`if only and ...`) | verified
- premise 3: "docs.py check --own HEAD prints no STALE once restamped" | reproduced: DOCS OK after run 1 | verified
- premise 4: "relock without a slug (docs.py:304) needs the empty = all meaning" | docs.py:304 | verified
- premise 5: "audit.py was 18,959 bytes before and is 18,991 after" | wc -c | verified, unverified=0

REALITY: premise-table pass five premises, all with file:line receipts, unverified=0 skills/workflow-docs/scripts/audit.py:226
REALITY: already-done pass origin/main has no commit touching audit.py restamp_own since 2026-11-22 other than unrelated rows-600-d re-renders; the issue is open skills/workflow-docs/scripts/audit.py:266
REALITY: surface-check pass `audit.py restamp-own SLUG` and `docs.py check --own HEAD` exist, no flag added skills/workflow-docs/scripts/audit.py:384
REALITY: binding-decisions pass the decision-search tool prints no binding decision for this branch; top's TD815/TD970 rulings are applied (own row, no fold, depth full) .loop/regression.tsv:699
REALITY: numbers pass 13 pages restamped on run 2 [measured: scratch clone run, loop over every page at skills/workflow-docs/scripts/audit.py:229]; audit.py is 18,991 bytes [measured: wc -c at skills/workflow-docs/scripts/audit.py:266]
REALITY: deferred-asks pass the issue asks only for no commit and no rows when nothing is stale, plus a two-run test with a negative control; nothing is left out .loop/goals/restamp-own-idempotent.md:1
REALITY: pr-count pass one PR for one patch goal .loop/goals/restamp-own-idempotent.md:1

Dream state: CURRENT every lane prep and goal.py pr moves HEAD, voiding lane .ok files, and a goal's pr starts a second lane -> THIS PLAN restamp-own is idempotent, pr reuses the lane -> 12-MONTH IDEAL restamps are computed, never committed, by a read-only freshness check.

Temporal (0I): HOUR 1 read relock and restamp_own (done); HOUR 2-3 the one-line guard (done); HOUR 4-5 the toy needs the repo's own prd helpers and a copied scripts tree with references/ for the negative control (done, learned); HOUR 6+ the row must be Given/When/Then and the Tests tables rendered (done).

<!-- autoplan-accepted:ceo -->
- (accepted obligations, canonical list) restamp_own returns [] when the stale set is empty, before relock is called; relock keeps its empty-set meaning for the slug-less auto-relock and the CLI restamp. audit.py stays under 19,000 bytes. A two-page toy shows: nothing stale makes no commit and appends no rows in two runs; one real change restamps exactly that page once and a second run makes no commit; the negative control (the fix undone in a copy of skills/workflow-docs) must fail. One regression row restamp-own-idempotent-5797 under DOC-2, not folded into another row.
- Also accepted, from frozen done lines 3 and 4: no existing row or check is loosened and nothing is trimmed; no file newly crosses 19,000 bytes (audit.py 18,991 and the new toy 4,898 measured; growth of Tests.md, Documentation.md and regression.tsv, which were already over, is accepted); the docs, package and private-name checks pass; the goal stops at a pull request. A crash of `docs.py check --own HEAD` inside restamp-own restamps nothing and is surfaced by the goal's own docs check, an accepted risk with 9 bytes of headroom.
- Also accepted (CEO outside voices): the toy adds one assertion that `audit.relock(repo, slug, ())` with an empty set still restamps every Reviewed page, so the overload the fix leans on is pinned by a test.
<!-- /autoplan-accepted:ceo -->

Spec review (3 launches, scores 7, 7, 8; cap reached). Gaps from launch 3 and their applied fixes: (1) obligations list incomplete: added the done-line 3 and 4 bullet to the accepted block; (2) crash of docs.py check swallowed: recorded as an accepted risk with its owner (the goal's docs check) in the same bullet; (3) regression.tsv size unmeasured (354,481 bytes, already over): added to that bullet, growth of already-over files accepted; (4) the 10x check wording: reworded in the CEO scope summary; (5) tense of item 1: the plan items are verification targets against the committed change dc3872db0, whose final lines are an `only = {...}` set built from the STALE lines of `seen` and `return relock(root, slug, only) if only else []`; with the fix undone and nothing stale, scenario 1 fails on "both runs print no RESTAMPED" and "no new commit", and scenario 2 fails on "run 2 prints nothing". issues verified: 5 of 5 (applied edits, not a verdict).

Approval readiness: PASS (S1 and S4 by the frozen done lines and top's TD970; S2 and S3 declined by autoplan P3/P5).


### CEO dual voices (native subagent, Codex gpt-6-astra, completed)

Native findings: (N1 Critical) the plan fixes the symptom, not the empty-means-all contract of relock; (N2 High) a crash of `docs.py check --own HEAD` is silent; (N3 High) 9 bytes of headroom blocks every later audit.py change; (N4 Medium) no assertion that relock's empty-set meaning survives; (N5 Medium) the negative control keys on a literal; (N6 Medium) row/size debt on Tests.md and Documentation.md.
Codex findings: (C1 High) "fresh" is not "still correct", a stamp is not evidence; (C2 High) the byte cap decides the reliability contract (silent crash); (C3 Medium) the toy does not exercise lanekit.prep on a loop/ branch.

Dispositions (auto-decided, P1-P6):
- N4: ACCEPTED (P2, the toy gets one assertion, no audit.py bytes). Added to the accepted block.
- N1 (sentinel in relock), N3 (split audit.py) : NOT in scope. Changing relock's contract touches the CLI restamp and docs.py audit --relock, and the frozen done line 3 forbids trimming or loosening; there is no byte room to move code. TASTE DECISION, surfaced at the gate; a follow-up goal, not written to TODOS.md because the repo keeps none.
- N2 = C2 (both voices): raising or printing on a non-zero exit of docs.py check would add roughly 50 bytes to audit.py and cross 19,000, which done line 3 forbids; done line 3 is frozen. Kept as an accepted risk with its owner (the goal's own docs check). TASTE DECISION, surfaced at the gate. Both voices recommending a change to a frozen done-line trade-off is flagged, not auto-approved.
- N5: ACCEPTED as is (the toy asserts the replace changed the file, so brittleness fails loudly).
- N6: ACCEPTED, growth of already-over files recorded in the accepted block; a follow-up to bring both pages under the cap is out of scope.
- C1: NOT in scope (documentation correctness is a different feature, DOC-2 only requires that a re-stamp is recorded).
- C3: NOT in scope for this goal's toy (done line 3 asks for the two-run check with a negative control); the goal's own pr step runs the fixed restamp-own inside lanekit.prep and is the lane-level proof.

CEO DUAL VOICES - CONSENSUS TABLE:
  Dimension                             Claude  Codex  Consensus
  1. Premises valid?                    yes*    yes*   CONFIRMED (*the silent-crash premise is shaky in both)
  2. Right problem to solve?            yes     yes    CONFIRMED (as a patch)
  3. Scope calibration correct?         yes     yes    CONFIRMED
  4. Alternatives sufficiently explored? no     no     CONFIRMED gap: relock sentinel and split of audit.py deferred without a byte budget
  5. Competitive/market risks covered?  n/a     n/a    CONFIRMED n/a (internal tooling)
  6. 6-month trajectory sound?          no      no     CONFIRMED concern: 9-byte cap and silent crash

### Review sections 1-11 (SELECTIVE EXPANSION, implementation-ready)

S1 Architecture: one function, one caller chain. Diagram:
```
 lanekit.prep --subprocess--> audit.py restamp-own SLUG
                                   | docs.py check --own HEAD  (stdout "STALE <page>: ...")
                                   v
                       only = {pages named STALE}
                         |  empty            |  non-empty
                         v                   v
                       return []          relock(root, SLUG, only) -> keep() -> commit .loop/kept/SLUG.tsv
```
Dependency before/after: unchanged except the new early return. Coupling: none new. Rollback: revert one line (seconds). SPOF: docs.py check output parsing, unchanged. No artifact about the work is added beyond one toy and one row, both asked by the done lines.
S2 Error and Rescue registry:
| capability | what can go wrong | class | rescued | rescue action | user sees |
|---|---|---|---|---|---|
| docs.py check subprocess | crash or timeout | none caught (returncode ignored, as before) | N, accepted | restamps nothing | no RESTAMPED line; the goal's docs check reports it |
| keep() | unwritable kept file, unknown slug | OSError / git error | N, unchanged | raises as before | traceback |
| relock | empty set with a slug | none | by design (all pages) | unchanged | all pages, only via the CLI restamp or direct call |
CRITICAL GAPS: 0 (the crash row is an accepted, owned risk).
S3 Security: no new input, path or secret; slug is passed as argv to git-managed paths as before; kept rows are written under .loop/kept/. Private-name scan covers the diff. 0 issues.
S4 Data flow and edge cases: INPUT slug+repo -> check output -> stale set -> relock -> kept row -> commit. Shadow paths: nil/empty stale set (fixed, returns []); malformed STALE line (split()[1:] guard exists); stale page text changed (relock refuses, LOCKED, unchanged); slug "--help" (known pitfall, out of scope); concurrent runs (two restamps race on one kept file: out of scope, one writer per goal). Async ordering: none. 0 unhandled new.
S5 Code quality: one set variable, one conditional expression, no duplication. The toy duplicates the fixture builder of test-merge-unblock.py (page(), build()); DRY would extract it, but the shared helper would change a second toy and cross this goal's scope. 1 note.
S6 Test review: diagram - restamp_own empty set (toy run 1 and run 2, nothing stale), restamp_own one stale page (toy), negative control (toy), relock empty set overload (toy, added), lanekit.prep integration (not covered here, proven by the goal's own pr step). Hostile-QA test: second run after a restamp; chaos: none. 1 gap (lane-level), declined above.
S7 Performance: removes one full relock pass per run when nothing is stale (saves reading every page and committing). 0 issues.
S8 Observability: the RESTAMPED lines and the kept rows are the log; an idempotent run prints nothing. A silent crash is the one gap (accepted).
S9 Deployment: no migration, no flag; rollback = revert the one line; the fix takes effect for the next restamp-own run, including this goal's own pr.
S10 Long-term: debt: 9-byte headroom on audit.py (carry the trigger: split the file when it next needs bytes), the overloaded empty set. Reversibility 5/5. A new engineer reads two lines.
S11 Design: SKIPPED (no UI scope).

NOT in scope (deferred or rejected): relock sentinel (declined, TASTE), splitting audit.py (declined, TASTE), raising on a non-zero docs check (declined, frozen size line), lane-level regression (declined), stamp validity evidence (declined), bringing Tests.md/Documentation.md under 19,000 (declined).
What already exists: relock and keep() (reused as is); the toy fixture pattern in test-merge-unblock.py (reused in shape); the 3122 row (left untouched).
Dream state delta: moves from a restamp that commits on every run toward a read-only freshness check; the 12-month ideal removes commits for restamps entirely.
Failure Modes Registry:
| codepath | failure mode | rescued | test | user sees | logged |
|---|---|---|---|---|---|
| restamp_own empty set | restamps every page | Y (fixed) | Y (toy) | nothing | n/a |
| restamp_own one stale page | second run restamps again | Y | Y (toy) | RESTAMPED A once | kept row |
| docs.py check crash | silent no-op | N (accepted) | N | no line | N |
| relock empty set overload | lost by a later refactor | Y | Y (toy, added) | n/a | n/a |
Critical gaps: 1 (the accepted silent crash, owner: the goal's docs check).
Stale diagram audit: no ASCII diagrams in touched files.
Implementation tasks: T1 (P1, human ~15min / CC ~5min) audit.py - already done in dc3872db0; T2 (P1) toy: add the relock empty-set assertion; T3 (P2) record the plan, review, qa, ship steps.
Scope proposals: 2 proposed, 0 accepted, 2 declined. TODOS.md updates: 0 (no TODOS.md in the repo).
Lake Score: N/A (no scored 0D question was asked).

### Phase 2 and 2.5 (autoplan)

Phase 2 (design) SKIPPED: no UI scope (scope helper: uiRequired=false, only the word "row" matched). Phase 2.5 (DX) SKIPPED: no developer-facing scope (dxRequired=false). A skip is not a completed review.


### Eng phase (autoplan)

Scope Challenge: scope accepted as-is. Complexity: 3 changed files (audit.py, new toy, regression.tsv; plus two rendered pages) and 0 new classes or services, under the 8-file / 2-class gate, so no structure question. Search check: no new architectural pattern or infrastructure (a guard clause and a toy): skipped, in-distribution knowledge only. Distribution check: no new shipped artifact; dev/toy is outside the package listing (package static PASS, 100 files).

REALITY: premise-table pass four premises (empty only = every page at skills/workflow-docs/scripts/audit.py:229; one slug caller restamp_own at skills/workflow-docs/scripts/audit.py:270; lanekit.prep commits only dirty pages at skills/workflow-delivery/scripts/lanekit.py:340; keep() commits only its kept file at skills/workflow-docs/scripts/audit.py:215) unverified=0 skills/workflow-docs/scripts/audit.py:229
REALITY: already-done pass no commit on origin/main touches restamp_own; the fix is only on this branch dc3872db0 skills/workflow-docs/scripts/audit.py:266
REALITY: surface-check pass `audit.py restamp-own SLUG` and `docs.py check --own HEAD` exist; no new flag skills/workflow-docs/scripts/audit.py:384
REALITY: binding-decisions pass the decision-search tool prints no binding decision; TD815 and TD970 applied .loop/regression.tsv:699
REALITY: numbers pass audit.py 18,991 bytes [measured: wc -c at skills/workflow-docs/scripts/audit.py:266]; the new toy 4,898 bytes [measured: wc -c at dev/toy/test-restamp-idempotent.py:1]
REALITY: deferred-asks pass the issue asks for no commit and no rows when nothing is stale plus a two-run test with a negative control; nothing left out .loop/goals/restamp-own-idempotent.md:1
REALITY: pr-count pass one PR for one patch goal .loop/goals/restamp-own-idempotent.md:1

ENG DUAL VOICES (native subagent and Codex gpt-6-astra, both completed)
Native: (1 Medium) crash of docs.py check is silent; (2 Medium) STALE-line parsing, add a fixture whose page names share a prefix; (3 Low-Med) empty-set overload stays; (4 Medium, process) 9-byte headroom, re-measure after the last merge from main; (5 Low) toy isolation: git env, clean tree after each run, no sleeps; (6 Low) TOCTOU on the kept file, pre-existing; (7 Low) no security surface; (8 Low) row text and the TD970 note in the PR.
Codex: (1 Medium) the toy discards exit status and stderr and samples only after both runs, so a crashing second run passes; snapshot HEAD, kept file and tree after each invocation; (2 Medium) the added relock assertion must run in a subprocess with cwd the fixture, because keep() runs git in the current directory.

Dispositions (auto-decided):
- Native 2: ACCEPTED (P1, in the toy only): the second page is named `AB` (files a.py and ab.py) so exact-match parsing is exercised.
- Native 5 and Codex 1: ACCEPTED (P1): the toy requires exit status 0 for every restamp-own call, prints stderr on failure, and after each call snapshots HEAD, the kept file's text and `git status --porcelain`; git runs with `commit.gpgsign=false` and no hooks path; no sleeps.
- Codex 2: ACCEPTED (P1): the relock-empty-set assertion runs as `python3 -c` in a subprocess with cwd the fixture repo.
- Native 1 (= CEO N2/C2): the accepted risk stays; ADDITIONALLY a toy case where `docs.py check` is made to fail is NOT added (a reliable crash trigger in the fixture would depend on docs.py internals and is brittle); TASTE DECISION surfaced at the gate.
- Native 3: out of scope (as CEO N1). Native 4: ACCEPTED as a process step: re-measure `wc -c` on audit.py after the last merge from main and before the pull request, and say so in the PR notes. Native 6, 7: no action. Native 8: PR notes carry the net-zero exception.

ENG DUAL VOICES - CONSENSUS TABLE:
  Dimension                           Claude  Codex  Consensus
  1. Architecture sound?               yes     yes    CONFIRMED
  2. Test coverage sufficient?         gaps    gaps   CONFIRMED (both ask for per-run snapshots; accepted)
  3. Perf risks + budget/bench named?  n/a     n/a    CONFIRMED n/a (removes work; no hot path)
  4. Security threats covered?         yes     yes    CONFIRMED
  5. Error paths handled?              gap     gap    CONFIRMED (silent docs-check crash, accepted risk)
  6. Deployment risk manageable?       yes     yes    CONFIRMED

Section 1 Architecture: dependency graph (new component: none).
```
 lanekit.prep --subprocess--> audit.py restamp-own SLUG --subprocess--> docs.py check --own HEAD
                                    |                                         | stdout STALE lines
                                    +--- only = {pages} <---------------------+
                                    |  empty -> return []   (no relock, no keep, no commit)
                                    |  else  -> relock(root, SLUG, only) -> keep() -> commit kept file
```
Design-twice: not applicable (no new module or boundary). Red flags: pass-through 0, split ownership 0, hand-synced list 0, two ways to one task 0: the CLI `restamp SLUG PAGE...` is a different task (explicit pages). Coupling unchanged; scaling: removes one full relock pass per run; SPOF: the STALE-line parse, now pinned by the one-real-change toy case; security: no new auth boundary; production failure: the silent docs-check crash (accepted risk, owner: the goal's docs check); rollback: revert one line. 0 new issues.
Section 2 Code quality: guard is one conditional expression; no duplication; the toy repeats test-merge-unblock.py's fixture helpers (page, build, write, git): 2 call sites is below the three-caller bar for a shared helper and extraction would change a second toy. 1 informational note, no action. Touched ASCII diagrams: none.
Section 3 Test review (coverage diagram):
```
CODE PATHS                                                   USER FLOWS
[+] audit.py restamp_own                                     [+] lane prep restamp
  |-- only empty -> []            [★★★ TESTED] toy s1          |-- nothing stale, run twice [★★★ TESTED] toy s1
  |-- only non-empty -> relock    [★★★ TESTED] toy s2          |-- one stale page, run twice [★★★ TESTED] toy s2
  |-- check crash (stdout empty)  [GAP, accepted risk]         |-- crash of docs check      [GAP, accepted]
[+] audit.py relock                                           [+] goal.py pr -> lanekit.prep
  |-- empty set, slug -> all pages [★★ TESTED] toy s3 (added)    '-- fixed restamp-own inside pr [proven by this goal's own pr step]
[+] negative control (fix undone) [★★★ TESTED] toy s4
COVERAGE: 5/7 paths tested | GAPS: 2 (one accepted, one proven by the pr step) | QUALITY: ★★★:3 ★★:1
```
Tests to add (value cards):
- test-restamp-idempotent.py s3: Value: protects=relock with an empty set and a slug still restamps every Reviewed page; fails_when=a refactor makes empty mean none; why_new=no toy pins the overload; seam=none; no_claim=CLI restamp path (library call only)
- test-restamp-idempotent.py hardening: Value: protects=a second run that crashes or leaves a dirty tree is detected; fails_when=exit status nonzero, HEAD, kept file or porcelain status changes between runs; why_new=the first toy sampled only after both runs; seam=none; no_claim=none beyond protects
- fixture page names A and AB: Value: protects=exact-match STALE parsing; fails_when=prefix matching restamps AB when only A is stale; why_new=single-letter names cannot show a prefix bug; seam=none; no_claim=none beyond protects
Tests made obsolete: none. Eval scope: no LLM or prompt change.
Section 4 Performance: removes the full-page relock pass and a commit when nothing is stale; no hot path; no scale concern (13 pages). 0 issues.
NOT in scope: relock sentinel, splitting audit.py, raising on a docs-check crash, lane-level regression, bringing already-over pages under 19,000, stamp validity.
What already exists: relock/keep (reused), the merge-unblock fixture pattern (copied in shape), TD970 row rule.
Failure modes: (restamp_own empty set: rescued Y, test Y, user sees nothing); (second run restamps again: Y, Y, RESTAMPED once); (docs.py check crash: N, N, no line - accepted, owner the goal's docs check); (toy second run crashes silently: now rescued by the exit-status assertion). Critical gaps: 1 (the accepted silent crash).
TODOS.md updates: 0 (no TODOS.md in this repo). Parallelization: sequential implementation, no parallelization opportunity.
Implementation Tasks:
- [ ] T1 (P1, human ~1h / CC ~10min) toy - harden test-restamp-idempotent.py: exit-status and per-run snapshots, names A and AB, git env, relock-empty-set assertion in a subprocess with cwd the fixture. Surfaced by: Test review (native 2, 5; Codex 1, 2). Files: dev/toy/test-restamp-idempotent.py. Verify: python3 dev/toy/test-restamp-idempotent.py exits 0 and still fails the control.
- [ ] T2 (P1, human ~15min / CC ~3min) audit.py - re-measure wc -c after the last merge from main (stop on >= 19,000). Surfaced by: native 4. Files: skills/workflow-docs/scripts/audit.py. Verify: wc -c prints under 19000.
- [ ] T3 (P2, human ~15min / CC ~3min) PR notes - state the TD970 net-zero exception and the accepted silent-crash risk. Verify: PR comment lists both.
Completion summary (eng): Step 0 scope accepted as-is; reality rows 7/7, 0 unverified; Architecture 0 issues; Code Quality 1 informational; Test Review diagram produced, 2 gaps; Performance 0; NOT in scope written; What already exists written; TODOS.md 0; Failure modes 1 critical gap (accepted); Unresolved decisions 2 (taste, at the gate); Outside voice Codex completed; Parallelization 0 lanes; Lake Score N/A.

<!-- autoplan-accepted:eng -->
- The toy (T1): every restamp-own subprocess must exit 0 (stderr shown on failure); after each call it snapshots HEAD, the kept file's text and `git status --porcelain`; with nothing stale all snapshots are identical across both runs and the kept file is absent; after one real change run 1 prints exactly `RESTAMPED A` and adds one commit and run 2 changes none of the snapshots; the fixture's two pages are named A and AB (files a.py and ab.py) so a prefix-matching parse would restamp AB; git runs with commit.gpgsign=false and no hooks; the relock empty-set assertion runs in a subprocess with cwd the fixture repo; no sleeps. After the last merge from main, `wc -c` on audit.py is re-measured and a result of 19,000 or more stops the goal. The silent crash of `docs.py check` stays an accepted, owned risk with no toy case.
<!-- /autoplan-accepted:eng -->
