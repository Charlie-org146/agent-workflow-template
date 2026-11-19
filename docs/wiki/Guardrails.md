<!-- workflow-docs -->
# Guardrails

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/11

Review: **Unreviewed** <!-- kept health-principles@4d09e1cc -->

How to use: [How-to-use-Guardrails](How-to-use-Guardrails)

## Problem

- My  guardrails are scattered across six features, some are promised but not built, and I can't see in one place what protects me, where it is enforced and whether it is on.
- Runs can quietly cost too much: CI minutes on superseded or no-code runs, a step spending far more tokens than usual, a run going far longer than usual.
- I want one set of guardrails that the health checks prove are on and that every adopted repo gets, each one showing what it protects against, where it lives and the setting that controls it.

## Requirements

### Functional

- GRD-4: **Reviewed 2026-11-19** Each session writes only what its role allows <!-- reviewed 5443f514 -->
  - A worker can't widen its own goal's touched files, resume itself or change its own budget, and it changes shared loop state only for its own goal through the goal's commands. Only the operation session can do the rest. [GRD-4]
  - A check-in never edits code, commits or pushes from the operation session; only merges and the post-merge steps change the repo. [OPS-7]
- GRD-5: **Reviewed 2026-11-19** Nothing is written outside without explicit say <!-- reviewed 391b2a85 -->
  - Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit --live switch; a token in the environment does not turn writing on. [GRD-5]
  - An integration reads by default. It writes outside only behind an explicit switch and, for shared text, an accepted delta. I attach each connector myself with the narrowest access, and its secrets live outside the repo. [INT-4]
- GRD-6: **Reviewed 2026-11-19** Base branch and hooks cannot be bypassed <!-- reviewed 38016892 -->
  - The base branch refuses direct and force pushes, and a pull request merges only when the repo's required checks pass. [GRD-6]
  - I set those rules on the platform; setup never edits them, and health reads that they are set. [GRD-6]
  - A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health. [GRD-16]
- GRD-7: **Reviewed 2026-11-19** CI minutes are spent only where needed <!-- reviewed 579d9629 -->
  - A newer run of the same workflow on the same branch cancels the one it replaces, and a heavy job is skipped for a change that touches no code. [GRD-7]
  - Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used. [GRD-17]
- GRD-8: **Reviewed 2026-11-19** Token and time use is real and watched <!-- reviewed 793633ab -->
  - Each step's tokens are read from its session record when the step is recorded. [GRD-15]
  - A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget. [GRD-15]
  - A step whose tokens or time pass a set multiple of that step's usual is flagged on the board and in the check-in while it runs. [GRD-8]
- GRD-20: **Reviewed 2026-11-19** The package always fits Agensi's rules <!-- reviewed c3325c66 -->
  - No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits. A failure names the rule and the file. [GRD-20]
  - One table on the Guardrails page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read. Ours may be tighter, never looser. Raising one of ours takes my own words, and health warns when the last read is over 30 days old. [GRD-21]
  - A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes. The refusal says how much room is left and what would free it. [GRD-22]

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

- GRD-1: moved to HLT-2
- GRD-10: moved to SET-1
- GRD-11: moved to REG-9
- GRD-12: moved to OPS-16
- GRD-13: moved to REG-7
- GRD-14: moved to DEL-17
- GRD-15: moved to GRD-8
- GRD-16: moved to GRD-6
- GRD-17: moved to GRD-7
- GRD-18: moved to MCH-1
- GRD-19: moved to HLT-11
- GRD-2: Retired
- GRD-21: moved to GRD-20
- GRD-22: moved to GRD-20
- GRD-3: moved to DEL-9
- GRD-9: moved to HLT-2

### GRD-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | One visible set of guardrails <br> This page lists every guardrail with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on. <br> It points to the requirement that owns each one and restates none of the owner's text. | consolidation (TOP-DECISION 89): absorbed into HLT-2 | o204: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | One visible set of guardrails <br> This page lists every guardrail with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on. <br> It points to the requirement that owns each one and restates none of the owner's text. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | One visible set of guardrails, each with its protection, owner, setting and health check <br> This page is an index: it lists every guardrail the template has or needs, each with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on. <br> Each guardrail points to the requirement id that owns it (DEL-8, REG-7, DEL-9, SET-8, MON-7, MON-8) and says "new" where none does yet; the page restates none of the owner's text, which holds the exact wording. <br> A guardrail counts as on only when its Tests row here passes; until then it reads not enforced. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Budgets and caps stop a runaway <br> Time, token and test budgets stop a goal or a step before it runs away. <br> Goal budgets and the ETA are Delivery's (DEL-7, DEL-17); test-run and preparation budgets and the test caps are Regression's (REG-7, REG-11, REG-14). | cut: pure cross-reference to DEL-7, DEL-17, REG-7, REG-11, REG-14; no guarantee of its own (TOP-DECISION 91) | o348: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Budgets and caps stop a runaway <br> Time, token and test budgets stop a goal or a step before it runs away. <br> Goal budgets and the ETA are Delivery's (DEL-7, DEL-17); test-run and preparation budgets and the test caps are Regression's (REG-7, REG-11, REG-14). | v2 rewrite (prd-rewrite-to-10): index only. | o155: "start regroup 3 and 4" |
| r1 | 2026-11-17 | Time and token budgets stop a goal or a step before it runs away <br> Review and ship step time limit: DEL-8. <br> In-loop test run time limit: REG-7. <br> The work before a lane's first test row (preparing, planning and waiting for a slot) stops at `prep_budget_minutes` (default 15, never under 15; this repo sets 25); the lane says which part ran long and the goal can rerun it (Delivery, Regression). <br> A goal past `time_budget_minutes` starts no new step, and the setting is in the settings reference with its default (Delivery, new). <br> A goal past `token_budget` starts no new step, whether its steps run in a session or headless (Delivery, DEL-8 for showing it on the board; new for steps run in a session: today only headless goals are refused). <br> A goal with no token count records "unknown" and the board shows "tokens unread", never 0, so an unread count is never mistaken for an unspent budget (Delivery, new). <br> Each worker step's tokens are read from its session transcript when it is recorded (input, cache reads, cache writes, output, calls, model and the largest context), kept in the run record and listed by `goal.py show`; `token_budget` counts the fresh part (input, cache writes and output, not cache reads) of those measured tokens, plus what the step in progress has spent so far (Delivery, token-diet). <br> A loop script's output is cut to 2,000 characters, the first half and the last half with a line naming the file that keeps the whole text, so a long result does not fill a session's context; the step prompt a worker must read whole is not cut (Delivery, token-diet). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Nothing private is committed <br> Every commit, push and pull request passes the private-name scan, and local settings and private values are never written into a repo. <br> A line in the list may be scoped to public repos or to named repos; an unscoped line applies everywhere. | consolidation (TOP-DECISION 89): absorbed into DEL-9 | o414: "consolidate the requirements ... absorb some requirements into the existing one requirement" |
| r2 | 2026-11-18 | Nothing private is committed <br> Every commit, push and pull request passes the private-name scan, and local settings and private values are never written into a repo. <br> A line in the list may be scoped to public repos or to named repos; an unscoped line applies everywhere. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-15 | Nothing private is committed, and no commit skips the hooks that check it <br> Private-name scan on every commit and push: DEL-9. <br> A commit or push that skips the repo's hooks (a no-verify flag, an empty hooks path) is refused by the loop's own commands and flagged by health (Delivery, new). <br> Where the scanned names live: SET-8 (SET-2 for the private layer). <br> A private-name line may be scoped with `@public` or `@repos=a,b`, so a private repo can hold a name a public one must never show; an unscoped line applies everywhere (Delivery, DEL-9). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Each session writes only what its role allows <br> A worker can't widen its own goal's touched files, resume itself or change its own budget, and it changes shared loop state only for its own goal through the goal's commands. Only the operation session can do the rest. [GRD-4] <br> A check-in never edits code, commits or pushes from the operation session; only merges and the post-merge steps change the repo. [OPS-7] | consolidation (TOP-DECISION 89) | o293: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A worker writes only its own goal's work <br> A worker can't widen its own goal's touched files, resume itself or change its own budget, and it changes shared loop state only for its own goal through the goal's commands. <br> Only the operation session can do the rest. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | A worker writes only its own goal's work, never shared loop state or its own limits <br> A worker can't widen its own goal's touches, resume itself or change its own budget; only the operation session can (Delivery, new: today a role check, not a boundary). <br> A worker changes shared loop state only for its own goal and only through the goal's commands (`goal.py step`, `record` and `pr`, `sessions.py bind` and `report`); the queue, other goals' run records and the session pool's other sessions are the operation session's to change (Monitoring, new: today the commands scope a worker to its own slug, and nothing stops a hand edit). <br> The operation session never edits code, commits or pushes: MON-7. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Nothing is written outside without explicit say <br> Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit --live switch; a token in the environment does not turn writing on. [GRD-5] <br> An integration reads by default. It writes outside only behind an explicit switch and, for shared text, an accepted delta. I attach each connector myself with the narrowest access, and its secrets live outside the repo. [INT-4] | consolidation (TOP-DECISION 89) | o295: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Nothing is written to GitHub without --live <br> Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit --live switch; a token in the environment does not turn writing on. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Nothing is written to GitHub without an explicit `--live` <br> Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit `--live` switch; a token in the environment does not turn writing on (Health, HLT-4, REG-5 and AUT-5 hold the wording; Regression new: today it writes whenever a token is present). <br> The scheduled workflows pass `--live`; the page of each such command says so (each owner, new). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Base branch and hooks cannot be bypassed <br> The base branch refuses direct and force pushes, and a pull request merges only when the repo's required checks pass. [GRD-6] <br> I set those rules on the platform; setup never edits them, and health reads that they are set. [GRD-6] <br> A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health. [GRD-16] | consolidation (TOP-DECISION 89) | o297: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | The base branch is protected <br> The base branch refuses direct and force pushes, and a pull request merges only when the repo's required checks pass. <br> I set those rules on the platform; setup never edits them, and health reads that they are set. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | The base branch is protected and merges only with its required checks green <br> The base branch refuses direct pushes and force pushes, and a pull request merges only when the repo's required checks pass; I set those rules on the platform, and setup never edits a ruleset or branch protection (it names, as BLOCKS, a required check no commit status can satisfy: Setup, SET-1). <br> Where the platform can enforce it (branch rules, required status checks), the platform does, and health reads that it is set (Health, new). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | CI minutes are spent only where needed <br> A newer run of the same workflow on the same branch cancels the one it replaces, and a heavy job is skipped for a change that touches no code. [GRD-7] <br> Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used. [GRD-17] | consolidation (TOP-DECISION 89) | o278: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | CI spends minutes only on runs that matter <br> A newer run of the same workflow on the same branch cancels the one it replaces, and a heavy job is skipped for a change that touches no code. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | CI spends minutes only on runs that matter, and too many runs raise an alarm <br> A newer run of the same workflow on the same branch cancels the one it supersedes (Automation, new: the workflows queue runs today). <br> A heavy job is skipped for a change that touches no code, such as docs only (Automation, new). <br> Each round shows its Actions minutes and goes over its limit loudly (Automation, AUT-7); runs or minutes per day past a set limit raise one alarm (Automation, new). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Token and time use is real and watched <br> Each step's tokens are read from its session record when the step is recorded. [GRD-15] <br> A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget. [GRD-15] <br> A step whose tokens or time pass a set multiple of that step's usual is flagged on the board and in the check-in while it runs. [GRD-8] | consolidation (TOP-DECISION 89) | o276: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A step far past its usual is flagged while it runs <br> A step whose tokens or time pass a set multiple of that step's usual is flagged on the board and in the check-in while it runs. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | A step far past its usual tokens or time is flagged while it runs <br> A step whose tokens pass a set multiple of that step's usual is flagged on the board and in the check-in (Monitoring, new). <br> A step past three times its estimate is shown as stalled under Issues on the board (Monitoring, MON-4, which keeps a stuck worker at the top of Issues), and a worker silent past `silent_minutes` shows under Needs you: MON-8. <br> A goal's test lane past `goal_lane_minutes` (default 10) says so in its LANE line (Regression, REG-8). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Health proves every guardrail <br> Each guardrail has a health rule that reads whether it is present and working, and each rule has a negative control run against a deliberately broken copy. <br> A guardrail its rule can't read shows as unread, never as passing. | consolidation (TOP-DECISION 89): absorbed into HLT-2 | o205: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Health proves every guardrail <br> Each guardrail has a health rule that reads whether it is present and working, and each rule has a negative control run against a deliberately broken copy. <br> A guardrail its rule can't read shows as unread, never as passing. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Health proves every guardrail is present and working, each rule with a negative control <br> Each guardrail has a health rule that reads whether it is present and working, in an existing group (Performance, Security and privacy, Hygiene or Adoption), within the cap of 12 groups (Health, HLT-2). <br> Each such rule has a negative control run against a deliberately broken copy, so it is known to fire (Health, HLT-2, Controls). <br> A guardrail its rule can't read shows as unread, never as passing (Health, HLT-3). <br> A page's requirement cap, `criteria_max` (17 in this repo), is read by health's Size group, so a page too large to review shows as a finding. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### GRD-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Setup installs the whole set <br> Adopting a repo installs every guardrail on this page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. | consolidation (TOP-DECISION 89): absorbed into SET-1 | o317: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
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
| r3 | 2026-11-19 | Nothing starts under the memory floor <br> No goal or test lane starts while free memory is below one setting, 3 GB by default and stated here only. <br> A machine may set its own value locally. <br> A lane already running is never stopped. | consolidation (TOP-DECISION 89): absorbed into OPS-16 | o281: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
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
| r2 | 2026-11-19 | Token counts are real or say unread <br> Each step's tokens are read from its session record when the step is recorded. <br> A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget. | consolidation (TOP-DECISION 89): absorbed into GRD-8 | o277: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Token counts are real or say unread <br> Each step's tokens are read from its session record when the step is recorded. <br> A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-16

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | No commit skips the hooks <br> A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health. | consolidation (TOP-DECISION 89): absorbed into GRD-6 | o298: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | No commit skips the hooks <br> A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-17

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Too many CI runs raise an alarm <br> Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used. | consolidation (TOP-DECISION 89): absorbed into GRD-7 | o279: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Too many CI runs raise an alarm <br> Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-18

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Windows-safe <br> A pull request that adds a POSIX-only call without its guard fails its checks, and long text for an issue, comment, pull request or release note is always passed to gh in a file, so nothing breaks on native Windows. | consolidation (TOP-DECISION 89): absorbed into MCH-1 | o416: "consolidate the requirements ... absorb some requirements into the existing one requirement" |
| r1 | 2026-11-18 | Windows-safe <br> A pull request that adds a POSIX-only call without its guard fails its checks, and long text for an issue, comment, pull request or release note is always passed to gh in a file, so nothing breaks on native Windows. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-19

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A page stays small enough to review <br> A feature page holds at most the number of requirements one setting allows, and health's Size group reports a page over it. | consolidation (TOP-DECISION 89): absorbed into HLT-11 | o288: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A page stays small enough to review <br> A feature page holds at most the number of requirements one setting allows, and health's Size group reports a page over it. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-20

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | The package always fits Agensi's rules <br> No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits. A failure names the rule and the file. [GRD-20] <br> One table on the Guardrails page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read. Ours may be tighter, never looser. Raising one of ours takes my own words, and health warns when the last read is over 30 days old. [GRD-21] <br> A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes. The refusal says how much room is left and what would free it. [GRD-22] | consolidation (TOP-DECISION 89) | o284: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | The package always passes Agensi's rules <br> No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits. <br> A failure names the rule and the file. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-21

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Our package limits are never looser than Agensi's <br> One table on this page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read. <br> Ours may be tighter, never looser. <br> Raising one of ours takes my own words, and health warns when the last read is over 30 days old. | consolidation (TOP-DECISION 89): absorbed into GRD-20 | o285: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Our package limits are never looser than Agensi's <br> One table on this page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read. <br> Ours may be tighter, never looser. <br> Raising one of ours takes my own words, and health warns when the last read is over 30 days old. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### GRD-22

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A goal learns at qa that it doesn't fit <br> A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes. <br> The refusal says how much room is left and what would free it. | consolidation (TOP-DECISION 89): absorbed into GRD-20 | o286: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A goal learns at qa that it doesn't fit <br> A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes. <br> The refusal says how much room is left and what would free it. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [mon7-govern-blocks](Tests#t-mon7-govern-blocks) | requirement | GRD-4 | Given the operation session, when it tries an edit, a commit or a push, then the govern hook refuses it with the fix, while workers, other sessions and the off switch pass. | PASS 2026-11-10 |
| [grd4-touches](Tests#t-grd4-touches) | requirement | GRD-4 | Given a worker session, when it tries to widen its goal's touches, then the command refuses. | not run |
| [grd4-resume](Tests#t-grd4-resume) | requirement | GRD-4 | Given a stopped goal, when its own worker tries to resume it, then the command refuses with WORKER_SELF_REPAIR. | not run |
| [grd4-budget](Tests#t-grd4-budget) | requirement | GRD-4 | Given a worker session, when it tries to set its own goal's budget, then the command refuses. | not run |
| [grd4-govern](Tests#t-grd4-govern) | requirement | GRD-4 | Given the operation session governing goals, when workers build, then the governing checkout gets no commit. | not run |
| [mon16-notes-pass](Tests#t-mon16-notes-pass) | requirement | GRD-4 | Given the operation session, when it writes a file outside every followed repo, then the govern hook lets it through. | not run |
| [mon16-edit-inside-refused](Tests#t-mon16-edit-inside-refused) | requirement | GRD-4 | Given the operation session, when it edits a file inside a followed repo, then the govern hook refuses it. | not run |
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
| [package-caps-held](Tests#t-package-caps-held) | requirement | GRD-20 | Given the package-limits table on How-to-use-Guardrails and dev/package.py's caps, when the table is missing, a figure of ours is above Agensi's, a script reaches 20,480 bytes or a 101st file is added, then the toy fails, and the real tree stays at 100 files and under the byte cap. | PASS 2026-11-14 FLAKY |
| [pull-ff-only-passes](Tests#t-pull-ff-only-passes) | defect | [#495](https://github.com/jcl2018/agent-workflow-template/issues/495) closed (2026-11-11) | Given the operation session, when it runs git pull --ff-only (also with -C and a remote), then the govern hook lets it through. | PASS 2026-11-12 |
| [pull-plain-blocked](Tests#t-pull-plain-blocked) | defect | [#495](https://github.com/jcl2018/agent-workflow-template/issues/495) closed (2026-11-11) | Given the operation session, when it runs a plain git pull, -r, --rebase=merges, --no-ff, --ff-only with --rebase or --ff, a +refspec or -f, then the govern hook still refuses it (negative control). | PASS 2026-11-12 |
| [issues-rest-fallback](Tests#t-issues-rest-fallback) | defect | [#4464](https://github.com/jcl2018/agent-workflow-template/issues/4464) closed (2026-11-16) | Given the GraphQL issue list times out, when a regression run is live, then it reads the REST pages and keeps one open issue per failing row. | not run |
| [issues-both-down-nochange](Tests#t-issues-both-down-nochange) | defect | [#4464](https://github.com/jcl2018/agent-workflow-template/issues/4464) closed (2026-11-16) | Given both issue reads time out, when a regression run is live, then no issue is opened, commented or closed. | not run |
| [quiet-plain-import-4892](Tests#t-quiet-plain-import-4892) | defect | [#4892](https://github.com/jcl2018/agent-workflow-template/issues/4892) closed (2026-11-17) | Given the quiet hook's remember(), when dev/package.py scans govern_hook.py, then it has no __import__ call and remember() still writes the signature held() reads back (issue 4892). | not run |
