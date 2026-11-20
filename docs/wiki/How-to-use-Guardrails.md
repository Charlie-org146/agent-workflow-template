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
| GRD-20 (with the former GRD-21 and GRD-22) | A release package that fails Agensi's rules, a package limit of ours looser than Agensi's, or a goal that outgrows a package limit, learned only at release | GRD-20 | none | none yet |

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

- GRD-4: A worker writes only its own goal's work, never shared loop state or its own limits. Example, from the grd4-touches test: given a worker session, when it tries to widen its goal's touches, then the command refuses.
- GRD-5: Nothing is written to GitHub without an explicit `--live`. Example, from the grd5-regression-dry test: given no token, when the regression run reaches an issue write, then it is a dry run and makes no gh call.
- GRD-6: The base branch is protected and merges only with its required checks green. Example, from the grd6-head-moved test: given a pull request head that moved since its checks ran, when the release merges, then it is refused with HEAD_MOVED and nothing is merged.
- GRD-7: CI spends minutes only on runs that matter, and too many runs raise an alarm. Example, from the grd7-round-cost test: given a scheduled round, when its digest is posted, then the round cost shows its minutes and Actions minutes.
- GRD-8: A step far past its usual tokens or time is flagged while it runs. Example, from the grd8-silent-worker test: given a worker silent past silent_minutes, when the board prints, then it shows under Needs you.
- GRD-20: The package always passes Agensi's rules. No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits. A failure names the rule and the file. (no test yet)

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

**Package limits**

Each package limit Agensi states on its packaging page, next to ours in `dev/package.py`. Ours may be tighter, never looser: `dev/toy/test-package-caps.py` fails when this table is missing or a figure of ours is above Agensi's. Agensi's page gives no unit for MB and KB, so the check reads them as binary (1 MB is 1,048,576 bytes and 1 KB is 1,024 bytes); the package size cap is 5,000,000 bytes, equal or tighter in either unit.

| Limit | Agensi's figure | Ours | Date Agensi's page was read |
|---|---|---|---|
| Files per package (upload from an agent) | 100 files | 100 files (MAX_FILES) | 2026-11-18 |
| Package size (upload from an agent; the page does not say per file or in total) | 5 MB | 5,000,000 bytes for the whole package, failing at 5,000,000 or more (MAX_BYTES) | 2026-11-18 |
| Files the buyer's agent receives besides SKILL.md | 200 files | 100 files in all, SKILL.md files included (MAX_FILES) | 2026-11-18 |
| Text the buyer's agent receives per listing | 6,000,000 characters | 5,000,000 characters, the package cap in bytes, which is at least as many characters (MAX_BYTES) | 2026-11-18 |
| Script size (a guideline on Agensi's page) | 20 KB | 20 KB, failing at 20,480 bytes (MAX_SCRIPT). Agensi guideline, unit unstated; binary assumed, 2.4% looser if Agensi means decimal | 2026-11-18 |
| ZIP size (upload from the website) | 50 MB | 5,000,000 bytes (MAX_BYTES) | 2026-11-18 |
| Files per package (upload from the website) | 1,000 files | 100 files (MAX_FILES) | 2026-11-18 |
| Skills per pack (upload from the website) | 50 skills | no cap of its own; at most 100 files | 2026-11-18 | <!-- not-a-count -->
| File content | text files only | text only: a file that is not UTF-8 text fails | 2026-11-18 |
| Executables and bundled dependencies | not allowed | not allowed: an executable bit, compiled files and dependency folders fail | 2026-11-18 |
| Listing fields (summary, tags, keywords, use_cases) | no limit stated | summary 300 characters, tags 10, keywords 10, use_cases 8 | 2026-11-18 |

- Wiki: [Guardrails](https://github.com/jcl2018/agent-workflow-template/wiki/Guardrails)
- Milestone: [Guardrails](https://github.com/jcl2018/agent-workflow-template/milestone/11)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Guardrails](Guardrails)
- Backlog: [Backlog: Guardrails](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept merge-batch-on@c7193d33 -->
