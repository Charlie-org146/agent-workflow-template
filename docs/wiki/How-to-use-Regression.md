<!-- workflow-docs -->
# How to use Regression

## What it's for

Keeps every requirement and defect tied to a test that runs, and shows the results, including red proof recorded from another runner or owed to another machine, without blocking a goal.

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

Each requirement and how it is delivered:

- REG-1: Three kinds of tests. Example, from the refused-unmet test: given a criterion with no test, when a release is cut, then it is refused.
- REG-2: Test format. Example, from the unproven-blocks test: given a test never seen failing, when the run happens, then the run is blocked.
- REG-3: One command, three places. Example, from the workflow-same-as-run test: given the same tests, when the workflow runs and regression.py runs locally, then both end the same way and open the same issues.
- REG-4: When tests run. Example, from the lanes-reuse test: given a first run on unchanged content, when a second run happens, then it reuses the first and runs no test.
- REG-5: Failures go to GitHub. Example, from the known-no-block test: given a known failure, when the run happens, then it does not block the run or open an issue.
- REG-6: Every fixed issue leaves a test. Example, from the release-lists-fixes test: given a goal that proved a defect row linked to an issue, when its release is cut, then the CHANGELOG and the release notes list the issue with its test.

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
