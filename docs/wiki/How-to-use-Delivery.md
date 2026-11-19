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

A small agentic workflow you can add to any repo. You state a goal and the checks that prove it's done. A background
agent takes it through your own skill suite's flow, unattended: your idea, plan, review, test and ship skills, with
frozen done lines and the repo's checks around them. You review the pull request. One session governs and the others
build.

**Delivery runs standalone, or with your own skill suite.** A private file outside the repo,
`~/.workflow-loop/flow.json`, names a skill for each step and how to run it in its own unattended mode. Setup fills it
with `built-in` steps, which run delivery's own routine for idea, plan, review, qa and ship; name your own skill for any
step and it replaces that routine. With no flow file, delivery refuses with one line saying how to set it. See
[the file contract](skills/loop-files.md).

**Status: early. Copy the `skills/` folders into your agent's skills folder, or run `dev/install-local.sh` for Claude
Code. No marketplace listing yet. What is left before V1 is in the [V1 section](docs/ROADMAP.md#v1) of the roadmap.** See the [wiki](docs/wiki/Home.md) for the features and the
[roadmap](docs/ROADMAP.md).

**This repo runs with no gates.** Its `.loop/config.json` turns on `auto_approve` and `auto_merge`. Review is the only gate: delivery runs no check step. What the skills leave for the
owner is approved automatically and logged as auto-approved, in the goal's log and on the board. The release step then
merges the pull request into `main` by itself, after bringing the wiki pages the goal touched up to date, and publishes the wiki once it has merged. The skills' own built-in refusals still apply, and the private-name leak
scan still guards every commit. The risk is plain: a broken or wrong change can reach `main` with nobody looking, and
the only check left is the regression workflow on GitHub, which reports and never blocks. A repo set up from this
template keeps every gate until its owner turns one off.

**What it aims to be**

- **Light:** Markdown instructions and a few small scripts, with no engine to run.
- **Yours:** delivery wraps the skill suite you already use instead of adding its own design or review steps.
- **Governed:** the session you talk to never builds. It starts background agents, shows what waits on you, and keeps a
  dashboard.
- **Checkable by you:** every pull request says how to verify it by hand, and your wiki stays in step with the code.

**Commands**

Each skill's `references/` folder has a chart for every command, with a status line saying what's proven. Most of these have run on a toy
repo, and `go` and `publish` have also run on a real repo. The skill flow has run for real only up to its first step. They may change while the first version settles. The examples use Claude Code. In other agents, you can ask
in plain words, such as "start a goal to add result caching".

Set up a repo once:

```text
/workflow-setup
```

Start a goal and watch it:

```text
/workflow-monitoring go "add result caching" --done "repeat searches are served from the cache"
/workflow-monitoring watch
```

**One session governs, and the others build.** `go` starts a background agent in its own worktree, and `watch` keeps
goals moving until nothing is left. You stay in one session and review pull requests.

Every goal runs the same flow: freeze the done lines, then your idea skill, your plan skill, the build, your review skill, your test skill and your
ship skill, then the pull request and the release. Review is the only gate; each step can be mapped to any skill in your private flow file. Each skill runs only after a probe proves its unattended mode, takes its recommended answers, and leaves
anything only you can decide under Waiting on you. Nothing is approved for you. The ship skill never pushes in that
mode, so delivery opens the pull request itself, with each step's result in its body.

Regression also runs on a schedule in GitHub Actions for a public repo (every 4 hours by default, `off` per routine in
`.loop/config.json`); health never runs in Actions, it runs on your Mac on its own schedule. They file failing tests as `defect` issues and health findings as tagged issues, and post one digest comment per round on a pinned `Automation digest` issue, which is also emailed to you
once per round when the mail secrets are set (Cloudflare Email Service or SMTP). Regression runs use Actions minutes, and
each round's cost is shown and flagged over 45 minutes.

**About this repo**

A small agentic workflow for any repo: you state a goal and the checks that prove it, and a background agent takes it
through your own skill suite's flow, unattended, to a pull request you review. One session governs and the others build: `/workflow-monitoring operate` plans queued goals as a dependency graph and starts the workers and prints the live board (issues, running goals, queued goals, dependencies and one finish time) every 30 minutes by default. To install it
and run a first goal, or to see where every file lives, read the rest of this README. It's released under the MIT license. The last step of every goal, the release step (see the [Delivery](https://github.com/jcl2018/agent-workflow-template/wiki/Delivery) page), also brings the wiki up to date and publishes it.


| You say | What happens |
|---|---|
| "Start a goal to add caching, done when the cache test passes" | The goal is drafted with its done lines and shown back to you to confirm. |
| "Go" | The goal is frozen and a worker session starts it right away. |
| "Queue it" | The goal waits in line and starts when its dependencies merge. |
| "What needs me?" | You get the questions waiting on you, each with a recommended answer. |
| "Approve it" / "a" | The decision is recorded with your words and the goal carries on. |
| "Merge it" | A ready pull request is merged and released. |
| (a lane says MEMORY_WAIT or LANE_ENV) | The machine was short of memory, not the goal: no try is spent, so run the same command again when memory frees. |

Delivery subprocesses fail instead of waiting for terminal prompts, including routed agent commands and their login checks.

The pull request's own record commit (the regression run and issue files, with re-rendered wiki tables) never sends a goal back to pr: a commit that moves only stamp files, or stamp files plus wiki pages, is tree-equal modulo stamps to the tested head and carries its pass. Any code path, symlink, rename or delete breaks that match. See the Release page for the rule.

Each requirement and how it is delivered:

- DEL-1: The loop. Example, from the no-done-line-refused test: given a goal with no done line, when it is started, then it is refused.
- DEL-3: Decisions. Example, from the pending-waits test: given a step that leaves a decision for the owner, when it ends, then the goal stops and waits.
- DEL-7: Work survives failure and moves by backup. A failed step is resumed from its recorded step, never from the start; `machine.py backup DIR` copies the restorable state to a folder outside every repo and `machine.py restore DIR` puts it back on a new machine.
- DEL-17: A goal's ETA is a hard limit.
- DEL-19: Every goal serves a requirement.

### Skill: workflow-delivery
- **Say:** "Start a goal to add caching, done when the cache test passes"
- **Command:** `/workflow-delivery go "goal" --done "line"`

### Skill: workflow-release
- **Say:** "Merge it"
- **Command:** `/workflow-release merge SLUG`

### Command: goal.py
- **Command:** `python3 skills/workflow-delivery/scripts/goal.py new SLUG --goal "goal" --done "line"` (also `record`, `pr`, `goal.py adopt SLUG`, `show`)
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

<!-- kept known-red-waves-batch@3411a49f -->
