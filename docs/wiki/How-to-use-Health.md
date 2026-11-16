<!-- workflow-docs -->
# How to use Health

## What it's for

Checks the repo with fixed rules and a full reviewer, and files every finding as an issue tagged with its group (and its feature, when feature_labels is on), a defect or a backlog item on its feature's Backlog milestone (an old Backlog milestone becomes Backlog: Other);.

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "How healthy is this repo?" | You get the formal report: every rule by group, each problem with its fix, the tests, and one verdict. |
| "Check only the docs health" | The same report for that one group. |
| "What would you file?" | Each issue it would open, update, close or reopen is listed; nothing is written. |
| "File the docs findings" | Only that group's findings become issues, each tagged with its group. |
| "Judge the repo" | The report, plus suggestions on requirement wording, test strength and speed, with ranked next steps; the verdict doesn't change. |

## URLs and deployments

- Wiki: [Health](https://github.com/jcl2018/agent-workflow-template/wiki/Health)
- Milestone: [Health](https://github.com/jcl2018/agent-workflow-template/milestone/4)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Automations and schedules

Scheduled health runs follow `health_cron` (every 4 hours by default) on your always-on machine; with the routine off they write nothing and say so.

## Runbooks

The scheduled health routine's Runbook lives in the [Health](Health) page, where the docs check keeps it in step with the routine.

## Links

- PRD page: [Health](Health)
- Backlog: [Backlog: Health](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept how-to-use-docs@02e7ddac -->
