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
| (a lane says MEMORY_WAIT or LANE_ENV) | The machine was short of memory, not the goal: no try is spent, so run the same command again when memory frees. |

## URLs and deployments

- Wiki: [Delivery](https://github.com/jcl2018/agent-workflow-template/wiki/Delivery)
- Milestone: [Delivery](https://github.com/jcl2018/agent-workflow-template/milestone/1)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Delivery](Delivery)
- Backlog: [Backlog: Delivery](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept how-to-use-docs@14272c88 -->
