<!-- workflow-docs -->
# How to use Delivery

## What it's for

Takes one sentence and its done lines to a merged, released pull request (a draft release you publish when auto_merge is off), unattended, through your own skills or its built-in routine, on Linux, macOS and native Windows, with pull requests queued only behind goals that share files and ready ones merged in batches, and it refuses to merge only for a wiki page its own diff made stale.

Every goal runs one list of steps: freeze, plan, build, quick checks, tests, merge, after the merge, release. Each step logs its start, end, active minutes, tokens and result in the goal's record; `python3 skills/workflow-docs/scripts/steps_page.py show SLUG` prints the table, `docs/wiki/Steps.md` is generated from the code, and the release text carries a `### Steps` block. A stop records its cause, previewed once with its fix (filing is off in v1.1.0). Whoever saves the record, a step stays open until it ends, and a copy loaded before another save cannot move the step or status back. `goal.py` writes its asks, notes, refusals and failures as before; every screen says the step in them by the list's name.

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

**The clock, from my ask to main (DEL-17).**

Every change runs on one clock, from my ask to main. The normal goal and the small fix (one script or page, a few lines, no requirement change) run side by side:

| Step | Normal goal | Small fix |
|---|---|---|
| Freeze, idea, plan, review, build | the goal's own ETA, frozen with it | skipped: the worker gets the whole instruction up front and changes only the files it names; 2 minutes to edit, commit and push |
| Local tests: one lane, only the tests the change reaches, reused by qa, ship and pr while the code is unchanged | 5 minutes | 2 minutes |
| Push and PR CI: one run per push, same test selection, parallel jobs | 5 minutes | 3 minutes |
| Ready to main: the merge queue tests the merged result with a small fixed set, merges, and the release is made from a tag with no second pass | 5 minutes | 3 minutes |
| **Total, after build** | **about 15 minutes** | **10 minutes from my ask** |
| Tokens | each step has a budget from its measured usual; a step past twice its budget is flagged while it runs; a step that only waits does so in a script, not in model turns; an unread count shows "unread", never 0 | same |

Rules that hold across the clock:

- A merge never makes another ready pull request re-run; the queue tests the merged result.
- A step that passes its limit says so at once. A small fix that passes one becomes a normal goal. A normal goal that reaches its ETA finishes its current step, starts no new one, and I choose: ship now, extend once, or defer. A missed limit or ETA stays on the board as missed, with its cause (principle 2).
- Tests the change does not reach go to the scheduled full suite, which names how many; a change to a goal's own record files reaches fewer than 20 tests; test count and suite time stay capped.
- CI runs or minutes per day past a set limit raise one alarm.
- Health prints each step's time and tokens for the last 20 changes and fails a step over its limit.

The clock also holds what REG-7 (test runs), GRD-7 and GRD-8 (CI minutes, tokens) and REL-13 and REL-15 (the queue and the 5-minute merge) each say; those requirements stay on their pages with their tests, and DEL-17 is the row that shows them together.

Each requirement and how it is delivered:

- DEL-1: The loop. Example, from the no-done-line-refused test: given a goal with no done line, when it is started, then it is refused. Also (was REL-3): The full regression suite passes on the release candidate, and each known-red row is fixed or waived with an issue. Example, from the rel-red-row-refused test: given a known-red row with no waiver, when the gate runs, then it refuses naming the row.
- DEL-3: Decisions. Example, from the pending-waits test: given a step that leaves a decision for the owner, when it ends, then the goal stops and waits. Also (was REL-12): A review hold before auto merge. Example, from the review-hold-blocks test: given review_hold is on, when no review of the pull request head is recorded, then merge.py refuses REVIEW_HOLD, merges nothing and the board shows a merge waiting on review.
- DEL-17: A goal's ETA is a hard limit, and every change runs on one clock from my ask to main (the table above). Also (was GRD-7): CI spends minutes only on runs that matter, and too many runs raise an alarm. Example, from the grd7-round-cost test: given a scheduled round, when its digest is posted, then the round cost shows its minutes and Actions minutes. Also (was GRD-8): A step far past its usual tokens or time is flagged while it runs. Example, from the grd8-silent-worker test: given a worker silent past silent_minutes, when the board prints, then it shows under Needs you. Also (was REL-13): Fast merge queue. Example, from the merge-batch-split test: given 3 ready pull requests with disjoint touches, when wiki.py batch run verifies them on one tree, then they merge together, and a failing batch splits to name the culprit. Also (was REL-15): A ready pull request is on main within 5 minutes. Example, from the merge-guard-base-head test: given the merge_queue setting on and a base that moved in paths the goal's rows reach, when merge.py runs, then it does not refuse BASE_MOVED and prints MERGED only after gh reports the pull request merged; with the setting off the refusal is unchanged. Also (was REG-7): Fast in the loop. Its budget and its limits, word for word from the page before the v2 rewrite: Also (was HLT-7): Checks, check-ins and rounds answer fast. Its budget and its limits for a scheduled round:
  - A round finishes within 45 minutes (the 30-minute regression budget of Regression REG-7 plus 15 for health and the digest, health starting when regression has finished, not at a fixed offset), and each report shows the round's wall time and its pass and fail counts, plus its Actions minutes when it ran in GitHub Actions, so I can slow the schedule if it costs too much.
- DEL-19: One change, one goal, one list of steps, every step logged
- DEL-21: Adopt a standard tool by default (v2.0 planned). Each requirement's Follows cell says whether it adopts the standard tool or adapts the proven design with a one-line reason. Example: a requirement with no reference is replaced by its industry-standard counterpart or cut. Also (was DOC-24): Every requirement names what it follows (v2.0 planned). The README's principle tables show each requirement's Follows cell, its tool or standard, a link to its source and its verdict, for example adapted from GitHub CODEOWNERS for DOC-2. Example: a requirement row with an empty Follows cell fails the docs check.
- DEL-23: Tasks: a brief I write once and freeze, run as goals
- DEL-22: Fast plans: a goal's plan is ready in a set time and never stalls on a tool fault
- DEL-25: Fast build and checks: quick checks before every push, no local test lane
- DEL-26: Fast tests: on GitHub, in parallel, only what the change reaches, results reused
- DEL-27: Fast merge: the full tests run once, on the merged result, through the merge queue
- DEL-28: Every step has a token budget: each step has a budget from its measured usual; past twice that it is flagged; waiting is done in a script.

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

Backup and restore (the folded DEL-7): `machine.py backup DIR` copies the restorable state to a folder outside every repo and `machine.py restore DIR` puts it back on a new machine.

## URLs and deployments

- Wiki: [Delivery](https://github.com/jcl2018/agent-workflow-template/wiki/Delivery)
- Milestone: [Delivery](https://github.com/jcl2018/agent-workflow-template/milestone/1)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Delivery](Delivery)
- Backlog: [Backlog: Delivery](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept rel-15-queue@88a93af7b -->
