<!-- workflow-docs -->
# How to use Guardrails

## What it's for

Lists every guardrail the template has or needs, each with what it protects against, its owner, its setting and the health check that must prove it is on, including the memory floor before a goal starts (owner records o1, o3).

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `goal.py step` | Command | Records a step of a goal's flow, and refuses when a guard says stop. | `python3 skills/workflow-delivery/scripts/goal.py step SLUG NAME`. |
| `goal.py show` | Command | Prints a goal's run record, with a `TOKENS` line per step first: the tokens that step spent, measured from the session transcript. | `python3 skills/workflow-delivery/scripts/goal.py show SLUG`. |
| `sessions.py bind` | Command | Binds a frozen goal to its worker session and prints the WORKER command. | `python3 skills/workflow-monitoring/scripts/sessions.py bind SLUG ID`. |
| `.loop/config.json` | API/file contract | The guardrail settings the loop reads: budgets, silence limits and the page criteria cap. | Ask for "Show me every setting"; edit a value in the file to change a guardrail. |

### System diagram

```text
[API/file contract: .loop/config.json | the repo] --budgets and silence limits--> [Command: goal.py step | the worker's worktree]
[Command: sessions.py bind | the operation session] --binds the goal to its worker session--> [Command: goal.py step | the worker's worktree]
[Command: goal.py step | the worker's worktree] --refuses--> (refused: a guard says stop)
[Command: goal.py step | the worker's worktree] --its run record, TOKENS first--> [Command: goal.py show | the worker's worktree]

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Show me every guardrail" | You get the Guardrails page: each guardrail with what it protects against, the feature that owns it, its setting, and whether its Tests row says it is enforced. |
| "Which guardrail settings are there?" | The settings reference lists each setting with its home, default and meaning: token_budget, step_budget_minutes, test_budget_minutes, goal_lane_minutes and silent_minutes among them (time_budget_minutes is not listed yet). |
| "Check the budgets" | Health's performance group runs: it warns on any of the last 10 finished goals over its time or token budget, a goal's test lane over goal_lane_minutes, and a full suite over 30 minutes. |
| "Which guardrails aren't enforced yet?" | Each guardrail whose Tests row reads not enforced is listed with the feature that owns the missing part. |
| "Will machine setup write my address into a repo?" | No: `machine.py apply` refuses a routine or item holding an address or home path, names the line and kind, and writes nothing. |

Each requirement and how it is delivered:

- GRD-1: One visible set of guardrails, each with its protection, owner, setting and health check. Example, from the grd1-guardrail-list test: given the Guardrails page, when it is read, then it lists every guardrail with its protection, owner, setting and health check (not built: the page is a definition only).
- GRD-2: Time and token budgets stop a goal or a step before it runs away. Example, from the reg7-budget-leaves test: given rows that would run past the test budget, when a loop test run happens, then it runs the rows that fit, stops at the budget and lists every row it left.
- GRD-3: Nothing private is committed, and no commit skips the hooks that check it. Example, from the del9-pr-refuses test: given a branch that adds a private name from the list, when goal.py pr runs, then nothing is pushed and the refusal names the place, never the text.
- GRD-4: A worker writes only its own goal's work, never shared loop state or its own limits. Example, from the grd4-touches test: given a worker session, when it tries to widen its goal's touches, then the command refuses.
- GRD-5: Nothing is written to GitHub without an explicit `--live`. Example, from the grd5-regression-dry test: given no token, when the regression run reaches an issue write, then it is a dry run and makes no gh call.
- GRD-6: The base branch is protected and merges only with its required checks green. Example, from the grd6-head-moved test: given a pull request head that moved since its checks ran, when the release merges, then it is refused with HEAD_MOVED and nothing is merged.
- GRD-7: CI spends minutes only on runs that matter, and too many runs raise an alarm. Example, from the grd7-round-cost test: given a scheduled round, when its digest is posted, then the round cost shows its minutes and Actions minutes.
- GRD-8: A step far past its usual tokens or time is flagged while it runs. Example, from the grd8-silent-worker test: given a worker silent past silent_minutes, when the board prints, then it shows under Needs you.
- GRD-9: Health proves every guardrail is present and working, each rule with a negative control. Example, from the grd9-controls test: given every health rule, when the controls run on broken copies, then each rule fires.
- GRD-10: Setup installs the whole set when a repo is adopted, and health judges it. Example, from the grd10-install-hooks test: given a repo being adopted, when setup runs by default, then it installs the three private-name hooks after its commit.
- GRD-11: A goal depends only on what its own machine can do. Example, from the machine-local-guardrail test: given a row whose red proof needs another machine and is recorded owed, when sync runs, then it reads PENDING and no longer blocks as UNPROVEN.
- GRD-12: The machine's status is read every round, and no goal starts under the memory floor. Example, from the config-memory-key-once test: given this repo's config, when min_free_memory_gb is read, then the key is there once as a positive number and the settings table registers it.
- GRD-13: Regression rows and full-suite time are capped, and going over a cap blocks delivery (owner record o51). Example, from the test-caps-consolidate-allowed test: given a repo over a cap, when a goal removes or merges at least as many rows as it adds, then qa lets it pass, so a goal that only consolidates is always allowed.
- GRD-14: A goal's ETA is a hard limit: past it the owner chooses ship now, extend once or defer. Example, from the eta-freeze test: given a goal being frozen, when its fields and goal file are built, then they hold a hard ETA in whole minutes (at least 30) with its basis, and the goal file has an ETA line next to the done lines.

### Command: goal.py show
- **Command:** `python3 skills/workflow-delivery/scripts/goal.py show SLUG`
- **Dry run:** none: it only reads.
- **Reads:** the goal's run record; a step's tokens were read from its session transcript when `goal.py record` ran.
- **Writes:** nothing. Its output is cut to 2,000 characters (the full text is kept under `.git/loop/out/`), so the `TOKENS` lines come first.
- **Exit codes:** 0, or nonzero when the goal has no run record.

### Command: goal.py step
- **Command:** `python3 skills/workflow-delivery/scripts/goal.py step SLUG NAME [--note TEXT] [--tokens N]`
- **Dry run:** none: it records the step.
- **Reads:** the goal's run record and the budget settings in `.loop/config.json`.
- **Writes:** the goal's run record.
- **Exit codes:** 0 when the step is recorded; nonzero with a `REFUSED` line when a time, token or round budget is spent.

### Command: sessions.py bind
- **Command:** `python3 skills/workflow-monitoring/scripts/sessions.py bind SLUG ID` (or `self`)
- **Dry run:** none: it records the binding.
- **Reads:** the session pool and the goal's run record.
- **Writes:** the goal's run record; it prints the `WORKER` command and the `WORKTREE`.
- **Exit codes:** 0 when it prints `BOUND`; nonzero with a `REFUSED` line.

### API/file contract: .loop/config.json
- **Path:** `.loop/config.json`
- **Fields:** `token_budget`, `step_budget_minutes`, `test_budget_minutes`, `goal_lane_minutes`, `silent_minutes` and `criteria_max`.
- **Example:** `"criteria_max": 19` is this repo's cap on a page's requirements.
- **Writer:** workflow-setup writes the defaults; the owner edits a value.
- **Reader:** the guards, the lanes, docs check and health.

## URLs and deployments

- Wiki: [Guardrails](https://github.com/jcl2018/agent-workflow-template/wiki/Guardrails)
- Milestone: [Guardrails](https://github.com/jcl2018/agent-workflow-template/milestone/11)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Guardrails](Guardrails)
- Backlog: [Backlog: Guardrails](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept row-cap-1300@4e362144 -->
