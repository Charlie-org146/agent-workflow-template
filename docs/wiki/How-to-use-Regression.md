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
| (a test shows ENV) | Windows could not start it under low memory (exit 0xC0000142 and like codes): it is not a failure, so rerun it when memory allows. |

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
