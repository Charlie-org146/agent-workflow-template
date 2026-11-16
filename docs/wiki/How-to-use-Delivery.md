<!-- workflow-docs -->
# How to use Delivery

## What it's for

Takes one sentence and its done lines to a merged, released pull request (a draft release you publish when auto_merge is off), unattended, through your own skills or its built-in routine, on Linux, macOS and native Windows, with pull requests queued only behind goals that share files and ready ones merged in batches, and it refuses to merge only for a wiki page its own diff made stale.

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

Each requirement and how it is delivered:

- DEL-1: The loop. Example, from the no-done-line-refused test: given a goal with no done line, when it is started, then it is refused.
- DEL-2: Frozen done lines. Example, from the frozen-done-lines test: given a running goal, when a frozen done line is changed, then the goal stops.
- DEL-3: Decisions. Example, from the pending-waits test: given a step that leaves a decision for the owner, when it ends, then the goal stops and waits.
- DEL-4: The pull request. Example, from the cut-needs-verify test: given no Verify by hand steps, when a release is cut, then it is refused.
- DEL-5: Release. Example, from the never-merges test: given auto_merge is off, when goals finish, then nothing is merged.
- DEL-6: Review depth fits the goal. Example, from the depth-condensed-refused test: given review_depth full, when a plan or review reply says it ran condensed, then it is refused with no try used.
- DEL-10: A goal started on another machine can be adopted. Example, from the adopt-record-qa test: given a goal pushed from another machine with an open pull request, when goal.py adopt runs on its branch, then a run record exists at step qa with the pull request, idea, plan and review done on another machine and qa, ship and pr not recorded.
- DEL-11: Adopt never trusts an unpushed branch. Example, from the adopt-refuses-unpushed test: given a branch that is not on origin, when goal.py adopt runs, then it is refused in one line and no run record is written.

## URLs and deployments

- Wiki: [Delivery](https://github.com/jcl2018/agent-workflow-template/wiki/Delivery)
- Milestone: [Delivery](https://github.com/jcl2018/agent-workflow-template/milestone/1)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Delivery](Delivery)
- Backlog: [Backlog: Delivery](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept how-to-use-docs@14272c88 -->
