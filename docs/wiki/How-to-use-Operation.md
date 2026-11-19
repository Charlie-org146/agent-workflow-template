<!-- workflow-docs -->
# How to use Operation

## What it's for

One session governs many goals at once: it gives every ready goal its own worker session, passes the owner's answers along, runs unattended and never builds.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-monitoring` | Skill | One session governs many goals and shows what is running and what needs you. | Say "Run the operation session" or "Where do things stand?". |
| `board.py` | Command | The operation session's progress board and the list of repos it follows. | `python3 skills/workflow-monitoring/scripts/board.py repos list`. |
| `checkin.py` | Command | Prints the check-in: the machine, every session, the dependency map and what needs you. | `python3 skills/workflow-monitoring/scripts/checkin.py`. |
| `monitor.py plan` | Command | Plans the backlog into releases with an ETA, budget, machine and agent for each goal, and sends the owner one plan to approve. | `python3 skills/workflow-monitoring/scripts/monitor.py plan --check`, then `plan approve --owner-record ID`. |

### System diagram

```text
[Skill: workflow-monitoring | the operation session] --the live board and the repos it follows--> [Command: board.py | the operation session]
[Command: board.py | the operation session] --every goal and session--> [Command: checkin.py | the operation session]
[Command: checkin.py | the operation session] --machine, sessions, dependency map, what waits on you--> (the owner)
[Skill: workflow-monitoring | the operation session] --plans the backlog into releases--> [Command: monitor.py plan | the operation session] --one plan to approve--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Adopt my recent GitHub repos" | Your repos are listed by last push, private ones included; the ones you choose are cloned into one folder, followed and set up or updated, each ending with its template version. |
| "Run the operation session" | Every ready goal gets its own worker session, and the full live board prints now and at each check-in, or sooner when a worker reports. |
| "Start a goal to add result caching, done when repeat searches are served from the cache" | The goal is queued and starts in its own worker as soon as a slot is free. |
| "Where do things stand?" | You get the live board: Issues first, then running goals with progress and time left, queued goals, dependencies and one finish time. |
| "Tell the caching worker to keep the old cache format" | Your answer reaches that worker session as a message. |
| "How much did the operation session spend?" | `<git common dir>/loop/op-tokens.tsv` holds one row per check-in with its context and the tokens spent under scheduled, peer, human and hook-retry. A scheduled check-in with nothing new is skipped by a prompt hook and logged in `quiet.log`. |
| "Start an operation session on this machine" | `operate.py start` prints the readiness table (session tool, workers mode, skills, hooks, memory, pool), each row ok or with its fix; no goal starts. `operate.py timer` then shows the check-in timer for your yes. |
| "Queue a goal under the Delivery page" | `batch.py add NAME --goal "..." --done "..." --feature Delivery` stores the page, so the check-in groups the goal there instead of under "no feature". |
| "Resume the failed caching goal" | A failed or stopped goal gets a new worker; any other goal is refused. |
| "Clean up merged branches, list them first" | You see the merged goal branches that would go; once you say so, they are deleted locally. |

Notification subprocesses use the same noninteractive prompt settings as delivery commands.

Each requirement and how it is delivered:

- OPS-1: Roles, start and planning. One command starts the operation session and drives the whole process the same way every time. The operation session plans queued goals as a dependency graph and gives every goal whose dependencies are met its own worker session in the app, renamed worker · <goal>, running in parallel; it never builds. A goal waits only on goals it truly depends on; sharing files is not a reason to wait. When a worker session finishes, the operation session gives it the next ready goal, renaming it again. Example, from the dependency-held test: given a goal that depends on an unmerged goal, when the queue runs, then it is held until that goal merges.
- OPS-2: Live communication. Operation and workers talk through session messages: a worker reports each change of step or status as it happens, and its result when it ends (merged, failed or waiting, with the pull request); the operation session sends a worker its answer or a follow-up. Background processes are used only when the app can't start or reach a session, and the board says so. Example, from the worker-reports test: given a merged goal, when the board is shown, then it shows its pull request.
- OPS-16: Fill every free slot at once; speed comes before tokens, within the guardrails. Example, from the mon16-machine-line test: given a check-in, when it is written, then a Machine line shows free RAM, free commit memory, CPU and how many goal starts memory allows.

### Skill: workflow-monitoring
- **Say:** "Run the operation session"
- **Command:** `/workflow-monitoring operate`

### Command: board.py
- **Command:** `python3 skills/workflow-monitoring/scripts/board.py repos list`, or `repos adopt [OWNER/NAME ...]`
- **Dry run:** `repos list` only lists; nothing is changed until `repos adopt` is given repos.
- **Reads:** `~/.workflow-loop/repos` and your recent GitHub repos.
- **Writes:** `repos adopt` clones, follows and sets up the named repos.
- **Exit codes:** 0 when it lists or adopts; nonzero with a refusal line.

### Command: checkin.py
- **Command:** `python3 skills/workflow-monitoring/scripts/checkin.py [--since ISO]`
- **Dry run:** none needed: it is read-only.
- **Reads:** the run records, the queue, the session pool and the followed repos.
- **Writes:** nothing.
- **Exit codes:** 0 after it prints.

### Command: monitor.py plan
- **Command:** `python3 skills/workflow-monitoring/scripts/monitor.py plan [--machines pc=GB,mac=GB] [--peer-plan FILE] [--first-release vX.Y] [--check]`, then `plan approve --owner-record ID [SLUG key=value ...]`
- **Dry run:** `plan` is the dry run: it prints the plan and starts nothing; only `plan approve` writes the queue.
- **Reads:** the queue, the run records, the session pool, the settings, the other machine's plan file and `agents.json`.
- **Writes:** `plan-round.json` under the git folder's `loop/`; `plan approve` also the release, machine and agent on each queue line.
- **Exit codes:** 0 after it prints; non-zero when `plan approve` refuses (no pending plan, no owner-words record, unknown slug).

## URLs and deployments

- Wiki: [Operation](https://github.com/jcl2018/agent-workflow-template/wiki/Operation)
- Milestone: [Operation](https://github.com/jcl2018/agent-workflow-template/milestone/6)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Operation](Operation)
- Backlog: [Backlog: Operation](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept merge-queue-b@af5727c7 -->
