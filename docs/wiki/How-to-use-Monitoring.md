<!-- workflow-docs -->
# How to use Monitoring

## What it's for

One session governs many goals at once and shows a live board of what's running and what needs you, and each check-in draws live goals with their time left and waits, with this machine's status;.

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Adopt my recent GitHub repos" | Your repos are listed by last push, private ones included; the ones you choose are cloned into one folder, followed and set up or updated, each ending with its template version. |
| "Run the operation session" | Every ready goal gets its own worker session, and the full live board prints now and at each check-in, or sooner when a worker reports. |
| "Start a goal to add result caching, done when repeat searches are served from the cache" | The goal is queued and starts in its own worker as soon as a slot is free. |
| "Where do things stand?" | You get the live board: Issues first, then running goals with progress and time left, queued goals, dependencies and one finish time. |
| "Tell the caching worker to keep the old cache format" | Your answer reaches that worker session as a message. |
| "Resume the failed caching goal" | A failed or stopped goal gets a new worker; any other goal is refused. |
| "Clean up merged branches, list them first" | You see the merged goal branches that would go; once you say so, they are deleted locally. |

## URLs and deployments

- Wiki: [Monitoring](https://github.com/jcl2018/agent-workflow-template/wiki/Monitoring)
- Milestone: [Monitoring](https://github.com/jcl2018/agent-workflow-template/milestone/6)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Monitoring](Monitoring)
- Backlog: [Backlog: Monitoring](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept apply-rerender@d974d643 -->
