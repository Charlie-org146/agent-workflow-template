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

Each requirement and how it is delivered:

- AUT-1: Routines run where they can run fully. Example, from the ci-summary test: given the nightly run, when it ends, then it writes a results table to the job summary.
- AUT-2: Regression every few hours. Example, from the aut-defect-issue test: given a failing test, when the scheduled regression runs, then one issue labelled defect opens, naming the test, the feature and the requirement it guards.
- AUT-3: Health every few hours. Example, from the aut-email-file test: given health findings, when the scheduled health run files them, then each is tagged with its group on no milestone (and with its feature when feature_labels is on), no open issue is duplicated, and an issue the owner put on a milestone stays.
- AUT-4: A digest by email. Example, from the aut-digest-create test: given no digest issue yet, when the first round ends, then the Automation digest issue is created and pinned.
- AUT-8: Every routine has a runbook an agent follows exactly. Example, from the runbook-repo test: given this repo's Health and Regression pages, when their Runbook sections are read, then each routine in the registry has every field, says a full run is live, and names a fixture or dry run as forbidden.
- AUT-9: Every routine declares what it may do, in its repo. Example, from the perms-undeclared test: given a routine in the registry with no rows in .loop/permissions.tsv, when permissions.py check runs, then it prints UNDECLARED and exits 1.

## URLs and deployments

- Wiki: [Automation](https://github.com/jcl2018/agent-workflow-template/wiki/Automation)
- Milestone: [Automation](https://github.com/jcl2018/agent-workflow-template/milestone/10)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Automations and schedules

Regression runs every 4 hours in GitHub Actions for a public repo, or on your Mac; health runs every 4 hours on your always-on machine and never in Actions. `health_cron` in `.loop/config.json` changes the health schedule, and one digest per round is posted to the pinned digest issue. Each routine's Runbook is kept in the repo, where its one-line scheduled prompt points.

## Links

- PRD page: [Automation](Automation)
- Backlog: [Backlog: Automation](https://github.com/jcl2018/agent-workflow-template/milestones)
