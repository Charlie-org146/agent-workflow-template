<!-- workflow-docs -->
# How to use Regression

## What it's for

Keeps every requirement and defect tied to a test that runs, and shows the results, including red proof recorded from another runner or owed to another machine, without blocking a goal.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-regression` | Skill | Keeps every requirement and defect tied to a test that runs. | Say "Run the land tests" or "What's untested?". |
| `regression.py` | Command | Adds, runs and proves the test rows. | `python3 skills/workflow-regression/scripts/regression.py run ID`. |
| `lanes_cli.py` | Command | Names the rows a change can affect. | `python3 skills/workflow-regression/scripts/lanes_cli.py affected PATH...`. |
| `.loop/regression.tsv` | API/file contract | The table of every test row. | `regression.py add` writes a row; `regression.py run` runs it. |
| regression-round | Scheduled routine | The scheduled regression round. | Its Runbook is on the [Regression](Regression) page; run the tests by hand with `regression.py run`. |

### System diagram

```text
[Command: regression.py | the repo checkout] --add writes a row--> [API/file contract: .loop/regression.tsv | the repo]
[Command: lanes_cli.py | the repo checkout] --names the rows a change can affect--> [API/file contract: .loop/regression.tsv | the repo]
[Scheduled routine: regression-round | GitHub Actions] --runs every row on schedule--> [Command: regression.py | the repo checkout]
[Skill: workflow-regression | the agent session] --add, red, run, sync--> [Command: regression.py | the repo checkout]
[Command: regression.py | the repo checkout] --files it--> (GitHub issue per failing row)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

Keep tests visible and enforced:

```text
/workflow-regression sync
/workflow-regression red <id> --break "<a command that breaks the code>"
/workflow-regression run land
/workflow-regression workflow
```

A row must be seen failing once before it counts. Known failures don't block, and each other failing row gets one issue.

| You say | What happens |
|---|---|
| "Run the land tests" | Every land test runs; each failing test gets one GitHub issue, and a test that passes again closes its issue. |
| "Add a test for DEL-1 that runs the delivery toy suite" | A test row is added and tied to that requirement. |
| "Prove the cache test can fail" | The test runs against deliberately broken code, and is marked seen failing or flagged as proving nothing. |
| "What's untested?" | Requirements with no test, draft tests and tests never seen failing are listed. |
| "List every test" | Every test, grouped by feature, with its kind, what it guards, what it checks and its last result. |
| "Write the GitHub workflow" | The GitHub Actions run is written, so the same tests run there on its schedule. |
| "Which tests does this change reach?" | The rows the change can affect are listed. Any change but one only to NO_EFFECT files such as VERSION or a goal file, a deleted file included, also reaches the root runners, on Windows as on Linux. An edit to `.loop/regression.tsv` or `.loop/regression-known.tsv` re-runs only the rows whose own line changed, plus the rows whose command or directly named script names `.loop/regression.tsv` and the rows that run tools on the repo's own files (TOP-DECISION 46, widened). A row that reads the table only through an unnamed helper isn't re-run on a table edit; the gate's full suite and the pull request's CI still run it. |
| (a test shows ENV) | Windows could not start it under low memory (exit 0xC0000142 and like codes), even on the lane's one rerun of it: it is not a failure, so rerun it when memory allows. |

Each requirement and how it is delivered:

- REG-1: Three kinds of tests. Example, from the refused-unmet test: given a criterion with no test, when a release is cut, then it is refused.
- REG-4: When tests run. Example, from the lanes-reuse test: given a first run on unchanged content, when a second run happens, then it reuses the first and runs no test.
- REG-7: Fast in the loop. Its budget and its limits, word for word from the page before the v2 rewrite:
  - Every in-loop test run (qa, ship and the pull-request lane) stays within a time budget, a setting that defaults to 15 minutes and can't be set lower. A run that would go past it, including changes the row picker can't map such as a deleted file, runs the affected tier that fits and leaves the rest to the scheduled full suite, saying what it left; the loop never runs the full suite. The scheduled full suite finishes in under 30 minutes: the GitHub job's time limit is that same 30 minutes and the suite is sharded over several jobs so each fits it, and health flags a suite that doesn't.
  - The work before a lane's first test row (preparing, planning and waiting for a slot) has its own budget, a setting that defaults to 15 minutes and can't be set lower; a lane whose preparation reaches it stops, says which part ran long, and the goal can rerun it instead of starting over.
  - Planning computes each row's closure once per lane, not once per row, and keeps it per branch, keyed by HEAD, the row file, the planner code, `LANES_WIDE` and the loop's uncommitted bookkeeping files; a dirty tree never uses it, a plan that read an ignored file, or one outside the repo through a symlink, is not saved (a file created or ignored later is outside the key: remove the plans folder or set `LANES_NO_CACHE=1`), and `LANES_NO_CACHE=1` turns it off.
  - Issue bodies and comments are passed to gh in a file (`--body-file`), so a long failure output never meets the Windows command-line limit.
  - A lane about to run rows waits while free memory is below `min_free_memory_gb` (default 4), and gives up after four times the lane's time limit; a lane already running is never stopped.

### Skill: workflow-regression
- **Say:** "Add a test for DEL-1 that runs the delivery toy suite"
- **Command:** `/workflow-regression add ID --level land --command "cmd" --goal DEL-1`

### Command: regression.py
- **Command:** `python3 skills/workflow-regression/scripts/regression.py run ID` (also `add`, `red`, `sync`)
- **Dry run:** a run without `--live` prints `WOULD` lines for the issues it would open or close.
- **Reads:** `.loop/regression.tsv` and the rows' commands.
- **Writes:** `.loop/regression-runs.tsv`; with `--live`, one GitHub issue per failing row.
- **Exit codes:** 0 when every selected row passed; nonzero when one failed.

### Command: lanes_cli.py
- **Command:** `python3 skills/workflow-regression/scripts/lanes_cli.py affected [--level land|nightly|all] PATH...`
- **Dry run:** none needed: it only reads.
- **Reads:** the row table and each test script's `# reads:` header.
- **Writes:** nothing.
- **Exit codes:** 0 after it prints `AFFECTED n of m rows`, with `ALWAYS`, `UNMAPPED` and `DELETED` lines where they apply.

### API/file contract: .loop/regression.tsv
- **Path:** `.loop/regression.tsv`
- **Fields:** id, level, command, goal, seen_red, description, category and link, tab separated.
- **Example:** `reg2-wording`, level `land`, a `grep` command and the goal `REG-2`.
- **Writer:** `regression.py add`, or by hand.
- **Reader:** `regression.py run`, the lane, the docs Tests tables and health.

## URLs and deployments

- Wiki: [Regression](https://github.com/jcl2018/agent-workflow-template/wiki/Regression)
- Milestone: [Regression](https://github.com/jcl2018/agent-workflow-template/milestone/7)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Automations and schedules

The land tests also run in GitHub Actions on the workflow's schedule (every 4 hours, `17 */4 * * *`) once `Write the GitHub workflow` has been merged; a failing test keeps one open issue.

## Runbooks

The scheduled regression routine's Runbook lives in the [Regression](Regression) page, where the docs check keeps it in step with the routine.

## Links

- PRD page: [Regression](Regression)
- Backlog: [Backlog: Regression](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept go-head-main-reds@751300a25 -->
