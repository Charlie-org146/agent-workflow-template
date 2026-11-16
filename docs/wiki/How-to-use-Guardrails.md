<!-- workflow-docs -->
# How to use Guardrails

## What it's for

Lists every guardrail the template has or needs, each with what it protects against, its owner, its setting and the health check that must prove it is on, including the memory floor before a goal starts (owner records o1, o3).

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Show me every guardrail" | You get the Guardrails page: each guardrail with what it protects against, the feature that owns it, its setting, and whether its Tests row says it is enforced. |
| "Which guardrail settings are there?" | The settings reference lists each setting with its home, default and meaning: token_budget, step_budget_minutes, test_budget_minutes, goal_lane_minutes and silent_minutes among them (time_budget_minutes is not listed yet). |
| "Check the budgets" | Health's performance group runs: it warns on any of the last 10 finished goals over its time or token budget, a goal's test lane over goal_lane_minutes, and a full suite over 30 minutes. |
| "Which guardrails aren't enforced yet?" | Each guardrail whose Tests row reads not enforced is listed with the feature that owns the missing part. |
| "Will machine setup write my address into a repo?" | No: `machine.py apply` refuses a routine or item holding an address or home path, names the line and kind, and writes nothing. |

## URLs and deployments

- Wiki: [Guardrails](https://github.com/jcl2018/agent-workflow-template/wiki/Guardrails)
- Milestone: [Guardrails](https://github.com/jcl2018/agent-workflow-template/milestone/11)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Guardrails](Guardrails)
- Backlog: [Backlog: Guardrails](https://github.com/jcl2018/agent-workflow-template/milestones)
