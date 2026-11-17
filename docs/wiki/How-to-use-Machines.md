<!-- workflow-docs -->
# How to use Machines

## What it's for

Brings a second Mac or Windows machine to the same working setup as the one you run on, from a git clone and one command.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `machine.py` | Command | Plans, applies and checks a second machine's setup. | `python3 dev/machine.py` (a dry run), then `machine.py apply --repo <your repo>`. |
| `machines.py` | Command | Hands a goal to the other machine, holds the cross-machine merge turn and publishes the SNAPSHOT a check-in draws its Machine lines from. | `machines.py handover SLUG --to MACHINE`, then on the other machine `machines.py take SLUG`. |
| `mailbox.py` | Command | Reads the owner's reply to a mailed question and records it as the owner's words. | `mailbox.py reply QID "1 recommended"`; `mailbox.py pending` lists open questions. |
| `setup.py desk` | Command | Lists, runs once and checks every setup step that needs a desk. | `setup.py desk list`, `desk run`, `desk done STEP`, `desk check`. |
| health-regression | Scheduled routine | The scheduled health and regression round a second machine runs every 4 hours. | `machine.py apply` registers it; its Runbook is below. |

## How to reach or run it

Say these to the agent; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Set up a second machine" | New machine, in order: git clone the template and link the skills, `machine.py` (a dry run), `machine.py apply --repo <your repo>`, the owner steps it prints, then `machine.py check` prints no gap. |
| "Check this machine against my setup" | `machine.py check` lists each gap with a one-line fix and writes nothing; health's Adoption group shows the same list. |
| "Move a goal to the other machine" | `machines.py handover SLUG --to MACHINE` pushes the branch and the record and marks it moved here; `machines.py take SLUG` on that machine binds a worker. |
| "Answer by email" | Reply "1", "1 recommended" or "approve"; the operation session runs `mailbox.py reply QID TEXT`, which records your words with `--source owner`. A risky step needs your own words. |
| "Make this machine phone-ready" | `setup.py desk run` prints each desk-only step once; `desk done STEP` records it; `desk check` prints DESK OK when nothing is left. |
| "Record that I registered a task" | `machine.py record-task NAME MODE` notes the permission mode you chose in the app; a missing or prompting mode is a gap. |

Each requirement and how it is delivered:

- MCH-1: A second machine reaches this one's setup from a git clone and one command. Example, from the machine-apply-installs test: given a clone and a toy home, when machine plan runs, then it writes nothing, and when apply runs, then it links the skills and writes the private-names file, the mailer, the hooks and the tasks.

- MCH-2: Goals move between machines, with one owner and one merge order. Example, from the machines-handover test: given a goal whose worker can't start, when it is handed over, then the other machine binds a worker on the pushed branch and the old record shows it moved.
- MCH-3: One email stream, answered by reply. Example, from the mailbox-reply-owner test: given a mailed question, when the owner replies "1 recommended", then it is recorded as owner words with source owner and sent to the worker.
- MCH-4: Phone-first: starting a worker never needs the desktop app. Example, from the desk-check-ok test: given every desk step done, when desk check runs, then it prints DESK OK.

### Command: machines.py
- **Command:** `python3 skills/workflow-monitoring/scripts/machines.py handover SLUG --to MACHINE | take SLUG | snapshot [--publish] | turn`
- **Dry run:** `snapshot` and `turn` only read; `handover` and `take` refuse rather than move a goal that is running, done or already taken.
- **Reads:** the goal's record and branch, and three kinds of ref on origin (handover, merge turn, snapshot).
- **Writes:** `handover` pushes the branch and a record ref and marks the old record moved; `take` writes the new record and worktree and starts a worker.
- **Exit codes:** 0 when it moved or showed; nonzero with a `REFUSED:` line, nothing moved.

### Command: mailbox.py
- **Command:** `python3 skills/workflow-monitoring/scripts/mailbox.py reply QID TEXT | pending`
- **Dry run:** `pending` lists open questions and writes nothing.
- **Reads:** the mailed questions kept beside the repo's loop records; it never reads mail or a secret.
- **Writes:** `reply` records the owner's words through `operate.py send --source owner` (or `sessions.py owner-words`) and drops the question.
- **Exit codes:** 0 recorded; 2 refused (unknown question, bad option, or a risky step answered with a bare number or approve).

### Command: setup.py desk
- **Command:** `python3 skills/workflow-setup/scripts/setup.py desk list | run | done STEP... | check [--repo DIR]`
- **Dry run:** `list` and `check` write nothing; `run` only records which steps it listed.
- **Reads:** whether the private-names file, mail.env and the Codex login file exist (never their contents), and `.loop/config.json`.
- **Writes:** one machine-local record of step names and times; nothing in the repo.
- **Exit codes:** 0 for list, run and done; `check` is 1 with a `GAP` line per open step, 0 with DESK OK.

### Command: machine.py
- **Command:** `python3 dev/machine.py [apply --repo REPO | check | record-task NAME MODE]`
- **Dry run:** `machine.py` with no `apply` is a dry run; `check` lists each gap and writes nothing.
- **Reads:** this machine's skills links, scheduled tasks and the followed repos.
- **Writes:** `apply` links the skills and registers one scheduled task per adopted repo; `record-task` notes a permission mode.
- **Exit codes:** 0 when the machine matches; nonzero when `check` finds a gap, each named with its fix.

## URLs and deployments

- Wiki: [Machines](https://github.com/jcl2018/agent-workflow-template/wiki/Machines)
- Milestone: [Machines](https://github.com/jcl2018/agent-workflow-template/milestone/23)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Automations and schedules

`machine.py apply` registers one scheduled task per adopted repo, named `<repo>-health-regression`, every 4 hours with staggered starts; it replaces local-schedule's launch agent so no repo has two 4-hourly runs.

## Runbooks

### health-regression

- **Serves:** MCH-1: a second machine runs health and the full regression every 4 hours on every adopted repo, public or private.
- **Schedule:** every 4 hours, with starts staggered per repo; one scheduled task per adopted repo, named `<repo>-health-regression`.
- **Steps:** `machine.py apply` registers the task; each run reads its prompt file in the loop folder and runs health, then the full regression.
- **Full run:** a real run, never a demo; it replaces local-schedule's launch agent so no repo has two 4-hourly runs.
- **Check:** `machine.py check` lists each gap with a one-line fix; run the fix, then check again until no gap is listed.
- **Output:** one `GAP` line per gap with its fix, and nothing when the machine matches; a failing row keeps its one issue.
- **Never:** write a secret, a private name or a home path into a repo file or a routine; `apply` refuses them.

## Links

- PRD page: [Machines](Machines)
- Backlog: [Backlog: Machines](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept full-auto-all@08ab9232 -->
