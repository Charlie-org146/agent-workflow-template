<!-- workflow-docs -->
# How to use Monitoring

## What it's for

One session governs many goals at once and shows a live board of what's running and what needs you, and each check-in draws live goals with their time left and waits, with this machine's status;.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-monitoring` | Skill | One session governs many goals and shows what is running and what needs you. | Say "Run the operation session" or "Where do things stand?". |
| `board.py` | Command | The operation session's progress board and the list of repos it follows. | `python3 skills/workflow-monitoring/scripts/board.py repos list`. |
| `checkin.py` | Command | Prints the check-in: the machine, every session, the dependency map and what needs you. | `python3 skills/workflow-monitoring/scripts/checkin.py`. |

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
| "Resume the failed caching goal" | A failed or stopped goal gets a new worker; any other goal is refused. |
| "Clean up merged branches, list them first" | You see the merged goal branches that would go; once you say so, they are deleted locally. |

Each requirement and how it is delivered:

- MON-1: Roles, start and planning. One command starts the operation session and drives the whole process the same way every time. The operation session plans queued goals as a dependency graph and gives every goal whose dependencies are met its own worker session in the app, renamed worker · <goal>, running in parallel; it never builds. A goal waits only on goals it truly depends on; sharing files is not a reason to wait. When a worker session finishes, the operation session gives it the next ready goal, renaming it again. Example, from the dependency-held test: given a goal that depends on an unmerged goal, when the queue runs, then it is held until that goal merges.
- MON-2: Live communication. Operation and workers talk through session messages: a worker reports each change of step or status as it happens, and its result when it ends (merged, failed or waiting, with the pull request); the operation session sends a worker its answer or a follow-up. Background processes are used only when the app can't start or reach a session, and the board says so. Example, from the worker-reports test: given a merged goal, when the board is shown, then it shows its pull request.
- MON-3: Live board. Example, from the waits-first test: given a live board, when the board page is opened, then it shows the live board.
- MON-4: Live board layout. Example, from the retired-leaves-waiting test: given a retired goal, when the board is shown, then it no longer shows under Issues.
- MON-5: Cadence and reply format. Example, from the no-change-quiet test: given a board field the old board lacked or gh not answering, when boards are compared, then it counts as no change.
- MON-6: Clean up after every goal. Example, from the mon6-merged-frees test: given a goal whose pull request merged, when its worker reports merged, then its session goes back to the pool (archived above pool_size) and its worktree and branch are removed.
- MON-10: Re-plan at every check-in. Example, from the mon10-replan test: given ready, mergeable and splittable goals, when the operation session re-plans, then each start, merge and split is logged once with its reason, shown in the check-in, and no running goal is stopped.
- MON-11: Full auto mode. Example, from the mon11-full-auto test: given full auto on, when a worker asks a routine question, then the recommended answer is sent and logged; destructive, unlabeled, risky-word and owner-answered questions wait; turning it off applies at the next decision.
- MON-12: Session pool. Example, from the mon12-pool test: given a session pool, when it runs low, then the check-in asks to create every missing session in one step; pool.py add fills it, no pool hides the ask, and a full pool makes ready goals wait with the fix.
- MON-13: Two layers per pod: one operation session governs every repo in its pod directly and talks to each worker, with no per-repo operation session; several pods may run concurrently and independently. Example, from the mon13-two-layers test: given a second session's claim, when it claims, then the first stays an operation session and nothing refuses or warns.
- MON-14: Dependency map grouped by repo. Example, from the mon14-repo-blocks test: given a cross-repo dependency, when the check-in prints, then it is listed between headed repo blocks.
- MON-15: Pods coordinate through shared state, not messages: every goal records its owning pod and only that pod starts, answers, merges or resumes it; other pods show it read-only as owned by that pod; merges into one repo's main are serialized across pods by a short lock. Example, from the mon15-pod-owner test: given another pod's goal, when a pod acts on it, then it is refused naming the owner and shown owned by that pod.
- MON-16: Fill every free slot at once; speed comes before tokens, within the guardrails. Example, from the mon16-machine-line test: given a check-in, when it is written, then a Machine line shows free RAM, free commit memory, CPU and how many goal starts memory allows.
- MON-17: A check-in lists only this machine's goals. Example, from the mon17-this-pod-only test: given goals of two pods, when the check-in is written, then only this pod's goals are listed and the other pod gets one line.
- MON-18: The operation session keeps running unattended. Example, from the unattended-sends-warn test: given 16 cross-session sends with no owner message, when the check-in reads the count, then it warns and asks for any owner message.
- MON-19: Blockers first. Each item under Needs you says what it holds up, so the owner sees the priorities. Example, from the blockers-first test: given owner items holding up different numbers of goals, when the check-in is written, then each says what it holds up and whether it is on the critical path, the one holding up the most is first, and the Stop hook refuses a reply that does not.

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

## URLs and deployments

- Wiki: [Monitoring](https://github.com/jcl2018/agent-workflow-template/wiki/Monitoring)
- Milestone: [Monitoring](https://github.com/jcl2018/agent-workflow-template/milestone/6)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Monitoring](Monitoring)
- Backlog: [Backlog: Monitoring](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept hotfix-4892@1ad8101b -->
