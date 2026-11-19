<!-- workflow-docs -->
# How to use Check in and board

## What it's for

Shows what is running, stuck or waiting on the owner the same way every time: the live board, a check-in on a cadence in one layout, and a dependency map with this machine's status.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `checkin.py` | Command | Prints the check-in: the machine, every session, the dependency map and what needs you. | `python3 skills/workflow-monitoring/scripts/checkin.py`. |

### System diagram

```text
[Command: checkin.py | the operation session] --machine, sessions, dependency map, what waits on you--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Where do things stand?" | You get the live board: Issues first, then running goals with progress and time left, queued goals, dependencies and one finish time. |

Each requirement and how it is delivered:

- CHK-1: Live board. Example, from the waits-first test: given a live board, when the board page is opened, then it shows the live board.

### Command: checkin.py
- **Command:** `python3 skills/workflow-monitoring/scripts/checkin.py [--since ISO]`
- **Dry run:** none needed: it is read-only.
- **Reads:** the run records, the queue, the session pool and the followed repos.
- **Writes:** nothing.
- **Exit codes:** 0 after it prints.

## URLs and deployments

- Wiki: [Check-in-and-board](https://github.com/jcl2018/agent-workflow-template/wiki/Check-in-and-board)
- Milestone: [Check-in-and-board](https://github.com/jcl2018/agent-workflow-template/milestone/6)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Check-in-and-board](Check-in-and-board)
- Backlog: [Backlog: Check-in-and-board](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept ops-findings-v20@6e40968b -->
