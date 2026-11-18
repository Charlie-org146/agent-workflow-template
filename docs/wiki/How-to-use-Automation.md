<!-- workflow-docs -->
# How to use Automation

## What it's for

Runs health on your always-on machine (the Mac, or a Windows PC with `local register`;.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `automation.py` | Command | Posts the digest comment each round and installs the local schedule. | `python3 skills/workflow-health/scripts/automation.py digest`. |
| `mail.py` | Command | Mails the owner the round's digest, at most once. | `python3 skills/workflow-health/scripts/mail.py send`. |
| `.loop/config.json` | API/file contract | The schedule and digest settings. | Say "Run health every 12 hours instead"; it changes `health_cron`. |

### System diagram

```text
[API/file contract: .loop/config.json | the repo] --schedule and digest settings--> [Command: automation.py | the always-on machine]
[Command: automation.py | the always-on machine] --posts the digest each round--> (GitHub issue comment)
[Command: automation.py | the always-on machine] --hands over the digest--> [Command: mail.py | the always-on machine]
[Command: mail.py | the always-on machine] --mails it at most once--> (the owner's inbox)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Set up the scheduled routines" | The regression workflow is written to run every 4 hours in GitHub Actions (public repo), for you to merge; health runs every 4 hours on your Mac, never in Actions. |
| "Run health every 12 hours instead" | `health_cron` changes in `.loop/config.json` and your Mac's next round follows it; no workflow is written. |
| "Turn off the scheduled health run" | Scheduled health runs write nothing and say the routine is off; you can still start one by hand. |
| "Post the automation digest" | One comment on the pinned digest issue lists what ran, the health findings table (feature, group, rule, severity, finding, issue), the new, still-open and fixed issues per feature (Other when none), and a request per open issue. |

| "Write the scheduled regression run again" | The regression workflow is rewritten from the current config, so its schedule matches. |

Each requirement and how it is delivered:

- AUT-1: Routines run where they can run fully. Example, from the ci-summary test: given the nightly run, when it ends, then it writes a results table to the job summary.
- AUT-2: Regression on a schedule. Example, from the aut-defect-issue test: given a failing test, when the scheduled regression runs, then one issue labelled defect opens, naming the test, the feature and the requirement it guards.
- AUT-3: Health on a schedule. Example, from the aut-email-file test: given health findings, when the scheduled health run files them, then each is tagged with its group on no milestone (and with its feature when feature_labels is on), no open issue is duplicated, and an issue the owner put on a milestone stays.
- AUT-4: A digest by email. Example, from the aut-digest-create test: given no digest issue yet, when the first round ends, then the Automation digest issue is created and pinned.
- AUT-9: Every routine declares what it may do. Example, from the perms-undeclared test: given a routine in the registry with no rows in .loop/permissions.tsv, when permissions.py check runs, then it prints UNDECLARED and exits 1.
- AUT-7: Bounded cost. Its budget and its limits, word for word from the page before the v2 rewrite:
  - A round finishes within 45 minutes (the 30-minute regression budget of Regression REG-7 plus 15 for health and the digest, health starting when regression has finished, not at a fixed offset), and each report shows the round's wall time and its pass and fail counts, plus its Actions minutes when it ran in GitHub Actions, so I can slow the schedule if it costs too much.
- AUT-10: A private repo needs no Actions check to merge. Example: given a private repo whose rules require named checks and a pull-request lane that passed, when the lane posts, then it posts those names as commit statuses itself and no GitHub Actions check is needed to merge.

### Command: automation.py
- **Command:** `python3 skills/workflow-health/scripts/automation.py digest [--owner L]` or `local status`
- **Dry run:** `automation.py local tick --dry-run` shows what a tick would run.
- **Reads:** the workflow files, `.loop/config.json` and the issues of the round.
- **Writes:** one comment on the pinned digest issue; `local install` writes the launch agent.
- **Exit codes:** 0 after it posts or prints; nonzero when an install is refused.

### Command: mail.py
- **Command:** `python3 skills/workflow-health/scripts/mail.py send`
- **Dry run:** none: `mail.py test` sends one fixed test mail through the configured sender.
- **Reads:** the digest comment and the sender's secrets, never printed.
- **Writes:** the digest comment's marker (`mailing`, then `mailed`).
- **Exit codes:** every outcome is one `MAIL:` line ending in a code; the codes are below.

### API/file contract: .loop/config.json
- **Path:** `.loop/config.json`
- **Fields:** `health_cron`, `digest_owner`, `digest_mail` and the `automation` list.
- **Example:** `"digest_mail": "cloudflare"` picks the Cloudflare sender.
- **Writer:** workflow-setup writes the defaults; the owner edits a value.
- **Reader:** the scheduled rounds, the digest and the mail step.

## URLs and deployments

- Wiki: [Automation](https://github.com/jcl2018/agent-workflow-template/wiki/Automation)
- Milestone: [Automation](https://github.com/jcl2018/agent-workflow-template/milestone/10)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Automations and schedules

Regression runs every 4 hours in GitHub Actions for a public repo, or on your Mac; health runs every 4 hours on your always-on machine and never in Actions. `health_cron` in `.loop/config.json` changes the health schedule, and one digest per round is posted to the pinned digest issue. Each routine's Runbook is kept in the repo, where its one-line scheduled prompt points.

## Links

- PRD page: [Automation](Automation)
- Backlog: [Backlog: Automation](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept health-feature-table@b869bb8a -->
