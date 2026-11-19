<!-- workflow-docs -->
# Guardrails

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/11

Review: **Unreviewed** <!-- kept known-red-w4b-docs-wording@c2470d39 -->

How to use: [How-to-use-Guardrails](How-to-use-Guardrails)

## Problem

- My  guardrails are scattered across six features, some are promised but not built, and I can't see in one place what protects me, where it is enforced and whether it is on.
- Runs can quietly cost too much: CI minutes on superseded or no-code runs, a step spending far more tokens than usual, a run going far longer than usual.
- I want one set of guardrails that the health checks prove are on and that every adopted repo gets, each one showing what it protects against, where it lives and the setting that controls it.

## Requirements

### Functional

- GRD-1: **Unreviewed** One visible set of guardrails
  - This page lists every guardrail with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on.
  - It points to the requirement that owns each one and restates none of the owner's text.
- GRD-2: **Unreviewed** Budgets and caps stop a runaway
  - Time, token and test budgets stop a goal or a step before it runs away.
  - Goal budgets and the ETA are Delivery's (DEL-7, DEL-17); test-run and preparation budgets and the test caps are Regression's (REG-7, REG-11, REG-14).
- GRD-3: **Unreviewed** Nothing private is committed
  - Every commit, push and pull request passes the private-name scan, and local settings and private values are never written into a repo.
  - A line in the list may be scoped to public repos or to named repos; an unscoped line applies everywhere.
- GRD-4: **Unreviewed** A worker writes only its own goal's work
  - A worker can't widen its own goal's touched files, resume itself or change its own budget, and it changes shared loop state only for its own goal through the goal's commands.
  - Only the operation session can do the rest.
- GRD-5: **Unreviewed** Nothing is written to GitHub without --live
  - Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit --live switch; a token in the environment does not turn writing on.
- GRD-6: **Unreviewed** The base branch is protected
  - The base branch refuses direct and force pushes, and a pull request merges only when the repo's required checks pass.
  - I set those rules on the platform; setup never edits them, and health reads that they are set.
- GRD-7: **Unreviewed** CI spends minutes only on runs that matter
  - A newer run of the same workflow on the same branch cancels the one it replaces, and a heavy job is skipped for a change that touches no code.
- GRD-8: **Unreviewed** A step far past its usual is flagged while it runs
  - A step whose tokens or time pass a set multiple of that step's usual is flagged on the board and in the check-in while it runs.
- GRD-9: **Unreviewed** Health proves every guardrail
  - Each guardrail has a health rule that reads whether it is present and working, and each rule has a negative control run against a deliberately broken copy.
  - A guardrail its rule can't read shows as unread, never as passing.
- GRD-10: **Unreviewed** Setup installs the whole set
  - Adopting a repo installs every guardrail on this page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template.
- GRD-12: **Unreviewed** Nothing starts under the memory floor
  - No goal or test lane starts while free memory is below one setting, 3 GB by default and stated here only.
  - A machine may set its own value locally.
  - A lane already running is never stopped.
- GRD-15: **Unreviewed** Token counts are real or say unread
  - Each step's tokens are read from its session record when the step is recorded.
  - A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget.
- GRD-16: **Unreviewed** No commit skips the hooks
  - A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health.
- GRD-17: **Unreviewed** Too many CI runs raise an alarm
  - Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used.
- GRD-18: **Unreviewed** Windows-safe
  - A pull request that adds a POSIX-only call without its guard fails its checks, and long text for an issue, comment, pull request or release note is always passed to gh in a file, so nothing breaks on native Windows.
- GRD-19: **Unreviewed** A page stays small enough to review
  - A feature page holds at most the number of requirements one setting allows, and health's Size group reports a page over it.
- GRD-20: **Unreviewed** The package always passes Agensi's rules
  - No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits.
  - A failure names the rule and the file.
- GRD-21: **Unreviewed** Our package limits are never looser than Agensi's
  - One table on this page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read.
  - Ours may be tighter, never looser.
  - Raising one of ours takes my own words, and health warns when the last read is over 30 days old.
- GRD-22: **Unreviewed** A goal learns at qa that it doesn't fit
  - A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes.
  - The refusal says how much room is left and what would free it.

### Non-functional

None

## Non-goals

- No code here: each guardrail is built by its owner feature's own goal; this page only defines the set.
- This page never says a guardrail is on; the Tests table does, from passing regression rows.

## Success metrics

- Every guardrail is on this page with its owner, setting and health check, each pointing to its owner's requirement for the exact wording.
- Each guardrail's Tests row passes.
- A freshly adopted repo has every guardrail on with its default setting.

## Revisions

### Retired

- GRD-11: moved to REG-10
- GRD-13: moved to REG-14
- GRD-14: moved to DEL-17

### GRD-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | One visible set of guardrails <br> This page lists every guardrail with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on. <br> It points to the requirement that owns each one and restates none of the owner's text. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | One visible set of guardrails, each with its protection, owner, setting and health check <br> This page is an index: it lists every guardrail the template has or needs, each with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on. <br> Each guardrail points to the requirement id that owns it (DEL-8, REG-7, DEL-9, SET-8, MON-7, MON-8) and says "new" where none does yet; the page restates none of the owner's text, which holds the exact wording. <br> A guardrail counts as on only when its Tests row here passes; until then it reads not enforced. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Budgets and caps stop a runaway <br> Time, token and test budgets stop a goal or a step before it runs away. <br> Goal budgets and the ETA are Delivery's (DEL-7, DEL-17); test-run and preparation budgets and the test caps are Regression's (REG-7, REG-11, REG-14). | v2 rewrite (prd-rewrite-to-10): index only. | o155: "start regroup 3 and 4" |
| r1 | 2026-11-17 | Time and token budgets stop a goal or a step before it runs away <br> Review and ship step time limit: DEL-8. <br> In-loop test run time limit: REG-7. <br> The work before a lane's first test row (preparing, planning and waiting for a slot) stops at `prep_budget_minutes` (default 15, never under 15; this repo sets 25); the lane says which part ran long and the goal can rerun it (Delivery, Regression). <br> A goal past `time_budget_minutes` starts no new step, and the setting is in the settings reference with its default (Delivery, new). <br> A goal past `token_budget` starts no new step, whether its steps run in a session or headless (Delivery, DEL-8 for showing it on the board; new for steps run in a session: today only headless goals are refused). <br> A goal with no token count records "unknown" and the board shows "tokens unread", never 0, so an unread count is never mistaken for an unspent budget (Delivery, new). <br> Each worker step's tokens are read from its session transcript when it is recorded (input, cache reads, cache writes, output, calls, model and the largest context), kept in the run record and listed by `goal.py show`; `token_budget` counts the fresh part (input, cache writes and output, not cache reads) of those measured tokens, plus what the step in progress has spent so far (Delivery, token-diet). <br> A loop script's output is cut to 2,000 characters, the first half and the last half with a line naming the file that keeps the whole text, so a long result does not fill a session's context; the step prompt a worker must read whole is not cut (Delivery, token-diet). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Nothing private is committed <br> Every commit, push and pull request passes the private-name scan, and local settings and private values are never written into a repo. <br> A line in the list may be scoped to public repos or to named repos; an unscoped line applies everywhere. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-15 | Nothing private is committed, and no commit skips the hooks that check it <br> Private-name scan on every commit and push: DEL-9. <br> A commit or push that skips the repo's hooks (a no-verify flag, an empty hooks path) is refused by the loop's own commands and flagged by health (Delivery, new). <br> Where the scanned names live: SET-8 (SET-2 for the private layer). <br> A private-name line may be scoped with `@public` or `@repos=a,b`, so a private repo can hold a name a public one must never show; an unscoped line applies everywhere (Delivery, DEL-9). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A worker writes only its own goal's work <br> A worker can't widen its own goal's touched files, resume itself or change its own budget, and it changes shared loop state only for its own goal through the goal's commands. <br> Only the operation session can do the rest. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | A worker writes only its own goal's work, never shared loop state or its own limits <br> A worker can't widen its own goal's touches, resume itself or change its own budget; only the operation session can (Delivery, new: today a role check, not a boundary). <br> A worker changes shared loop state only for its own goal and only through the goal's commands (`goal.py step`, `record` and `pr`, `sessions.py bind` and `report`); the queue, other goals' run records and the session pool's other sessions are the operation session's to change (Monitoring, new: today the commands scope a worker to its own slug, and nothing stops a hand edit). <br> The operation session never edits code, commits or pushes: MON-7. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Nothing is written to GitHub without --live <br> Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit --live switch; a token in the environment does not turn writing on. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Nothing is written to GitHub without an explicit `--live` <br> Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit `--live` switch; a token in the environment does not turn writing on (Health, HLT-4, REG-5 and AUT-5 hold the wording; Regression new: today it writes whenever a token is present). <br> The scheduled workflows pass `--live`; the page of each such command says so (each owner, new). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | The base branch is protected <br> The base branch refuses direct and force pushes, and a pull request merges only when the repo's required checks pass. <br> I set those rules on the platform; setup never edits them, and health reads that they are set. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | The base branch is protected and merges only with its required checks green <br> The base branch refuses direct pushes and force pushes, and a pull request merges only when the repo's required checks pass; I set those rules on the platform, and setup never edits a ruleset or branch protection (it names, as BLOCKS, a required check no commit status can satisfy: Setup, SET-1). <br> Where the platform can enforce it (branch rules, required status checks), the platform does, and health reads that it is set (Health, new). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | CI spends minutes only on runs that matter <br> A newer run of the same workflow on the same branch cancels the one it replaces, and a heavy job is skipped for a change that touches no code. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | CI spends minutes only on runs that matter, and too many runs raise an alarm <br> A newer run of the same workflow on the same branch cancels the one it supersedes (Automation, new: the workflows queue runs today). <br> A heavy job is skipped for a change that touches no code, such as docs only (Automation, new). <br> Each round shows its Actions minutes and goes over its limit loudly (Automation, AUT-7); runs or minutes per day past a set limit raise one alarm (Automation, new). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A step far past its usual is flagged while it runs <br> A step whose tokens or time pass a set multiple of that step's usual is flagged on the board and in the check-in while it runs. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | A step far past its usual tokens or time is flagged while it runs <br> A step whose tokens pass a set multiple of that step's usual is flagged on the board and in the check-in (Monitoring, new). <br> A step past three times its estimate is shown as stalled under Issues on the board (Monitoring, MON-4, which keeps a stuck worker at the top of Issues), and a worker silent past `silent_minutes` shows under Needs you: MON-8. <br> A goal's test lane past `goal_lane_minutes` (default 10) says so in its LANE line (Regression, REG-8). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Health proves every guardrail <br> Each guardrail has a health rule that reads whether it is present and working, and each rule has a negative control run against a deliberately broken copy. <br> A guardrail its rule can't read shows as unread, never as passing. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Health proves every guardrail is present and working, each rule with a negative control <br> Each guardrail has a health rule that reads whether it is present and working, in an existing group (Performance, Security and privacy, Hygiene or Adoption), within the cap of 12 groups (Health, HLT-2). <br> Each such rule has a negative control run against a deliberately broken copy, so it is known to fire (Health, HLT-2, Controls). <br> A guardrail its rule can't read shows as unread, never as passing (Health, HLT-3). <br> A page's requirement cap, `criteria_max` (17 in this repo), is read by health's Size group, so a page too large to review shows as a finding. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Setup installs the whole set <br> Adopting a repo installs every guardrail on this page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Setup installs the whole set when a repo is adopted, and health judges it <br> Adopting a repo installs every guardrail on this page with its default setting, and setup lists each one it installed (Setup, SET-1 for installing; listing each one is new). <br> Health judges a freshly adopted repo's guardrails on the same rules as the template's (Setup, SET-1). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A goal depends only on what its own machine can do <br> A step only another machine can do (a red proof on another platform, a smoke cell, a Mac-only check) is filed as a to-do issue on the feature's milestone and never blocks the goal, its merge or the release. <br> A row whose red proof needs another platform is recorded owed (Regression, `red ID --owed --runner R`): it reads PENDING, opens one `other-machine` to-do on its feature milestone, and its goal merges. <br> Health warns on an owed proof older than 7 days and never fails on it (Health); the check-in lists owed items under Coming up, and the operation session never holds a goal for another pod or machine (Monitoring). | A goal depends only on what its own machine can do now lives on Regression as REG-10 | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | A goal depends only on what its own machine can do <br> A step only another machine can do (a red proof on another platform, a smoke cell, a Mac-only check) is filed as a to-do issue on the feature's milestone and never blocks the goal, its merge or the release. <br> A row whose red proof needs another platform is recorded owed (Regression, `red ID --owed --runner R`): it reads PENDING, opens one `other-machine` to-do on its feature milestone, and its goal merges. <br> Health warns on an owed proof older than 7 days and never fails on it (Health); the check-in lists owed items under Coming up, and the operation session never holds a goal for another pod or machine (Monitoring). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-12

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Nothing starts under the memory floor <br> No goal or test lane starts while free memory is below one setting, 3 GB by default and stated here only. <br> A machine may set its own value locally. <br> A lane already running is never stopped. | v2 rewrite (prd-rewrite-to-10): changed: 3 GB default (your decision, o39). | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | The machine's status is read every round, and no goal starts under the memory floor. <br> Each check-in reads free RAM, free commit memory, CPU and the number of claude and node processes (Monitoring, MON-16). A goal starts only while free commit memory is at or above `min_free_memory_gb` (default 3.5, in `.loop/config.json`; 0 turns the floor off). The pool creates no session and the board holds every ready goal as "memory low" until memory frees up. A figure that can't be read never blocks a start. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-13

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Regression rows and full-suite time are capped, and going over a cap blocks delivery (owner record o51) <br> `max_regression_rows` (default 1200) and `max_suite_seconds` (default 1900) are settings in `.loop/config.json`, shown in Home's settings table (Setup, SET-1). <br> A goal whose rows take the repo over either cap is refused at qa, with the numbers, unless it removes or merges at least as many rows as it adds, or the owner raises the cap in their own words; a goal that only consolidates is always allowed. The caps read are the base branch's, so a goal can't raise its own (GRD-4). <br> Health shows the rows and the slowest full-suite time against both caps, warns at 90% and fails over the cap, and each rule has a negative control (GRD-9). | Regression rows and full-suite time are capped now lives on Regression as REG-14 | o155: "start regroup 3 and 4" |
| r1 | 2026-11-16 | Regression rows and full-suite time are capped, and going over a cap blocks delivery (owner record o51) <br> `max_regression_rows` (default 1200) and `max_suite_seconds` (default 1900) are settings in `.loop/config.json`, shown in Home's settings table (Setup, SET-1). <br> A goal whose rows take the repo over either cap is refused at qa, with the numbers, unless it removes or merges at least as many rows as it adds, or the owner raises the cap in their own words; a goal that only consolidates is always allowed. The caps read are the base branch's, so a goal can't raise its own (GRD-4). <br> Health shows the rows and the slowest full-suite time against both caps, warns at 90% and fails over the cap, and each rule has a negative control (GRD-9). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-14

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A goal's ETA is a hard limit: past it the owner chooses ship now, extend once or defer <br> Owner o52 (2026-11-15): the ETA is a hard criterion so goals stop sliding. Every goal records an ETA when it is frozen: the estimate model's high end plus a 25 percent margin, or the time budget when there is no estimate. It sits in the run record and as an ETA line in the goal file, and the check-in shows it for every goal. <br> A goal past its ETA may finish the step it is on, starts no new step and appears under Needs you with three choices: ship now with what is done (the steps left are recorded as skipped and named in the pull request), extend once by an amount in the owner's own words, or move it to the next release. <br> goal.py refuses to extend an ETA or raise a time or token budget without an owner-words record that covers the goal and has not been used; the operation session alone cannot. <br> Health warns on a live goal with no ETA, fails on an ETA extended without a record, and fails on a goal past its ETA that is not under Needs you; each rule has a negative control. <br> Pre-flight: when a goal is frozen, every owner decision it can foresee goes on one Needs you line, each with its options and a recommendation. Until you answer, the ETA reads "after your answers", and the hard ETA counts from your answers. At the pull-request step, a refusal the freeze list didn't foresee (the private-name scan, the memory floor) is logged as a missed pre-flight item. | A goal's ETA is a hard limit now lives on Delivery as DEL-17 | o155: "start regroup 3 and 4" |
| r1 | 2026-11-16 | A goal's ETA is a hard limit: past it the owner chooses ship now, extend once or defer <br> Owner o52 (2026-11-15): the ETA is a hard criterion so goals stop sliding. Every goal records an ETA when it is frozen: the estimate model's high end plus a 25 percent margin, or the time budget when there is no estimate. It sits in the run record and as an ETA line in the goal file, and the check-in shows it for every goal. <br> A goal past its ETA may finish the step it is on, starts no new step and appears under Needs you with three choices: ship now with what is done (the steps left are recorded as skipped and named in the pull request), extend once by an amount in the owner's own words, or move it to the next release. <br> goal.py refuses to extend an ETA or raise a time or token budget without an owner-words record that covers the goal and has not been used; the operation session alone cannot. <br> Health warns on a live goal with no ETA, fails on an ETA extended without a record, and fails on a goal past its ETA that is not under Needs you; each rule has a negative control. <br> Pre-flight: when a goal is frozen, every owner decision it can foresee goes on one Needs you line, each with its options and a recommendation. Until you answer, the ETA reads "after your answers", and the hard ETA counts from your answers. At the pull-request step, a refusal the freeze list didn't foresee (the private-name scan, the memory floor) is logged as a missed pre-flight item. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-15

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Token counts are real or say unread <br> Each step's tokens are read from its session record when the step is recorded. <br> A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-16

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | No commit skips the hooks <br> A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-17

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Too many CI runs raise an alarm <br> Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-18

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Windows-safe <br> A pull request that adds a POSIX-only call without its guard fails its checks, and long text for an issue, comment, pull request or release note is always passed to gh in a file, so nothing breaks on native Windows. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-19

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A page stays small enough to review <br> A feature page holds at most the number of requirements one setting allows, and health's Size group reports a page over it. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-20

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | The package always passes Agensi's rules <br> No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits. <br> A failure names the rule and the file. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-21

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Our package limits are never looser than Agensi's <br> One table on this page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read. <br> Ours may be tighter, never looser. <br> Raising one of ours takes my own words, and health warns when the last read is over 30 days old. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-22

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A goal learns at qa that it doesn't fit <br> A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes. <br> The refusal says how much room is left and what would free it. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

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
| [del9-pr-refuses](Tests#t-del9-pr-refuses) | requirement | GRD-3 | Given a branch that adds a private name from the list, when goal.py pr runs, then nothing is pushed and the refusal names the place, never the text. Also, given a goal that changes a Reviewed requirement no done line states and no owner record covers, when goal.py pr runs, then it refuses naming the requirement, and a gap is filed as a finding on the page's Backlog milestone. | PASS 2026-11-18 |
| [set8-hooks](Tests#t-set8-hooks) | requirement | GRD-3 | Given a repo with the hooks setup installs, when a staged change adds a private line, then git commit refuses naming the file and line and never the text, and nothing is committed. | PASS 2026-11-19 |
| [set8-setup-commit](Tests#t-set8-setup-commit) | requirement | GRD-3 | Given an adoption whose staged file holds a private line, when setup runs, then it refuses before its own commit, naming the place, and commits nothing. | PASS 2026-11-19 |
| [del9-hooks](Tests#t-del9-hooks) | requirement | GRD-3 | Given the pre-push hook and a branch whose commit holds a private line, when it is pushed, then the hook refuses naming file and line, and nothing reaches the remote. | PASS 2026-11-12 |
| [set8-local-setting-refused](Tests#t-set8-local-setting-refused) | requirement | GRD-3 | Given a private-home key in the config the adoption would commit, when setup runs, then it refuses naming the key and the line, never the value, and writes nothing. | PASS 2026-11-19 |
| [set8-private-value-refused](Tests#t-set8-private-value-refused) | requirement | GRD-3 | Given a home path or a local setting value on a line the adoption adds, when setup runs, then it refuses naming file and line and never the value, while text the repo already had, a short value and a template default pass. | PASS 2026-11-19 |
| [set8-health](Tests#t-set8-health) | requirement | GRD-3 | Given a repo with the private-name hooks installed or removed, when health runs its hooks rule, then the row appears in the Security and privacy group with its PASS or WARN text, and a wrong group, which prints no hooks row, fails the row. | PASS 2026-11-19 |
| [grd3-private-commit](Tests#t-grd3-private-commit) | requirement | GRD-3 | Given a staged line holding a private name, when git commit runs with the installed hook, then it is refused naming the file and line and the commit does not happen. | not run |
| [grd3-hooks-health](Tests#t-grd3-hooks-health) | requirement | GRD-3 | Given a repo with the private-name hooks installed, when health runs, then it passes the hooks rule. | not run |
| [perms-private-never-written](Tests#t-perms-private-never-written) | requirement | GRD-3 | Given a routine's permission row holding a home path or a token, when the project settings are written, then it is refused and nothing private reaches the committed file. | not run |
| [private-names-scoped](Tests#t-private-names-scoped) | requirement | GRD-3 | Given a private-name line scoped to one repo, when another repo stages that name, then it is refused only in the scoped repo. | PASS 2026-11-19 |
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
| [config-memory-key-once](Tests#t-config-memory-key-once) | requirement | GRD-12 | Given this repo's config, when min_free_memory_gb is read, then the key is there once as a positive number and the settings table registers it. | not run |
| - | requirement | GRD-12 | no passing test | not enforced |
| - | requirement | GRD-15 | no passing test | not enforced |
| - | requirement | GRD-16 | no passing test | not enforced |
| - | requirement | GRD-17 | no passing test | not enforced |
| - | requirement | GRD-18 | no passing test | not enforced |
| - | requirement | GRD-19 | no passing test | not enforced |
| - | requirement | GRD-20 | no passing test | not enforced |
| [package-caps-held](Tests#t-package-caps-held) | requirement | GRD-21 | Given the package-limits table on How-to-use-Guardrails and dev/package.py's caps, when the table is missing, a figure of ours is above Agensi's, a script reaches 20,480 bytes or a 101st file is added, then the toy fails, and the real tree stays at 100 files and under the byte cap. | PASS 2026-11-14 FLAKY |
| - | requirement | GRD-22 | no passing test | not enforced |
| [workers-setting-listed](Tests#t-workers-setting-listed) | defect | [#4040](https://github.com/jcl2018/agent-workflow-template/issues/4040) closed (2026-11-14) | Given the workers setting, when the settings are listed, then workers is in the settings table beside the other guardrails. | not run |
| [stop-tree-step-limit](Tests#t-stop-tree-step-limit) | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | Given a step or lane past its time limit, when it is stopped on any platform, then its whole process tree goes with it. | not run |
| [hook-count](Tests#t-hook-count) | defect | 4345 | Given a settings.local.json with one hook entry per script, when MIG_HOOKS runs, then it reports no duplicate; with two entries it reports installed 2 times. | PASS 2026-11-19 |
| [issues-rest-fallback](Tests#t-issues-rest-fallback) | defect | [#4464](https://github.com/jcl2018/agent-workflow-template/issues/4464) closed (2026-11-16) | Given the GraphQL issue list times out, when a regression run is live, then it reads the REST pages and keeps one open issue per failing row. | not run |
| [issues-both-down-nochange](Tests#t-issues-both-down-nochange) | defect | [#4464](https://github.com/jcl2018/agent-workflow-template/issues/4464) closed (2026-11-16) | Given both issue reads time out, when a regression run is live, then no issue is opened, commented or closed. | not run |
| [quiet-plain-import-4892](Tests#t-quiet-plain-import-4892) | defect | [#4892](https://github.com/jcl2018/agent-workflow-template/issues/4892) closed (2026-11-17) | Given the quiet hook's remember(), when dev/package.py scans govern_hook.py, then it has no __import__ call and remember() still writes the signature held() reads back (issue 4892). | not run |
