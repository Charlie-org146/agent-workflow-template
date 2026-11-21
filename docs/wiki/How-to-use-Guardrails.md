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

### Guardrail list

Each guardrail with what it protects against, the requirement that owns it ("new" where this page's own requirement is the only one), the setting that controls it and the health rule that proves it is on ("none yet" where no rule reads it). The exact wording is in the owner's requirement; whether a guardrail is on is in the Tests table of the Guardrails page.

| Guardrail | Protects against | Owner | Setting | Health check |
|---|---|---|---|---|
| DEL-7 (was GRD-2) | A goal or step running away in time, tokens or tests | DEL-7, DEL-17, REG-7, REG-11, REG-14 | `time_budget_minutes`, `token_budget`, `step_budget_minutes`, `test_budget_minutes`, `prep_budget_minutes`, `max_merge_rounds`, `max_active_goals` | Performance |
| DEL-9 (was GRD-3) | A private name, local setting or private value committed or pushed | DEL-9, SET-8, SET-2 | `leak_prefixes` (private flow file) | Security and privacy: `private`, `scan-hook` |
| GRD-4 | A worker widening its own goal, resuming itself or changing its own budget | OPS-7 | `govern_hook`, `workers` | none yet |
| GRD-5 | A write to GitHub that nobody asked for | AUT-5, HLT-4, REG-5 | none: `--live` is the switch | none yet |
| GRD-6 (with the former GRD-16) | A direct or force push to the base branch, a merge with failing required checks, or a commit or push that skips the repo's hooks | SET-1, GRD-6 | set on the platform, not in the repo | none yet |
| GRD-7 (with the former GRD-17) | CI minutes spent on a superseded or no-code run, or too many CI runs or Actions minutes in a day | AUT-7, GRD-7 | `ci_levels` | none yet: the round digest shows the minutes it used |
| GRD-8 (with the former GRD-15) | A step running far past its usual tokens or time unseen, or an unread token count taken for an unspent budget | OPS-8, CHK-1, REG-8, GRD-8 | `silent_minutes`, `token_budget` | none yet: the board shows it under Needs you |
| HLT-2 (was GRD-9) | A guardrail that is off or broken without anyone seeing | HLT-2, HLT-3, HLT-6 | none | Controls |
| SET-1 (was GRD-10) | A repo adopted without the whole set | SET-1 | none | Adoption |
| OPS-16 (was GRD-12) | A goal or test lane starting while free memory is low | OPS-16 | `min_free_memory_gb` | Performance |
| MCH-1 (was GRD-18) | A POSIX-only call, or long text passed on a command line, breaking native Windows | MCH-1 | none | none yet |
| HLT-11 (was GRD-19) | A feature page too large to review | HLT-11 | `criteria_max` | Size: `requirements-per-page` |
| GRD-20 (with the former GRD-21 and GRD-22) | A page, a page's requirements or the test rows outgrowing their limit | GRD-20 | `criteria_max`, `max_regression_rows` | Size: `requirements-per-page`, `rows-cap` |

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Show me every guardrail" | You get the Guardrails page: each guardrail with what it protects against, the feature that owns it, its setting, and whether its Tests row says it is enforced. |
| "Which guardrail settings are there?" | The settings reference lists each setting with its home, default and meaning: token_budget, step_budget_minutes, test_budget_minutes and silent_minutes among them (time_budget_minutes is not listed yet). |
| "Check the budgets" | Health's performance group runs: it warns on any of the last 10 finished goals over its time or token budget, and a full suite over 30 minutes. |
| "Which guardrails aren't enforced yet?" | Each guardrail whose Tests row reads not enforced is listed with the feature that owns the missing part. |
| "Will machine setup write my address into a repo?" | No: `machine.py apply` refuses a routine or item holding an address or home path, names the line and kind, and writes nothing. |

Each requirement and how it is delivered:

- GRD-4: A worker writes only its own goal's work, never shared loop state or its own limits. Example, from the grd4-touches test: given a worker session, when it tries to widen its goal's touches, then the command refuses. Also (was AUT-9): Every routine declares what it may do. Example, from the perms-undeclared test: given a routine in the registry with no rows in .loop/permissions.tsv, when permissions.py check runs, then it prints UNDECLARED and exits 1. Also: `setup.py desk` lists every desk-only setup step once and `desk check` ends with DESK OK when none is left. Also: `setup.py desk` lists every desk-only setup step once, and `desk check` ends with DESK OK when none is left.
- GRD-5: Nothing is written to GitHub without an explicit `--live`. Example, from the grd5-regression-dry test: given no token, when the regression run reaches an issue write, then it is a dry run and makes no gh call.
- GRD-6: The base branch is protected and merges only with its required checks green. Example, from the grd6-head-moved test: given a pull request head that moved since its checks ran, when the release merges, then it is refused with HEAD_MOVED and nothing is merged.
- GRD-20: Sizes are one table, enforced on main. One table holds every size limit: pages, requirements per page and test rows. There is no script byte limit and no package file cap: both came from the Agensi package, and the loop ships only as the template (SET-10). (no test yet) Also (was HLT-11): Health keeps the repo lean. Health flags an in-loop test run over its time budget, naming the slowest tests to move to the full suite, and flags stale worktrees and branches, printing the commands that remove them without running them. (no test yet)

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
- **Fields:** `token_budget`, `step_budget_minutes`, `test_budget_minutes`, `silent_minutes` and `criteria_max`.
- **Example:** `"criteria_max": 19` is this repo's cap on a page's requirements.
- **Writer:** workflow-setup writes the defaults; the owner edits a value.
- **Reader:** the guards, the lanes, docs check and health.

## URLs and deployments

The loop ships only as a GitHub template (SET-10), so there is no package to build, upload or limit.

- Wiki: [Guardrails](https://github.com/jcl2018/agent-workflow-template/wiki/Guardrails)
- Milestone: [Guardrails](https://github.com/jcl2018/agent-workflow-template/milestone/11)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Guardrails](Guardrails)
- Backlog: [Backlog: Guardrails](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept queue-smoke@7132b5722 -->
