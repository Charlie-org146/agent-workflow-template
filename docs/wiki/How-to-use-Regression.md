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

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Run the land tests" | Every land test runs; each failing test gets one GitHub issue, and a test that passes again closes its issue. |
| "Add a test for DEL-1 that runs the delivery toy suite" | A test row is added and tied to that requirement. |
| "Prove the cache test can fail" | The test runs against deliberately broken code, and is marked seen failing or flagged as proving nothing. |
| "What's untested?" | Requirements with no test, draft tests and tests never seen failing are listed. |
| "List every test" | Every test, grouped by feature, with its kind, what it guards, what it checks and its last result. |
| "Write the GitHub workflow" | The GitHub Actions run is written, so the same tests run there on its schedule. |
| (a test shows ENV) | Windows could not start it under low memory (exit 0xC0000142 and like codes), even on the lane's one rerun of it: it is not a failure, so rerun it when memory allows. |

Each requirement and how it is delivered:

- REG-1: Three kinds of tests. Example, from the refused-unmet test: given a criterion with no test, when a release is cut, then it is refused.
- REG-2: Test format. Example, from the unproven-blocks test: given a test never seen failing, when the run happens, then the run is blocked.
- REG-3: One command, three places. Example, from the workflow-same-as-run test: given the same tests, when the workflow runs and regression.py runs locally, then both end the same way and open the same issues.
- REG-4: When tests run. Example, from the lanes-reuse test: given a first run on unchanged content, when a second run happens, then it reuses the first and runs no test.
- REG-5: Failures go to GitHub. Example, from the known-no-block test: given a known failure, when the run happens, then it does not block the run or open an issue.
- REG-6: Every fixed issue leaves a test. Example, from the release-lists-fixes test: given a goal that proved a defect row linked to an issue, when its release is cut, then the CHANGELOG and the release notes list the issue with its test.

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

The land tests also run in GitHub Actions on the workflow's schedule (every 4 hours) once `Write the GitHub workflow` has been merged; a failing test keeps one open issue.

## Runbooks

The scheduled regression routine's Runbook lives in the [Regression](Regression) page, where the docs check keeps it in step with the routine.

## Links

- PRD page: [Regression](Regression)
- Backlog: [Backlog: Regression](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept how-to-use-docs@7286f62f -->
