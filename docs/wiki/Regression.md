<!-- workflow-docs -->
# Regression

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/7

Review: **Reviewed 2026-11-20** <!-- prd P=14b68802 R=94b657f1 N=f86bd012 M=d4d1a48b U=03828777 -->

How to use: [How-to-use-Regression](How-to-use-Regression)

## Problem
- I can't trust a requirement or a fix unless a test proves it, and every fix I've ever shipped should stay fixed without me re-checking it.
- Running every test on every change is too slow, but skipping tests lets breakage slip through; I need fast checks in the loop and the full suite somewhere I can see it, like GitHub Actions.
- I need failures to reach me as GitHub issues, every test shown in one format, and control over what runs when.

## Runbook

### regression-round
- **Serves:** REG-4, HLT-4, REG-4, AUT-1, AUT-1.
- **Schedule:** every 4 hours (`regression_cron` in `.loop/config.json`, default `17 */4 * * *`) and by hand: the Actions tab (Run workflow on `regression`, with `target` land, nightly or one row id) or `gh workflow run regression.yml`. `off` stops the schedule only.
- **Steps:** Start the `regression` workflow (`.github/workflows/regression.yml`): its "Run the rows" step runs every land and nightly row of `.loop/regression.tsv`, keeps one issue per failing row, the rows are split over sixteen parallel jobs (a matrix, each row in exactly one shard, each row given the job time that is left), and a final `summary` job merges every shard's results into one run summary, one table per feature, ending with how many shards reported and how many rows were skipped for out of job time. Runs are grouped per ref, so a newer run on a ref cancels the one it supersedes and a branch run never waits behind a release tag run. A local `regression.py run` is not this run: it can write records and, with `--live` only (a token in the environment writes nothing), open issues, so do not use it in place of the workflow. A row runs without the job's token, its runner files and the runner's own `REGRESSION_SHARD`, `REGRESSION_LEVELS`, `REGRESSION_TARGET` and `REGRESSION_CLEANUP`, so a row that runs the workflow's code (the `workflow-same-as-run` row) runs every row it is given. The health round that follows reads the newest suite-time artifact this workflow keeps. The written workflow also has a `matrix-smoke` job that runs `dev/toy/matrix-smoke.py --agent ci` on Linux and keeps the dated record as an artifact. A local `run --live` whose GraphQL issue list times out reads the issues over REST, 100 a page, before it gives up, and then it changes no issue. The lane names every file a row reads with forward slashes, on Windows too, and matches a changed path with either slash form.
- **Full run:** a full run executes every row of the levels the run covers, which on the schedule is every land and nightly row in `.loop/regression.tsv` (draft and covered rows are not run; a by-hand run with target land runs land rows only and is not a full run) against the checked-out repo with no row left out and no reuse of an earlier result, and records each real result as the row ends. It opens, updates or closes one `defect` issue per failing row, tagged with its feature only when `feature_labels` is true. A row that exits 77 is `SKIPPED`, never `PASS`, and opens no issue. A row skipped because the job ran out of time is also `SKIPPED` and files no issue; a run with such a row is not a full run, so say so and run it again. Working out which rows a change affects (`lanes_cli.py affected`) holds at most 32 million characters of file text at once and answers each file-and-path question once, so a large repo stays under about 200 MB (#4151). The rows that run first in a lane are the goal's new and changed rows, then failure reruns, then rows that reach a changed file, then the picks, so a base merge never leaves the goal's own rows to the scheduled suite (#531); a failing row that ends in `| grep -q` shows its own text in the lane (#3911). A failing row whose output names a missing tool (node, pnpm, npm, npx, yarn) or a POSIX-only module such as fcntl is printed `NOTRUN`, not `FAIL`; with a row that exits 77 it is counted as not runnable here, never blocks qa, which records `N pass; M not runnable here`, and files one `other-machine` to-do per goal listing them (REG-10, #4492). Any change to a file that isn't NO_EFFECT, a deletion included, also runs the root runners; a change only to NO_EFFECT files such as a release's VERSION or a goal's `.loop/goals/` file runs none, on Windows too (#4554). A row that exits 0xC0000142 or a like Windows start code is rerun once, after the other rows; one still dying is `ENV` with its exit code, never `FAIL`, and a skip never overwrites a row's last result (#4639).
- **Output:** the run summary (a header with totals and the run time, then one table per feature) and one open issue per failing row, whose body holds the row's last 40 output lines (a line saying it printed nothing when it did, never an empty block); the regression digest is the failing-test part of the health round's digest comment and email, which the health round posts after this run.
- **Never:** never run a subset, `--reuse` or `--tier` on a scheduled run; never report a row as passed that did not run; never write results by hand into `.loop/regression-runs.tsv`; never close an issue while its row fails; never push, merge or release.
- **Check:** the run summary's passed, known, failed and skipped counts add up to the number of land and nightly rows in `.loop/regression.tsv` (draft and covered rows excluded; a row listed in `.loop/regression-known.tsv` counts as known, with its reason); each failing row has exactly one open issue; every `SKIPPED` row names its reason (cannot run here, or out of job time); the run time is real and under the time budget.

## Requirements

### Functional
- REG-4: **Reviewed 2026-11-20** Every requirement has its tests, written and run one way, with honest results <!-- reviewed 05626ff1 -->
  - Every Reviewed requirement, whole flow and fixed issue has its kind of test: requirement, flow or defect. [REG-4]
  - A requirement with no passing test shows "not enforced". [REG-4]
  - One format, and one command runs them everywhere. [REG-4]
  - **The table has one row per test script and requirement, and at most 600 rows**; a row runs every case of its script for that requirement. [REG-4]
  - A test counts as proven only after it was seen failing. [REG-4]
  - A flaky test is marked, never silently retried. [REG-4]
  - A fix leaves a defect test behind. [REG-4]
  - Coverage comes from main's full run and never drops silently. [REG-4]
  - **No test stays parked:** a known-red row needs an open issue and a fix goal, and a major release needs the known list empty. [REG-4]

### Non-functional

None

## Non-goals
- The owner never writes or manages tests; the loop does.
- The loop never runs the full suite on every goal.
- A known failure does not block a run.

## Success metrics
- No goal's test run in the loop takes over 15 minutes (REG-7's budget floor), and the nightly full suite runs green or every failure has its issue.
- Every closed issue fixed by a goal has a passing defect test listed in its release note.
- A GitHub run and a local run of the same rows end the same way.

## Revisions

### Retired

- REG-1: moved to REG-4
- REG-10: moved to REG-4
- REG-11: moved to DEL-17
- REG-12: moved to REG-4
- REG-13: moved to REG-4
- REG-14: moved to DEL-17
- REG-15: moved to REG-4
- REG-16: moved to REG-4
- REG-2: moved to REG-4
- REG-3: moved to REG-4
- REG-5: moved to HLT-4
- REG-6: moved to REG-4
- REG-7: moved to DEL-17
- REG-8: moved to REG-4
- REG-9: moved to REG-4

### REG-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Three kinds of tests <br> Every Reviewed requirement has at least one requirement test, every whole flow has an end-to-end workflow test on a toy repo, and every fixed issue has a defect test. [REG-1] <br> A requirement with no passing test shows as not enforced. [REG-1] | readme-six: absorbed into REG-4 (o514) | o598: "yes build it" |
| r3 | 2026-11-19 | Three kinds of tests <br> Every Reviewed requirement has at least one requirement test, every whole flow has an end-to-end workflow test on a toy repo, and every fixed issue has a defect test. [REG-1] <br> A requirement with no passing test shows as not enforced. [REG-1] | consolidation (TOP-DECISION 89) | o201: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Three kinds of tests <br> Every Reviewed requirement has at least one requirement test, every whole flow has an end-to-end workflow test on a toy repo, and every fixed issue has a defect test. A requirement with no passing test shows as not enforced. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | Three kinds of tests <br> Requirement tests: one or more for every Reviewed requirement, functional and non-functional alike. <br> Workflow tests: end-to-end runs of a whole flow on a toy repo (for example a goal from freeze to release), proving the steps work together. <br> Defect tests: one for every issue, finding or bug that gets fixed, proving it stays fixed. <br> A requirement with no passing test shows as not enforced; a fix isn't finished until its defect test exists and passes. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Test format <br> Every test is listed in one fixed format, grouped by feature, wherever tests are shown: its kind, what it guards, what it checks and its last result. | consolidation (TOP-DECISION 89): absorbed into REG-4 | o241: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Test format <br> Every test is listed in one fixed format, grouped by feature, wherever tests are shown: its kind, what it guards, what it checks and its last result. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | Test format <br> Every test is listed in one fixed format, grouped by feature, wherever tests are shown (the wiki, the GitHub run summary, the health report): its kind, what it guards (the requirement, the workflow, or the issue with its state), what it checks in one plain line, when it runs, its last result and date, and whether it has been seen failing once. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | One command, three places <br> One command runs the suite the same way for me, the loop and GitHub Actions. | consolidation (TOP-DECISION 89): absorbed into REG-4 | o242: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-10 | One command, three places <br> One command runs the suite the same way for me, the loop and GitHub Actions. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r5 | 2026-11-20 | Every requirement has its tests, written and run one way, with honest results <br> Every Reviewed requirement, whole flow and fixed issue has its kind of test: requirement, flow or defect. [REG-4] <br> A requirement with no passing test shows "not enforced". [REG-4] <br> One format, and one command runs them everywhere. [REG-4] <br> **The table has one row per test script and requirement, and at most 600 rows**; a row runs every case of its script for that requirement. [REG-4] <br> A test counts as proven only after it was seen failing. [REG-4] <br> A flaky test is marked, never silently retried. [REG-4] <br> A fix leaves a defect test behind. [REG-4] <br> Coverage comes from main's full run and never drops silently. [REG-4] <br> **No test stays parked:** a known-red row needs an open issue and a fix goal, and a major release needs the known list empty. [REG-4] | v2.0 text, owner record o666 (relayed by operation-top) | o666: "So at the let's add these 5 goals to 2.0, and I" |
| r4 | 2026-11-20 | Every requirement has its tests, written and run one way, with honest results <br> Every Reviewed requirement, whole flow and fixed issue has its kind of test: requirement, flow or defect. [REG-4] <br> A requirement with no passing test shows "not enforced". [REG-4] <br> One format, and one command runs them everywhere. [REG-4] <br> **The table has one row per test script and requirement, and at most 600 rows**; a row runs every case of its script for that requirement. [REG-4] <br> A test counts as proven only after it was seen failing. [REG-4] <br> A flaky test is marked, never silently retried. [REG-4] <br> A fix leaves a defect test behind. [REG-4] <br> Coverage comes from main's full run and never drops silently. [REG-4] | readme-six: the owner-approved final README (o514) | o571: "yes build it" |
| r3 | 2026-11-19 | Tests are written, listed and run one way <br> Once I review a PRD, the loop writes Given/When/Then tests for each requirement, links each to a regression test, and keeps them in step when a requirement changes. I never write or manage tests. [DOC-3] <br> Every test is listed in one fixed format, grouped by feature, wherever tests are shown: its kind, what it guards, what it checks and its last result. [REG-2] <br> One full Tests page is generated, listing every test with its latest result. [DOC-10] <br> One command runs the suite the same way for me, the loop and GitHub Actions. [REG-3] <br> In the loop a goal runs only the tests its change affects plus its own new ones, and they run again on the merged result before a pull request merges. The full suite runs on the schedule and on every release, never on every goal, and I can run any part at any time. [REG-4] <br> Which tests run where, the schedule, the time limits and how many test lanes run at once are settings. [REG-8] <br> Test lanes running side by side never share files or ports or time each other out, and a lane over its limit says so. [REG-12] <br> A test that fails on one machine but passes on CI is filed as an issue and is not counted as a failure of the goal. [REG-13] <br> (v2.0) ci-shards-unrun0: every test runs in the full CI run, with nothing left unrun. <br> (v2.0) lanes-table-data: an edit to the test list re-runs only the rows it changes. | consolidation (TOP-DECISION 89) | o236: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | When tests run <br> In the loop a goal runs only the tests its change affects plus its own new ones, and they run again on the merged result before a pull request merges. The full suite runs on the schedule and on every release, never on every goal, and I can run any part at any time. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | When tests run <br> In the loop, each goal runs only the rows affected by its changes plus its own new rows, at qa; ship and release reuse that run when no code changed since. <br> Before a pull request merges, the affected rows run again on the merged result. <br> The full suite (every requirement, workflow and defect test) runs in GitHub Actions on the Automation schedule (every few hours by default) and on every release, never on every goal. <br> I can run the full suite or any part of it at any time. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Failures go to GitHub <br> Each failing test has one labelled issue, updated while it fails and closed when it passes. Known failures don't block, and nothing is written without --live. | consolidation (TOP-DECISION 89): absorbed into HLT-4 | o217: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Failures go to GitHub <br> Each failing test has one labelled issue, updated while it fails and closed when it passes. Known failures don't block, and nothing is written without --live. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Failures go to GitHub <br> One labeled issue per failing test, updated while it fails and closed when it passes; known failures don't block; it only previews unless `--live` is given, and the scheduled workflows pass `--live`. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Every fixed issue leaves a test <br> A goal that fixes an issue adds that issue's defect test, seen failing on the old code and passing on the fix, before the issue closes. A reopened issue's test is marked failing until it passes again. | consolidation (TOP-DECISION 89): absorbed into REG-9 | o248: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Every fixed issue leaves a test <br> A goal that fixes an issue adds that issue's defect test, seen failing on the old code and passing on the fix, before the issue closes. A reopened issue's test is marked failing until it passes again. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | Every fixed issue leaves a test <br> A goal that fixes an issue adds that issue's defect test, seen failing on the old code and passing on the fix, before the issue closes. <br> Each release note lists the issues it fixed, each with its defect test, so every version carries the regressions for what it fixed. <br> A reopened issue's test is marked failing until it passes again. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Test lanes and suite stay within budgets <br> Every in-loop test run stays within a time budget, 15 minutes by default and never lower. A run that would go past it runs what fits and defers the rest to the full suite, naming how many. It is the only time limit on a lane. [REG-7] <br> The work before a lane's first test, preparing, planning and waiting for a slot, has its own budget, 15 minutes by default and never lower. A lane that reaches it stops, says which part ran long, and can be rerun. [REG-11] <br> The number of tests and the full-suite time are capped by settings. A goal that takes the repo over a cap is refused at qa unless it removes or merges as many tests as it adds, or I raise the cap in my own words. The suite time is measured from the latest full run. [REG-14] | readme-six: absorbed into DEL-17 (o514) | o601: "yes build it" |
| r3 | 2026-11-19 | Test lanes and suite stay within budgets <br> Every in-loop test run stays within a time budget, 15 minutes by default and never lower. A run that would go past it runs what fits and defers the rest to the full suite, naming how many. It is the only time limit on a lane. [REG-7] <br> The work before a lane's first test, preparing, planning and waiting for a slot, has its own budget, 15 minutes by default and never lower. A lane that reaches it stops, says which part ran long, and can be rerun. [REG-11] <br> The number of tests and the full-suite time are capped by settings. A goal that takes the repo over a cap is refused at qa unless it removes or merges as many tests as it adds, or I raise the cap in my own words. The suite time is measured from the latest full run. [REG-14] | consolidation (TOP-DECISION 89) | o268: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Fast in the loop <br> Every in-loop test run stays within a time budget, 15 minutes by default and never lower. A run that would go past it runs what fits and defers the rest to the full suite, naming how many. It is the only time limit on a lane. | v2 rewrite (prd-rewrite-to-10): changed: one lane limit (your decision, o39). | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Fast in the loop <br> Every in-loop test run (qa, ship and the pull-request lane) stays within a time budget, a setting that defaults to 15 minutes and can't be set lower. A run that would go past it, including changes the row picker can't map such as a deleted file, runs the affected tier that fits and leaves the rest to the scheduled full suite, saying what it left; the loop never runs the full suite. The scheduled full suite finishes in under 30 minutes: the GitHub job's time limit is that same 30 minutes and the suite is sharded over several jobs so each fits it, and health flags a suite that doesn't. <br> The work before a lane's first test row (preparing, planning and waiting for a slot) has its own budget, a setting that defaults to 15 minutes and can't be set lower; a lane whose preparation reaches it stops, says which part ran long, and the goal can rerun it instead of starting over. <br> Planning computes each row's closure once per lane, not once per row, and keeps it per branch, keyed by HEAD, the row file, the planner code, `LANES_WIDE` and the loop's uncommitted bookkeeping files; a dirty tree never uses it, a plan that read an ignored file, or one outside the repo through a symlink, is not saved (a file created or ignored later is outside the key: remove the plans folder or set `LANES_NO_CACHE=1`), and `LANES_NO_CACHE=1` turns it off. <br> Issue bodies and comments are passed to gh in a file (`--body-file`), so a long failure output never meets the Windows command-line limit. <br> A lane about to run rows waits while free memory is below `min_free_memory_gb` (default 4), and gives up after four times the lane's time limit; a lane already running is never stopped. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Controllable <br> Which tests run where, the schedule, the time limits and how many test lanes run at once are settings. | consolidation (TOP-DECISION 89): absorbed into REG-4 | o243: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Controllable <br> Which tests run where, the schedule, the time limits and how many test lanes run at once are settings. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | Controllable <br> Which levels run where, the GitHub schedule, the time limits and how many test lanes run at once are settings. <br> Lanes running side by side never share files or ports or time each other out, and a lane over its limit says so. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Test results and coverage are honest <br> Every test has been seen failing once, or shows as unproven. A test that fails then passes on the same commit is marked flaky, never silently retried. [REG-9] <br> A goal that fixes an issue adds that issue's defect test, seen failing on the old code and passing on the fix, before the issue closes. A reopened issue's test is marked failing until it passes again. [REG-6] <br> A test this machine can't run is skipped with its reason and never counted as seen failing. Its failing proof is recorded as owed, runs on a machine that can, and is written back with that machine and commit. An owed proof never blocks the goal, its merge or the release. [REG-10] <br> Each requirement's coverage step, from Stated to Fresh, is computed from the latest full run on main and shown beside it on its page. One test may prove several requirements. Nothing else is a source. [REG-15] <br> A goal that would remove the only proof of a Reviewed requirement is refused at qa, and a release that lowers coverage needs my words. [REG-16] | readme-six: absorbed into REG-4 (o514) | o599: "yes build it" |
| r3 | 2026-11-19 | Test results and coverage are honest <br> Every test has been seen failing once, or shows as unproven. A test that fails then passes on the same commit is marked flaky, never silently retried. [REG-9] <br> A goal that fixes an issue adds that issue's defect test, seen failing on the old code and passing on the fix, before the issue closes. A reopened issue's test is marked failing until it passes again. [REG-6] <br> A test this machine can't run is skipped with its reason and never counted as seen failing. Its failing proof is recorded as owed, runs on a machine that can, and is written back with that machine and commit. An owed proof never blocks the goal, its merge or the release. [REG-10] <br> Each requirement's coverage step, from Stated to Fresh, is computed from the latest full run on main and shown beside it on its page. One test may prove several requirements. Nothing else is a source. [REG-15] <br> A goal that would remove the only proof of a Reviewed requirement is refused at qa, and a release that lowers coverage needs my words. [REG-16] | consolidation (TOP-DECISION 89) | o244: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Honest results <br> Every test has been seen failing once, or shows as unproven. A test that fails then passes on the same commit is marked flaky, never silently retried. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | Honest results <br> Every test has been seen failing once, or shows as unproven. <br> A test that fails then passes on the same commit is marked flaky, never silently retried. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Tests a machine can't run <br> A test this machine can't run is skipped with its reason and never counted as seen failing. Its failing proof is recorded as owed, runs on a machine that can, and is written back with that machine and commit. An owed proof never blocks the goal, its merge or the release. | consolidation (TOP-DECISION 89): absorbed into REG-9 | o245: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Tests a machine can't run <br> A test this machine can't run is skipped with its reason and never counted as seen failing. Its failing proof is recorded as owed, runs on a machine that can, and is written back with that machine and commit. An owed proof never blocks the goal, its merge or the release. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Red proof for rows a platform can't run <br> A row whose red proof needs another machine can be recorded owed (`red ID --owed --runner R`): it reads PENDING instead of UNPROVEN, one to-do issue labelled `other-machine` opens on the row's feature milestone, and neither the goal's pr lane nor the release waits for it. A real red proof clears it. <br> A row the local platform can't run (the bash toy rows on native Windows exit 77) is skipped with its reason and is never counted as seen failing: a skip, on any platform, never sets the seen-failing date. <br> Its red proof runs on a capable runner (Linux or macOS, in CI or a session), and the result is written back to the row with the runner and the commit it ran on; a Windows runner can't be named. <br> A pull request that adds such a row lists the exact red commands still owed, so the proof is run and written back before the row counts as proven. <br> A loop run that fails only on rows both skipped on this platform and unproven (qa or ship) waits for the off-platform proof, naming the rows and the red commands, and spends no failed try; a real failure still does. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### REG-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Preparation is budgeted too <br> The work before a lane's first test, preparing, planning and waiting for a slot, has its own budget, 15 minutes by default and never lower. A lane that reaches it stops, says which part ran long, and can be rerun. | consolidation (TOP-DECISION 89): absorbed into REG-7 | o269: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-14 | Preparation is budgeted too <br> The work before a lane's first test, preparing, planning and waiting for a slot, has its own budget, 15 minutes by default and never lower. A lane that reaches it stops, says which part ran long, and can be rerun. | migration r1; date from the Review line | o155: "start regroup 3 and 4" |

### REG-12

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Lanes don't disturb each other <br> Test lanes running side by side never share files or ports or time each other out, and a lane over its limit says so. | consolidation (TOP-DECISION 89): absorbed into REG-4 | o239: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-14 | Lanes don't disturb each other <br> Test lanes running side by side never share files or ports or time each other out, and a lane over its limit says so. | migration r1; date from the Review line | o155: "start regroup 3 and 4" |

### REG-13

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | One machine's failure is not the goal's failure <br> A test that fails on one machine but passes on CI is filed as an issue and is not counted as a failure of the goal. | consolidation (TOP-DECISION 89): absorbed into REG-4 | o240: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-14 | One machine's failure is not the goal's failure <br> A test that fails on one machine but passes on CI is filed as an issue and is not counted as a failure of the goal. | migration r1; date from the Review line | o155: "start regroup 3 and 4" |

### REG-14

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Caps on tests and suite time <br> The number of tests and the full-suite time are capped by settings. A goal that takes the repo over a cap is refused at qa unless it removes or merges as many tests as it adds, or I raise the cap in my own words. The suite time is measured from the latest full run. | consolidation (TOP-DECISION 89): absorbed into REG-7 | o270: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-14 | Caps on tests and suite time <br> The number of tests and the full-suite time are capped by settings. A goal that takes the repo over a cap is refused at qa unless it removes or merges as many tests as it adds, or I raise the cap in my own words. The suite time is measured from the latest full run. | migration r1; date from the Review line | o155: "start regroup 3 and 4" |

### REG-15

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Coverage is measured in one place <br> Each requirement's coverage step, from Stated to Fresh, is computed from the latest full run on main and shown beside it on its page. One test may prove several requirements. Nothing else is a source. | consolidation (TOP-DECISION 89): absorbed into REG-9 | o246: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-14 | Coverage is measured in one place <br> Each requirement's coverage step, from Stated to Fresh, is computed from the latest full run on main and shown beside it on its page. One test may prove several requirements. Nothing else is a source. | migration r1; date from the Review line | o155: "start regroup 3 and 4" |

### REG-16

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Coverage never drops silently <br> A goal that would remove the only proof of a Reviewed requirement is refused at qa, and a release that lowers coverage needs my words. | consolidation (TOP-DECISION 89): absorbed into REG-9 | o247: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-14 | Coverage never drops silently <br> A goal that would remove the only proof of a Reviewed requirement is refused at qa, and a release that lowers coverage needs my words. | migration r1; date from the Review line | o155: "start regroup 3 and 4" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [unproven-blocks](Tests#t-unproven-blocks) | requirement | REG-4 | Given REG-4, when test-regression.sh runs its 10 cases, then each passes: the run is blocked; it stays unproven; it is flagged; the date is kept; both end the same way and open the same issues; it is refused and the row's seen-failing date stay; it is refused and the row stays unproven; it is refused; the row has a seen-failing date; it names the row, date, runner and commit. | PASS 2026-11-20 |
| [one-link](Tests#t-one-link) | requirement | REG-4 | Given REG-4, when test-criteria.sh runs its 2 cases, then each passes: the check fails; each test's result and date are recorded. | PASS 2026-11-20 |
| [refused-unmet](Tests#t-refused-unmet) | requirement | REG-4 | Given REG-4, when test-criteria.sh runs its 3 cases, then each passes: it is refused; its table row carries the test link, its Given/Whe; the row carries its anchor, result, date, run and. | PASS 2026-11-20 |
| [milestones-once](Tests#t-milestones-once) | requirement | REG-4 | Given a free-form milestone title such as v1.0, when new runs twice, then one milestone is made and the second run says it exists. | PASS 2026-11-20 |
| [every-row-described](Tests#t-every-row-described) | requirement | REG-4 | Given this repo's test rows, when they are checked, then every row has a plain one-line description. | PASS 2026-11-19 |
| [untested-listed](Tests#t-untested-listed) | requirement | REG-4 | Given REG-4, when test-docs-command.sh runs its 2 cases, then each passes: it is listed; it is found. | PASS 2026-11-19 |
| [defect-categories](Tests#t-defect-categories) | requirement | REG-4 | Given REG-4, when test-defect.sh runs its 3 cases, then each passes: every row has a category, defect rows link their i; it is refused; defect tests exist for each. | FAIL 2026-11-12 |
| [lanes-reuse](Tests#t-lanes-reuse) | requirement | REG-4 | Given REG-4, when test-lanes.sh runs its 6 cases, then each passes: it reuses the first and runs no test; only the tests that read the changed files run; an; it is never reused; every test runs; it reuses the qa run; it records the run with the exact command ship che. | PASS 2026-11-10 |
| [lanes-pr-affected](Tests#t-lanes-pr-affected) | requirement | REG-4 | Given the base merged before the pull request, when tests run, then only the affected tests rerun. | PASS 2026-11-10 |
| [prd-scenarios](Tests#t-prd-scenarios) | requirement | REG-4 | Given REG-4, when test-prd.sh runs its 3 cases, then each passes: each row is a Given/When/Then scenario with its te; it lists that requirement as UNTESTED; they all find the same requirement IDs and the rel. | PASS 2026-11-19 |
| [lanes-headers](Tests#t-lanes-headers) | requirement | REG-4 | Given REG-4, when tree-once.sh runs its 2 cases, then each passes: every script a row names has a valid header; fewer than half the land rows rerun and every row. | FAIL 2026-11-10 |
| [lanes-declared](Tests#t-lanes-declared) | requirement | REG-4 | Given REG-4, when test-narrow.sh runs its 7 cases, then each passes: only the rows whose closure reaches it rerun; its row still reruns; the row still reruns; only those rerun, and a change every row reaches r; the check refuses it until the folder is declared; the rows that name or reach it run and no full run; it names the code, the file and line, and the line. | PASS 2026-11-10 |
| [lanes-wide-parity](Tests#t-lanes-wide-parity) | requirement | REG-4 | Given REG-4, when test-narrow.sh runs its 2 cases, then each passes: the mapping is the same as the wide one, and LANES; only that row and the rows that read this repo's t. | PASS 2026-11-10 |
| [lanes-trace-check](Tests#t-lanes-trace-check) | requirement | REG-4 | Given a row whose run reads a skill file outside its closure, when check-reads runs, then that row fails with the line to add. | PASS 2026-11-10 |
| [lanes-trace](Tests#t-lanes-trace) | requirement | REG-4 | Given every land row, when check-reads traces their runs, then each run's skill reads are inside its closure. | FAIL 2026-11-10 |
| [reg2-wording](Tests#t-reg2-wording) | requirement | REG-4 | Given the owner's REG-2 wording approved in the operation session on 2026-11-10, when the Regression page is read, then REG-2 keeps it as its first revision r1, dated 2026-11-10. | PASS 2026-11-19 |
| [local-row-env](Tests#t-local-row-env) | requirement | REG-4 | Given the REG-4 cases of test-summary.sh, when it runs once, then it prints every PASS line the 20 merged rows checked and no FAIL line. | PASS 2026-11-20 |
| [tests-page-stale](Tests#t-tests-page-stale) | requirement | REG-4 | Given REG-4, when test-docs-format.sh runs its 2 cases, then each passes: it is reported stale with its first differing line; each result links its Actions run, or that day's C. | PASS 2026-11-19 |
| [runs-sha](Tests#t-runs-sha) | requirement | REG-4 | Given REG-4, when test-runs-column.sh runs its 6 cases, then each passes: its run cell is empty; its run cell is the Actions run URL; the run cell is empty; every row has 4 columns and old rows have an empty; its run cell is unchanged; the run files are identical. | PASS 2026-11-10 |
| [reg-same-env](Tests#t-reg-same-env) | requirement | REG-4 | Given the same test, when it runs locally, in the loop or in GitHub Actions, then it gets the same environment from the same command. | PASS 2026-11-12 |
| [tiers-unmapped-qa-pr](Tests#t-tiers-unmapped-qa-pr) | requirement | REG-4 | Given REG-4, when test-tiers.sh runs its 6 cases, then each passes: only the rows that reach it, name it or run the ru; the rows that name the file and the runners run wi; it is FULL (no merge-base with <base>) and every r; the next lane reuses it and reruns only its failur; its LANE line ends with rows: S selected (A affect; only that kind's rows run. | PASS 2026-11-10 |
| [workflow-kind-shown](Tests#t-workflow-kind-shown) | requirement | REG-4 | Given REG-4, when test-workflow-kind.sh runs its 3 cases, then each passes: it is accepted and shown as kind workflow, after t; only that kind's rows are listed; each prints the same grouped lines. | PASS 2026-11-10 |
| [defect-owed-branch-proved](Tests#t-defect-owed-branch-proved) | requirement | REG-4 | Given an old defect row for an issue proved before the goal, when the goal that fixes that issue runs goal.py pr, then the pull request is refused until the branch adds its own row seen failing. | PASS 2026-11-10 |
| [flaky-marked](Tests#t-flaky-marked) | requirement | REG-4 | Given REG-4, when test-flaky.sh runs its 2 cases, then each passes: each run prints the FLAKY line with the raw result; no FLAKY line is printed and no flag is set. | PASS 2026-11-10 |
| [ci-target-input](Tests#t-ci-target-input) | requirement | REG-4 | Given REG-4, when test-ci-target.sh runs its 3 cases, then each passes: the yml has an optional target input and only that; it fails with the REFUSED (BAD_TARGET) line and ex; the scheduled run with no target runs every row an. | PASS 2026-11-10 |
| [merge-guard-base-head](Tests#t-merge-guard-base-head) | requirement | REG-4 | Given REG-4, when test-merge-guard.sh runs its 5 cases, then each passes: merge.py refuses with its fix, and a move elsewher; it notes it and goes on instead of refusing HEAD_M; it refuses HEAD_MOVED; it refuses HEAD_MOVED; it refuses HEAD_MOVED. | PASS 2026-11-11 |
| [release-lists-fixes](Tests#t-release-lists-fixes) | requirement | REG-4 | Given a goal that proved a defect row linked to an issue, when its release is cut, then the CHANGELOG and the release notes list the issue with its test. | PASS 2026-11-12 |
| [reopened-shows-failing](Tests#t-reopened-shows-failing) | requirement | REG-4 | Given a defect row whose issue was closed and then reopened, when tests are listed, then it shows failing (issue reopened) until the issue closes or a later run passes. | PASS 2026-11-11 |
| [lane-ports-tmpdir](Tests#t-lane-ports-tmpdir) | requirement | REG-4 | Given two lanes running at once, when their rows run, then each has its own leased port base and TMPDIR, and with all leases held a lane says so. | PASS 2026-11-16 FLAKY |
| [lane-messages-table](Tests#t-lane-messages-table) | requirement | REG-4 | Given every message code a lane, the runner or merge.py prints, when the reference is read, then each code has a row with its exit and what to do. | PASS 2026-11-11 |
| [merge-reach-fail-closed](Tests#t-merge-reach-fail-closed) | requirement | REG-4 | Given REG-4, when test-merge-guard.sh runs its 4 cases, then each passes: it refuses BASE_MOVED rather than merging unchecke; it refuses BASE_MOVED; no root runner is reached, so a release commit doe; it refuses BASE_MOVED instead of merging unchecked. | PASS 2026-11-11 |
| [goal-levels-nightly](Tests#t-goal-levels-nightly) | requirement | REG-4 | Given goal_levels nightly, when a goal lane plans, then it selects the nightly rows a change reaches as well as land rows. | PASS 2026-11-11 |
| [lane-tmpdir-outside-repo](Tests#t-lane-tmpdir-outside-repo) | requirement | REG-4 | Given REG-4, when test-lane-tmpdir.sh runs its 2 cases, then each passes: it passes, because the lane's TMPDIR is outside an; each has its own loop-lane folder under the system. | not run |
| [lanes-abs-not-walked](Tests#t-lanes-abs-not-walked) | requirement | REG-4 | Given the REG-4 cases of test-lanes-abs-path.sh, when it runs once, then it prints every PASS line the 3 merged rows checked and no FAIL line. | PASS 2026-11-14 |
| [reg10-owed-waits](Tests#t-reg10-owed-waits) | requirement | REG-4 | Given the REG-9 cases of test-owed.sh, when it runs once, then it prints every PASS line the 4 merged rows checked and no FAIL line. | not run |
| [backlog-renames-old](Tests#t-backlog-renames-old) | requirement | REG-4 | Given an old milestone named Backlog, when the Backlog milestones are made with --live, then it is renamed Backlog: Other with its number kept, none is made beside it, and a dry run only says it would. | not run |
| [mac-rows-skip-77](Tests#t-mac-rows-skip-77) | requirement | REG-4 | Given the macOS-only local-schedule toy, when it runs on a host that is not macOS, then it exits 77 with its reason, so its rows are SKIPPED and open no issue. | PASS 2026-11-13 |
| [machine-local-owed](Tests#t-machine-local-owed) | requirement | REG-4 | Given REG-4, when test-machine-local.py runs its 2 cases, then each passes: it reads PENDING not UNPROVEN, a to-do issue is pl; it reads PENDING and no longer blocks as UNPROVEN. | not run |
| [list-link-ids](Tests#t-list-link-ids) | requirement | REG-4 | Given a feature page whose PRD lives at a link, when tests.py list runs, then the requirement ids come from that PRD. | PASS 2026-11-13 |
| [tests-own-folder](Tests#t-tests-own-folder) | requirement | REG-4 | Given the regression skill, when tests.py reads a link-form page's ids, then it imports nothing outside its own folder. | PASS 2026-11-13 |
| [skill-workflow-in-references](Tests#t-skill-workflow-in-references) | requirement | REG-4 | Given the regression skill's workflow command, when SKILL.md and its references folder are read, then the nightly job's text sits in references/commands.md, SKILL.md points to it, and SKILL.md is under 150 lines. | PASS 2026-11-14 |
| [scripts-c-regression-under-19000](Tests#t-scripts-c-regression-under-19000) | requirement | REG-4 | Given the workflow-regression scripts, when their LF sizes are measured, then a WARN line names each over 19,000 and each fails only over 20,480 (GRD-20; TD482: aligned to approved GRD-20); a 20,481-byte fixture fails and a 19,500-byte one only warns. | not run |
| [prd-copy-rows-list](Tests#t-prd-copy-rows-list) | requirement | REG-4 | Given a page with a PRD source and a copy in .loop/prd and no block yet, when tests.py list runs with no reader, then it groups the page's rows under the page, not under Other. | not run |
| [config-lane-duplicate-key](Tests#t-config-lane-duplicate-key) | requirement | REG-4 | Given the REG-4 cases of test-config-lane.py, when it runs once, then it prints every PASS line the 4 merged rows checked and no FAIL line. | PASS 2026-11-15 |
| [private-checks-classify](Tests#t-private-checks-classify) | requirement | REG-4 | Given a private repo's required checks, when they are classified, then a regression-only job, plain script jobs and a third-party-action job are told apart (#4537). | not run |
| [toys-no-leak-schedule](Tests#t-toys-no-leak-schedule) | requirement | REG-4 | Given REG-4, when test-home-guard.py runs its 3 cases, then each passes: the home guard fails it with a LEAK line, while th; it reports no LEAK (#4760); it still reports the LEAK (#4760). | not run |
| [toys-no-leak-lane-pool](Tests#t-toys-no-leak-lane-pool) | requirement | REG-4 | Given a toy that takes a lane port lease and counter lock as the CI runner's four LEAK rows did, when it runs under a fresh home, then ~/.workflow-loop stays empty because the harness points LOOP_LANES_DIR at a temp pool, and a toy aimed at the real lanes/ is still caught. | not run |
| [budget-order-first](Tests#t-budget-order-first) | requirement | REG-4 | Given a toy diff that changes one toy, when a shard's budget fits a few rows, then that toy's row runs first, where before it was LEFT. | not run |
| [workflow-goal-to-release](Tests#t-workflow-goal-to-release) | workflow | REG-4 | Given a toy goal that fixes an issue, when it runs from goal.py new through its flow, its defect row seen failing, goal.py pr, merge.py and the automatic release, then the published release note and the CHANGELOG list Fixes #N with its defect test. | PASS 2026-11-10 |
| [toy-no-leftovers](Tests#t-toy-no-leftovers) | defect | [#100](https://github.com/jcl2018/agent-workflow-template/issues/100) closed (2026-11-11) | Given a toy test that starts stand-in agents, when it passes, fails, is interrupted or its pipe closes, then no process it started is left running. | PASS 2026-11-12 |
| [summary-only-real-rows](Tests#t-summary-only-real-rows) | defect | [#92](https://github.com/jcl2018/agent-workflow-template/issues/92) closed (2026-11-10) | Given a row that writes to the run summary, env or outputs like a toy test, when the GitHub run runs it, then nothing it writes reaches the real summary, env or outputs. | PASS 2026-11-10 |
| [docs-milestone-line-issue-130](Tests#t-docs-milestone-line-issue-130) | defect | [#130](https://github.com/jcl2018/agent-workflow-template/issues/130) closed (2026-11-11) | Given a page whose Milestone line names a milestone with another title, when the audit runs, then it reports no missing milestone. | PASS 2026-11-10 |
| [port-base-windows](Tests#t-port-base-windows) | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | Given native Windows Python, when a lane leases its ports, then lanekit.port_base() and slots.port_base() return a port base instead of raising AttributeError. | not run |
| [tests-links-workflow-3839](Tests#t-tests-links-workflow-3839) | defect | [#3839](https://github.com/jcl2018/agent-workflow-template/issues/3839) closed (2026-11-14) | Given an automation entry that runs the regression routine from another workflow file, when the Tests page is rendered, then its CI links name that file, and regression.yml only when none is set (issue 3839). | PASS 2026-11-14 |
| [lane-fail-text](Tests#t-lane-fail-text) | defect | 3911 | Given a failing row that ends in grep -q, when a lane runs it, then the lane shows the row's own text, not a bare FAIL. | not run |
| [owed-close](Tests#t-owed-close) | defect | 3907 | Given an owed red proof with a to-do issue, when the real red proof is recorded live, then that issue is closed and the record clears. | not run |
| [toys-set-userprofile](Tests#t-toys-set-userprofile) | defect | [#4393](https://github.com/jcl2018/agent-workflow-template/issues/4393) closed (2026-11-15) | Given the toy tests, when one sets HOME, then it also sets USERPROFILE, so Python's expanduser on Windows stays inside the toy. | not run |
