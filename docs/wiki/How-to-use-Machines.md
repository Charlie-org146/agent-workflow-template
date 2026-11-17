<!-- workflow-docs -->
# How to use Machines

## What it's for

Brings a second Mac or Windows machine to the same working setup as the one you run on, from a git clone and one command.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `machine.py` | Command | Plans, applies and checks a second machine's setup. | `python3 dev/machine.py` (a dry run), then `machine.py apply --repo <your repo>`. |
| health-regression | Scheduled routine | The scheduled health and regression round a second machine runs every 4 hours. | `machine.py apply` registers it; its Runbook is below. |

## How to reach or run it

Say these to the agent; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Set up a second machine" | New machine, in order: git clone the template and link the skills, `machine.py` (a dry run), `machine.py apply --repo <your repo>`, the owner steps it prints, then `machine.py check` prints no gap. |
| "Check this machine against my setup" | `machine.py check` lists each gap with a one-line fix and writes nothing; health's Adoption group shows the same list. |
| "Back up or restore this machine" | `machine.py backup DIR` copies the restorable state to a folder outside every repo; `machine.py restore DIR` puts it back on a new machine or account. Secrets and private-names lists are never copied; both name them. |
| "Set up the operation session and peer link" | `machine.py apply --repo <your repo> [--peer NAME]` also writes the operation session's routine and task, its hooks and `peer.json`; then do the owner steps it prints. |
| "Record that I registered a task" | `machine.py record-task NAME MODE` notes the permission mode you chose in the app; a missing or prompting mode is a gap. |

Each requirement and how it is delivered:

- MCH-2: A new machine or account reaches a working operation session and its peer link from one command. Example, from the machine-operation-peer test: given a fresh clone and toy home, when machine apply runs, then the operation session, its tasks and the peer link exist and the output names only the owner-only items left.
- MCH-3: Backup and restore are commands. Example, from the machine-backup-restore test: given a set-up home, when backup and restore run, then restorable state moves to a new home and no secret or private-names list is copied.
- MCH-1: A second machine reaches this one's setup from a git clone and one command. Example, from the machine-apply-installs test: given a clone and a toy home, when machine plan runs, then it writes nothing, and when apply runs, then it links the skills and writes the private-names file, the mailer, the hooks and the tasks.

### Command: machine.py
- **Command:** `python3 dev/machine.py [apply --repo REPO [--peer NAME] | check | record-task NAME MODE | backup DIR | restore DIR]`
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

<!-- kept machine-setup-and-restore@8497ebf6 -->
