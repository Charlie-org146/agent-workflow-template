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

- REG-4: When tests run. Example, from the lanes-reuse test: given a first run on unchanged content, when a second run happens, then it reuses the first and runs no test. Also (was REG-1): Three kinds of tests. Example, from the refused-unmet test: given a criterion with no test, when a release is cut, then it is refused.

### Skill: workflow-regression
- **Say:** "Add a test for DEL-1 that runs the delivery toy suite"
- **Command:** `/workflow-regression add ID --level land --command "cmd" --goal DEL-1`

### Command: regression.py
- **Command:** `python3 skills/workflow-regression/scripts/regression.py run ID` (also `add`, `red`, `sync`)
- **Dry run:** a run without `--live` prints `WOULD` lines for the issues it would open or close.
- **Reads:** `.loop/regression.tsv`, the rows' commands and `.loop/regression-limits.tsv`.
- **Writes:** `.loop/regression-runs.tsv`; with `--live`, one GitHub issue per failing row.
- **Exit codes:** 0 when every selected row passed; nonzero when one failed.
- **Run order:** inside a time budget, selected rows run closest to the change first: rows that name a changed file, then rows whose requirement is in the diff, then the rest, shortest first. Rows past the budget are left to the full run.
- **Row limits:** every row runs under the run's row limit (300 seconds in a pull-request run). `.loop/regression-limits.tsv` lists the owner's exceptions: a number gives one row its own limit in seconds, and the word `nightly` keeps a nightly row out of the pull-request shards while the nightly run still runs it. Each entry has an approved line in `dev/toy/approved-row-changes.tsv`.

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

The land tests also run in GitHub Actions on the workflow's schedule (every 4 hours, `17 */4 * * *`) once `Write the GitHub workflow` has been merged; a failing test keeps one open issue. The job that runs the tests checks out the full history, so a test that compares a past merge can run there.

## Runbooks

The scheduled regression routine's Runbook lives in the [Regression](Regression) page, where the docs check keeps it in step with the routine.

## Links

- PRD page: [Regression](Regression)
- Backlog: [Backlog: Regression](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept fast-3min@d0a4c4b38 -->

Before a push, run `python3 skills/workflow-regression/scripts/slots.py slots`: `SLOTS used/cap` counts open PRs with any check not COMPLETED. Exit 1 means full, 2 could not count; `.loop/config.json` key `check_slots` defaults to 2.
