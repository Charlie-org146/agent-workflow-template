# Implement DEL-26.4: a test cut for time, or not run, fails the checks (v1.1.0 task 5, part 5a)

- Slug: v110-fast-cut
- Touches: .github/workflows, skills/workflow-regression, skills/workflow-delivery, dev/toy, .loop/regression.tsv, docs, .loop/regression-skips.tsv
- ETA: 225 active minutes (estimate 179m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every DEL-26.4 test case on its page, then each runs as a real test linked to its requirement and passes, and each fails on a fixture that breaks only that rule.
2. Given a PR, then a test cut for time, or not run, fails the checks and names the test and its time; green means every chosen test ran and passed.
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.
4. Given DEL-26.4's test case, then "A toy job with one test over its limit doesn't end green."

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Open a pull request whose reached rows include one that cannot finish within its shard budget, and read the `affected` job's log.
   Expect: the job is red and prints `FAIL cut or not run: <row> <CUT or LEFT> <seconds>s: raise the shard budget (owner) or move the row` for each such row, and no row is rerun.
2. Open a documents-only pull request.
   Expect: the shards finish at once, each uploads an empty `t.tsv`, and `affected` is green.

## PR notes

### Owner: decisions this change forces (found by measuring, not decided here)

1. **Measured effect: under this rule 9 of the last 11 PR runs of `regression-pr` would have failed** (the job's own "LEFT ... not failed:" line, read from each run's log). `known-no-block` was LEFT in 7 runs (it runs `test-regression.sh` three times, so it passes its 200 s row limit every time it is selected), one run left a long list of `adopt-*` rows to the budget, and one left `lane-start-mark-once`. This PR changes `regression.py`, so it selects `known-no-block` and its own `affected` job will go red until the owner chooses: split or move that row, raise the shard budget (120 s per shard, a constant in the generator), or accept red PRs. The budget value is the owner's, as the red-team gate said. Basis, restated at the merge of main (top's TD1032): the count is the 11 most recent `regression-pr` runs before the build, each read from its own log for the unfinished-row line; the reviewer calls 9 of 11 a lower bound because a run that never printed the line is counted as passing. After merging main, `test-regression.sh` fails the same 11 lines on this branch and on main (identical sets), so none comes from this change.
2. Follow-ups outside this goal's scope are tracked as their own issues (#5759 among them), not here.

### Targeted fix after the gate (top's TD832)

- `known-no-block` ran `test-regression.sh` six times in one row; it is split into five rows (`known-no-block`, `-reads-all`, `-cut-off-refused`, `-job-skip`, `-opens-issue`), same commands, same requirement HLT-4, each seen red on its own break and each now under the 200 s row limit (142, 111, 141, 45 and 6 s, measured by `regression.py run`). It adds four rows; no coverage is lost.
- The cache save can no longer store an empty times file: the step's first command is `ls $T>/dev/null`, so with no shard file it stops before `all.tsv` exists and `actions/cache/save` finds nothing to save; the toy asserts no `all.tsv` is left. Helper files are named `r` and `b`; lanes_cli.py is 20,454 bytes [measured: wc -c] (26 free), regression.py 20,467.
- Other DEL-26 and DEL-27 requirements belong to their own goals.
- `test-regression.sh` prints the same failures on `origin/main` and on this tree (8 `FAIL` lines each, identical sets): not caused by this change.

### Found by the gate, fixed in the build

The plan first wrote the empty shard file on a documents-only exit with `: >`, which truncates the cache-restored previous-times file at the same path; the gate's second reply caught it. The build uses `>>` (create, never truncate), asserted by the toy.

### What changed

- `lanes_cli.py` (generator, `NARROW` template): the `affected` step reads only `s/shard-[0-7]/t.tsv` (the tree artifact and a documents-only run upload a restored file with stale RAN lines), fails every row that is SEL or RAN somewhere and RAN nowhere, printing `FAIL cut or not run: <id> <STATUS> <seconds>s: raise the shard budget (owner) or move the row`; no rerun; `shell: bash` (Actions' default is `bash -e`, no pipefail); the times cache is saved with `always() && needs.shard.result == 'success'` so a red run keeps its CUT marks; a documents-only shard writes its file with `>>`. `regression.py` line 323 loses ", not failed". The workflow was regenerated with `regression.py workflow`.
- Bytes [measured: wc -c], final: lanes_cli.py 20,477 to **20,454** (26 free) and regression.py 20,479 to **20,467** (13 free). The plan text's "20,473, 7 free" is the figure of the first replay, before the helper files were renamed to pay for the cache guard; it is stale and the gated plan is left as it was. No new file. fix-5727-smoke-env-2 changes lanes_cli.py to 20,454 on main; re-measure after it lands and merge main up.
- Toy `dev/toy/test-cut-fails.py`, row `cut-fails-checks` (linked to this goal's done line 4, `v110-fast-cut:4`, because the dotted id DEL-26.4 matches no requirement until v110-fast-text's page lands; this goal merges after it, then the row's goal column becomes DEL-26.4). The toy uses the real writer (`regression.merged`), runs the step's script under the shell Actions would use, and has no sleep. `test-shard-balance.py` got only its stale-assert fixes: the message text, the `$3 == "RAN"` assert, and the affected-fixture section, which asserted that a row no shard ran is rerun; it now asserts that row fails by name (a requirement change, not a loosened test).
- Tests Page rendered and the pages restamped (`audit.py restamp-own`); `docs.py check`: DOCS OK.

### Red proofs (seen failing on the break, each also green on the fixed tree)

- `regression.py red cut-fails-checks --break` restoring the parent's `lanes_cli.py`: SEEN RED 2026-11-22.
- Per case, in a detached copy: parent generator makes `left`, `cut`, `not-run`, `two`, `empty` (default shell, no pipefail) and `generated` fail; replacing `s/shard-[0-7]/t.tsv` by `s/*/t.tsv` fails `tree`; taking every status as an id source fails `stale`; a truncating early exit, no `shell: bash` and a cache save only on green each fail `generated`; no `shell: bash` also fails `empty`.
- The premise that a restored times file keeps only CUT as a state is its own case (`writer`), tested against `regression.merged`.

### Job time

The affected step on 8 shard files of 240 rows each: 0.03 s (limit 5 s in the toy); no new job, no new network call.

### Lanes

Not run: waiting for the operation session's slot word. Checks run in the worktree before it: `shard-balance`, `rows-pr-full`, `cut-fails-checks` rows pass; `size-check.py` 0; `dev/package.py --static` PASS (100 files); `docs.py check` OK.

### Cut gate moved into one script (top's TD1048, o745)

The cut-gate check is no longer inline in the generated `affected` step. It is `skills/workflow-regression/scripts/cutgate.py` (1,964 bytes, one new file under skills/, allowed within MAX_FILES by o745: 99 of 100). The template's step is one line that calls it, so a later gate can call the same script with no copy. `lanes_cli.py` is 19,993 bytes (438 freed, still above 19,000 as it was before this goal; 487 under the limit). `regression.py` is unchanged at 20,467. `test-cut-fails.py` runs the step's real command (taken from the generator) so the green and red cases are the negative control; with the script's exit forced to 0, five cases fail. The step no longer needs `shell: bash`: it is one python command, so the shell's pipefail no longer matters; the toy's `generated` case checks the cutgate.py call and the cache-save condition.

### Shards rebalanced by time (owner's o852: "rebalance shards then 866 seconds")

- Measured: the shard job's times cache never restored. It was restored from `${{ runner.temp }}/t.tsv` and saved from `all.tsv`, so the cache version never matched ("Cache not found" on every shard), and the split fell back to an even count of rows (81 or 82 per shard). On the two latest PR runs that ran every row (45102544766, 45104570186) the shards took 387 to 1,305 s.
- Fix: the restore path is now `all.tsv`, the path the affected job saves, and the shard step lays the committed times `.github/workflows/row-times.tsv` under the cache's, so a PR's first run also splits by time. The committed file holds 656 rows: the larger of each row's RAN seconds in those two runs, plus the Mac times of the six rows this goal adds or splits. Actions reads only `.yml` files in that folder. A repo with neither file gets an empty times file and the step goes on.
- Fit: with `regression.split` over the committed times (rows with no time weigh the median), every one of the 8 shards carries 778 s. A split made from the first run's times and applied to the second run's times gives 653 to 696 s.
- Test: toy `dev/toy/test-shard-budget.py`, row `shard-fits-budget` (seen red on the parent generator). It checks that the restore and save paths match, that the seed line works with and without a cache and with neither file, and that the most loaded shard fits 866 s. Its negative controls are the old restore path and one row grown past the budget.
- The budget stays 120 s in this commit. It moves to 866 s in a separate commit, only after a real PR run shows every shard under 866 s.

### test-tasks' negative control runs in the PR (TD1176, TD1184)

- TD1176 points the skills-file half of `tasks-rows-only-added` at the files v110-tasks' merge added under skills/. TD1184 accepts that under done line 3 on one condition: the negative control is in the toy and runs in the PR. The control is that a fixture of that merge adding another skills file still fails.
- The row now also requires that control's PASS line, so a FAIL in it turns the row red. Mutation check: with the control broken (its fixture's extra file renamed), the row exits 1; intact, it exits 0. The record in `dev/toy/approved-row-changes.tsv` cites "TD1176, TD1184".

### The row `guards-null-report-nofiles` follows o863 (TD1194)

- This goal adds `cutgate.py` (allowed by o745, 99 of 100 files), so the old form of the row, which read every change for added skills files, failed on it. The owner's answer (o863, "Yes, narrow it") is carried here under TD1194: the row now reads the change it was written for and v110-tasks' own merge against their first parents, with `board_tasks.py` allowed. GRD-21's package cap (200 files) stays in force.
- Negative controls run in the row: a fixture of either merge adding another skills file still fails. Mutation checks (each turned the row red, exit 1): the v110-tasks fixture no longer adds its extra file; every file allowed; the row's own-change fixture adds nothing.
- The package cap still holds: `dev/toy/test-package-caps.py` asserts 200 files pass and 201 fail, and a temp copy with 201 skills files was refused by `dev/package.py --static` (`Size: 204 files, at most 200 allowed`).
- The record in `dev/toy/approved-row-changes.tsv` cites "o863, TD1194".

### A row counts as run only when it finished (TD1202, TD1215; plan revision 4)

- `completion.py` gives each selected row its status: RAN only when it finished on the shard, SKIP when the row asked to be skipped, NOTRUN when the runner could not start it. A known row past its row limit is LEFT. `cutgate.py` never counts SKIP or NOTRUN as run: such a row passes only when its id is on `.loop/regression-skips.tsv` (the 13 rows main's run 45110588623 at c2ce6460a reports SKIPPED, each with its own reason), printed `SKIPPED <id>: <reason>`, with a count of skipped rows among the selected ones; any other skipped row fails and names the repair. A row the runner could not start passes only if its list row carries the `notrun` flag; only `package-rows-tracked` has it. It is the one list row without its own skip message: main's run prints SKIPPED for it with no message, and finding the missing tool is on the list of work after the cut.
- The list cannot grow without a record: each id needs a `skip:<id>` line in `dev/toy/approved-row-changes.tsv` (TD1215), checked by `dev/toy/test-skip-list.py`, row `skip-list-approved`, with negative controls.
- The shard step reads the diff once and fails with a message when it cannot; the tree job runs with `--budget -1` and runs the same gate on its own times file, so a whole-tree row that skips is judged by the skip list too; `cutgate.py` fails with a message on an unreadable skip list, a malformed times line (file and line), a times file it cannot write, or no arguments, and writes the times cache whole and only when there is a record.
- Toy `dev/toy/test-cut-complete.py`, row `cut-complete`: each case runs the real runner, the real gate or the generated step and was seen red before its fix (known timeout, skip, could not start, unreadable diff, empty record, tree budget, skip-list read, malformed line, usage, write failure), with controls that stay green. The rows `cut-fails-checks` and `skip-list-approved` check the generated call in full and the list.
- The row-table PR rule is unchanged: a change to `.loop/regression.tsv` runs every row with no budget, so this PR's first run shows each shard's measured time against 866 s; the budget commit follows that run (o852, TD1183, TD1202).
