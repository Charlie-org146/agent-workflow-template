<!-- workflow-docs -->
# How to use Setup

## What it's for

Turns any repo into a ready workspace for any agent without ever blocking, judged by health before and after, keeps it in step with the template, adopts several repos in one pass through `board.py repos adopt`, and lists, with the exact instruction, what the owner must still do on a new machine.

`update.py` ships `steps.py` as a shared file, so an updated pack still has `shared/steps.py`; `update.py`'s helpers that moved whole into `moved_set.py` ship beside it, with the same no-prompt guard variables as the other scripts.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-setup` | Skill | Turns any repo into a ready workspace for any agent without blocking it. | Say "Set up this repo"; it shows what it found and writes a setup branch. |
| `setup.py` | Command | Surveys a repo and writes its `.loop/` config on a branch. | `python3 skills/workflow-setup/scripts/setup.py`. |
| `setup.py desk` | Command | Lists and records the desk steps needed before phone-only operation. | `python3 skills/workflow-setup/scripts/setup.py desk list`. |
| `unattended.py` | Command | Checks what an unattended run needs, replays the golden adoption and lists connectors. | `python3 skills/workflow-monitoring/scripts/unattended.py prerequisites`. |

### System diagram

```text
[Skill: workflow-setup | the agent session] --surveys the repo--> [Command: setup.py | the repo checkout]
[Command: setup.py | the repo checkout] --writes it--> (.loop/ config on a branch)
[Command: setup.py desk | the repo checkout] --lists and records desk steps--> (machine-local desk.json and phone-start gaps)
[Command: unattended.py | the repo checkout] --checks what an unattended run needs--> (connector and prerequisite list)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

**Getting started**

From install to one finished goal.

1. **Install.** Run `dev/install-local.sh`. It links each `skills/workflow-*` folder into `~/.claude/skills` (or
   `$CLAUDE_SKILLS_DIR`) and prints `LINKED <name>`. It skips a name that is already a real folder. For another agent,
   copy the `skills/` folders into its skills folder.
2. **Set up your repo.** Run `/workflow-setup`. It writes `.loop/config.json`, `.loop/queue.md` and `.loop/findings.md`
   on a branch called `workflow-setup`. Preview with `/workflow-setup setup --dry-run`, using the path to the skill's
   folder. Then allow the
   tools a background agent needs in `agent_command` (for example
   `["claude", "-p", "--allowedTools=Bash,Read,Write,Edit"]`; you choose the list), and review and merge the branch
   yourself. The other skills read the config from the base branch. Setup also writes `.loop/START.md`, the entry point
   any new session reads first, and the same workflow-loop block into `CLAUDE.md` and `AGENTS.md`, so Claude Code and
   Codex run the same loop.

   To run the loop from Codex, use `codex exec -s workspace-write` with these writable roots in
   `sandbox_workspace_write.writable_roots`: the repo's git folder, its remote, and `~/.workflow-loop` (setup and `go`
   write the private settings there; a read-only home leaves them unwritten and `go` is refused). The git folder root
   also lets a run write `.git/hooks`, which a narrower `.git/loop` root would not. The first setup run exits 1 until
   `agent_command` names the tools you allow. Pick the model yourself (`-m`): a model your account does not support is
   rejected before anything runs. `dev/toy/test-codex.sh` proves this on a clean toy repo and is skipped, never passed,
   where Codex cannot answer.
3. **Start a goal.** From the main checkout, on the base branch:
   `/workflow-monitoring go "add result caching" --done "repeat searches are served from the cache"`. Done lines are
   frozen once the goal starts, so make each one provable before the pull request, by a test or by what a person
   can see (see [Delivery](docs/wiki/Delivery.md)). Setup filled `~/.workflow-loop/flow.json` with `built-in` steps,
   so this works with no skill suite; name your own skill for any step there and it replaces that step's routine.
4. **Watch it.** `/workflow-monitoring watch` starts queued goals in their own worktrees, prints what changed, and ends
   with what waits on you. Use `report` for a snapshot.
5. **Answer what waits on you**, in the exact words `watch` prints.
6. **Review.** The goal ends at a pull request. A monitored goal answers `leave` by itself, unless you started it with
   `--release ask`; then it waits for `cut <slug>` or `leave <slug>` (see [Delivery](docs/wiki/Delivery.md)). With
   `"release_auto": true`, it decides from its diff and may cut a draft instead. Answer before you merge, because `cut`
   commits on the goal's branch. Review and merge the pull request yourself; nothing here merges unless `auto_merge` is on.
7. **Keep it current.** `/workflow-setup update --check` shows what a newer template version brings;
   `/workflow-setup update` applies it and puts this repo's generated files on a `workflow-update-vX` branch for you to
   merge. A skill you fixed here is kept, and `/workflow-setup update --propose` sends the fix back to the template.

**File reference**

In the repo:

| File | Holds |
|---|---|
| `.loop/config.json` | Base branch, agent commands, risky paths, wiki folder |
| `.loop/queue.md` | Goals to run, one line each |
| `.loop/goals/<slug>.md` | One goal: frozen done lines, plan, verify steps |
| `.loop/findings.md` | Open findings |
| `.loop/docs.tsv` | Each wiki page and the paths it describes |
| `.loop/regression.tsv` | Test rows |
| `.loop/regression-known.tsv` | Rows expected to fail, with a reason |
| `.loop/regression-red.tsv` | Red results proven on another runner, with runner and commit |
| `.loop/regression-runs.tsv`, `.loop/regression-issues.tsv` | Each row's last result; each defect test's issue state |
| `.github/workflows/regression.yml`, `.github/workflows/regression-pr.yml` | A public repo's regression routines (written by setup); health and a private repo's regression run on the Mac |
| `docs/wiki/` | Wiki pages, each starting with `<!-- workflow-docs -->` |

Outside the repo, run state lives in `<git common dir>/loop/`: `runs/<slug>.json`, `logs/<slug>.log`,
`dashboard.html`, `wiki.json`, `board.json`, `board.html`, `board-artifact.html`, `cadence` (minutes between
check-ins, or `off`) and `handoff.md`. Nothing there is committed. `board.py repos add` keeps a list of repo paths in `~/.workflow-loop/repos`, and
`~/.workflow-loop/flow.json` names your skill flow.

In this template: `skills/` (the seven skills; the full contract is `skills/loop-files.md`), `dev/` (install, package and
toy tests), `listing.json`, `VERSION`, `DECISIONS.md`, `FINDINGS.md`, `docs/ROADMAP.md` and `LICENSE`.

**License**

MIT. See [LICENSE](LICENSE).

| You say | What happens |
|---|---|
| "Set up this repo" | It shows what it found and would add, then writes it on a setup branch for you to review and merge. |
| "Show me what setup would do first" | Every file it would add or convert is listed; nothing is written. |
| "Show me every setting" | Each repo and private setting, with its default and a one-line explanation. |
| "Fill in any missing settings" | Missing repo settings are added with their defaults; your own values are kept. |
| "Check this machine before setting up" | One checklist of git, python3, gh installed and signed in, real symlinks and the platform, each gap with its exact fix; a setup run prints it first and is never blocked by it. |
| "Replay the first adoption against the golden run" | The eight golden steps are compared with what this machine shows and it stops at the first mismatch, saying what differs; the live check-in step is reported as not observed, never passed. |
| "Which connectors do my repos need?" | Each connector a followed repo's PRDs name is listed as connected, needs sign-in or missing, and nothing is enabled for you. |
| "Install the reply hook" | Operation-session replies to a scheduled or asked-for check-in that don't follow the check-in layout are blocked, saying what is missing; it also installs a prompt hook that skips the model turn of a scheduled check-in when nothing changed. |
| "Is there a newer template version?" | It shows what the newest release brings and which skill files you changed here; nothing is written. |
| "Update this repo to the newest template" | The skills update, and this repo's new settings, entry point and agent files land on an update branch for you to merge; your own values and pages are kept. |
| "Send my skill fix back to the template" | It drafts one issue with the diff and no repo name, and files it once you say so. |
| "Wire the skills into CLAUDE.md and AGENTS.md" | Both files get the same block pointing every new session at `.loop/START.md`; your own text is kept. |
| "Set up a second machine" | `machine.py` in the clone lists the skill links, hooks, private-names file, mailer, check-in and scheduled tasks it would install; `apply` installs them and prints the owner checklist. |

Each requirement and how it is delivered:

- SET-1: One command adopts a repo. Example, from the adopt-set-1 test: given SET-1, when the toy adopt-and-update test runs, then it holds. Also (was SET-4): Updates flow both ways. Example, from the adopt-set-4 test: given SET-4, when the toy adopt-and-update test runs, then check shows the change, apply keeps the repo's data and lands the repo half on its branch. Also (was SET-6): Adoption is proven. Example, from the adopt-fixture-existing-checks test: given a repo whose config lists its own checks (pull request 83), when setup adopts it, then the written config keeps every check and the seeded row runs all of them.
- SET-2: Layered settings. Example, from the settings-reference test: given every repo and private setting, when the reference is read, then each is listed with its default and a one-line explanation.
- SET-10: The right format for every agent. Example, from the agents-wire test: given a repo, when setup or agents.py wire runs, then CLAUDE.md and AGENTS.md hold the same workflow-loop block, text outside it is kept, and a second run changes nothing.

### Skill: workflow-setup
- **Say:** "Set up this repo"
- **Command:** `/workflow-setup setup`

### Command: setup.py
- **Command:** `python3 skills/workflow-setup/scripts/setup.py [--dry-run]`
- **Dry run:** `--dry-run` lists every file it would add or convert and writes nothing.
- **Reads:** the repo and its settings.
- **Writes:** `.loop/` files, README and agent files on a setup branch.
- **Exit codes:** 0 on a ready repo; setup never blocks, and a refusal prints its fix.

### Command: setup.py desk
- **Command:** `python3 skills/workflow-setup/scripts/setup.py desk list`, `python3 skills/workflow-setup/scripts/setup.py desk run`, `python3 skills/workflow-setup/scripts/setup.py desk done STEP [STEP ...]`, and `python3 skills/workflow-setup/scripts/setup.py desk check`.
- **Dry run:** `list` and `check` report without writing; `run` lists open steps once and records that they were listed.
- **Reads:** machine-local step records, file existence, the agent command on PATH and the repo's worker settings.
- **Writes:** `run` and `done` update `~/.workflow-loop/desk.json` (or the folder set by `LOOP_DESK_HOME`); nothing in the repo.
- **Exit codes:** `list` and `run` return 0; `check` returns 0 with `DESK OK` or 1 with each `GAP`; `done` returns 2 for an unknown step.

### Command: unattended.py
- **Command:** `python3 skills/workflow-monitoring/scripts/unattended.py prerequisites` (also `replay` and `connectors`)
- **Dry run:** none needed: each part only reports.
- **Reads:** this machine's tools and the followed repos' PRDs.
- **Writes:** nothing.
- **Exit codes:** 0 after it prints its checklist; a gap is a `MISSING` line with its exact fix.

<!-- settings:begin -->
### Settings

Every repo setting from the template's settings reference, with this repo's value from `.loop/config.json`.

| Name | What it means | How to set it | Default | This repo |
|---|---|---|---|---|
| `base` | The branch goals start from and pull requests target. | set "base" in .loop/config.json | `main` | default |
| `agent_command` | The command that runs a goal in the background; the prompt is its last argument. | set "agent_command" in .loop/config.json | `[]` | **overridden:** `["claude", "-p", "--model=sonnet", "--allowedTools=Bash,Read,Write,Edit,Skill"]` |
| `check_slots` | Open PRs with unfinished checks allowed before a push. | set "check_slots" in .loop/config.json | `2` | default |
| `parallel` | Workers running at once; 0 means unlimited. | set "parallel" in .loop/config.json | `0` | default |
| `cadence` | Minutes between operation check-ins, 1 to 60, or off. | set "cadence" in .loop/config.json | `30` | **overridden:** `30` |
| `auto_approve` | true approves what a flow step leaves for the owner, logged auto-approved. | set "auto_approve" in .loop/config.json | `false` | **overridden:** `true` |
| `auto_merge` | true lets the release step merge a goal's PR and publish. | set "auto_merge" in .loop/config.json | `false` | **overridden:** `true` |
| `merge_queue` | true: GitHub's merge queue checks a moved base; merge.py waits for MERGED. | set "merge_queue" in .loop/config.json | `false` | default |
| `merge_batch` | true lets merge.py --batch merge 2-3 green goals as one. | set "merge_batch" in .loop/config.json | `false` | **overridden:** `true` |
| `review_hold` | true: merge.py waits (REVIEW_HOLD) for the operation session's review.py record. | set "review_hold" in .loop/config.json | `false` | default |
| `pr_bumps_version` | true moves the last version number once on a goal's branch. | set "pr_bumps_version" in .loop/config.json | `false` | default |
| `version_file` | The file holding the version; a release bumps it, writes the changelog. | set "version_file" in .loop/config.json | `VERSION` | default |
| `routines` | Commands the release step runs on the base before it merges. | set "routines" in .loop/config.json | `[]` | default |
| `regression_cron` | Five cron fields: when the full regression runs; off is off. | set "regression_cron" in .loop/config.json | `17 */4 * * *` | default |
| `health_cron` | Five cron fields: when health, the judge and its digest run on the Mac; or off. | set "health_cron" in .loop/config.json | `47 */4 * * *` | default |
| `judge_env` | No longer read. | set "judge_env" in .loop/config.json | `ANTHROPIC_API_KEY` | default |
| `judge_setup` | No longer read; old configs stay valid. | set "judge_setup" in .loop/config.json | `(empty)` | default |
| `digest_owner` | Who the digest comment mentions; empty is the repo owner (an organisation: none). | set "digest_owner" in .loop/config.json | `(empty)` | default |
| `digest_mail` | How the round's digest is mailed: cloudflare, smtp or off; keys live only in Actions secrets. | set "digest_mail" in .loop/config.json | `cloudflare` | default |
| `smtp_host` | The SMTP server digest_mail smtp uses (with the DIGEST_SMTP_* secrets). | set "smtp_host" in .loop/config.json | `smtp.gmail.com` | default |
| `smtp_port` | 465 (TLS) or 587 (STARTTLS) for digest_mail smtp. | set "smtp_port" in .loop/config.json | `465` | default |
| `review_depth` | full runs the whole plan and review pipeline and refuses a condensed one; condensed allows a shorter run. | set "review_depth" in .loop/config.json | `full` | default |
| `criteria` | true makes docs check enforce the PRD page contract (Problem, Requirements, Non-goals, Success metrics, Tests). | set "criteria" in .loop/config.json | `true` | default |
| `criteria_max` | Most criteria a wiki page may hold, 1 to 50; docs check and health fail a page over it. | set "criteria_max" in .loop/config.json | `10` | **overridden:** `24` |
| `wiki_dir` | The folder of wiki pages. | set "wiki_dir" in .loop/config.json | `docs/wiki` | default |
| `risky_paths` | Regexes for paths whose goals need extra care. | set "risky_paths" in .loop/config.json | `["^\\.github/", "(^|/)auth", "(^|/)migrations?/", "(^|/)(schema|data)\\b"]` | default |
| `step_limit` | Seconds a flow step may run when the flow file sets none; 0 is built-in. | set "step_limit" in .loop/config.json | `0` | default |
| `goal_levels` | Row levels a goal lane plans from: land, or nightly (land and nightly rows). | set "goal_levels" in .loop/config.json | `land` | default |
| `regression_runs` | Where the full regression runs: actions (public repo) or mac (private repo, each Mac tick); setup records it. | set "regression_runs" in .loop/config.json | `(empty)` | **overridden:** `actions` |
| `machine_setup` | Machine setup items (allow, routine, secret, connector) machine.py applies on adoption. | set "machine_setup" in .loop/config.json | `[]` | default |
| `automation` | Routines the Automation table lists: {name, does, cadence, runs}. | set "automation" in .loop/config.json | `[]` | **overridden:** `[{"name": "health", "does": "Checks the repo, files findings.", "cadence": "47 */4 * * *", "runs": "mac:agent-workflow-template-health-regression"}, {"name": "regression", "does": "Runs the regression rows.", "cadence": "17 */4 * * *", "runs": "mac:agent-workflow-template-health-regression"}, {"name": "digest email", "does": "Mails the round's digest.", "cadence": "with each health round", "runs": "mac:agent-workflow-template-health-regression"}]` |
| `topics` | Home's Topic column: {topic: [feature pages]} in order; unlisted pages go under Other; empty is no column. | set "topics" in .loop/config.json | `{}` | **overridden:** `{"Build loop": ["Delivery", "Monitoring", "Operation", "Check-in-and-board"], "Quality": ["Regression", "Health", "Guardrails"], "Operations": ["Automation", "Setup", "Machines"], "Docs": ["Documentation"]}` |
| `ci_levels` | Target of scheduled and tag regression runs: nightly (every row) or land. | set "ci_levels" in .loop/config.json | `nightly` | default |
| `time_budget_minutes` | Active minutes before no new step starts; 0 is none. | set "time_budget_minutes" in .loop/config.json | `240` | default |
| `max_merge_rounds` | Merge rounds goal.py pr may take before it waits. | set "max_merge_rounds" in .loop/config.json | `8` | default |
| `max_active_goals` | Goals live at once (or parallel, if smaller); 0 is none. | set "max_active_goals" in .loop/config.json | `20` | default |
| `plan_pause_percent` | Weekly plan % above which no goal starts; 0 is off. | set "plan_pause_percent" in .loop/config.json | `80` | default |
| `min_free_memory_gb` | Free GB below which no lane or goal starts; 0 off. | set "min_free_memory_gb" in .loop/config.json | `3` | default |
| `eta_margin_percent` | Percent added to a goal's estimate for its hard ETA, 0 to 300. | set "eta_margin_percent" in .loop/config.json | `25` | default |
| `token_budget` | Tokens a goal may spend before no new step starts; 0 means none. | set "token_budget" in .loop/config.json | `0` | **overridden:** `3000000` |
| `max_regression_rows` | Most rows the regression table may hold; qa refuses a goal over it. | set "max_regression_rows" in .loop/config.json | `1200` | **overridden:** `1300` |
| `max_suite_seconds` | Longest the full suite may take (slowest of the last 3 runs); qa refuses a goal over it. | set "max_suite_seconds" in .loop/config.json | `1900` | **overridden:** `2800` |
| `test_budget_minutes` | Minutes one in-loop test run may take, 15 or more; later rows wait for the full suite. | set "test_budget_minutes" in .loop/config.json | `15` | default |
| `prep_budget_minutes` | Minutes a lane may spend before its first test row, 15 or more; past it, it stops. | set "prep_budget_minutes" in .loop/config.json | `15` | **overridden:** `25` |
| `step_budget_minutes` | Minutes one review or ship step may take, 15 or more. | set "step_budget_minutes" in .loop/config.json | `30` | default |
| `stale_branch_days` | Days a local branch on no remote may sit before health lists it. | set "stale_branch_days" in .loop/config.json | `14` | default |
| `mend` | true lets watch start a fresh agent for a failed goal. | set "mend" in .loop/config.json | `false` | **overridden:** `true` |
| `mend_wait` | Seconds a failed goal waits before a mender starts. | set "mend_wait" in .loop/config.json | `120` | default |
| `max_tries` | Failed tries a goal gets before it stops and files a finding. | set "max_tries" in .loop/config.json | `3` | default |
| `resume_on_limit` | true lets watch resume a goal that hit a usage limit. | set "resume_on_limit" in .loop/config.json | `false` | default |
| `limit_wait` | Seconds to wait after a usage limit before resuming. | set "limit_wait" in .loop/config.json | `1800` | default |
| `watch_interval` | Seconds between rounds of watch. | set "watch_interval" in .loop/config.json | `20` | default |
| `agent_files` | Agent entry files setup wires the loop block into; [] turns wiring off. | set "agent_files" in .loop/config.json | `["CLAUDE.md", "AGENTS.md"]` | default |
| `template_repo` | The template's GitHub repo (owner/name) update reads releases from, if the package names none. | set "template_repo" in .loop/config.json | `(empty)` | **overridden:** `Charlie-org146/agent-workflow-template` |
| `milestones_source` | Opt-in: url:<link> or mcp:<server>:<id> (mcp:notion: plus 32 hex), an outside Milestones page docs sync follows. | set "milestones_source" in .loop/config.json | `(empty)` | default |
| `reply_hook` | false turns off the reply-format hook (setup.py --reply-hook installs it) in the operation session. | set "reply_hook" in .loop/config.json | `true` | default |
| `govern_hook` | false turns off the govern-only hook (edits, commits, pushes refused in the operation session). | set "govern_hook" in .loop/config.json | `true` | default |
| `full_auto` | Off keeps every gate; true lets the operation session take a worker's recommended option, safety ones wait. | set "full_auto" in .loop/config.json | `false` | **overridden:** `true` |
| `pool_size` | Idle worker sessions the pool keeps; low, the operation session asks you for more. | set "pool_size" in .loop/config.json | `20` | default |
| `silent_minutes` | Minutes a worker may send nothing before it shows under Needs you; LOOP_SESSION_QUIET (seconds) overrides. | set "silent_minutes" in .loop/config.json | `30` | default |
| `health_script_bytes` | Script size health fails, in bytes (warns at 90%). | set "health_script_bytes" in .loop/config.json | `20480` | default |
| `health_skill_lines` | SKILL.md line cap health fails. | set "health_skill_lines" in .loop/config.json | `150` | default |
| `feature_labels` | true tags each health and regression issue feature:<Page>, creating the label. | set "feature_labels" in .loop/config.json | `false` | default |
| `workers` | app: no background process; a goal no session took waits for sessions.py bind. auto: a background agent when no session can start. | set "workers" in .loop/config.json | `(empty)` | **overridden:** `app` |
<!-- settings:end -->

## URLs and deployments

- Wiki: [Setup](https://github.com/Charlie-org146/agent-workflow-template/wiki/Setup)
- Milestone: [Setup](https://github.com/Charlie-org146/agent-workflow-template/milestone/9)
- Releases: https://github.com/Charlie-org146/agent-workflow-template/releases

## Links

- PRD page: [Setup](Setup)
- Backlog: [Backlog: Setup](https://github.com/Charlie-org146/agent-workflow-template/milestones)

<!-- kept machine-email-phone@9a67a8ff -->
<!-- kept safety-fixes@585daa17 -->

<!-- kept rel-15-queue@88a93af7b -->
