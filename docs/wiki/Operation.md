<!-- workflow-docs -->
# Operation

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/6

Review: **Unreviewed** <!-- kept prd-revisions@71f2d8b1 -->

How to use: [How-to-use-Operation](How-to-use-Operation)

## Problem
- One session governs: it starts every ready goal in its own worker, passes my answers along, runs unattended and never builds.

## Requirements

### Functional
- MON-1: **Unreviewed** One command starts the operation session
  - One command starts the operation session and drives the whole process the same way every time.
  - It governs only: it never builds.
- MON-2: **Unreviewed** Live communication
  - A worker reports each change of step or status as it happens, and its result when it ends; the operation session sends a worker its answer or a follow-up.
  - Background processes are used only when a session can't be started or reached, and the board says so.
- MON-6: **Unreviewed** Clean up after every goal
  - When a goal merges, its worker session is given the next ready goal or archived, and its worktree and branch are removed.
- MON-10: **Unreviewed** Re-plan at every check-in
  - At each check-in the operation session re-reads every goal's progress and re-plans to finish soonest: it merges goals that do the same thing, splits a goal that blocks others, and puts the critical path first.
  - It never stops a running goal to re-plan, and every change is logged with its reason.
- MON-11: **Unreviewed** Full auto mode
  - Full auto is off in a new repo until I turn it on.
  - With it on, the operation session applies every recommendation without asking, except a safety class: destructive, money, security, private data, a merge on another machine, or anything that contradicts my words.
  - Those wait for me.
  - A safety class is judged by what the action does, not by a word in its name.

- MON-12: **Unreviewed** Session pool
  - The operation session keeps a pool of idle worker sessions, sized by one setting, and hands each ready goal one from the pool.
  - When the pool runs low it asks me to fill it, at the desktop.
  - When I've chosen app sessions, a goal never falls back to a background worker: it waits and says so.

- MON-13: **Unreviewed** Two layers per pod
  - One operation session governs every repo in its pod directly and talks to each worker, with no per-repo operation session.
  - Several pods may run at once, independently.


- MON-15: **Unreviewed** Pods coordinate through shared state
  - Every goal records the pod that owns it, and only that pod starts, answers, merges or resumes it; other pods see it read-only.
- MON-16: **Unreviewed** Fill every free slot at once
  - When goals are ready and slots, sessions and memory are free, every one starts in the same pass; budgets still hold.
  - A ready goal waits while live goals, weekly plan usage or free memory are past their limits, and the check-in names the limit.
- MON-18: **Unreviewed** I say it once
  - One standing instruction to merge, recorded once for named goals or all, replaces a go per merge, and a worker accepts an owner record the operation session names without asking me again.
  - A record covers only the IDs it lists.
- MON-20: **Unreviewed** Every ready goal gets its own worker
  - The operation session plans queued goals as a dependency graph and gives every goal whose dependencies are met its own worker session, in parallel.
  - A goal waits only on goals it truly depends on; sharing files is not a reason to wait.
- MON-23: **Unreviewed** The operation session keeps itself running
  - On start the operation session runs a self-check and lists what is missing, each with its fix.
  - It re-creates its check-in timer before the timer expires, and warns before the app's limit on unanswered messages is reached.

### Non-functional
- MON-7: **Reviewed 2026-11-10** Govern only <!-- reviewed da6f1852 -->
  - A check-in never edits code, commits or pushes from the operation session; only merges and the post-merge steps change the repo.
- MON-8: **Reviewed 2026-11-10** No silent worker <!-- reviewed 68d94ecf -->
  - A worker with no report for 30 minutes shows under Needs you.

## Non-goals
- The operation session never builds; workers do.
- It never merges unless auto_merge is on (MON-7, MON-15); the delivery loop merges and releases.
- Full auto never answers for me on destructive, money, security or owner-contradicting decisions.

## Success metrics
- Every ready goal gets its own worker session within one check-in, and no goal waits on a goal it doesn't depend on.
- The check-in prints in the same format every time, at least every 30 minutes by default.
- With full auto on, a run needs me only for the safety-class decisions MON-11 excludes. Notification subprocesses disable Git and GitHub terminal prompts, matching the unattended delivery commands.

## Revisions

### Retired

- MON-14: moved to CHK-5
- MON-17: moved to CHK-6
- MON-19: moved to CHK-7
- MON-3: moved to CHK-1
- MON-4: moved to CHK-1
- MON-5: moved to CHK-2
- MON-9: moved to CHK-8

### MON-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | One command starts the operation session <br> One command starts the operation session and drives the whole process the same way every time. <br> It governs only: it never builds. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-17 | Roles, start and planning <br> One command starts the operation session and drives the whole process the same way every time. <br> The operation session plans queued goals as a dependency graph and gives every goal whose dependencies are met its own worker session in the app, renamed worker · <goal>, running in parallel; it never builds. <br> A goal waits only on goals it truly depends on; sharing files is not a reason to wait. <br> When a worker session finishes, the operation session gives it the next ready goal, renaming it again. <br> `operate.py start` prints one readiness table before any goal runs: the session tool, the workers mode, the installed skills against the template, the hooks, free memory and the idle pool, each ok or with its fix; it starts no goal and no background worker. <br> A worker start from a scheduled check-in or a Remote Control turn, where the app refuses to start a session, falls back to a background agent only when `workers` is `auto` or the start is asked with `--background`: the agent is launched in the goal's worktree and bound to the goal, and the board says background; with `workers: app` and no flag nothing is launched. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Live communication <br> A worker reports each change of step or status as it happens, and its result when it ends; the operation session sends a worker its answer or a follow-up. <br> Background processes are used only when a session can't be started or reached, and the board says so. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-08 | Live communication. Operation and workers talk through session messages: a worker reports each change of step or status as it happens, and its result when it ends (merged, failed or waiting, with the pull request); the operation session sends a worker its answer or a follow-up. Background processes are used only when the app can't start or reach a session, and the board says so. <br> Operation and workers talk through session messages: a worker reports each change of step or status as it happens, and its result when it ends (merged, failed or waiting, with the pull request); the operation session sends a worker its answer or a follow-up. <br> Background processes are used only when the app can't start or reach a session, and the board says so. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Live board <br> Report, dashboard and the artifact show the live board in the one fixed layout MON-4 lists; this requirement owns the board, and a check-in never prints it. <br> The board lists each open PRD delta of a page that opted in to syncing as waiting on the owner, with its issue and the words to accept either side; a page with no external source never shows one. | Monitoring split into Operation and Check-in and board; v2 rewrite | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Live board <br> Report, dashboard and the artifact show the live board in the one fixed layout MON-4 lists; this requirement owns the board, and a check-in never prints it. <br> The board lists each open PRD delta of a page that opted in to syncing as waiting on the owner, with its issue and the words to accept either side; a page with no external source never shows one. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Live board layout <br> `report`, `dashboard` and "Where do things stand?" print the live board in one fixed format: Issues first (only what is open now, each with its fix in plain words); then Running goals with progress bar, time left, step flow with the current step marked and the next step; then Queued goals; then dependency arrows; then one finish time. <br> Merged work, history and totals are left out; a stuck worker stays at the top of Issues until I answer. <br> Check-ins don't print this board; MON-5 owns the check-in reply. | Monitoring split into Operation and Check-in and board; v2 rewrite | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Live board layout <br> `report`, `dashboard` and "Where do things stand?" print the live board in one fixed format: Issues first (only what is open now, each with its fix in plain words); then Running goals with progress bar, time left, step flow with the current step marked and the next step; then Queued goals; then dependency arrows; then one finish time. <br> Merged work, history and totals are left out; a stuck worker stays at the top of Issues until I answer. <br> Check-ins don't print this board; MON-5 owns the check-in reply. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Cadence and reply format <br> The operation session updates the board on a set cadence, 30 minutes by default and changeable, and at once whenever a worker reports something new, and each check-in prints only its reply layout, never the board. <br> Every check-in reply has the same layout: one headline line, then a Machine line (free RAM, free commit memory, CPU, claude and node counts); <br> All sessions, one table of every session across my repos with what it is doing (a short plain sentence of under about 12 words from its goal's first line, then its slug and issue in brackets), its status, progress, time left, tokens left and latest report; <br> Dependencies, a drawn graph marking what is running, holding, queued or stuck, with each goal's status marker, expected time left and machine (pc or mac); <br> Needs you, each question numbered with its options and a recommended answer, or Nothing needs you; and last, Coming up, the next expected events and what I will need to do. <br> A hook that setup installs blocks a reply that doesn't follow this layout, or has no Machine line, or has a Dependencies goal with no status marker, time or machine, or an All sessions row whose "for" cell is only a slug or issue number, saying what is missing; it never checks worker sessions or other repos, and one setting turns it off. <br> The check-in lists owed off-machine to-dos under Coming up, and the operation session never holds a goal for another pod or machine. <br> A goal shows as [x] in one check-in only, the one right after it merges; a goal that merged before the previous check-in is never listed, and a goal whose pull request merged, or that is retired or stopped, is closed for good. <br> When notification is on for this machine (a private setting, off by default), each check-in mails me once per new event through the health round's mailer: a new Needs you item, a goal that stopped or passed its ETA, and a goal merged and released; each mail names the goal and what I must do, a repeat sends nothing, and the address lives only in mail.env outside the repo. <br> Only a scheduled check-in, or my asking for one (check-in, status, report, board, where do things stand), must be answered in this layout; a reply to a peer message or any other talk is 1 to 3 lines and the hook does not check it, and a turn the hook cannot read is checked as before. <br> A scheduled check-in whose check-in, apart from its Machine line and numbers, is the same as the last full one skips the model turn: a prompt hook blocks it with one line, at most two hours in a row, and any error lets the prompt through. <br> Each check-in adds one row to `op-tokens.tsv`: the time, the operation session, its context, and the tokens it spent since the last row under each trigger (scheduled, peer, human, hook-retry). <br> The operation session sets up its own check-in timer: it shows the owner the interval, the steps each fire runs (checkin.py and board_page.py checkin for every followed repo, post the layout, send the peer a SNAPSHOT on change or every 30 minutes) and what it never does (start goals, merge, answer owner questions, edit private-name lists), creates it on the owner's yes and records it; a missing timer, or one set for another cadence, shows under Needs you with the words to fix it. <br> Dependencies groups goals by feature: the page that defines the requirement ID in the goal, else the feature given to `batch.py add --feature`, else the goal's issue label `feature:<Page>`, else the page whose `.loop/docs.tsv` paths cover the goal's touches, else "no feature"; a queued goal shows its estimated time, not "~?", once finished goals give a basis. <br> Each check-in names the worker sessions archived since the last one under Archived. | Monitoring split into Operation and Check-in and board; v2 rewrite | o155: "start regroup 3 and 4" |
| r1 | 2026-11-17 | Cadence and reply format <br> The operation session updates the board on a set cadence, 30 minutes by default and changeable, and at once whenever a worker reports something new, and each check-in prints only its reply layout, never the board. <br> Every check-in reply has the same layout: one headline line, then a Machine line (free RAM, free commit memory, CPU, claude and node counts); <br> All sessions, one table of every session across my repos with what it is doing (a short plain sentence of under about 12 words from its goal's first line, then its slug and issue in brackets), its status, progress, time left, tokens left and latest report; <br> Dependencies, a drawn graph marking what is running, holding, queued or stuck, with each goal's status marker, expected time left and machine (pc or mac); <br> Needs you, each question numbered with its options and a recommended answer, or Nothing needs you; and last, Coming up, the next expected events and what I will need to do. <br> A hook that setup installs blocks a reply that doesn't follow this layout, or has no Machine line, or has a Dependencies goal with no status marker, time or machine, or an All sessions row whose "for" cell is only a slug or issue number, saying what is missing; it never checks worker sessions or other repos, and one setting turns it off. <br> The check-in lists owed off-machine to-dos under Coming up, and the operation session never holds a goal for another pod or machine. <br> A goal shows as [x] in one check-in only, the one right after it merges; a goal that merged before the previous check-in is never listed, and a goal whose pull request merged, or that is retired or stopped, is closed for good. <br> When notification is on for this machine (a private setting, off by default), each check-in mails me once per new event through the health round's mailer: a new Needs you item, a goal that stopped or passed its ETA, and a goal merged and released; each mail names the goal and what I must do, a repeat sends nothing, and the address lives only in mail.env outside the repo. <br> Only a scheduled check-in, or my asking for one (check-in, status, report, board, where do things stand), must be answered in this layout; a reply to a peer message or any other talk is 1 to 3 lines and the hook does not check it, and a turn the hook cannot read is checked as before. <br> A scheduled check-in whose check-in, apart from its Machine line and numbers, is the same as the last full one skips the model turn: a prompt hook blocks it with one line, at most two hours in a row, and any error lets the prompt through. <br> Each check-in adds one row to `op-tokens.tsv`: the time, the operation session, its context, and the tokens it spent since the last row under each trigger (scheduled, peer, human, hook-retry). <br> The operation session sets up its own check-in timer: it shows the owner the interval, the steps each fire runs (checkin.py and board_page.py checkin for every followed repo, post the layout, send the peer a SNAPSHOT on change or every 30 minutes) and what it never does (start goals, merge, answer owner questions, edit private-name lists), creates it on the owner's yes and records it; a missing timer, or one set for another cadence, shows under Needs you with the words to fix it. <br> Dependencies groups goals by feature: the page that defines the requirement ID in the goal, else the feature given to `batch.py add --feature`, else the goal's issue label `feature:<Page>`, else the page whose `.loop/docs.tsv` paths cover the goal's touches, else "no feature"; a queued goal shows its estimated time, not "~?", once finished goals give a basis. <br> Each check-in names the worker sessions archived since the last one under Archived. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Clean up after every goal <br> When a goal merges, its worker session is given the next ready goal or archived, and its worktree and branch are removed. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-17 | Clean up after every goal <br> When a goal merges, its worker session is given the next ready goal or archived, and its worktree and branch are removed. <br> A merged report always frees the session (issue 175). <br> A worker session whose goal's merge and published release the operation session has verified (GitHub says merged, and the release is published) is archived by the operation session, and the next check-in names it; a session whose goal is running, waiting or has an open pull request, and every operation session, is never archived. <br> Under memory pressure (free memory below `min_free_memory_gb`) it also archives idle sessions whose goal is released or retired, oldest first, until memory is back above the floor. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-10 | Govern only <br> A check-in never edits code, commits or pushes from the operation session; only merges and the post-merge steps change the repo. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-10 | No silent worker <br> A worker with no report for 30 minutes shows under Needs you. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Fast board <br> The board builds in under 10 seconds. | Monitoring split into Operation and Check-in and board; v2 rewrite | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | Fast board <br> The board builds in under 10 seconds. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Re-plan at every check-in <br> At each check-in the operation session re-reads every goal's progress and re-plans to finish soonest: it merges goals that do the same thing, splits a goal that blocks others, and puts the critical path first. <br> It never stops a running goal to re-plan, and every change is logged with its reason. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-18 | Re-plan at every check-in <br> At each check-in the operation session re-reads every goal's progress and re-plans the graph to finish soonest. <br> It starts every goal whose dependencies are met in a free or freed session, up to the slot limit, so no ready goal sits idle. <br> It merges goals that do the same thing or touch the same files for the same PRD, splits a goal that blocks others when part of it is ready, and reorders the merge line so the critical path goes first. <br> It never stops or restarts a running goal to re-plan, and every change is logged with its reason and shown in the check-in. <br> Each planning round takes the backlog with no release and plans it itself: `monitor.py plan` gives each goal a release, an estimate, a hard ETA and a token budget from past runs and settings, and a machine (the PC or the Mac, by free memory and platform needs) and an agent profile with a one-line reason, cross-checks the plan on a second agent when the agent routing config names one, and sends one plan to the owner and to the other machine's operation session; goals already started are left out, nothing starts until the owner approves with the words "approve" or line edits, and ETA choices stay the owner's. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Full auto mode <br> Full auto is off in a new repo until I turn it on. <br> With it on, the operation session applies every recommendation without asking, except a safety class: destructive, money, security, private data, a merge on another machine, or anything that contradicts my words. <br> Those wait for me. <br> A safety class is judged by what the action does, not by a word in its name. | v2 rewrite (prd-rewrite-to-10): first and last sentences are new (off by default: your decision, o39; today's misjudged questions). | o155: "start regroup 3 and 4" |
| r1 | 2026-11-18 | Full auto mode <br> A setting, off by default in the template; this repo turns it on in its config. When it is on, the operation session applies every recommendation without asking, whatever its kind (routine, or an owner one such as un-reviewing a requirement, a row cap, a budget or a pre-flight list), logs the question, the answer, my standing rule record and the words that revert it, and lists them in the next check-in and the email; only a safety-class decision waits under Needs you. <br> It never auto-answers a safety class: destructive (deletes, force pushes, history rewrites, closing other people's work), money, security (secrets, credentials, permissions, sandbox or security settings), private data (private-name lists and the owner's personal accounts), steward merges, an ETA choice, or anything I marked always-ask; health fails an auto answer in one of those classes or one without my rule record. <br> My standing rule is recorded once in the operation session with the owner words (sessions.py owner-words, covering full-auto-rule). A goal that changes requirement wording un-reviews it with that record and goes on; the page shows Unreviewed until I read it, and only I stamp it. <br> Turning it off takes effect at the next decision. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-12

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Session pool <br> The operation session keeps a pool of idle worker sessions, sized by one setting, and hands each ready goal one from the pool. <br> When the pool runs low it asks me to fill it, at the desktop. <br> When I've chosen app sessions, a goal never falls back to a background worker: it waits and says so. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Session pool <br> The operation session keeps a pool of idle worker sessions, sized by a setting (default 20), and hands each ready goal one from the pool instead of starting a new session. <br> Because sessions can only be created from the desktop app, whenever the pool runs low the operation session asks me, at the desktop, to fill it, and it creates every missing session in one step on my word. <br> A finished goal's session goes back to the pool (MON-6), the board shows the pool as free, busy and total, and a goal that finds the pool empty waits under Needs you with the one action that fixes it. <br> A ready goal also waits while live goals are at `max_active_goals` (default 20), weekly plan usage is above `plan_pause_percent` (default 80) or free memory is below `min_free_memory_gb` (default 4); the check-in names the limit that holds. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-13

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Two layers per pod <br> One operation session governs every repo in its pod directly and talks to each worker, with no per-repo operation session. <br> Several pods may run at once, independently. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-15 | Two layers per pod: one operation session governs every repo in its pod directly and talks to each worker, with no per-repo operation session; several pods may run concurrently and independently <br> A claim adds the session to every repo the pod follows and keeps the other sessions already claimed; nothing refuses or warns when a second operation session runs. <br> `board.py repos adopt` lists my recent GitHub repos by last push, or clones, follows and sets up the named ones in one pass, ending with each repo's template version (Setup, SET-12). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-14

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Dependency map grouped by repo <br> The check-in dependency map is grouped by repo first: one block per repo headed by the repo's name, cross-repo dependencies drawn between blocks; inside every repo's block, in the operation repo and every other repo, goals are grouped by release milestone and then by feature, a goal with none under "no release" or "no feature". <br> Each goal shows its status marker, its expected time left from past runs and the machine that runs it (pc or mac, from its pod record); each repo block ends with its expected finish, and each wait is drawn as an arrow. <br> A repo owned by another pod is one line marked with that pod's machine, from its last report. <br> The map lists only live goals: a record with no goal or status, a stopped goal and a goal left with release: leave are not drawn, and a worker held at pr reads holding, not stuck. <br> The check requires only live goals: running, holding, queued, waiting on the owner, or merged since the previous check-in; a goal merged before the previous check-in is never required. <br> Each repo prints as `== name ==` within 60 characters, then a `Between repos` list for `repo/slug` dependencies, then the legend once. <br> Each release milestone's header starts with its expected release time, the latest expected finish among its goals, and its count of goals not started, for example "v1.1 release ETA tomorrow ~20:00 (11 goals, 6 not started)"; a release with nothing started reads "release ETA unknown (N not started)". <br> The reply hook flags a check-in whose Dependencies section leaves out a goal on the board, or a release header with no release ETA, or shows a goal with no status marker, time or machine, or a repo block whose goals are not under a release and a feature. | Monitoring split into Operation and Check-in and board; v2 rewrite | o155: "start regroup 3 and 4" |
| r1 | 2026-11-16 | Dependency map grouped by repo <br> The check-in dependency map is grouped by repo first: one block per repo headed by the repo's name, cross-repo dependencies drawn between blocks; inside every repo's block, in the operation repo and every other repo, goals are grouped by release milestone and then by feature, a goal with none under "no release" or "no feature". <br> Each goal shows its status marker, its expected time left from past runs and the machine that runs it (pc or mac, from its pod record); each repo block ends with its expected finish, and each wait is drawn as an arrow. <br> A repo owned by another pod is one line marked with that pod's machine, from its last report. <br> The map lists only live goals: a record with no goal or status, a stopped goal and a goal left with release: leave are not drawn, and a worker held at pr reads holding, not stuck. <br> The check requires only live goals: running, holding, queued, waiting on the owner, or merged since the previous check-in; a goal merged before the previous check-in is never required. <br> Each repo prints as `== name ==` within 60 characters, then a `Between repos` list for `repo/slug` dependencies, then the legend once. <br> Each release milestone's header starts with its expected release time, the latest expected finish among its goals, and its count of goals not started, for example "v1.1 release ETA tomorrow ~20:00 (11 goals, 6 not started)"; a release with nothing started reads "release ETA unknown (N not started)". <br> The reply hook flags a check-in whose Dependencies section leaves out a goal on the board, or a release header with no release ETA, or shows a goal with no status marker, time or machine, or a repo block whose goals are not under a release and a feature. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-15

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Pods coordinate through shared state <br> Every goal records the pod that owns it, and only that pod starts, answers, merges or resumes it; other pods see it read-only. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-12 | Pods coordinate through shared state, not messages: every goal records its owning pod and only that pod starts, answers, merges or resumes it; other pods show it read-only as owned by that pod; merges into one repo's main are serialized across pods by a short lock <br> The pod id is `LOOP_POD_ID`, else the operation session's own id; a goal with no recorded pod belongs to no one. Another pod's attempt prints one `REFUSED: goal <slug> is owned by pod <id>. Fix: ...` line, exit 2, and changes nothing. <br> `merge.py` takes `<git common dir>/loop/merge.lock` for the whole merge step; a dead holder or one older than 30 minutes is replaced. <br> A pod's watch, auto-answers and mending skip other pods' goals, and its check-in lists their questions as read-only. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-16

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Fill every free slot at once <br> When goals are ready and slots, sessions and memory are free, every one starts in the same pass; budgets still hold. <br> A ready goal waits while live goals, weekly plan usage or free memory are past their limits, and the check-in names the limit. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-16 | Fill every free slot at once; speed comes before tokens, within the guardrails. <br> When goals are ready and slots, sessions and memory are free, every one starts in the same pass; token and time budgets (Guardrails) still hold. The check-in's Machine line, always printed first, shows free RAM, free commit memory, CPU and the claude and node counts, and says how many goal starts memory allows. Each pass checks that the main checkout is current with origin/main; when it is behind, the check-in asks a free worker to fast-forward it, because the operation session's govern hook blocks the pull itself. A goal waiting in the pr queue with a fresh queue file reads alive, never silent. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-17

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A check-in lists only this machine's goals. <br> Goals of another pod are not listed; each other pod gets one line, "<pod>: N goals, last activity HH:MM" (the owner's decision), and never a question for this pod. | Monitoring split into Operation and Check-in and board; v2 rewrite | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | A check-in lists only this machine's goals. <br> Goals of another pod are not listed; each other pod gets one line, "<pod>: N goals, last activity HH:MM" (the owner's decision), and never a question for this pod. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-18

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | I say it once <br> One standing instruction to merge, recorded once for named goals or all, replaces a go per merge, and a worker accepts an owner record the operation session names without asking me again. <br> A record covers only the IDs it lists. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | The operation session keeps running unattended. <br> One standing instruction to merge, recorded once by the operation session for named goals or all, replaces a go per merge; a worker at pr reads it and does not wait for another. <br> The check-in says how many cross-session sends are left before the app's cap of 20 without an owner message; from 16 sent it asks the owner for any message, which resets the count. <br> The check-in loop is re-created before its 7 days run out; the check-in says when. <br> Every worker accepts an owner-words record the operation session names, per the Delivery rule, and does not ask the owner again; a record covers only its listed ids. <br> On start the operation session runs a self-check and lists what is missing, each with its fix: a permission mode that holds cross-session messages for approval, a routine whose rules are not written or do not cover its Runbook (AUT-9), and the main checkout behind origin/main (MON-16). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-19

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Blockers first. Each item under Needs you says what it holds up, so the owner sees the priorities. <br> An item names the goals, merges or release it holds up, with the count of goals behind it, and says whether it is on the critical path to the next release; an item that holds nothing says "blocks nothing". <br> Items are sorted with the one holding up the most goals first, and the Dependencies graph marks the owner item on each chain. <br> The Stop hook refuses a check-in whose Needs you items do not say what they hold up. | Monitoring split into Operation and Check-in and board; v2 rewrite | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Blockers first. Each item under Needs you says what it holds up, so the owner sees the priorities. <br> An item names the goals, merges or release it holds up, with the count of goals behind it, and says whether it is on the critical path to the next release; an item that holds nothing says "blocks nothing". <br> Items are sorted with the one holding up the most goals first, and the Dependencies graph marks the owner item on each chain. <br> The Stop hook refuses a check-in whose Needs you items do not say what they hold up. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MON-20

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Every ready goal gets its own worker <br> The operation session plans queued goals as a dependency graph and gives every goal whose dependencies are met its own worker session, in parallel. <br> A goal waits only on goals it truly depends on; sharing files is not a reason to wait. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### MON-23

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | The operation session keeps itself running <br> On start the operation session runs a self-check and lists what is missing, each with its fix. <br> It re-creates its check-in timer before the timer expires, and warns before the app's limit on unanswered messages is reached. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [dependency-held](Tests#t-dependency-held) | requirement | MON-1 | Given a goal that depends on an unmerged goal, when the queue runs, then it is held until that goal merges. | PASS 2026-11-09 |
| [no-line-in-governor](Tests#t-no-line-in-governor) | requirement | MON-1 | Given the governing session, when goals run, then no goal runs inside it. | PASS 2026-11-18 |
| [skill-says-governs](Tests#t-skill-says-governs) | requirement | MON-1 | Given the delivery skill, when it is read, then it says the operation session only governs. | PASS 2026-11-18 |
| [dependencies-on-map](Tests#t-dependencies-on-map) | requirement | MON-1 | Given a goal that waits on others, when it starts, then it records what it waits on. | PASS 2026-11-09 |
| [failed-waits-mender](Tests#t-failed-waits-mender) | requirement | MON-1 | Given a failed goal, when mending is due, then it waits before a mender starts. | PASS 2026-11-09 |
| [worker-refuses](Tests#t-worker-refuses) | requirement | MON-1 | Given the governing session, when building is attempted inside it, then it is refused with one line. | PASS 2026-11-18 |
| [worker-per-goal](Tests#t-worker-per-goal) | requirement | MON-1 | Given several goals, when they run, then each runs in its own process and worktree. | PASS 2026-11-18 |
| [one-way-to-run](Tests#t-one-way-to-run) | requirement | MON-1 | Given the tools, when a goal is started, then no old way to start it remains. | PASS 2026-11-18 |
| [operate-all](Tests#t-operate-all) | requirement | MON-1 | Given the operate command's toy suite, when it runs, then the whole suite passes. | PASS 2026-11-09 |
| [session-assign](Tests#t-session-assign) | requirement | MON-1 | Given a ready goal, when it is assigned, then it gets its own worker session in the app. | PASS 2026-11-12 |
| [session-rename](Tests#t-session-rename) | requirement | MON-1 | Given a worker session, when it takes a goal, then it is renamed after that goal. | PASS 2026-11-12 |
| [session-reuse](Tests#t-session-reuse) | requirement | MON-1 | Given a finished worker session, when a goal is ready, then the session is given the next ready goal. | PASS 2026-11-12 |
| [steps-in-session](Tests#t-steps-in-session) | requirement | MON-1 | Given a worker session, when it runs steps, then it runs each step itself with no headless agent. | PASS 2026-11-12 |
| [record-in-session](Tests#t-record-in-session) | requirement | MON-1 | Given a step a worker session ran, when it is recorded, then it is recorded as in session and a goal with no session is refused. | PASS 2026-11-12 |
| [session-holds-slot](Tests#t-session-holds-slot) | requirement | MON-1 | Given a goal in a worker session, when the parallel limit is counted, then it counts against the limit. | PASS 2026-11-12 |
| [scripts-a-monitoring-under-19000](Tests#t-scripts-a-monitoring-under-19000) | requirement | MON-1 | Given the workflow-monitoring scripts (board_report.py folded into board_log.py, whose --help exits 0), when their sizes are counted in LF bytes, then each is under 19,000 bytes. | PASS 2026-11-15 |
| [worker-reports](Tests#t-worker-reports) | requirement | MON-2 | Given a merged goal, when the board is shown, then it shows its pull request. | PASS 2026-11-18 |
| [worker-reports-live](Tests#t-worker-reports-live) | requirement | MON-2 | Given a report to a running worker, when goal.py next runs, then the report reaches its agent once. | PASS 2026-11-09 |
| [session-reports](Tests#t-session-reports) | requirement | MON-2 | Given a worker session's step report, when it arrives, then it is recorded on its goal. | PASS 2026-11-12 |
| [session-fallback](Tests#t-session-fallback) | requirement | MON-2 | Given no session can be started, when a goal runs, then it falls back to a background process and the board says so. | PASS 2026-11-12 |
| [session-answer](Tests#t-session-answer) | requirement | MON-2 | Given the owner's answer, when it is sent, then it reaches the worker session by session message. | PASS 2026-11-12 |
| [session-quiet](Tests#t-session-quiet) | requirement | MON-2 | Given a worker session silent past silent_minutes (30 by default), when the board is printed, then it shows under Issues. | PASS 2026-11-10 |
| [session-ended-waiting](Tests#t-session-ended-waiting) | requirement | MON-2 | Given a goal that ends with its pull request open, when it finishes, then it stays done and frees its session. | PASS 2026-11-10 |
| [session-tool-timeout](Tests#t-session-tool-timeout) | requirement | MON-2 | Given a hung session tool, when its timeout passes, then it is cut off and the goal falls back to a background process at once. | PASS 2026-11-10 |
| [session-tool-helper](Tests#t-session-tool-helper) | requirement | MON-2 | Given a helper process the session tool leaves running, when the call returns, then the helper never holds it up. | PASS 2026-11-10 |
| [guards-null-report-bind-mend](Tests#t-guards-null-report-bind-mend) | requirement | MON-2 | Given a failed or stopped goal restarted by a worker bind or by mend, when its record is written, then report is an empty record, never null. | not run |
| [mon6-merged-frees](Tests#t-mon6-merged-frees) | requirement | MON-6 | Given a goal whose pull request merged, when its worker reports merged, then its session goes back to the pool (archived above pool_size) and its worktree and branch are removed. | PASS 2026-11-10 |
| [mon10-replan](Tests#t-mon10-replan) | requirement | MON-10 | Given ready, mergeable and splittable goals, when the operation session re-plans, then each start, merge and split is logged once with its reason, shown in the check-in, and no running goal is stopped. | PASS 2026-11-10 |
| [mon11-full-auto](Tests#t-mon11-full-auto) | requirement | MON-11 | Given full auto on and a standing owner rule recorded, when a worker asks a recommended question, then the recommendation is sent with the rule record and logged; money, security, destructive-kind, unknown-kind and safety-class-word questions wait; turning it off applies at the next decision. | PASS 2026-11-10 |
| [auto-owner-words-wait](Tests#t-auto-owner-words-wait) | requirement | MON-11 | Given full auto on and a standing owner rule recorded, when a question asks for the owner's words (an un-review, a criteria_max raise), then it is answered with its recommendation and not held for an owner-words record (o118, which supersedes #4287). | PASS 2026-11-17 |
| [mon12-pool](Tests#t-mon12-pool) | requirement | MON-12 | Given a session pool, when it runs low, then the check-in asks to create every missing session in one step; pool.py add fills it, no pool hides the ask, and a full pool makes ready goals wait with the fix. | PASS 2026-11-10 |
| [mon13-two-layers](Tests#t-mon13-two-layers) | requirement | MON-13 | Given a second session's claim, when it claims, then the first stays an operation session and nothing refuses or warns. | PASS 2026-11-12 |
| [operation-checkout-ff](Tests#t-operation-checkout-ff) | requirement | MON-13 | Given a main checkout that is behind origin, when the operation loop runs a pass, then the checkout moves by fast-forward only, uncommitted work stays, and one line says it moved or could not. | not run |
| [mon15-pod-owner](Tests#t-mon15-pod-owner) | requirement | MON-15 | Given another pod's goal, when a pod acts on it, then it is refused naming the owner and shown owned by that pod. | PASS 2026-11-12 |
| [mon15-merge-lock](Tests#t-mon15-merge-lock) | requirement | MON-15 | Given two pods merging into one main, when they run together, then the lock serializes them. | PASS 2026-11-12 |
| [resume-ask-prompt](Tests#t-resume-ask-prompt) | requirement | MON-15 | Given a goal set to ask and auto_merge on, when it is resumed, then its prompt asks the owner and never tells the worker to run merge.py. | not run |
| [pr-queue-order](Tests#t-pr-queue-order) | requirement | MON-15 | Given three goals asking for their pr turn in one repo, when they ask oldest first, then the first runs its lane and the others are told who is ahead; a goal that left the pr step, a stopped holder and a ticket older than 30 minutes each give their place to the next. | not run |
| [pr-parallel-disjoint](Tests#t-pr-parallel-disjoint) | requirement | MON-15 | Given goals at pr, when their touches share no path, then their lanes run at once, and a goal waits only for an earlier goal whose touches overlap. | not run |
| [queue-merged-free-4343](Tests#t-queue-merged-free-4343) | requirement | MON-15 | Given a goal whose pull request merged, when the pr queue is read, then its ticket and beat are removed and it holds nobody. | not run |
| [merge-leaves-queue-4343](Tests#t-merge-leaves-queue-4343) | requirement | MON-15 | Given a merged goal, when merge.py finishes the merge, then its pr-queue ticket and beat are gone. | not run |
| [mon16-machine-line](Tests#t-mon16-machine-line) | requirement | MON-16 | Given a check-in, when it is written, then a Machine line shows free RAM, free commit memory, CPU and how many goal starts memory allows. | not run |
| [mon16-memory-floor](Tests#t-mon16-memory-floor) | requirement | MON-16 | Given free commit memory under min_free_memory_gb, when goals are ready, then none starts and each is held as memory low. | not run |
| [mon16-checkout-ff](Tests#t-mon16-checkout-ff) | requirement | MON-16 | Given a main checkout behind origin/main, when the pass runs, then the check-in asks a free worker to fast-forward it. | not run |
| [mon16-checkin-grouped](Tests#t-mon16-checkin-grouped) | requirement | MON-16 | Given a check-in, when it prints, then the Machine line follows the headline and each repo block is grouped by release milestone, then feature, with each goal's marker, time left and machine. | PASS 2026-11-16 |
| [unattended-sends-warn](Tests#t-unattended-sends-warn) | requirement | MON-18 | Given 16 cross-session sends with no owner message, when the check-in reads the count, then it warns and asks for any owner message. | not run |
| [unattended-loop-recreate](Tests#t-unattended-loop-recreate) | requirement | MON-18 | Given a check-in loop with under a day left, when the status is read, then it says RECREATE. | not run |
| [unattended-standing-worker-refused](Tests#t-unattended-standing-worker-refused) | requirement | MON-18 | Given a worker session, when it adds a standing instruction, then it is refused. | not run |
| [unattended-selfcheck-missing](Tests#t-unattended-selfcheck-missing) | requirement | MON-18 | Given a main checkout behind origin, when the start-up self-check runs, then it lists it as MISSING with its fix (the routine-rules line runs audit.py permissions check). | not run |
| [unattended-checkin-line](Tests#t-unattended-checkin-line) | requirement | MON-18 | Given the check-in, when it prints Coming up, then an Operation line carries the sends left, the loop's expiry and the standing instructions. | not run |
| - | requirement | MON-18 | no passing test | not enforced |
| - | requirement | MON-20 | no passing test | not enforced |
| - | requirement | MON-23 | no passing test | not enforced |
| [mon7-govern-blocks](Tests#t-mon7-govern-blocks) | requirement | MON-7 | Given the operation session, when it tries an edit, a commit or a push, then the govern hook refuses it with the fix, while workers, other sessions and the off switch pass. | PASS 2026-11-10 |
| [mon16-notes-pass](Tests#t-mon16-notes-pass) | requirement | MON-7 | Given the operation session, when it writes a file outside every followed repo, then the govern hook lets it through. | not run |
| [mon16-edit-inside-refused](Tests#t-mon16-edit-inside-refused) | requirement | MON-7 | Given the operation session, when it edits a file inside a followed repo, then the govern hook refuses it. | not run |
| [mon8-silent-30](Tests#t-mon8-silent-30) | requirement | MON-8 | Given a worker with no report for 31 minutes, when the operation session checks in, then it shows under Needs you; at 29 minutes it does not. | PASS 2026-11-10 |
| [mon8-silent-worker](Tests#t-mon8-silent-worker) | requirement | MON-8 | Given a running worker whose last report is 31 minutes old, when the check-in is built, then Needs you names it and a worker that reported 5 minutes ago is not named. | not run |
| [stalled-no-process-4359](Tests#t-stalled-no-process-4359) | requirement | MON-8 | Given a live goal whose log has not moved for silent_minutes and no goal.py, flow.py or lane process for it, when the check-in is built, then Needs you says STALLED, since when, and which worker to restart. Also, given a quiet goal with a process running for it, then it is not STALLED. | PASS 2026-11-17 |
| [operate-toy-no-check](Tests#t-operate-toy-no-check) | defect | [#3906](https://github.com/jcl2018/agent-workflow-template/issues/3906) closed (2026-11-13) | Given test-operate.sh, when it is read, then it no longer calls the removed goal.py check command. | PASS 2026-11-13 |
| [runs-skips-non-dict](Tests#t-runs-skips-non-dict) | defect | [#4040](https://github.com/jcl2018/agent-workflow-template/issues/4040) closed (2026-11-14) | Given a list or string JSON file in the runs folder, when watch reads the goals, then it skips it and keeps the real goals. | not run |
| [app-refuses-headless-4184](Tests#t-app-refuses-headless-4184) | defect | [#4184](https://github.com/jcl2018/agent-workflow-template/issues/4184) closed (2026-11-14) | Given workers: app and a goal with no bound session, when flow.py would start a step, then it refuses and names sessions.py bind, and a bound goal is not refused (issue 4184). | PASS 2026-11-14 |
| [new-binds-app-session-4257](Tests#t-new-binds-app-session-4257) | defect | [#4257](https://github.com/jcl2018/agent-workflow-template/issues/4257) closed (2026-11-15) | Given goal.py new run inside a Claude app worker session, when it freezes the goal, then the goal is bound to that session and BOUND is printed; outside an app session nothing is bound (issue 4257). | PASS 2026-11-15 |
| [session-board-issue98](Tests#t-session-board-issue98) | defect | [#98](https://github.com/jcl2018/agent-workflow-template/issues/98) closed (2026-11-09) | Given a goal worked in a session, when the board is printed, then it shows its session name and step and never shows it as a failed background worker. | PASS 2026-11-12 |
| [report-done-final](Tests#t-report-done-final) | defect | [#108](https://github.com/jcl2018/agent-workflow-template/issues/108) closed (2026-11-10) | Given a goal whose pull request is open (done), when a session report says running or failed, then the goal stays done. | PASS 2026-11-10 |
| [guards-resume](Tests#t-guards-resume) | defect | [#149](https://github.com/jcl2018/agent-workflow-template/issues/149) closed (2026-11-11) | Given a stopped goal worked in a session, when the operation runs goal.py resume, then it runs again in that session with who and why logged, and no headless worker starts. | PASS 2026-11-12 |
| [guards-worker-role](Tests#t-guards-worker-role) | defect | [#121](https://github.com/jcl2018/agent-workflow-template/issues/121) closed (2026-11-11) | Given a goal step run without LOOP_ROLE=worker, when it is refused, then the refusal gives the exact LOOP_ROLE=worker command for the goal's bound session, and bind prints it. | PASS 2026-11-10 |
| [guards-worktree](Tests#t-guards-worktree) | defect | [#160](https://github.com/jcl2018/agent-workflow-template/issues/160) closed (2026-11-13) | Given a session bound to a goal, when it is bound or assigned, then it is told the goal worktree to work in, and a session folder outside it is refused. | PASS 2026-11-10 |
| [worker-save-159](Tests#t-worker-save-159) | defect | [#159](https://github.com/jcl2018/agent-workflow-template/issues/159) closed (2026-11-11) | Given a worker loop whose run record is merged from outside while it runs, when the loop saves, then the outside merge is kept. | not run |
| [issue-117-bind-self](Tests#t-issue-117-bind-self) | defect | [#117](https://github.com/jcl2018/agent-workflow-template/issues/117) closed (2026-11-11) | Given a worker session that doesn't know its own id, when it runs sessions.py bind SLUG self, then it is bound by its own session id (issue: Goals can't name GitHub-side changes ... a worker session cannot find its own session id). | not run |
| [stop-tree-session-tool](Tests#t-stop-tree-session-tool) | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | Given a hung session tool or a late mender, when it is stopped on any platform, then its whole process tree goes with it. | not run |
| [who-merges-report](Tests#t-who-merges-report) | defect | [#3868](https://github.com/jcl2018/agent-workflow-template/issues/3868) closed (2026-11-13) | Given two goals at pr with auto_merge on, when a session report arrives for one, then merge.py runs for neither, and merge.py for one goal merges only that goal. | not run |
| [who-merges-fallback](Tests#t-who-merges-fallback) | defect | [#3868](https://github.com/jcl2018/agent-workflow-template/issues/3868) closed (2026-11-13) | Given a goal the operation holds and an unheld goal, both done at pr with auto_merge on, when the worker exits, then merge.py runs only for the unheld goal. | not run |
| [who-merges-hold-flag](Tests#t-who-merges-hold-flag) | defect | [#3868](https://github.com/jcl2018/agent-workflow-template/issues/3868) closed (2026-11-13) | Given a goal reported with --hold, when the worker exits, then merge.py does not run for it, whatever the report's wording says. | not run |
| [merged-frees-175](Tests#t-merged-frees-175) | defect | [#175](https://github.com/jcl2018/agent-workflow-template/issues/175) closed (2026-11-11) | Given a done goal, when its worker reports merged, then its session is freed. | PASS 2026-11-10 |
| [slot-pool-112](Tests#t-slot-pool-112) | defect | [#112](https://github.com/jcl2018/agent-workflow-template/issues/112) closed (2026-11-11) | Given a held session goal whose session was freed, when slots are counted, then it holds none and a queued goal can start. | PASS 2026-11-10 |
| [attempt-114](Tests#t-attempt-114) | defect | [#114](https://github.com/jcl2018/agent-workflow-template/issues/114) closed (2026-11-11) | Given a goal re-bound to a new session, when the old worker reports, then the report is recorded but not applied, and the freed session keeps its history. | PASS 2026-11-10 |
| [pool-edges-122](Tests#t-pool-edges-122) | defect | [#122](https://github.com/jcl2018/agent-workflow-template/issues/122) closed (2026-11-11) | Given a malformed pool entry and a retired goal with a busy session, when the pool is read, then the entry is set aside without blocking and the session is named and freed. | PASS 2026-11-10 |
| [defect-4375-toys-fake-machine](Tests#t-defect-4375-toys-fake-machine) | defect | [#4375](https://github.com/jcl2018/agent-workflow-template/issues/4375) closed (2026-11-15) | Given a runner or PC short of free memory, when a toy that starts goals runs, then it sees a made-up machine with room, and a toy that sets its own machine keeps it. | not run |
| [pr-order-one-queue](Tests#t-pr-order-one-queue) | defect | [#3922](https://github.com/jcl2018/agent-workflow-template/issues/3922) closed (2026-11-14) | Given three goals retrying their pr turn in a loop, when each asks, then every goal sees one order by first-join time, a retry touches only the heartbeat, and no goal without a readable ticket counts as first. | not run |
| [pull-ff-only-passes](Tests#t-pull-ff-only-passes) | defect | [#495](https://github.com/jcl2018/agent-workflow-template/issues/495) closed (2026-11-11) | Given the operation session, when it runs git pull --ff-only (also with -C and a remote), then the govern hook lets it through. | PASS 2026-11-12 |
| [pull-plain-blocked](Tests#t-pull-plain-blocked) | defect | [#495](https://github.com/jcl2018/agent-workflow-template/issues/495) closed (2026-11-11) | Given the operation session, when it runs a plain git pull, -r, --rebase=merges, --no-ff, --ff-only with --rebase or --ff, a +refspec or -f, then the govern hook still refuses it (negative control). | PASS 2026-11-12 |
