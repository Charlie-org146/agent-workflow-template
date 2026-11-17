<!-- workflow-docs -->
# How to use Delivery

## What it's for

Takes one sentence and its done lines to a merged, released pull request (a draft release you publish when auto_merge is off), unattended, through your own skills or its built-in routine, on Linux, macOS and native Windows, with pull requests queued only behind goals that share files and ready ones merged in batches, and it refuses to merge only for a wiki page its own diff made stale.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-delivery` | Skill | Takes one sentence and its done lines to a pull request, unattended. | Say "Start a goal ...", then "Go"; the goal is frozen and a worker session starts it. |
| `workflow-release` | Skill | Releases a goal once it has a pull request. | Say "Merge it" for a ready pull request. |
| `goal.py` | Command | Holds one goal's record: its done lines, the skill flow's steps and its pull request. | `python3 skills/workflow-delivery/scripts/goal.py <command> <slug>`. |
| `flow.py` | Command | Runs one step of a goal's skill flow (idea, plan, review, qa, ship). | `python3 skills/workflow-delivery/scripts/flow.py SLUG STEP`, again until it stops printing `RUNNING`. |

### System diagram

```text
[Skill: workflow-delivery | the agent session] --freezes the done lines--> [Command: goal.py | the worker's worktree]
[Command: goal.py | the worker's worktree] --runs each step: idea, plan, build, review, qa, ship--> [Command: flow.py | the worker's worktree]
[Command: goal.py | the worker's worktree] --pr opens it--> (GitHub pull request)
(GitHub pull request) --a ready pull request--> [Skill: workflow-release | the agent session]
[Skill: workflow-release | the agent session] --merges and publishes--> (main and its release)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Start a goal to add caching, done when the cache test passes" | The goal is drafted with its done lines and shown back to you to confirm. |
| "Go" | The goal is frozen and a worker session starts it right away. |
| "Queue it" | The goal waits in line and starts when its dependencies merge. |
| "What needs me?" | You get the questions waiting on you, each with a recommended answer. |
| "Approve it" / "a" | The decision is recorded with your words and the goal carries on. |
| "Merge it" | A ready pull request is merged and released. |
| (a lane says MEMORY_WAIT or LANE_ENV) | The machine was short of memory, not the goal: no try is spent, so run the same command again when memory frees. |

Each requirement and how it is delivered:

- DEL-1: The loop. Example, from the no-done-line-refused test: given a goal with no done line, when it is started, then it is refused.
- DEL-2: Frozen done lines. Example, from the frozen-done-lines test: given a running goal, when a frozen done line is changed, then the goal stops.
- DEL-3: Decisions. Example, from the pending-waits test: given a step that leaves a decision for the owner, when it ends, then the goal stops and waits.
- DEL-4: The pull request. Example, from the cut-needs-verify test: given no Verify by hand steps, when a release is cut, then it is refused.
- DEL-5: Release. Example, from the never-merges test: given auto_merge is off, when goals finish, then nothing is merged.
- DEL-6: Review depth fits the goal. Example, from the depth-condensed-refused test: given review_depth full, when a plan or review reply says it ran condensed, then it is refused with no try used.
- DEL-10: A goal started on another machine can be adopted. Example, from the adopt-record-qa test: given a goal pushed from another machine with an open pull request, when goal.py adopt runs on its branch, then a run record exists at step qa with the pull request, idea, plan and review done on another machine and qa, ship and pr not recorded.
- DEL-11: Adopt never trusts an unpushed branch. Example, from the adopt-refuses-unpushed test: given a branch that is not on origin, when goal.py adopt runs, then it is refused in one line and no run record is written.

### Skill: workflow-delivery
- **Say:** "Start a goal to add caching, done when the cache test passes"
- **Command:** `/workflow-delivery go "goal" --done "line"`

### Skill: workflow-release
- **Say:** "Merge it"
- **Command:** `/workflow-release merge SLUG`

### Command: goal.py
- **Command:** `python3 skills/workflow-delivery/scripts/goal.py new SLUG --goal "goal" --done "line"` (also `record`, `pr`, `adopt SLUG`, `show`)
- **Dry run:** none: `new` freezes the goal when it runs; `show SLUG` only prints the record.
- **Reads:** `.loop/config.json` and the goal's run record under the git common dir's `loop/runs`.
- **Writes:** `.loop/goals/SLUG.md`, the goal's branch and its run record; `pr` pushes the branch and opens the pull request.
- **Exit codes:** 0 when the command is done; nonzero with a `REFUSED` line that names the fix (a budget, a missing step or the queue).

### Command: flow.py
- **Command:** `python3 skills/workflow-delivery/scripts/flow.py SLUG STEP`
- **Dry run:** none: a step runs for real; the lane rows it starts are the only preview.
- **Reads:** the goal's run record, `.loop/config.json` and the step's reply file.
- **Writes:** the step's prompt and reply file and the lane logs under the git common dir's `loop/runs`.
- **Exit codes:** 0 when the step prints its `NEXT` line or `RUNNING`; nonzero when it refuses or the step fails.

## URLs and deployments

- Wiki: [Delivery](https://github.com/jcl2018/agent-workflow-template/wiki/Delivery)
- Milestone: [Delivery](https://github.com/jcl2018/agent-workflow-template/milestone/1)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Delivery](Delivery)
- Backlog: [Backlog: Delivery](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept agent-routing@b060a78f -->
