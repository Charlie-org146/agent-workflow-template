# Plan (revision 3): a test cut for time, or not run, fails the PR's checks, naming the test and its time (DEL-26.4, #5757)

Revision 2 (one revision after the first gate, on operation-mac's order): the cache save runs even when `affected` fails, the pin is a deterministic fixture made by the real writer instead of a sleeping row, the fail line says who can change the budget, bytes were measured in a scratch copy first, and the dependency on v110-fast-text is stated. The three reviews ran on revision 1; revision 2 changes the lines named here and the reviews were not run again (the record at the end says so).

Revision 3 (one targeted fix, top's TD832, after the owner's accept of the first gates' breaks as o753/o754): (1) the row `known-no-block` ran `test-regression.sh` six times in one row and passed the 200 s row limit every time it was selected (measured: 9 of the last 11 PR runs would have failed on it), so it is split into five rows, one per run, with the same commands and the same requirement (HLT-4), each seen red with its own break and each measured under 200 s (142, 111, 141, 45 and 6 s); (2) a guard so an empty times file is never saved: the redirect `> all.tsv` creates the file before awk can fail, so the guard is a first command `ls $T>/dev/null` that stops the step before any file exists (a `test -s all.tsv` after the redirect would not be reached, since the step already exited); the helper files are renamed `r` and `b` to pay for it: lanes_cli.py is now 20,454 bytes [measured: wc -c], 26 free; (3) other DEL-26 and DEL-27 requirements are left to their own goals.

Dependency: DEL-26.4's page text (its test case and wording) comes from v110-fast-text, so this goal merges after v110-fast-text; this plan writes no page text.

Source: revision 6 of the retired fix-5757 (branch `loop/fix-5757`, b7ba2d9b7) for the numbered-shard glob and the stale-file toy case; its rerun is dropped (no rerun: operation-mac's order TD786/TD787). The plan of the retired v110-fast-ci (64dfaf64b) is kept for reference only; its record overstated its review depth (the three review skills were not loaded). This plan's reviews are the three skills, loaded and run.

## Implementation plan

Goal: when a selected row is written LEFT or CUT by a shard, or no shard ran it, the `affected` job fails and names the row and its recorded seconds. Green means every selected row ran (RAN) on some shard.

What exists (read in this worktree, parent c91fddbd5; bytes by `wc -c`): `regression-pr.yml` is written by `regression.py workflow` from the `NARROW` template in `lanes_cli.py` (20,477 bytes). Each shard writes `t.tsv` rows `id<TAB>seconds<TAB>status`: RAN (this shard ran it), SEL (another shard's), CUT (budget ran out), LEFT (passed the 200 s row limit; regression.py:320 takes it out of the failures when more than one shard runs). The `affected` job counts RAN, LEFT and CUT as accounted for, prints "LEFT (row limit or budget), not failed" and reruns only a row no shard wrote, so every check can be green with a selected row never finished (#5757). The `shard-tree` artifact and the documents-only early exit upload the cache-restored previous `all.tsv`, which holds stale RAN lines.

Changes:
1. `lanes_cli.py`, the `affected` run block of the template only. It reads only the numbered shard files (`T=s/shard-[0-7]/t.tsv`, unquoted so it expands where used). `all.tsv` and `ran.txt` read `$T`; `ran.txt` holds the ids with status RAN. The unfinished ids are those with SEL or RAN anywhere and no RAN anywhere (`awk '$3 ~ /^(SEL|RAN)$/ ... | comm -23 - ran.txt`): a row cut or left on its shard is SEL on every other shard, so it is named; a stale CUT or LEFT for an unselected id has no SEL, so it is not; a restored documents-only file has no SEL, so it is not. For each unfinished id the step prints one line per row, `FAIL cut or not run: <id> <STATUS> <seconds>s: raise the shard budget (owner) or move the row` (STATUS and seconds from `all.tsv`: LEFT carries the 200 s limit it passed, CUT the last recorded time or 0, and `not run` replaces both when no shard wrote the row), and the step ends with `test ! -s bad.txt`. The rerun loop, the "LEFT ... not failed" echo and the `test -z "$bad"` line are deleted. No rerun. The "run twice:" echo stays (a toy reads it). The cache-save step becomes `if: always() && needs.shard.result == 'success'`, so a red `affected` still saves `all.tsv` (the CUT marks that order cut rows first on the next push, TD497, survive a red run instead of the same rows being cut on every push). The last step `test "${{ needs.shard.result }}" = success` stays, so a crashed shard still fails. The step gets `shell: bash` (Actions' default for `run:` is `bash -e {0}` with no pipefail, so a failing awk inside a pipeline would be ignored and an empty glob would end green; `shell: bash` runs `bash --noprofile --norc -eo pipefail {0}`), so an empty glob or a failing awk is red. A shard that takes the documents-only early exit also writes an empty `t.tsv` (`: > <temp>/t.tsv`), so "no numbered file at all" always means a missing artifact and is red, never a legitimate case. Shard budgets, the tree line, `runs.py` and TD512 are unchanged.
2. `regression.py` line 323: the message loses ", not failed" (shrinks).
3. The workflow file is regenerated with `regression.py workflow`, never hand-edited; the toy asserts the generator's output equals the file on disk and that the affected step carries `shell: bash`.
4. Test (REG-4, one row per script): one new toy script `dev/toy/test-cut-fails.py`, one row `cut-fails-checks` (goal column `DEL-26.4`; the page's test case, "A toy job with one test over its limit doesn't end green"). It takes the affected step's run block from `NARROW` by text (hard fail if empty or holding a `${{` expression), runs it with `bash --noprofile --norc -eo pipefail` in a temp tree, and has the cases: a row LEFT on one shard and SEL on the others fails and names the row and its seconds; the same for CUT; a row SEL on every shard and RAN on none fails with `not run`; two failing rows are both named; all rows RAN is green; a stale CUT for an unselected id is green; a restored documents-only file (no SEL) is green; a stale `shard-tree/t.tsv` with RAN for a row this run's numbered shards cut is still red; an empty glob (no numbered file) is red; a documents-only run whose shards wrote empty files is green. The pin is deterministic and has no sleep: the toy calls the real writer, `regression.merged(path, results, left=[slow], limit=200)`, to produce the LEFT row a shard writes for a row past its limit, composes three files (`shard-0/t.tsv`: the fast row RAN and the slow row LEFT; `shard-1/t.tsv`: both rows SEL; a stale `shard-tree/t.tsv`), asserts the precondition that the writer put LEFT on the slow row, then runs the real affected block on them: it must end red and name the slow row. The generated file is also asserted to carry `shell: bash` and the cache-save condition `always() && needs.shard.result == 'success'` (red when either is absent). `rows-pr-full` greps the PASS lines of `test-shard-balance.py`: it is run before and after the stale-assert edits and must stay green. `test-shard-balance.py` gets only its stale-assert fixes (the ", not failed" message and the `not failed: e` expectation), no case loosened; its row description is updated to what it still checks.
5. Red proofs (each seen failing on the parent, `regression.py red cut-fails-checks --break CMD`, one case at a time): break = restore the parent's generator (`git show c91fddbd5:skills/workflow-regression/scripts/lanes_cli.py > ...`), which ends green on LEFT, CUT and the end-to-end case; break = replace `$T` by `s/*/t.tsv` (stale tree file case); break = count every non-empty status as an id source (stale CUT case). Each case is also run without the break to show it passes.
6. Bytes: the whole revised template, with `shell: bash`, the empty-file early exit, the always() save and the fail line, was replayed in a scratch copy of the parent: lanes_cli.py 20,477 to 20,473 [measured: wc -c on the scratch copy], 7 free under 20,480; the build trims the fail line wording further if a measure at build is higher, and stops and reports if it cannot fit (no new file is planned); regression.py 20,479 to 20,467; the toy is under dev/ (not shipped). Nothing crosses 19,000 that does not now; no new file under skills/ is needed, so MAX_FILES and the release-gate change are not touched. If a measure says otherwise the build stops and reports.
7. Docs: `docs.py audit` and `docs.py check`; the DEL-26.4 page text is v110-fast-text's, not edited here.

Measurement before the build (owner-facing cost): count, over the last 10 PR runs of `regression-pr` (`gh run view --log`, the existing "LEFT (row limit or budget), not failed:" line), how many would have failed under this rule; the number goes in the PR notes. It decides nothing by itself; the shard budget stays the owner's lever.

Test plan: `dev/toy/test-cut-fails.py`, `test-shard-balance.py`, `test-package-static.py`, `test-regression.sh`, the size check, rows none red, the PR's own CI run.

Owner-level, reported and not decided here: the shard budget value (120 s per shard; a large reached set ends red until the owner raises it or a row moves, an unattended worker cannot decide that).

Failure modes: a PR with a large reached set now fails when its rows exceed the shard budget (120 s each of 8 shards), naming them: that is the intended behaviour, and the budget constant is the owner's lever (not changed here); a crashed shard (`needs.shard.result`, red); an empty or stale artifact set (red).

Not in scope: reruns (ordered out), the budget value (the owner's), and the other DEL-26 and DEL-27 requirements (their own goals).

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
