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
- CHK-2: A check-in on a cadence, in one layout. Example, from the no-change-quiet test: given a board field the old board lacked or gh not answering, when boards are compared, then it counts as no change.
- CHK-3: Notify me by mail. When notification is on for this machine, each check-in mails me once per new event, such as a new Needs you item or a goal that stopped or passed its ETA. (no test yet)
- CHK-4: A check-in with nothing new costs nothing. A scheduled check-in that is the same as the last full one, apart from its machine line and numbers, is one line, printed without a model turn, for at most two hours in a row. Each check-in logs the tokens the operation session spent. (no test yet)
- CHK-5: Dependency map. Example, from the mon14-repo-blocks test: given a cross-repo dependency, when the check-in prints, then it is listed between headed repo blocks.
- CHK-6: What a check-in shows of other machines. Example, from the mon17-this-pod-only test: given goals of two pods, when the check-in is written, then only this pod's goals are listed and the other pod gets one line.
- CHK-7: Blockers first. Example, from the blockers-first test: given owner items holding up different numbers of goals, when the check-in is written, then each says what it holds up and whether it is on the critical path, the one holding up the most is first, and the Stop hook refuses a reply that does not.
- CHK-9: I can answer and steer from my phone or mail. I can answer any question under Needs you by replying to its mail or from my phone, with the same words a typed answer takes, and start, stop or reorder goals the same way. A reply counts as my words only when it comes from my own address or signed-in session. (no test yet)

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

<!-- kept three-level-ops-reland@6115642b -->
