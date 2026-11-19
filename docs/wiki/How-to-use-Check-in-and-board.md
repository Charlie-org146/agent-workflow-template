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
- CHK-10: Every goal's STATUS carries an ETA, and a slip is reported at once. `layers.py status` sends STATUS with each goal's eta, eta_basis and slip, and sends it at once when a slip is over 15 minutes; top's board shows one SLIP line. Example, from the release-eta test: given an eta that slipped 20 minutes, when status runs, then STATUS is sent at once and the board carries the SLIP line.
- CHK-11: The finish is forecast from measured merge pace, not step estimates. The board's Finish line shows the measured forecast, from the median and quartiles of the last 5 gaps between merges, and the step estimate on a second line. Example, from the release-eta test: given merge gaps of 44, 49, 22 and 20 minutes, when 3 goals are left, then the forecast is the last merge plus 3 times 33 minutes.

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

<!-- kept known-red-w8-size@90e0f6a3 -->
