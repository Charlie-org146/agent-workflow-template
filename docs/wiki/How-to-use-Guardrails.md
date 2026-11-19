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
- GRD-12: The machine's status is read every round, and no goal starts under the memory floor. Example, from the config-memory-key-once test: given this repo's config, when min_free_memory_gb is read, then the key is there once as a positive number and the settings table registers it.
- GRD-15: Token counts are real or say unread. Each step's tokens are read from its session record when the step is recorded. A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget. (no test yet)
- GRD-16: No commit skips the hooks. A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health. (no test yet)
- GRD-17: Too many CI runs raise an alarm. Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used. (no test yet)
- GRD-18: Windows-safe. A pull request that adds a POSIX-only call without its guard fails its checks, and long text for an issue, comment, pull request or release note is always passed to gh in a file, so nothing breaks on native Windows. (no test yet)
- GRD-19: A page stays small enough to review. A feature page holds at most the number of requirements one setting allows, and health's Size group reports a page over it. (no test yet)
- GRD-20: The package always passes Agensi's rules. No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits. A failure names the rule and the file. (no test yet)
- GRD-21: Our package limits are never looser than Agensi's. One table on this page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read. Ours may be tighter, never looser. Raising one of ours takes my own words, and health warns when the last read is over 30 days old. (no test yet)
- GRD-22: A goal learns at qa that it doesn't fit. A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes. The refusal says how much room is left and what would free it. (no test yet)

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

<!-- kept v2-health-green@696066cd -->
