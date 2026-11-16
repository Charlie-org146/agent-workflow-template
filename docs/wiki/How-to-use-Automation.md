<!-- workflow-docs -->
# How to use Automation

## What it's for

Runs health on your always-on machine (the Mac, or a Windows PC with `local register`;.

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Set up the scheduled routines" | The regression workflow is written to run every 4 hours in GitHub Actions (public repo), for you to merge; health runs every 4 hours on your Mac, never in Actions. |
| "Run health every 12 hours instead" | `health_cron` changes in `.loop/config.json` and your Mac's next round follows it; no workflow is written. |
| "Turn off the scheduled health run" | Scheduled health runs write nothing and say the routine is off; you can still start one by hand. |
| "Post the automation digest" | One comment on the pinned digest issue lists what ran, the new, still-open and fixed issues, and a request per open issue. |
| "Write the scheduled regression run again" | The regression workflow is rewritten from the current config, so its schedule matches. |

## URLs and deployments

- Wiki: [Automation](https://github.com/jcl2018/agent-workflow-template/wiki/Automation)
- Milestone: [Automation](https://github.com/jcl2018/agent-workflow-template/milestone/10)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Automations and schedules

Regression runs every 4 hours in GitHub Actions for a public repo, or on your Mac; health runs every 4 hours on your always-on machine and never in Actions. `health_cron` in `.loop/config.json` changes the health schedule, and one digest per round is posted to the pinned digest issue. Each routine's Runbook is kept in the repo, where its one-line scheduled prompt points.

## Links

- PRD page: [Automation](Automation)
- Backlog: [Backlog: Automation](https://github.com/jcl2018/agent-workflow-template/milestones)
