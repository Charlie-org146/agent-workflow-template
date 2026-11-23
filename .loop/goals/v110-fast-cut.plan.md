# Plan (revision 4): a test cut for time, or not run, fails the PR's checks, naming the test and its time (DEL-26.4, #5757)

Revision 4 (after the full autoplan gate, answered by operation-mac's delegated review): this plan now states the design that ships. The earlier revisions described an inline script in the generated step with a few spare bytes; the gate is now one script, `cutgate.py`, called by the `affected` step, with its status rules in `completion.py`. The three reviews of revision 1, the red-team passes and the autoplan gate of revision 3 are kept below as the record.

Dependency: DEL-26.4's page text (its test case and wording) comes from v110-fast-text, so this goal merges after v110-fast-text; this plan writes no page text.

Source: revision 6 of the retired fix-5757 (branch `loop/fix-5757`, b7ba2d9b7) for the numbered-shard glob and the stale-file toy case; its rerun is dropped (no rerun: operation-mac's order TD786/TD787).

## Implementation plan

Goal: a selected row counts as run only when it finished on a shard. A row cut for time, left over its row limit, or run by no shard fails the `affected` job and is named with its status and seconds; a row that could not run is named as skipped and is never counted as run. Green means every selected row finished (RAN) on some shard.

Design (read in this worktree; bytes by `wc -c`): `regression-pr.yml` is written by `regression.py workflow` from the `NARROW` template in `lanes_cli.py`. Each shard writes `t.tsv` rows `id<TAB>seconds<TAB>status`: RAN (finished on this shard), SEL (another shard's row), CUT (the shard's budget ran out), LEFT (passed the row limit), SKIP (could not run here).

Changes:
1. `skills/workflow-regression/scripts/cutgate.py` (one new script, allowed by o745): called by the `affected` step as `cutgate.py 's/shard-[0-7]/t.tsv'`. It reads only the numbered shard files. A row that is SEL or RAN somewhere and RAN nowhere is unfinished: it prints `FAIL cut or not run: <id> <STATUS> <seconds>s: raise the shard budget (owner) or move the row` and exits 1; a missing shard file leaves its rows named as not run; no file at all is exit 1. A SKIP row is never counted as run: it passes only when its id is on the committed list `.loop/regression-skips.tsv` (the rows that skip by design on main), printed `SKIPPED <id>: <reason>`; any other SKIP row prints `FAIL skipped and not skipped on main: <id>` and the gate exits 1. It prints `run twice: <ids>` for a row two shards ran, reruns nothing, writes the times cache `all.tsv` only when there is a record to write, and answers `--help` with its description (the package check runs every script alone).
2. `skills/workflow-regression/scripts/completion.py` (one new script): `state()` gives the status a shard writes for a selected row: LEFT stays, CUT when the budget ran out, SEL for another shard's rows, SKIP for a row whose result says it could not run, else RAN. `regression.py` calls it; a known row that passes its row limit is LEFT like any other row. `.loop/regression-skips.tsv` lists the 13 rows main's run 45110588623 (at c2ce6460a) reports SKIPPED, each with its own reason; an id on it needs a `skip:<id>` line in `approved-row-changes.tsv` (TD1215), checked by `dev/toy/test-skip-list.py`, row `skip-list-approved`.
3. `lanes_cli.py` (the generator): the shard step reads the diff against the base once, stops with `FAIL cannot read the diff against origin/<base>` when it cannot, and takes the documents-only exit only from a diff it read; the `affected` step calls `cutgate.py`; the times cache is restored from and saved to the same path `all.tsv`, the committed times `.github/workflows/row-times.tsv` seed a first run, and the cache save runs even when `affected` is red. The workflow is regenerated with `regression.py workflow`, never hand-edited.
4. Rebalance (o852, TD1183, TD1202): PR shards split rows by measured time. The budget stays 120 s in this plan's commits and moves to 866 s in its own commit after a real PR run shows every shard under 866 s; it is never raised or removed to make a shard fit.
5. Tests (REG-4, one row per script): `dev/toy/test-cut-fails.py` (row `cut-fails-checks`: the gate's cases, the generated step, `--help`), `dev/toy/test-cut-complete.py` (row `cut-complete`: a known row past its row limit, a row that cannot run (passes only when on the skip list, fails otherwise), a diff that cannot be read, no empty times record; each case on the real runner, the real gate or the generated step, with controls that stay green), `dev/toy/test-skip-list.py` (row `skip-list-approved`), `dev/toy/test-shard-budget.py` (row `shard-fits-budget`), and `test-shard-balance.py` with its message and affected-fixture assertions updated to the new behaviour, none loosened. A toy showing the generated step fails a shard over its budget joins the budget commit (TD1202). Each new case is seen red on the parent.
6. Approved row changes, each cited in `dev/toy/approved-row-changes.tsv`: `known-no-block` split into five one-run rows (TD842), `tasks-rows-only-added` (TD1176, TD1184), `guards-null-report-nofiles` (o863, TD1194), each with a negative control that runs in the row.
7. Bytes [measured: wc -c]: `lanes_cli.py` 20,272, `regression.py` 20,451, `cutgate.py` 2,278, `completion.py` 568; every script stays under 20,480 and none newly crosses 19,000; MAX_FILES stays within 200.
8. Docs: `docs.py audit` and `docs.py check`; the DEL-26.4 page text is v110-fast-text's, not edited here.

Test plan: `test-cut-fails.py`, `test-cut-complete.py`, `test-shard-balance.py`, `test-shard-budget.py`, `dev/package.py` (not only `--static`), the size check, rows none red, the PR's own CI run (a first run unbudgeted because the diff changes the row table, so it shows each shard's measured time against 866 s).

Owner-level, reported and not decided here: the shard budget value (o852's 866 s, set only after the measured fit).

Failure modes: a PR whose rows exceed the shard budget fails and names them; a crashed shard (`needs.shard.result`) is red; a missing or empty artifact set is red; a diff that cannot be read is red.

Not in scope: reruns (ordered out), and the other DEL-26 and DEL-27 requirements (their own goals).

## Review record

Reviews run for this revision: `/plan-ceo-review` (HOLD SCOPE), `/plan-eng-review` and `/plan-devex-review`, each loaded and run against this plan and the code in this worktree. The Skill tool did not list `plan-eng-review`, so its installed SKILL.md and sections were read directly from disk and followed (scope challenge, sections 1 to 4, outputs). Not run: the outside voice (no second model was invoked; the fresh red-team gate that follows is the independent read) and the design review (no UI). This replaces the record of 64dfaf64b (retired v110-fast-ci), whose "DEPTH: full" overstated its depth: that plan's reviews were short notes written by hand and the three skills were not loaded.

Revision 2 note: these reviews were run on revision 1. Revision 2 changes the lines listed at the top and was not reviewed again by the three skills; the fresh red-team gate on revision 2 is the only new read.

Reality rows (CEO and eng):
- REALITY: premise-table pass six claims checked: the affected block counts LEFT/CUT as accounted for (lanes_cli.py:234-238), LEFT is written for a row past the limit with n>1 (regression.py:320-323), merged() writes CUT/LEFT/RAN/SEL (regression.py:248-331), tree shard and docs-only exit upload a restored file (lanes_cli.py:205-216), the ruleset requires `affected` and `small` (gh api rulesets), lanes_cli.py is 20,477 bytes (wc -c). unverified=0
- REALITY: already-done pass `git log origin/main` shows no change to lanes_cli.py or regression-pr.yml since the parent; no commit names #5757. lanes_cli.py:1
- REALITY: surface-check pass `regression.py workflow` and `regression.py red` exist (regression.py:375, 211, 395); no new command or flag is added. regression.py:395
- REALITY: binding-decisions pass operation-mac's TD786/TD787: no rerun, glob `s/shard-[0-7]/t.tsv`, three review skills loaded; the plan keeps all three. v110-fast-cut.plan.md:3
- REALITY: numbers pass bytes [measured: wc -c] 20,477 and 20,479; the block replacement [measured: scratch copy] 20,372 before the later edits, re-measure at build; suite and run times [measured: gh run list] 18 to 28 min for PR runs.
- REALITY: deferred-asks pass no linked issue beyond #5757 whose asks (affected counts cut rows as done) are all in scope; #5759 is its own issue. v110-fast-cut.plan.md
- REALITY: pr-count pass one PR; the other DEL-26 and DEL-27 lines are v110-fast-ci-2. v110-fast-cut.md:1
PLAN_REALITY rows=7 verdict=complete (hand tally; the helper's check line is run at the gate)

### CEO review (HOLD SCOPE; sections 1 to 10, section 11 skipped: no UI scope)

Mode: HOLD SCOPE (given). No scope addition or cut was proposed: nothing is deferred, nothing added.
- Premise: the false green is real and bounded: `affected` counts a cut or left row as accounted for. Do-nothing cost: every PR can be green with rows never finished. The plan solves the cause, not a proxy.
- Section 1 (architecture), one finding fixed in the body: the default shell for `run:` is `bash -e {0}` with no pipefail, so the plan's claim that an empty glob ends red was wrong; the step now sets `shell: bash` and shards that exit early on a documents-only diff write an empty `t.tsv`, so "no numbered file" always means a missing artifact and is red.
```
shard[0..7] --t.tsv (RAN|SEL|CUT|LEFT)--> affected --reads shard-[0-7] only--> FAIL per unfinished row
shard-tree / docs-only restored file: not read (stale RAN lines)     needs.shard.result stays the last check
```
- Section 2 (error and rescue): see the registry below; no catch-all; every failure ends red and names its cause.
- Section 3 (security): no new input, secret or dependency; the block reads artifact files made by the same run. No findings.
- Section 4 (data flow): nil path (no t.tsv: red), empty path (empty file: no rows, green only when every shard wrote one), error path (shard crash: `needs.shard.result`), stale path (restored file: no SEL, not counted), conflict path (a row RAN on two shards: "run twice" echo). The restored-file RAN lines can enter `ran.txt`, which only subtracts; checked against merged() (regression.py:248): a restored row keeps state "CUT" or "" and a LEFT/RAN restored row is written with an empty state, so stale statuses are CUT or empty.
- Section 5 (quality): the new block is shorter than the one it replaces; no new branch above 5.
- Section 6 (tests): see the test review; each rule has a fixture that breaks only it.
- Section 7 (performance): the step reads at most nine small files; no new job time. The cost is the owner-facing one: a PR whose reached rows exceed the shard budget now fails. Measurement step added before the build (the last 10 runs' existing LEFT lines).
- Section 8 (observability): the FAIL line names the row, status, seconds and the fix; the "run twice" echo stays.
- Section 9 (rollout): one generated file and one script; rollback is a revert of one commit; the first PR after the merge shows the change on its own run. The PR's own run is the live test.
- Section 10 (trajectory): reversibility 5/5; the budget constant (120 s per shard) stays the owner's lever; #5759 remains its own issue.
- Section 11: SKIPPED (no UI scope).

### Eng review (scope challenge, sections 1 to 4)

Scope challenge: 3 files edited under skills/ and dev/ (lanes_cli.py, regression.py, test-shard-balance.py), 1 new toy, 1 row, 1 regenerated workflow: under 8 files, no new class or service, so no complexity question. What already solves it: `regression.py workflow` (generator), `regression.py red` (red proofs), `merged()` statuses; reused, nothing rebuilt. Search check: [Layer 1] Actions' default `bash -e {0}` versus `shell: bash` (`-eo pipefail`) is documented platform behavior; no new pattern or dependency. Distribution: the generated file is the only artifact.
- Architecture: one block, one file, no new coupling. Finding: CUT rows carry the last recorded seconds (0 when none): the line prints status next to seconds so the number is not misread (done).
- Code quality: `T=...` unquoted on purpose (glob), commented in the template line; the unfinished set is one `comm -23` of SEL-or-RAN against RAN.
- Test review (diagram):
```
NEW CODEPATH                         TEST (dev/toy/test-cut-fails.py)                 RED WITHOUT THE FIX BECAUSE
LEFT on one shard, SEL elsewhere     affected exits 1, names id and LEFT 200s         parent block counts LEFT as done
CUT on one shard, SEL elsewhere      same, CUT                                        same
SEL everywhere, RAN nowhere          exits 1, "not run"                               parent reruns it, green if it passes
two bad rows                         both named                                       parent: one rerun result only
all RAN                              exits 0                                          (control)
stale CUT, unselected id             exits 0                                          break: every status as source
restored docs-only file              exits 0 (no SEL)                                 break: same
stale shard-tree/t.tsv with RAN      still exits 1                                    break: glob s/*/t.tsv
empty glob / no artifact             exits 1                                          parent: green (bash -e)
shell: bash present in the step      generated file asserted                          break: pipefail off
end to end (real regression.py, 2 shards, slow row, --timeout 2)   real affected block exits 1 and names it   parent ends green (the pin)
```
  Flakiness: the end-to-end case uses a 2 s limit and a `sleep 5` row; timing margin 2.5x, asserted as a precondition so a slow machine fails the precondition, not the claim.
- Performance: no change to run time.
- Failure modes registry (CODEPATH | FAILURE | RESCUED | TEST | USER SEES | LOGGED): affected | row cut | n/a, fails | yes | FAIL line | yes. affected | row LEFT | fails | yes | FAIL line | yes. affected | no numbered file | fails | yes | step red, awk error | yes. affected | stale tree file | not read | yes | n/a | n/a. shard | crash | needs.shard.result | existing row | red check | yes. regression.py | message text | n/a | toy assert | log line | yes. No critical gap.
- NOT in scope: reruns (ordered out), the budget value (the owner's), the other DEL-26 and DEL-27 requirements (their own goals).
- What already exists: `regression.py workflow`, `red`, `merged()`, the shard-balance toy (kept, stale asserts fixed only), `size-check.py`, `dev/package.py --static`.
- Parallelization: sequential implementation, no parallelization opportunity (one module, one workflow file).
- Implementation tasks: T1 (P1) measure the last 10 runs' LEFT lines; T2 (P1) toy and row red on the parent first; T3 (P1) the affected block with `shell: bash` and the docs-only empty file; T4 (P1) regenerate the workflow, size check; T5 (P2) stale asserts in test-shard-balance.py and its row description; T6 (P2) PR notes and the lanes on the slot word. Each verifies with its toy case, the size check and rows none red.

### DX review (DX POLISH; persona: a goal worker, human or agent, and the owner reading a red PR check)

Product type: CLI/CI tool output. Persona (auto-decided, recommended): the owner or an unattended agent that opens a failed `affected` step and must act without reading the source. Magical moment: the failed step's last lines name the row, its status and seconds, and the fix, with no digging. TTHW (time from red check to knowing the row and the fix): today never red; with this change under 1 minute (the line is in the step output). Competitive benchmark: not measured (no peer comparison applies; the reference is GitHub's own failed-step annotation). Journey: PR red, open `affected`, read the FAIL lines, fix or move the row, push.
- Pass 1 getting started 8/10: no new command. Pass 2 CLI/API design 8/10: one format, stable code `cut-or-not-run`. Pass 3 error messages 8/10: matrix below. Pass 4 documentation 6/10 (the DEL-26.4 page is v110-fast-text's, not edited here; the row description is). Pass 5 upgrade 8/10: revert is one commit. Pass 6 environment 8/10 (`shell: bash` removes a silent platform default). Pass 7 community n/a (internal tool). Pass 8 measurement 7/10 (the measurement step counts how often it fires).
```
ERROR PATH MATRIX
Path                    | what | fix  | recovery        | code | channel
row LEFT/CUT/not run    | pass | pass | push after fix  | pass | step output (stdout), exit 1
no numbered t.tsv       | pass | pass | rerun shards    | pass | awk error line plus exit
shard crashed           | pass | pass | rerun jobs      | n/a  | needs.shard.result red
unexpected (awk fails)  | pass | n/a  | rerun           | n/a  | step red under pipefail
```
Dispositions: the "no numbered t.tsv" message is awk's own text; a one-line `echo` would name the cause but costs bytes; accepted as is, listed for the owner.

## DX review scorecard

Overall DX 8/10 (Pass 4 documentation 6/10: page text is another goal's); TTHW under 1 minute from a red check; mode DX POLISH; magical moment designed via the step output.

## Review report

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | CLEAR | mode HOLD SCOPE, 1 finding fixed (shell: bash), 0 critical gaps |
| Outside Review | none | Independent 2nd opinion | 0 | skipped | no completed outside review; the fresh gate follows |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR | 2 findings fixed (shell, CUT seconds), 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | skipped | no UI scope |
| DX Review | `/plan-devex-review` | Developer experience gaps | 1 | CLEAR | score 8/10, TTHW under 1 min |

**OUTSIDE COVERAGE:** none; no outside model ran (design and outside voice not run).
**VERDICT:** CEO + ENG + DX CLEARED by their own reviews; the independent red-team gate is still to come.

NO UNRESOLVED DECISIONS
