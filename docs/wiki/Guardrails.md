<!-- workflow-docs -->
# Guardrails

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/11

Review: **Unreviewed** <!-- kept hotfix-4892@4e2ea952 -->

How to use: [How-to-use-Guardrails](How-to-use-Guardrails)

## Problem

- My  guardrails are scattered across six features, some are promised but not built, and I can't see in one place what protects me, where it is enforced and whether it is on.
- Runs can quietly cost too much: CI minutes on superseded or no-code runs, a step spending far more tokens than usual, a run going far longer than usual.
- I want one set of guardrails that the health checks prove are on and that every adopted repo gets, each one showing what it protects against, where it lives and the setting that controls it.

## Requirements

### Functional

- GRD-1: **Reviewed 2026-11-13** One visible set of guardrails, each with its protection, owner, setting and health check <!-- reviewed 22acc59d -->
  - This page is an index: it lists every guardrail the template has or needs, each with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on.
  - Each guardrail points to the requirement id that owns it (DEL-8, REG-7, DEL-9, SET-8, MON-7, MON-8) and says "new" where none does yet; the page restates none of the owner's text, which holds the exact wording.
  - A guardrail counts as on only when its Tests row here passes; until then it reads not enforced.
- GRD-2: **Unreviewed** Time and token budgets stop a goal or a step before it runs away
  - Review and ship step time limit: DEL-8.
  - In-loop test run time limit: REG-7.
  - The work before a lane's first test row (preparing, planning and waiting for a slot) stops at `prep_budget_minutes` (default 15, never under 15; this repo sets 25); the lane says which part ran long and the goal can rerun it (Delivery, Regression).
  - A goal past `time_budget_minutes` starts no new step, and the setting is in the settings reference with its default (Delivery, new).
  - A goal past `token_budget` starts no new step, whether its steps run in a session or headless (Delivery, DEL-8 for showing it on the board; new for steps run in a session: today only headless goals are refused).
  - A goal with no token count records "unknown" and the board shows "tokens unread", never 0, so an unread count is never mistaken for an unspent budget (Delivery, new).
  - Each worker step's tokens are read from its session transcript when it is recorded (input, cache reads, cache writes, output, calls, model and the largest context), kept in the run record and listed by `goal.py show`; `token_budget` counts the fresh part (input, cache writes and output, not cache reads) of those measured tokens, plus what the step in progress has spent so far (Delivery, token-diet).
  - A loop script's output is cut to 2,000 characters, the first half and the last half with a line naming the file that keeps the whole text, so a long result does not fill a session's context; the step prompt a worker must read whole is not cut (Delivery, token-diet).
- GRD-3: **Reviewed 2026-11-15** Nothing private is committed, and no commit skips the hooks that check it <!-- reviewed eecc70d8 -->
  - Private-name scan on every commit and push: DEL-9.
  - A commit or push that skips the repo's hooks (a no-verify flag, an empty hooks path) is refused by the loop's own commands and flagged by health (Delivery, new).
  - Where the scanned names live: SET-8 (SET-2 for the private layer).
  - A private-name line may be scoped with `@public` or `@repos=a,b`, so a private repo can hold a name a public one must never show; an unscoped line applies everywhere (Delivery, DEL-9).
- GRD-4: **Reviewed 2026-11-13** A worker writes only its own goal's work, never shared loop state or its own limits <!-- reviewed 2267af49 -->
  - A worker can't widen its own goal's touches, resume itself or change its own budget; only the operation session can (Delivery, new: today a role check, not a boundary).
  - A worker changes shared loop state only for its own goal and only through the goal's commands (`goal.py step`, `record` and `pr`, `sessions.py bind` and `report`); the queue, other goals' run records and the session pool's other sessions are the operation session's to change (Monitoring, new: today the commands scope a worker to its own slug, and nothing stops a hand edit).
  - The operation session never edits code, commits or pushes: MON-7.
- GRD-5: **Reviewed 2026-11-13** Nothing is written to GitHub without an explicit `--live` <!-- reviewed 197dd819 -->
  - Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit `--live` switch; a token in the environment does not turn writing on (Health, HLT-4, REG-5 and AUT-5 hold the wording; Regression new: today it writes whenever a token is present).
  - The scheduled workflows pass `--live`; the page of each such command says so (each owner, new).
- GRD-6: **Reviewed 2026-11-13** The base branch is protected and merges only with its required checks green <!-- reviewed 82216f02 -->
  - The base branch refuses direct pushes and force pushes, and a pull request merges only when the repo's required checks pass; I set those rules on the platform, and setup never edits a ruleset or branch protection (it names, as BLOCKS, a required check no commit status can satisfy: Setup, SET-1).
  - Where the platform can enforce it (branch rules, required status checks), the platform does, and health reads that it is set (Health, new).
- GRD-7: **Reviewed 2026-11-13** CI spends minutes only on runs that matter, and too many runs raise an alarm <!-- reviewed d26f9f97 -->
  - A newer run of the same workflow on the same branch cancels the one it supersedes (Automation, new: the workflows queue runs today).
  - A heavy job is skipped for a change that touches no code, such as docs only (Automation, new).
  - Each round shows its Actions minutes and goes over its limit loudly (Automation, AUT-7); runs or minutes per day past a set limit raise one alarm (Automation, new).
- GRD-8: **Reviewed 2026-11-13** A step far past its usual tokens or time is flagged while it runs <!-- reviewed 2dcdc9cb -->
  - A step whose tokens pass a set multiple of that step's usual is flagged on the board and in the check-in (Monitoring, new).
  - A step past three times its estimate is shown as stalled under Issues on the board (Monitoring, MON-4, which keeps a stuck worker at the top of Issues), and a worker silent past `silent_minutes` shows under Needs you: MON-8.
  - A goal's test lane past `goal_lane_minutes` (default 10) says so in its LANE line (Regression, REG-8).
- GRD-9: **Reviewed 2026-11-13** Health proves every guardrail is present and working, each rule with a negative control <!-- reviewed 97e6018b -->
  - Each guardrail has a health rule that reads whether it is present and working, in an existing group (Performance, Security and privacy, Hygiene or Adoption), within the cap of 12 groups (Health, HLT-2).
  - Each such rule has a negative control run against a deliberately broken copy, so it is known to fire (Health, HLT-2, Controls).
  - A guardrail its rule can't read shows as unread, never as passing (Health, HLT-3).
  - A page's requirement cap, `criteria_max` (17 in this repo), is read by health's Size group, so a page too large to review shows as a finding.
- GRD-10: **Reviewed 2026-11-13** Setup installs the whole set when a repo is adopted, and health judges it <!-- reviewed c53adea9 -->
  - Adopting a repo installs every guardrail on this page with its default setting, and setup lists each one it installed (Setup, SET-1 for installing; listing each one is new).
  - Health judges a freshly adopted repo's guardrails on the same rules as the template's (Setup, SET-1).
- GRD-11: **Reviewed 2026-11-13** A goal depends only on what its own machine can do <!-- reviewed c1c9c836 -->
  - A step only another machine can do (a red proof on another platform, a smoke cell, a Mac-only check) is filed as a to-do issue on the feature's milestone and never blocks the goal, its merge or the release.
  - A row whose red proof needs another platform is recorded owed (Regression, `red ID --owed --runner R`): it reads PENDING, opens one `other-machine` to-do on its feature milestone, and its goal merges.
  - Health warns on an owed proof older than 7 days and never fails on it (Health); the check-in lists owed items under Coming up, and the operation session never holds a goal for another pod or machine (Monitoring).
- GRD-12: **Reviewed 2026-11-14** The machine's status is read every round, and no goal starts under the memory floor. <!-- reviewed 0b68aa9f -->
  - Each check-in reads free RAM, free commit memory, CPU and the number of claude and node processes (Monitoring, MON-16). A goal starts only while free commit memory is at or above `min_free_memory_gb` (default 3.5, in `.loop/config.json`; 0 turns the floor off). The pool creates no session and the board holds every ready goal as "memory low" until memory frees up. A figure that can't be read never blocks a start.
- GRD-13: **Reviewed 2026-11-16** Regression rows and full-suite time are capped, and going over a cap blocks delivery (owner record o51) <!-- reviewed 89fdf6a8 -->
  - `max_regression_rows` (default 1200) and `max_suite_seconds` (default 1900) are settings in `.loop/config.json`, shown in Home's settings table (Setup, SET-1).
  - A goal whose rows take the repo over either cap is refused at qa, with the numbers, unless it removes or merges at least as many rows as it adds, or the owner raises the cap in their own words; a goal that only consolidates is always allowed. The caps read are the base branch's, so a goal can't raise its own (GRD-4).
  - Health shows the rows and the slowest full-suite time against both caps, warns at 90% and fails over the cap, and each rule has a negative control (GRD-9).
- GRD-14: **Reviewed 2026-11-16** A goal's ETA is a hard limit: past it the owner chooses ship now, extend once or defer <!-- reviewed 43180cea -->
  - Owner o52 (2026-11-15): the ETA is a hard criterion so goals stop sliding. Every goal records an ETA when it is frozen: the estimate model's high end plus a 25 percent margin, or the time budget when there is no estimate. It sits in the run record and as an ETA line in the goal file, and the check-in shows it for every goal.
  - A goal past its ETA may finish the step it is on, starts no new step and appears under Needs you with three choices: ship now with what is done (the steps left are recorded as skipped and named in the pull request), extend once by an amount in the owner's own words, or move it to the next release.
  - goal.py refuses to extend an ETA or raise a time or token budget without an owner-words record that covers the goal and has not been used; the operation session alone cannot.
  - Health warns on a live goal with no ETA, fails on an ETA extended without a record, and fails on a goal past its ETA that is not under Needs you; each rule has a negative control.
  - Pre-flight: when a goal is frozen, every owner decision it can foresee goes on one Needs you line, each with its options and a recommendation. Until you answer, the ETA reads "after your answers", and the hard ETA counts from your answers. At the pull-request step, a refusal the freeze list didn't foresee (the private-name scan, the memory floor) is logged as a missed pre-flight item.

### Non-functional

None

## Non-goals

- No code here: each guardrail is built by its owner feature's own goal; this page only defines the set.
- This page never says a guardrail is on; the Tests table does, from passing regression rows.

## Success metrics

- Every guardrail is on this page with its owner, setting and health check, each pointing to its owner's requirement for the exact wording.
- Each guardrail's Tests row passes.
- A freshly adopted repo has every guardrail on with its default setting.

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [grd1-guardrail-list](Tests#t-grd1-guardrail-list) | requirement | GRD-1 | Given the Guardrails page, when it is read, then it lists every guardrail with its protection, owner, setting and health check (not built: the page is a definition only). | not run |
| [config-holds-topics](Tests#t-config-holds-topics) | requirement | GRD-1 | Given the repo's config, when the settings are shown, then topics is held in the committed config. | PASS 2026-11-14 |
| [reg7-budget-leaves](Tests#t-reg7-budget-leaves) | requirement | GRD-2 | Given rows that would run past the test budget, when a loop test run happens, then it runs the rows that fit, stops at the budget and lists every row it left. | not run |
| [del8-step-stops](Tests#t-del8-step-stops) | requirement | GRD-2 | Given a review or ship step that reaches its limit, when it is stopped, then it is recorded done with what it left and the goal goes on without a failed try. | not run |
| [grd2-step-budget](Tests#t-grd2-step-budget) | requirement | GRD-2 | Given a review or ship step that reaches step_budget_minutes, when it is stopped, then it records done with what it left and costs no failed try. | not run |
| [grd2-test-budget](Tests#t-grd2-test-budget) | requirement | GRD-2 | Given an in-loop test run that reaches test_budget_minutes, when it stops, then it runs rows in order until the budget and lists the rest for the scheduled full suite. | not run |
| [grd2-goal-over](Tests#t-grd2-goal-over) | requirement | GRD-2 | Given a goal past its time and token budget, when the live board prints, then it flags OVER time and OVER tokens. | not run |
| [tokens-unread-shown](Tests#t-tokens-unread-shown) | requirement | GRD-2 | Given a goal with no token count, when the board or the pull request shows its spend, then it says tokens unread, never 0, and a goal with a count shows the number. | not run |
| [grd2-time-stop](Tests#t-grd2-time-stop) | requirement | GRD-2 | Given a goal past time_budget_minutes, when a step or goal.py pr is asked for, then it is refused with one line naming goal.py set. | not run |
| [grd2-token-stop](Tests#t-grd2-token-stop) | requirement | GRD-2 | Given a goal past token_budget, when a step is asked for, then it is refused with one line naming goal.py set. | not run |
| [grd2-tokens-unknown](Tests#t-grd2-tokens-unknown) | requirement | GRD-2 | Given a session worker that passes unknown tokens, when the step is recorded, then the goal reads tokens unread, never 0. | not run |
| [grd2-merge-rounds](Tests#t-grd2-merge-rounds) | requirement | GRD-2 | Given a goal that merged the base eight times, when goal.py pr would merge a 9th round, then it is refused and the goal waits for the owner. | not run |
| [grd2-active-goals](Tests#t-grd2-active-goals) | requirement | GRD-2 | Given max_active_goals live goals, when watch plans, then no new goal starts. | not run |
| [grd2-plan-pause](Tests#t-grd2-plan-pause) | requirement | GRD-2 | Given weekly plan usage above plan_pause_percent, when the operation plans, then no new goal starts and it says why. | not run |
| [grd2-limits-in-settings](Tests#t-grd2-limits-in-settings) | requirement | GRD-2 | Given the settings table, when it is read, then it lists the four limits with their defaults. | not run |
| [grd2-memory-lane-waits](Tests#t-grd2-memory-lane-waits) | requirement | GRD-2 | Given free memory below min_free_memory_gb, when a lane is about to run rows, then it waits and does not start them. | not run |
| [grd2-memory-new-goal](Tests#t-grd2-memory-new-goal) | requirement | GRD-2 | Given free memory below min_free_memory_gb, when the operation plans, then no new goal starts and the hold names LOW_MEMORY. | not run |
| [grd2-memory-health](Tests#t-grd2-memory-health) | requirement | GRD-2 | Given lanes that waited for memory, when health runs, then its Performance group warns. | not run |
| [grd2-default-240](Tests#t-grd2-default-240) | requirement | GRD-2 | Given the settings table and this repo's config, when the default goal time budget is read, then it is 240 minutes. | not run |
| [grd2-merge-rounds-default-8](Tests#t-grd2-merge-rounds-default-8) | requirement | GRD-2 | Given no max_merge_rounds in the config, when goal.py pr merges the base, then eight rounds are allowed. | PASS 2026-11-15 |
| [grd2-pr-lane-holds-merge-slot](Tests#t-grd2-pr-lane-holds-merge-slot) | requirement | GRD-2 | Given a goal whose pr lane started before another's, when the other's merge.py runs, then it waits until the first merges or fails. | PASS 2026-11-15 |
| [del9-pr-refuses](Tests#t-del9-pr-refuses) | requirement | GRD-3 | Given a branch that adds a private name from the list, when goal.py pr runs, then nothing is pushed and the refusal names the place, never the text. | not run |
| [del9-hooks](Tests#t-del9-hooks) | requirement | GRD-3 | Given the pre-push hook and a branch whose commit holds a private line, when it is pushed, then the hook refuses naming file and line, and nothing reaches the remote. | PASS 2026-11-12 |
| [grd3-private-commit](Tests#t-grd3-private-commit) | requirement | GRD-3 | Given a staged line holding a private name, when git commit runs with the installed hook, then it is refused naming the file and line and the commit does not happen. | not run |
| [grd3-hooks-health](Tests#t-grd3-hooks-health) | requirement | GRD-3 | Given a repo with the private-name hooks installed, when health runs, then it passes the hooks rule. | not run |
| [grd3-hook-bypass](Tests#t-grd3-hook-bypass) | requirement | GRD-3 | Given a commit or push that skips hooks (no-verify, empty hooks path), when a loop command runs it, then it is refused and health flags it (not built). | not run |
| [perms-private-never-written](Tests#t-perms-private-never-written) | requirement | GRD-3 | Given a routine's permission row holding a home path or a token, when the project settings are written, then it is refused and nothing private reaches the committed file. | not run |
| [machine-guardrail-private](Tests#t-machine-guardrail-private) | requirement | GRD-3 | Given a repo routine holding an address or home path, when machine apply runs, then it refuses naming the line and kind, writes nothing and never echoes the value. | not run |
| [grd4-touches](Tests#t-grd4-touches) | requirement | GRD-4 | Given a worker session, when it tries to widen its goal's touches, then the command refuses. | not run |
| [grd4-resume](Tests#t-grd4-resume) | requirement | GRD-4 | Given a stopped goal, when its own worker tries to resume it, then the command refuses with WORKER_SELF_REPAIR. | not run |
| [grd4-budget](Tests#t-grd4-budget) | requirement | GRD-4 | Given a worker session, when it tries to set its own goal's budget, then the command refuses. | not run |
| [grd4-govern](Tests#t-grd4-govern) | requirement | GRD-4 | Given the operation session governing goals, when workers build, then the governing checkout gets no commit. | not run |
| [grd4-worker-commit-main-refused](Tests#t-grd4-worker-commit-main-refused) | requirement | GRD-4 | Given a pool worker session, when it runs git commit in the main checkout, then the govern hook refuses it; a worktree commit and other sessions pass. | PASS 2026-11-15 |
| [grd5-regression-dry](Tests#t-grd5-regression-dry) | requirement | GRD-5 | Given no token, when the regression run reaches an issue write, then it is a dry run and makes no gh call. | not run |
| [grd5-health-close](Tests#t-grd5-health-close) | requirement | GRD-5 | Given open findings, when triage close runs without --yes, then it lists them and writes nothing. | not run |
| [issues-live-only-ci](Tests#t-issues-live-only-ci) | requirement | GRD-5 | Given a GitHub token and no --live, when the workflow's issue step runs, then it prints WOULD lines and writes no issue, comment or label. | not run |
| [issues-live-only-local](Tests#t-issues-live-only-local) | requirement | GRD-5 | Given a GitHub token and no --live, when regression.py run reaches an issue write, then it prints WOULD and makes no gh write. | not run |
| - | requirement | GRD-5 | no passing test | not enforced |
| [grd6-head-moved](Tests#t-grd6-head-moved) | requirement | GRD-6 | Given a pull request head that moved since its checks ran, when the release merges, then it is refused with HEAD_MOVED and nothing is merged. | not run |
| - | requirement | GRD-6 | no passing test | not enforced |
| [grd7-round-cost](Tests#t-grd7-round-cost) | requirement | GRD-7 | Given a scheduled round, when its digest is posted, then the round cost shows its minutes and Actions minutes. | not run |
| - | requirement | GRD-7 | no passing test | not enforced |
| [grd8-silent-worker](Tests#t-grd8-silent-worker) | requirement | GRD-8 | Given a worker silent past silent_minutes, when the board prints, then it shows under Needs you. | not run |
| - | requirement | GRD-8 | no passing test | not enforced |
| [grd9-controls](Tests#t-grd9-controls) | requirement | GRD-9 | Given every health rule, when the controls run on broken copies, then each rule fires. | SKIPPED 2026-11-14 |
| [repo-rules-control](Tests#t-repo-rules-control) | requirement | GRD-9 | Given a repo rule with a break command, when the Controls group runs, then the rule whose break makes it fail passes its control and one whose break changes nothing is reported as unable to fire. | not run |
| [repo-rules-refuse](Tests#t-repo-rules-refuse) | requirement | GRD-9 | Given a repo rule with no break command, when health runs, then it refuses with exit 2 naming the rule. | not run |
| [repo-rules-off](Tests#t-repo-rules-off) | requirement | GRD-9 | Given a default rule turned off in .loop/health-rules.json, when health checks, then its group prints the reason, and a default turned off with no reason stays on and is UNREAD. | not run |
| - | requirement | GRD-9 | no passing test | not enforced |
| [grd10-install-hooks](Tests#t-grd10-install-hooks) | requirement | GRD-10 | Given a repo being adopted, when setup runs by default, then it installs the three private-name hooks after its commit. | not run |
| - | requirement | GRD-10 | no passing test | not enforced |
| [machine-local-guardrail](Tests#t-machine-local-guardrail) | requirement | GRD-11 | Given a row whose red proof needs another machine and is recorded owed, when sync runs, then it reads PENDING and no longer blocks as UNPROVEN. | not run |
| - | requirement | GRD-11 | no passing test | not enforced |
| [config-memory-key-once](Tests#t-config-memory-key-once) | requirement | GRD-12 | Given this repo's config, when min_free_memory_gb is read, then the key is there once as a positive number and the settings table registers it. | not run |
| - | requirement | GRD-12 | no passing test | not enforced |
| [test-caps-consolidate-allowed](Tests#t-test-caps-consolidate-allowed) | requirement | GRD-13 | Given a repo over a cap, when a goal removes or merges at least as many rows as it adds, then qa lets it pass, so a goal that only consolidates is always allowed. | PASS 2026-11-16 |
| [test-caps-own-cap](Tests#t-test-caps-own-cap) | requirement | GRD-13 | Given a goal that raises max_regression_rows in its own config, when qa checks the caps, then it reads the base branch's cap and still refuses; the owner raising the cap on the base lets the goal pass. | PASS 2026-11-16 |
| [eta-freeze](Tests#t-eta-freeze) | requirement | GRD-14 | Given a goal being frozen, when its fields and goal file are built, then they hold a hard ETA in whole minutes (at least 30) with its basis, and the goal file has an ETA line next to the done lines. | not run |
| [eta-gate](Tests#t-eta-gate) | requirement | GRD-14 | Given a goal that has spent its ETA, when a step or pr is asked for, then it is refused with one line naming goal.py set and an owner record, and a goal inside its ETA starts its step. | not run |
| [eta-needs-you](Tests#t-eta-needs-you) | requirement | GRD-14 | Given a goal past its ETA, when the refusal is recorded, then the goal waits with three choices (ship now, extend, defer) as an owner question that full auto never answers, so the check-in lists it under Needs you. | not run |
| [eta-owner-record](Tests#t-eta-owner-record) | requirement | GRD-14 | Given goal.py set with an ETA extension or a budget raise, when no owner-words record covers the goal or the record was used before, then it is refused and nothing changes; with a fresh covering record it is accepted. | not run |
| [eta-ship-defer](Tests#t-eta-ship-defer) | requirement | GRD-14 | Given a goal past its ETA and an owner record, when the owner chooses ship now or defer, then ship now records the steps left as skipped and lets the pull request go on, and defer retires the goal for the next release. | not run |
| [eta-checkin](Tests#t-eta-checkin) | requirement | GRD-14 | Given goals with and without an ETA, when the check-in builds its All sessions table, then each goal's cell shows its ETA clock time, ETA passed, or no ETA. | not run |
| [eta-health-missing](Tests#t-eta-health-missing) | requirement | GRD-14 | Given a live goal with no ETA, when health runs, then it warns (eta-missing), and the rule's negative control fires. | not run |
| [eta-health-extended](Tests#t-eta-health-extended) | requirement | GRD-14 | Given an ETA extension whose owner-words record is missing or does not cover the goal, when health runs, then it fails (eta-extended), and the rule's negative control fires. | not run |
| [eta-health-overrun](Tests#t-eta-health-overrun) | requirement | GRD-14 | Given a goal past its ETA that is not waiting under Needs you, when health runs, then it fails (eta-overrun), and the rule's negative control fires; a goal waiting for the owner's choice is clean. | not run |
| - | requirement | GRD-14 | no passing test | not enforced |
| [workers-setting-listed](Tests#t-workers-setting-listed) | defect | [#4040](https://github.com/jcl2018/agent-workflow-template/issues/4040) closed (2026-11-14) | Given the workers setting, when the settings are listed, then workers is in the settings table beside the other guardrails. | not run |
| [stop-tree-step-limit](Tests#t-stop-tree-step-limit) | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | Given a step or lane past its time limit, when it is stopped on any platform, then its whole process tree goes with it. | not run |
| [issues-rest-fallback](Tests#t-issues-rest-fallback) | defect | [#4464](https://github.com/jcl2018/agent-workflow-template/issues/4464) closed (2026-11-16) | Given the GraphQL issue list times out, when a regression run is live, then it reads the REST pages and keeps one open issue per failing row. | not run |
| [issues-both-down-nochange](Tests#t-issues-both-down-nochange) | defect | [#4464](https://github.com/jcl2018/agent-workflow-template/issues/4464) closed (2026-11-16) | Given both issue reads time out, when a regression run is live, then no issue is opened, commented or closed. | not run |
