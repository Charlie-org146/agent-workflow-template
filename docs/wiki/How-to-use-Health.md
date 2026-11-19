<!-- workflow-docs -->
# How to use Health

## What it's for

Checks the repo with fixed rules and a full reviewer, and files every finding as an issue tagged with its group and its feature (Other when none), a defect or a backlog item on its feature's Backlog milestone (an old Backlog milestone becomes Backlog: Other);.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-health` | Skill | Checks the repo against its own PRDs with fixed rules. | Say "How healthy is this repo?"; you get the formal report and one verdict. |
| `health.py` | Command | Checks the repo with twelve fixed rule groups and prints one verdict. | `python3 skills/workflow-health/scripts/health.py check`. |
| `automation.py` | Command | Posts the digest comment each round and installs the local schedule. | `python3 skills/workflow-health/scripts/automation.py digest`. |
| `mail.py` | Command | Mails the owner the round's digest, at most once. | `python3 skills/workflow-health/scripts/mail.py send`. |
| health-round | Scheduled routine | The scheduled health round on the always-on machine. | Its Runbook is on the [Health](Health) page; start a round by hand with `health.py check`. |

### System diagram

```text
[Scheduled routine: health-round | the always-on machine] --starts the check on schedule--> [Command: health.py | the always-on machine]
[Skill: workflow-health | the agent session] --check, review, preview, file, triage--> [Command: health.py | the always-on machine]
[Command: health.py | the always-on machine] --twelve rule groups--> (one HEALTH verdict)
[Command: health.py | the always-on machine] --findings to the digest--> [Command: automation.py | the always-on machine]
[Command: automation.py | the always-on machine] --digest to the mailer--> [Command: mail.py | the always-on machine]
[Command: mail.py | the always-on machine] --at most once--> (the owner's inbox)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

**Reading the charts**

The charts in each skill's `references/` folder are read this way. Each chart shows a command's stages, with amber at each stop for the owner. Under it, `Status:` puts every stage in one
of three groups, `Stops for the owner:` names the stops, and `Proof:` says what the status rests on.

| Status | Means |
|---|---|
| Built and proven | A toy test passes on this stage, or a real run on this repo is on record |
| Built only | It exists, but no test exercises it and no real run is on record |
| Planned | Not built yet |

A toy test uses a throwaway repo and a stand-in for GitHub, so built and proven doesn't mean it has run on a real repo.
`Proof:` says when it hasn't. Real runs were read on 2026-11-06 from the run records of this repo and one other it
follows, plus their pull requests, releases and wikis. That second repo isn't named here. On this repo, eight real goals
reached a pull request, all at the level now called 1, and three publishes reached the wiki. The second repo ran ten
goals, including one real `cut` to a draft release. This repo has since had its own real `cut`, v0.1.1. Neither repo shows a regression workflow run in CI, a
or a batch with a real agent. Records older than these goals may be gone, so "not on record" doesn't mean it never happened.

**What is proven**

- "`report` left out queued goals that were ready to start. It now lists them." (FINDINGS.md)
- Toy tests cover goals, the board, docs, criteria, releases and regression, each under `dev/toy/`.
- Codex ran a level 0 toy goal from design to pull request with no failed try (FINDINGS.md).
- The regression workflow passes on GitHub. Its first run failed 2 rows, and both are fixed (FINDINGS.md).

**What is not proven**

- "Real repos differ from the toy: four-number versions, changelogs with bracket headings and an intro paragraph, tests
  outside `tests/`, a wiki with pages from another tool, and a pre-push hook that takes minutes." (FINDINGS.md)
- Several goals pushing at once can fail with a bare git error, and a plain re-push works; `pr` retries twice
  (FINDINGS.md).
- Some scripts are within a few hundred bytes of the 20 KB limit, so the next feature needs a new script
  (FINDINGS.md).
- "Codex's `workspace-write` sandbox blocks writes to `.git` and outside the workspace." (FINDINGS.md)

**Gaps for the owner**

- The timed check-in loop (`cadence`, then `watch --once` and `board` on each wait) has not fired on its timer. No
  finding or decision records a run of it, and its toy test uses fixtures.
- The skill flow has run for real only up to the idea step, which waited for the owner as it should (docs/ROADMAP.md).

| You say | What happens |
|---|---|
| "How healthy is this repo?" | You get the formal report: one table of every finding by feature (feature, group, rule, severity, finding, issue), every rule by group, each problem with its fix, the tests, and one verdict. |
| "Check only the docs health" | The same report for that one group. |
| "What would you file?" | Each issue it would open, update, close or reopen is listed; nothing is written. |
| "File the docs findings" | Only that group's findings become issues, each tagged with its group and its feature (Other when none), and the table is printed again naming each issue. |
| "Judge the repo" | The report, plus suggestions on requirement wording, test strength and speed, with ranked next steps; the verdict doesn't change. |
| "Is this machine set up like my other one?" | The Adoption group's machine rule runs `machine.py check` and lists each gap as one WARN with its one-line fix. |

The consistency group counts definitions in Requirements sections; How-to items refer to those definitions. Reworded savings about the same file keep the same issue subject.

Each requirement and how it is delivered:

- HLT-2: The rules. Example, from the size-fail test: given a script over 20 KB, when health runs, then it is a FAIL with a fix.
- HLT-4: Findings become issues tagged with their group and their feature. Example, from the health-feature-always test: given findings filed by health.py file, when issues are created or updated, then each carries its feature label whatever feature_labels says, and a finding with no feature is filed under Other. Another example
, from the no-token-would test: given no token and no --live flag, when health previews its findings, then it prints only WOULD lines and writes nothing.
- HLT-7: Checks, check-ins and rounds answer fast. Its budget and its limits for a scheduled round:
  - A round finishes within 45 minutes (the 30-minute regression budget of Regression REG-7 plus 15 for health and the digest, health starting when regression has finished, not at a fixed offset), and each report shows the round's wall time and its pass and fail counts, plus its Actions minutes when it ran in GitHub Actions, so I can slow the schedule if it costs too much.
- HLT-11: Health keeps the repo lean. Health flags an in-loop test run over its time budget, naming the slowest tests to move to the full suite, and flags stale worktrees and branches, printing the commands that remove them without running them. It warns on a script over 19,000 bytes and fails one at 20 KB. (no test yet)

### Skill: workflow-health
- **Say:** "How healthy is this repo?"
- **Command:** `/workflow-health check`

### Command: health.py
- **Command:** `python3 skills/workflow-health/scripts/health.py check [--group NAME]` (also `health.py review`, `health.py judge`, `health.py preview`, `health.py file`, `health.py triage`)
- **Dry run:** `health.py check` writes no file and calls no model; `preview` lists the issues `file` would write and writes nothing.
- **Reads:** the repo, its PRD pages, its tests and its issues (a check of every group reads the open health issues for the findings table's issue column; `--group` does not).
- **Writes:** `check` writes nothing; `file` and `triage` write and close GitHub issues.
- **Exit codes:** 0 when the verdict is green; 1 when a rule is FAIL or UNREAD.

### Command: automation.py
- **Command:** `python3 skills/workflow-health/scripts/automation.py digest [--owner L]`, or `skills/workflow-health/scripts/automation.py local status`, `local install` and `local tick --dry-run`
- **Dry run:** `automation.py local tick --dry-run` shows what a tick would run.
- **Reads:** the workflow files, `.loop/config.json` and the issues of the round.
- **Writes:** one comment on the pinned digest issue; `local install` writes the launch agent.
- **Exit codes:** 0 after it posts or prints; nonzero when an install is refused.

### Command: mail.py
- **Command:** `python3 skills/workflow-health/scripts/mail.py send`
- **Dry run:** none: `mail.py test` sends one fixed test mail through the configured sender.
- **Reads:** the digest comment and the sender's secrets, never printed.
- **Writes:** the digest comment's marker (`mailing`, then `mailed`).
- **Exit codes:** every outcome is one `MAIL:` line ending in a code; the codes are on the Automation page.

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

<!-- kept readme-principles-table4@24c3c984 -->
