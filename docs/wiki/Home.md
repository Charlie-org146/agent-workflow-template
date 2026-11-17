<!-- workflow-docs -->
# agent-workflow-template

## Features

| Topic | Feature | What it does | How to use | Milestone |
|---|---|---|---|---|
| Build loop | [Delivery](Delivery) | Takes one sentence and its done lines to a merged, released pull request (a draft release you publish when auto_merge is off), unattended, through your own skills or its built-in routine, on Linux, macOS and native Windows, with pull requests queued only behind goals that share files and ready ones merged in batches, and it refuses to merge only for a wiki page its own diff made stale. | [How to use Delivery](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Delivery) | [Delivery](https://github.com/jcl2018/agent-workflow-template/milestone/1) |
| Build loop | [Monitoring](Monitoring) | One session governs many goals at once and shows a live board of what's running and what needs you, and each check-in draws live goals with their time left and waits, with this machine's status; it records the owner's own words for workers to use (owner-words), with one pr queue order every goal sees; its Needs you ranks each item by the goals it holds up, most first (MON-19); it keeps running unattended, counting the sends left before the app's cap, re-creating its check-in loop before it expires, applying one standing merge instruction and listing what is missing at start, and the board lists each open PRD delta of an opted-in page as waiting on you. | [How to use Monitoring](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Monitoring) | [Monitoring](https://github.com/jcl2018/agent-workflow-template/milestone/6) |
| Quality | [Guardrails](Guardrails) | Lists every guardrail the template has or needs, each with what it protects against, its owner, its setting and the health check that must prove it is on, including the memory floor before a goal starts (owner records o1, o3) and each goal's hard ETA (GRD-14, owner record o52). | [How to use Guardrails](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Guardrails) | [Guardrails](https://github.com/jcl2018/agent-workflow-template/milestone/11) |
| Quality | [Health](Health) | Checks the repo with fixed rules and a full reviewer, and files every finding as an issue tagged with its group and its feature (Other when none), a defect or a backlog item on its feature's Backlog milestone (an old Backlog milestone becomes Backlog: Other); triage closes one finding by its issue number, and a review finding that cites no file line or test row is dropped; the roadmap's V1 section says what green on main still needs. It also reads a dated matrix of smoke runs, so an agent or machine that was never proven shows up. | [How to use Health](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Health) | [Health](https://github.com/jcl2018/agent-workflow-template/milestone/4) |
| Quality | [Regression](Regression) | Keeps every requirement and defect tied to a test that runs, and shows the results, including red proof recorded from another runner or owed to another machine, without blocking a goal. | [How to use Regression](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Regression) | [Regression](https://github.com/jcl2018/agent-workflow-template/milestone/7) |
| Operations | [Automation](Automation) | Runs health on your always-on machine (the Mac, or a Windows PC with `local register`; the digest's mail file can be named with `LOOP_MAIL_ENV`) and regression in GitHub Actions for a public repo or on your Mac for a private one, every 4 hours by default, plus any routine a repo adds with one config entry, each with a Runbook in the repo that its one-line scheduled prompt points to; files each failure and finding as an issue tagged with its group and its feature (Other when none), and emails you one digest per round; the CI suite runs in eight shards with one combined summary; each routine declares the permissions it needs in `.loop/permissions.tsv`, setup writes them into the project settings and the docs check keeps them in step with its Runbook. | [How to use Automation](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Automation) | [Automation](https://github.com/jcl2018/agent-workflow-template/milestone/10) |
| Operations | [Machines](Machines) | Brings a second Mac or Windows machine to this one's setup from a git clone and one command: skills, hooks, the empty private-names file, the unattended mailer, one health-and-regression task per repo, and a check that lists every gap; what only the owner can do (logins, secrets, the permission mode) is a numbered checklist. | [How to use Machines](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Machines) | [Machines](https://github.com/jcl2018/agent-workflow-template/milestone/23) |
| Operations | [Setup](Setup) | Turns any repo into a ready workspace for any agent without ever blocking, judged by health before and after, keeps it in step with the template, adopts several repos in one pass through `board.py repos adopt`, and lists, with the exact instruction, what the owner must still do on a new machine. | [How to use Setup](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Setup) | [Setup](https://github.com/jcl2018/agent-workflow-template/milestone/9) |
| Docs | [Documentation](Documentation) | Keeps the wiki and README in one enforced format (feature pages are PRDs with no Usage section; each feature's How-to-use page, with a short start in the README's How to use tables and each skill's command reference, covers usage), and publishes them on every release; the README's Automation rows follow the Automation requirements and show health on the Mac's local schedule; a PRD the owner opts in, at a `url:` or `mcp:` source, is kept as a copy in the repo, `.loop/prd/PAGE.md`, which every check reads and the page shows as a generated block, and `docs.py sync` keeps it in step with the source, showing every difference as a delta and a change on both sides as a conflict (DOC-17). | [How to use Documentation](https://github.com/jcl2018/agent-workflow-template/wiki/How-to-use-Documentation) | [Documentation](https://github.com/jcl2018/agent-workflow-template/milestone/3) |

<!-- settings:begin -->
## Settings

Every repo setting from the template's settings reference, with this repo's value from `.loop/config.json`.

| Name | What it means | How to set it | Default | This repo |
|---|---|---|---|---|
| `base` | The branch goals start from and pull requests target. | set "base" in .loop/config.json | `main` | default |
| `agent_command` | The command that runs a goal in the background; the prompt is its last argument. | set "agent_command" in .loop/config.json | `[]` | **overridden:** `["claude", "-p", "--model=sonnet", "--allowedTools=Bash,Read,Write,Edit,Skill"]` |
| `parallel` | Workers running at once; 0 means unlimited. | set "parallel" in .loop/config.json | `0` | default |
| `cadence` | Minutes between check-ins of the operation session, 1 to 60, or off. | set "cadence" in .loop/config.json | `30` | **overridden:** `30` |
| `auto_approve` | true approves what a flow step leaves for the owner, logged as auto-approved. | set "auto_approve" in .loop/config.json | `false` | **overridden:** `true` |
| `auto_merge` | true lets the release step merge a goal's pull request and publish. | set "auto_merge" in .loop/config.json | `false` | **overridden:** `true` |
| `review_hold` | true: merge.py waits (REVIEW_HOLD) for the operation session's review.py record. | set "review_hold" in .loop/config.json | `false` | default |
| `pr_bumps_version` | true moves the last number of the version file once on a goal's branch. | set "pr_bumps_version" in .loop/config.json | `false` | default |
| `version_file` | The file that holds the version; a release bumps it and writes the changelog. | set "version_file" in .loop/config.json | `VERSION` | default |
| `routines` | Commands the release step runs on the base branch before it merges. | set "routines" in .loop/config.json | `[]` | default |
| `regression_cron` | Five cron fields: when the full regression runs; off is off. | set "regression_cron" in .loop/config.json | `17 */4 * * *` | default |
| `health_cron` | Five cron fields: when health, the judge and its digest run on the Mac; off is off. | set "health_cron" in .loop/config.json | `47 */4 * * *` | default |
| `judge_env` | No longer read. | set "judge_env" in .loop/config.json | `ANTHROPIC_API_KEY` | default |
| `judge_setup` | No longer read: kept so old configs stay valid. | set "judge_setup" in .loop/config.json | `(empty)` | default |
| `digest_owner` | Who the digest comment mentions; empty means the repo owner (an organisation notifies none). | set "digest_owner" in .loop/config.json | `(empty)` | default |
| `digest_mail` | How the round's digest is mailed: cloudflare, smtp or off; keys live only in Actions secrets. | set "digest_mail" in .loop/config.json | `cloudflare` | default |
| `smtp_host` | The SMTP server digest_mail smtp sends through (with the DIGEST_SMTP_* secrets). | set "smtp_host" in .loop/config.json | `smtp.gmail.com` | default |
| `smtp_port` | 465 (TLS) or 587 (STARTTLS) for digest_mail smtp. | set "smtp_port" in .loop/config.json | `465` | default |
| `review_depth` | full runs the whole plan and review pipeline and refuses a condensed one; condensed allows a shorter run. | set "review_depth" in .loop/config.json | `full` | default |
| `criteria` | true makes docs check enforce the PRD page contract (Problem, Requirements, Non-goals, Success metrics, Tests). | set "criteria" in .loop/config.json | `true` | default |
| `criteria_max` | Most criteria a wiki page may hold, 1 to 50, default 10; docs check and health fail a page over it. | set "criteria_max" in .loop/config.json | `10` | **overridden:** `19` |
| `wiki_dir` | The folder of wiki pages. | set "wiki_dir" in .loop/config.json | `docs/wiki` | default |
| `risky_paths` | Regexes for paths whose goals need extra care. | set "risky_paths" in .loop/config.json | `["^\\.github/", "(^|/)auth", "(^|/)migrations?/", "(^|/)(schema|data)\\b"]` | default |
| `step_limit` | Seconds one flow step may run when the flow file sets no limit; 0 means the built-in limit. | set "step_limit" in .loop/config.json | `0` | default |
| `goal_lane_minutes` | Minutes a goal's regression lane may take before health warns and its LANE line says over. | set "goal_lane_minutes" in .loop/config.json | `10` | default |
| `goal_levels` | Row levels a goal lane plans from: land, or nightly for land and nightly rows. | set "goal_levels" in .loop/config.json | `land` | default |
| `regression_runs` | Where the full regression runs: actions (public repo) or mac (private repo, each Mac tick); setup records it and keeps a recorded mac. | set "regression_runs" in .loop/config.json | `(empty)` | **overridden:** `actions` |
| `machine_setup` | Machine setup items (allow, routine, secret, connector) machine.py applies where this repo is adopted. | set "machine_setup" in .loop/config.json | `[]` | default |
| `automation` | Routines the Automation table lists: {name, does, cadence, runs}. | set "automation" in .loop/config.json | `[]` | **overridden:** `[{"name": "health", "does": "Checks the repo, files findings.", "cadence": "47 */4 * * *", "runs": "mac:agent-workflow-template-health-regression"}, {"name": "regression", "does": "Runs the regression rows.", "cadence": "17 */4 * * *", "runs": "mac:agent-workflow-template-health-regression"}, {"name": "digest email", "does": "Mails the round's digest.", "cadence": "with each health round", "runs": "mac:agent-workflow-template-health-regression"}]` |
| `topics` | Home's Topic column: {topic: [feature pages]}, in this order; unlisted pages go under Other; empty means no column. | set "topics" in .loop/config.json | `{}` | **overridden:** `{"Build loop": ["Delivery", "Monitoring"], "Quality": ["Regression", "Health", "Guardrails"], "Operations": ["Automation", "Setup", "Machines"], "Docs": ["Documentation"]}` |
| `ci_levels` | Target of the scheduled and tag regression runs: nightly (every row) or land. | set "ci_levels" in .loop/config.json | `nightly` | default |
| `time_budget_minutes` | Active minutes before no new step starts; 0 is none. | set "time_budget_minutes" in .loop/config.json | `240` | default |
| `max_merge_rounds` | Merge rounds goal.py pr may take before the goal waits. | set "max_merge_rounds" in .loop/config.json | `8` | default |
| `max_active_goals` | Goals live at once (or parallel, if smaller); 0 is none. | set "max_active_goals" in .loop/config.json | `20` | default |
| `plan_pause_percent` | Weekly plan % above which no goal starts (pool.py usage N); 0 is off. | set "plan_pause_percent" in .loop/config.json | `80` | default |
| `min_free_memory_gb` | Free GB below which no lane or goal starts; 0 off. | set "min_free_memory_gb" in .loop/config.json | `4` | **overridden:** `3.0` |
| `eta_margin_percent` | Percent added to a goal's estimate for its hard ETA, 0 to 300; a goal's ETA is fixed when it is frozen. | set "eta_margin_percent" in .loop/config.json | `25` | default |
| `token_budget` | Tokens a goal may spend before no new step starts; 0 means none. | set "token_budget" in .loop/config.json | `0` | **overridden:** `3000000` |
| `max_regression_rows` | Most rows the regression table may hold; a goal adding rows past it is refused at qa. | set "max_regression_rows" in .loop/config.json | `1200` | default |
| `max_suite_seconds` | Longest the full suite may take (slowest of the last 3 runs); a goal adding rows past it is refused at qa. | set "max_suite_seconds" in .loop/config.json | `1900` | default |
| `test_budget_minutes` | Minutes one in-loop test run may take, 15 or more; rows past it wait for the full suite. | set "test_budget_minutes" in .loop/config.json | `15` | default |
| `prep_budget_minutes` | Minutes a lane may spend before its first test row, 15 or more; a lane past it stops. | set "prep_budget_minutes" in .loop/config.json | `15` | **overridden:** `25` |
| `step_budget_minutes` | Minutes one review or ship step may take, 15 or more; a step at its limit finishes what it has. | set "step_budget_minutes" in .loop/config.json | `30` | default |
| `stale_branch_days` | Days a local branch on no remote may sit before health lists it. | set "stale_branch_days" in .loop/config.json | `14` | default |
| `mend` | true lets watch start a fresh agent for a failed goal. | set "mend" in .loop/config.json | `false` | **overridden:** `true` |
| `mend_wait` | Seconds a failed goal waits before a mender starts. | set "mend_wait" in .loop/config.json | `120` | default |
| `max_tries` | Failed tries a goal gets before it stops and files a finding. | set "max_tries" in .loop/config.json | `3` | default |
| `resume_on_limit` | true lets watch resume a goal that hit a usage limit. | set "resume_on_limit" in .loop/config.json | `false` | default |
| `limit_wait` | Seconds to wait after a usage limit before resuming. | set "limit_wait" in .loop/config.json | `1800` | default |
| `watch_interval` | Seconds between rounds of watch. | set "watch_interval" in .loop/config.json | `20` | default |
| `agent_files` | Agent entry files setup wires the workflow-loop block into; [] turns wiring off. | set "agent_files" in .loop/config.json | `["CLAUDE.md", "AGENTS.md"]` | default |
| `template_repo` | The template's GitHub repo (owner/name) update reads releases from, when the installed package names none. | set "template_repo" in .loop/config.json | `(empty)` | default |
| `reply_hook` | false turns off the reply-format hook (setup.py --reply-hook installs it) in the operation session. | set "reply_hook" in .loop/config.json | `true` | default |
| `govern_hook` | false turns off the govern-only hook: edits, commits and pushes are refused in the operation session. | set "govern_hook" in .loop/config.json | `true` | default |
| `full_auto` | true lets the operation session answer a worker's routine decision with its recommended option; risky ones wait. | set "full_auto" in .loop/config.json | `true` | default |
| `pool_size` | Idle worker sessions the pool keeps; when it runs low the operation session asks you to create more. | set "pool_size" in .loop/config.json | `20` | default |
| `silent_minutes` | Minutes a worker may send nothing before it shows under Needs you; LOOP_SESSION_QUIET (seconds) overrides. | set "silent_minutes" in .loop/config.json | `30` | default |
| `health_script_bytes` | Script size health fails, in bytes (warns at 90%). | set "health_script_bytes" in .loop/config.json | `20480` | default |
| `health_skill_lines` | SKILL.md line cap health fails. | set "health_skill_lines" in .loop/config.json | `150` | default |
| `feature_labels` | true tags each health and regression issue feature:<Page>, creating the label. | set "feature_labels" in .loop/config.json | `false` | default |
| `workers` | app: app sessions only; no background process starts; a goal no session took waits for sessions.py bind. | set "workers" in .loop/config.json | `(empty)` | **overridden:** `app` |
<!-- settings:end -->

<!-- automation:begin -->
## Automation

Health and regression, then each `automation` entry in `.loop/config.json`; to add one, add an entry.

| Routine | What it does | State | Cadence | Runs on | Last run | Owed by you |
|---|---|---|---|---|---|---|
| [health](https://github.com/jcl2018/agent-workflow-template/wiki/Health#health-round) | Checks the repo, files findings. | on (declared) | every 4 hours | this Mac (launch agent agent-workflow-template-health-regression) | docs.py automation | confirm it is live: docs.py automation |
| [regression](https://github.com/jcl2018/agent-workflow-template/wiki/Regression#regression-round) | Runs the regression rows. | on (declared) | every 4 hours | this Mac (launch agent agent-workflow-template-health-regression) | docs.py automation | confirm it is live: docs.py automation |
| digest email | Mails the round's digest. | on (declared) | cron `with each health round` | this Mac (launch agent agent-workflow-template-health-regression) | docs.py automation | confirm it is live: docs.py automation |
<!-- automation:end -->
