<!-- workflow-docs -->
# How to use Check in and board

## What it's for

Shows what is running, stuck or waiting on the owner the same way every time: the live board, a check-in on a cadence in one layout, and a dependency map with this machine's status.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `checkin.py` | Command | Prints the check-in: the machine, every session, each repo's work as a queue (Building now, then Queue, in order), the dependency map and what needs you. | `python3 skills/workflow-monitoring/scripts/checkin.py`. |

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

- CHK-1: Live board. Example, from the waits-first test: given a live board, when the board page is opened, then it shows the live board. Also (was MCH-5): One email stream, answered by reply. Example, from the mailbox-two-mails test: given a mailed question, when the owner replies "1 recommended", then it is recorded as owner words with source owner and sent to the worker.

### Command: checkin.py
- **Command:** `python3 skills/workflow-monitoring/scripts/checkin.py [--since ISO]`
- **Dry run:** none needed: it is read-only.
- **Reads:** the run records, the queue, the session pool and the followed repos.
- **Writes:** nothing.
- **Exit codes:** 0 after it prints.
- **Reading the queue:** each repo block starts with **Building now** (one row per running goal: its PR, session, step with progress k/8, and ETA) and then **Queue, in order** (position, goal, what it waits for, ETA to start). A goal is in one block only. The order is queue.md's order; "waits for" is the loop's own reason (a goal it waits on, or "slots full"); a queued goal starts when what it waits on ends, so its ETA is that goal's end, or the first running goal's end when only a slot is missing. A row with no estimate says "ETA unknown: <what has no estimate>" and never shows a guessed time.
- **Reading the bars:** under each release, each goal lists one bar per frozen done line (the owner's sub-steps), `d1 [####----] 1/2 ETA 13:12 (about 30m)`: the bar and done/total are the regression rows linked to that line (goal `slug:N`) that last passed over the rows linked; a line with no linked row reads `0/8 by step` (the goal's recorded flow steps done of 8) until rows exist. The ETA is the goal's own finish, since its lines finish together; it reads `ETA unknown: <goal> has no estimate` when there is none. The release's roll-up line counts the done lines complete over all its goals' lines, with the release's finish (the latest goal's).

## URLs and deployments

- Wiki: [Check-in-and-board](https://github.com/jcl2018/agent-workflow-template/wiki/Check-in-and-board)
- Milestone: [Check-in-and-board](https://github.com/jcl2018/agent-workflow-template/milestone/6)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Check-in-and-board](Check-in-and-board)
- Backlog: [Backlog: Check-in-and-board](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept slot-hold-release@75f0feff -->
