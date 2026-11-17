<!-- workflow-docs -->
# How to use Health

## What it's for

Checks the repo with fixed rules and a full reviewer, and files every finding as an issue tagged with its group and its feature (Other when none), a defect or a backlog item on its feature's Backlog milestone (an old Backlog milestone becomes Backlog: Other);.

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "How healthy is this repo?" | You get the formal report: one table of every finding by feature (feature, group, rule, severity, finding, issue), every rule by group, each problem with its fix, the tests, and one verdict. |
| "Check only the docs health" | The same report for that one group. |
| "What would you file?" | Each issue it would open, update, close or reopen is listed; nothing is written. |
| "File the docs findings" | Only that group's findings become issues, each tagged with its group and its feature (Other when none), and the table is printed again naming each issue. |
| "Judge the repo" | The report, plus suggestions on requirement wording, test strength and speed, with ranked next steps; the verdict doesn't change. |
| "Is this machine set up like my other one?" | The Adoption group's machine rule runs `machine.py check` and lists each gap as one WARN with its one-line fix. |

Each requirement and how it is delivered:

- HLT-2: The rules. Example, from the size-fail test: given a script over 20 KB, when health runs, then it is a FAIL with a fix.
- HLT-3: Formal report with one findings table. Example, from the health-findings-table test: given a health run with findings from at least three groups, when the report prints, then findings are one table with feature, group, rule, severity, finding and issue columns, every row naming a feature page or Other, and the digest shows the same table. Another example, from the unread-not-green test: given a health rule that cannot be read, when health runs, then it is never shown green.
- HLT-4: Findings become issues tagged with their group and their feature. Example, from the health-feature-always test: given findings filed by health.py file, when issues are created or updated, then each carries its feature label whatever feature_labels says, and a finding with no feature is filed under Other. Another example
, from the no-token-would test: given no token and no --live flag, when health previews its findings, then it prints only WOULD lines and writes nothing.
- HLT-5: Repo review. Example, from the judge-section-format test: given the judge, when it runs, then it prints its three reviews in a section marked as suggestions.
- HLT-6: Health keeps itself honest and the repo lean. Example, from the hlt6-controls-fire test: given every health rule, when health check runs its controls, then each rule's negative control makes it fire.
- HLT-8: Triage. Example, from the hlt8-triage test: given open health findings, when triage runs, then it lists them per feature by kind, count and age, and a closed batch carries the owner's words and is not refiled until its evidence changes.

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

<!-- kept health-feature-table@b869bb8a -->
