<!-- workflow-docs -->
# Check-in and board

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/6

Review: **Unreviewed** <!-- kept merge-private-lane-import@3b270e3c -->

How to use: [How-to-use-Check-in-and-board](How-to-use-Check-in-and-board)

## Problem

- I can see what is running, stuck or waiting on me, the same way every time, without opening each session.

## Requirements

### Functional

- CHK-1: **Reviewed 2026-11-19** One live board and fixed check-in layout <!-- reviewed 96a5321f -->
  - Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. Merged work and history are left out, and a stuck worker stays at the top until I answer. [CHK-1]
  - Only operation-top publishes the 5-minute Loop Board; its layout (Your move, Release goals with progress, Critical path with clock ETAs and no tags, Workers) is fixed by the frozen board template until the skillset board skill exists (planned). A machine session prints one line and sends STATUS. [CHK-1]
  - The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. A hook blocks a reply that doesn't follow it. [CHK-2]
  - A machine session's check-in is one line (the time plus 'STATUS sent' or 'no change') once STATUS went to top; top keeps the full layout. The hook accepts the one-line form only in machine mode. [CHK-2]
  - The check-in's dependency map is grouped by repo, then by release. Each goal shows its status, expected time left and machine; each release shows its expected time and how many goals haven't started; only live goals are drawn. [CHK-5]
  - A check-in lists this machine's goals in full and, for every other machine, one row per goal with its agent, step and status from that machine's latest report. It never asks me another machine's questions. [CHK-6]

### Non-functional

None

## Non-goals

- The check-in and board only report: they never start, stop or merge a goal; the operation session does (Operation).
- They never show merged work or history, and never ask me another machine's questions.

## Success metrics

- The board and every full check-in print in the same layout every time, at least every 30 minutes by default.
- Every item under Needs you says what it holds up, and the board builds in under 10 seconds.

## Revisions

### Retired

- CHK-2: moved to CHK-1
- CHK-3: moved to MCH-5
- CHK-4: moved to HLT-7
- CHK-5: moved to CHK-1
- CHK-6: moved to CHK-1
- CHK-7: moved to OPS-1
- CHK-8: moved to HLT-7
- CHK-9: moved to MCH-5

### CHK-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r6 | 2026-11-19 | One live board and fixed check-in layout <br> Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. Merged work and history are left out, and a stuck worker stays at the top until I answer. [CHK-1] <br> Only operation-top publishes the 5-minute Loop Board; its layout (Your move, Release goals with progress, Critical path with clock ETAs and no tags, Workers) is fixed by the frozen board template until the skillset board skill exists (planned). A machine session prints one line and sends STATUS. [CHK-1] <br> The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. A hook blocks a reply that doesn't follow it. [CHK-2] <br> A machine session's check-in is one line (the time plus 'STATUS sent' or 'no change') once STATUS went to top; top keeps the full layout. The hook accepts the one-line form only in machine mode. [CHK-2] <br> The check-in's dependency map is grouped by repo, then by release. Each goal shows its status, expected time left and machine; each release shows its expected time and how many goals haven't started; only live goals are drawn. [CHK-5] <br> A check-in lists this machine's goals in full and, for every other machine, one row per goal with its agent, step and status from that machine's latest report. It never asks me another machine's questions. [CHK-6] | TOP-DECISION 136: the board layout is fixed by the frozen template until the skillset board skill exists | o444: "approved by operation-top under owner delegation (DOC-2, o371); TOP-DECISION 136: CHK-1's board" |
| r5 | 2026-11-19 | One live board and fixed check-in layout <br> Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. Merged work and history are left out, and a stuck worker stays at the top until I answer. [CHK-1] <br> Only operation-top publishes the 5-minute Loop Board; its layout (Your move, Release goals with progress, Critical path with clock ETAs and no tags, Workers) is owned by the skillset board skill. A machine session prints one line and sends STATUS. [CHK-1] <br> The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. A hook blocks a reply that doesn't follow it. [CHK-2] <br> A machine session's check-in is one line (the time plus 'STATUS sent' or 'no change') once STATUS went to top; top keeps the full layout. The hook accepts the one-line form only in machine mode. [CHK-2] <br> The check-in's dependency map is grouped by repo, then by release. Each goal shows its status, expected time left and machine; each release shows its expected time and how many goals haven't started; only live goals are drawn. [CHK-5] <br> A check-in lists this machine's goals in full and, for every other machine, one row per goal with its agent, step and status from that machine's latest report. It never asks me another machine's questions. [CHK-6] | carries the owner-approved #5186 CHK-1 r3 sentences (o141-o144) | o427: "approve OPS-11 r3, OPS-16 r3, OPS-13 r2, CHK-1 r3. (owner ~23:28, relayed" |
| r4 | 2026-11-19 | One live board and fixed check-in layout <br> Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. Merged work and history are left out, and a stuck worker stays at the top until I answer. [CHK-1] <br> Top's 5-minute board order is: Issues and needs-owner first, then Running goals, Queued goals, dependency arrows, per-machine STATUS with a call-out for any STATUS over 30 minutes old, then one finish time. Only top publishes it; a machine session prints one line and sends STATUS. [CHK-1] <br> The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. A hook blocks a reply that doesn't follow it. [CHK-2] <br> A machine session's check-in is one line (the time plus 'STATUS sent' or 'no change') once STATUS went to top; top keeps the full layout. The hook accepts the one-line form only in machine mode. [CHK-2] <br> The check-in's dependency map is grouped by repo, then by release. Each goal shows its status, expected time left and machine; each release shows its expected time and how many goals haven't started; only live goals are drawn. [CHK-5] <br> A check-in lists this machine's goals in full and, for every other machine, one row per goal with its agent, step and status from that machine's latest report. It never asks me another machine's questions. [CHK-6] | consolidation (TOP-DECISION 89) | o339: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r3 | 2026-11-19 | Live board <br> Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. <br> Merged work and history are left out, and a stuck worker stays at the top until I answer. <br> Only operation-top publishes the 5-minute Loop Board; its layout (Your move, Release goals with progress, Critical path with clock ETAs and no tags, Workers) is owned by the skillset board skill. A machine session prints one line and sends STATUS. | TOP-DECISION 65 and 66: the Loop Board layout is owned by the skillset board skill; the report and dashboard order is unchanged. owner, typed in operation-top at about 23:28, relayed verbatim: "approve OPS-11 r3, OPS-16 r3, OPS-13 r2, CHK-1 r3." | o144: "approve OPS-11 r3, OPS-16 r3, OPS-13 r2, CHK-1 r3. (owner, typed in" |
| r2 | 2026-11-18 | Live board <br> Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. <br> Merged work and history are left out, and a stuck worker stays at the top until I answer. <br> Top's 5-minute board order is: Issues and needs-owner first, then Running goals, Queued goals, dependency arrows, per-machine STATUS with a call-out for any STATUS over 30 minutes old, then one finish time. Only top publishes it; a machine session prints one line and sends STATUS. | three-level-ops re-landed: its three-layer, machine-session and STATUS rule, ported onto CHK-1 from the old Monitoring requirement | o80: "Yes, I want you to handle all of the questions except the" |
| r1 | 2026-11-18 | Live board <br> Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. <br> Merged work and history are left out, and a stuck worker stays at the top until I answer. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | A check-in on a cadence, in one layout <br> The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. <br> Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. <br> A hook blocks a reply that doesn't follow it. <br> A machine session's check-in is one line (the time plus 'STATUS sent' or 'no change') once STATUS went to top; top keeps the full layout. The hook accepts the one-line form only in machine mode. | consolidation (TOP-DECISION 89): absorbed into CHK-1 | o340: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A check-in on a cadence, in one layout <br> The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. <br> Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. <br> A hook blocks a reply that doesn't follow it. <br> A machine session's check-in is one line (the time plus 'STATUS sent' or 'no change') once STATUS went to top; top keeps the full layout. The hook accepts the one-line form only in machine mode. | three-level-ops re-landed: its three-layer, machine-session and STATUS rule, ported onto CHK-2 from the old Monitoring requirement | o80: "Yes, I want you to handle all of the questions except the" |
| r1 | 2026-11-18 | A check-in on a cadence, in one layout <br> The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. <br> Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. <br> A hook blocks a reply that doesn't follow it. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Notify me by mail <br> When notification is on for this machine, each check-in mails me once per new event, such as a new Needs you item or a goal that stopped or passed its ETA. | consolidation (TOP-DECISION 89): absorbed into MCH-5 | o337: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Notify me by mail <br> When notification is on for this machine, each check-in mails me once per new event, such as a new Needs you item or a goal that stopped or passed its ETA. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A check-in with nothing new costs nothing <br> A scheduled check-in that is the same as the last full one, apart from its machine line and numbers, is one line, printed without a model turn, for at most two hours in a row. <br> Each check-in logs the tokens the operation session spent. | consolidation (TOP-DECISION 89): absorbed into HLT-7 | o273: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A check-in with nothing new costs nothing <br> A scheduled check-in that is the same as the last full one, apart from its machine line and numbers, is one line, printed without a model turn, for at most two hours in a row. <br> Each check-in logs the tokens the operation session spent. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Dependency map <br> The check-in's dependency map is grouped by repo, then by release. <br> Each goal shows its status, expected time left and machine; each release shows its expected time and how many goals haven't started; only live goals are drawn. | consolidation (TOP-DECISION 89): absorbed into CHK-1 | o341: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Dependency map <br> The check-in's dependency map is grouped by repo, then by release. <br> Each goal shows its status, expected time left and machine; each release shows its expected time and how many goals haven't started; only live goals are drawn. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | What a check-in shows of other machines <br> A check-in lists this machine's goals in full and, for every other machine, one row per goal with its agent, step and status from that machine's latest report. <br> It never asks me another machine's questions. | consolidation (TOP-DECISION 89): absorbed into CHK-1 | o342: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | What a check-in shows of other machines <br> A check-in lists this machine's goals in full and, for every other machine, one row per goal with its agent, step and status from that machine's latest report. <br> It never asks me another machine's questions. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Blockers first <br> Each item under Needs you says what it holds up and whether it is on the critical path to the next release, and items are sorted with the one holding up the most goals first. | consolidation (TOP-DECISION 89): absorbed into OPS-1 | o259: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Blockers first <br> Each item under Needs you says what it holds up and whether it is on the critical path to the next release, and items are sorted with the one holding up the most goals first. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Fast board <br> The live board builds and prints in under 10 seconds on this repo. | consolidation (TOP-DECISION 89): absorbed into HLT-7 | o274: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Fast board <br> The live board builds and prints in under 10 seconds on this repo. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### CHK-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | I can answer and steer from my phone or mail <br> I can answer any question under Needs you by replying to its mail or from my phone, with the same words a typed answer takes, and start, stop or reorder goals the same way. <br> A reply counts as my words only when it comes from my own address or signed-in session. | consolidation (TOP-DECISION 89): absorbed into MCH-5 | o338: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | I can answer and steer from my phone or mail <br> I can answer any question under Needs you by replying to its mail or from my phone, with the same words a typed answer takes, and start, stop or reorder goals the same way. <br> A reply counts as my words only when it comes from my own address or signed-in session. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [retired-leaves-waiting](Tests#t-retired-leaves-waiting) | requirement | CHK-1 | Given a retired goal, when the board is shown, then it no longer shows under Issues. | PASS 2026-11-09 |
| [waits-first](Tests#t-waits-first) | requirement | CHK-1 | Given a live board, when the board page is opened, then it shows the live board. | PASS 2026-11-09 |
| [no-change-quiet](Tests#t-no-change-quiet) | requirement | CHK-1 | Given a board field the old board lacked or gh not answering, when boards are compared, then it counts as no change. | PASS 2026-11-09 |
| [board-sections](Tests#t-board-sections) | requirement | CHK-1 | Given a live board, when the board page is built, then it carries the live board's sections. | PASS 2026-11-09 |
| [stuck-stays-top](Tests#t-stuck-stays-top) | requirement | CHK-1 | Given a stuck goal, when the board is shown, then it stays on top until answered. | PASS 2026-11-19 |
| [status-order](Tests#t-status-order) | requirement | CHK-1 | Given the live board, when it is printed, then it lists Issues, Running goals, Queued goals, Dependencies and Finish in that order. Given two machines' STATUS, when top builds the board, then one board lists both machines' running goals. | PASS 2026-11-19 |
| [needs-you-stuck](Tests#t-needs-you-stuck) | requirement | CHK-1 | Given failed and waiting goals, when the board is printed, then Issues holds them with the exact words to type. | PASS 2026-11-19 |
| [estimates-shown](Tests#t-estimates-shown) | requirement | CHK-1 | Given a running goal, when the board is printed, then it shows its time left from past runs and its step flow. | PASS 2026-11-19 |
| [status-roadmap-features](Tests#t-status-roadmap-features) | requirement | CHK-1 | Given merged goals, when the live board is printed, then they do not appear. | PASS 2026-11-09 |
| [operate-wakes-on-report](Tests#t-operate-wakes-on-report) | requirement | CHK-1 | Given a worker's report, when it arrives before the cadence, then operate wakes and every pass prints the full board. | PASS 2026-11-09 |
| [status-graph-order](Tests#t-status-graph-order) | requirement | CHK-1 | Given the live board, when it is printed, then its sections come in a fixed order. | PASS 2026-11-12 |
| [status-graph-levels](Tests#t-status-graph-levels) | requirement | CHK-1 | Given chained goals, when the board is printed, then they are drawn as a top-to-bottom graph between running and queued goals. | PASS 2026-11-12 |
| [status-graph-marks](Tests#t-status-graph-marks) | requirement | CHK-1 | Given running and merged goals, when the board is printed, then a running goal shows a 10-cell bar and time left and merged goals are left out. | PASS 2026-11-12 |
| [status-graph-total](Tests#t-status-graph-total) | requirement | CHK-1 | Given chained estimates, when the finish time is computed, then it is the longest chain of estimates, not their sum. | PASS 2026-11-12 |
| [status-graph-board](Tests#t-status-graph-board) | requirement | CHK-1 | Given the live board, when the board artifact page is shown, then it shows the same live board. | PASS 2026-11-12 |
| [step-label-live](Tests#t-step-label-live) | requirement | CHK-1 | Given a step, when it starts, then its label changes and a finished step is never shown as current. | PASS 2026-11-12 |
| [live-board-header](Tests#t-live-board-header) | requirement | CHK-1 | Given the board, when it is printed, then it starts with a LIVE BOARD header of repo, local time, version and health. | PASS 2026-11-12 |
| [live-board-flow](Tests#t-live-board-flow) | requirement | CHK-1 | Given a running goal, when the board is printed, then its step flow ticks done steps and brackets the current one. | PASS 2026-11-12 |
| [live-board-arrows](Tests#t-live-board-arrows) | requirement | CHK-1 | Given dependencies between running and queued goals, when the board is printed, then they are drawn as a top-to-bottom graph. | PASS 2026-11-12 |
| [live-board-issues](Tests#t-live-board-issues) | requirement | CHK-1 | Given a stuck worker, when the board is printed, then Issues puts it first with its fix in plain words. | PASS 2026-11-12 |
| [live-board-leftouts](Tests#t-live-board-leftouts) | requirement | CHK-1 | Given merged work, history, totals, milestones, tokens and done lines, when the board is printed, then they are left off. | PASS 2026-11-12 |
| [live-board-no-oneline](Tests#t-live-board-no-oneline) | requirement | CHK-1 | Given an unchanged pass, when the operation session checks in, then the full check-in is printed again and there is no one-line mode. Given the machine role, when a pass runs, then it prints one line, no board, and publishes no Loop Board. | PASS 2026-11-19 |
| [live-board-cadence](Tests#t-live-board-cadence) | requirement | CHK-1 | Given no cadence setting, when check-ins are scheduled, then the cadence is 30 minutes. Given a STATUS older than 30 minutes, when top builds the board, then it calls the machine out and not a fresh one. | PASS 2026-11-19 |
| [reply-hook-blocks](Tests#t-reply-hook-blocks) | requirement | CHK-1 | Given an operation-session check-in reply, when it stops without the headline, All sessions, Dependencies, Needs you and Coming up last, then the hook blocks it and says what is missing, and a reply in that layout passes. | PASS 2026-11-10 |
| [reply-hook-scope](Tests#t-reply-hook-scope) | requirement | CHK-1 | Given a worker session or a session in another repo, when it stops with any reply, then the hook never checks it, and only the operation session is checked. Given a machine session's one-line check-in once STATUS went to top, when the reply hook checks it, then it passes, while top keeps the full-layout check. | PASS 2026-11-19 |
| [reply-hook-off](Tests#t-reply-hook-off) | requirement | CHK-1 | Given reply_hook set to false in the config, when the operation session stops without the board, then the hook lets it through. | PASS 2026-11-19 |
| [reply-hook-guard](Tests#t-reply-hook-guard) | requirement | CHK-1 | Given a reply blocked twice in a row or a broken hook input, when the session stops again, then the hook lets it through and logs it instead of looping. | PASS 2026-11-19 |
| [reply-hook-install](Tests#t-reply-hook-install) | requirement | CHK-1 | Given a repo, when setup --reply-hook runs, then the Stop hook is merged into its machine-local Claude settings, which git ignores, and a second run changes nothing. | PASS 2026-11-19 |
| [reply-hook-all](Tests#t-reply-hook-all) | requirement | CHK-1 | Given the reply hook's toy suite, when it runs, then every check passes. | PASS 2026-11-10 |
| [reply-hook-mon5-wording](Tests#t-reply-hook-mon5-wording) | requirement | CHK-1 | Given the Check-in and board PRD, when CHK-2 is read, then it carries the check-in layout the hook enforces. | PASS 2026-11-19 |
| [depth-on-board](Tests#t-depth-on-board) | requirement | CHK-1 | Given a running goal with recorded steps, when the live board prints, then it shows each step's depth and the setting. | PASS 2026-11-10 |
| [held-all](Tests#t-held-all) | requirement | CHK-1 | Given the board-held toy repo, when every check runs (held, freezing, pool lock, free, bind, done is final, fail-closed watch and mend, assign races), then all pass. | PASS 2026-11-10 |
| [est-area](Tests#t-est-area) | requirement | CHK-1 | Given touched paths, when a goal's size is counted, then each folds to one area: a skill folder, else its first folder, else the root file. | not run |
| [est-size](Tests#t-est-size) | requirement | CHK-1 | Given a goal file and a queue line, when a goal's size is read, then the goal file's numbered done lines and touches win, and fenced or verify steps never count. | not run |
| [est-similar](Tests#t-est-similar) | requirement | CHK-1 | Given five finished goals of a similar size, when a goal is estimated, then their times set it and it is not rough; with four it falls back to every finished goal and reads rough. | not run |
| [est-monotone](Tests#t-est-monotone) | requirement | CHK-1 | Given goals of growing size, when they are estimated, then a goal with more done lines or touched areas always gets a longer estimate. | not run |
| [est-lift-bound](Tests#t-est-lift-bound) | requirement | CHK-1 | Given a small size whose past goals were slow, when a larger goal is estimated, then it is never shorter, and the lift stays within one minute per extra unit. | not run |
| [est-range-text](Tests#t-est-range-text) | requirement | CHK-1 | Given an estimate, when the board shows it, then it reads low to high left, adds rough when rough, and fits the board width. | not run |
| [est-pace](Tests#t-est-pace) | requirement | CHK-1 | Given a running goal faster or slower than its estimate, when it is re-estimated, then the steps left scale by its pace, held between half and double. | not run |
| [est-overrun-range](Tests#t-est-overrun-range) | requirement | CHK-1 | Given a running step before, at and past its estimate, when the goal is estimated, then its low, estimate and high stay in order. | not run |
| [est-offflow](Tests#t-est-offflow) | requirement | CHK-1 | Given a goal at an off-flow step after build, when it is estimated, then it counts from build onward, never from idea. | not run |
| [est-flow-seconds](Tests#t-est-flow-seconds) | requirement | CHK-1 | Given a run log with reports, checks and a pause, when step times are counted, then reports and checks count toward the step in force and the pause counts nothing. | not run |
| [est-partial](Tests#t-est-partial) | requirement | CHK-1 | Given a goal whose later steps have no history, when the board is shown, then it reads rough and the finish time says at least. | not run |
| [est-unsafe-slug](Tests#t-est-unsafe-slug) | requirement | CHK-1 | Given a bad slug or an unreadable goal file, when a goal is estimated, then it is unknown size and rough, and the board still renders. | not run |
| [est-big-goal](Tests#t-est-big-goal) | requirement | CHK-1 | Given a goal larger than every finished one, when the board is shown, then it renders quickly and reads rough. | not run |
| [est-cache](Tests#t-est-cache) | requirement | CHK-1 | Given a finished run that changes, when the board is shown again in the same process, then the estimate changes. | not run |
| [mon4-checkin-no-board](Tests#t-mon4-checkin-no-board) | requirement | CHK-1 | Given running goals, when the operation session checks in, then it prints the check-in layout and not the live board, while report still prints the board. | PASS 2026-11-10 |
| [checkin-passes-hook](Tests#t-checkin-passes-hook) | requirement | CHK-1 | Given the check-in operate.py prints, when the reply hook checks it, then it passes the layout. | PASS 2026-11-10 |
| [est-worktree](Tests#t-est-worktree) | requirement | CHK-1 | Given a running goal whose goal file sits only in its worktree, when its size is read, then the worktree's goal file sizes it, and a worktree outside the loop worktrees folder is never read. | not run |
| [est-similar-step](Tests#t-est-similar-step) | requirement | CHK-1 | Given five similar finished goals that never logged a step, when that step is estimated, then it comes from every finished goal, while steps they logged come from them. | not run |
| [est-stall-held](Tests#t-est-stall-held) | requirement | CHK-1 | Given a goal far past three times its step estimate, when it has no worker and is held, then it is never shown as stalled under Issues. | not run |
| [est-backtest-best](Tests#t-est-backtest-best) | requirement | CHK-1 | Given two fixture sets of 12 finished goals, one where time grows with size and one where it does not, when the board picks its estimate model, then it is the backtest's lowest score in both: the size rule in the first, step medians in the second. | not run |
| [est-backtest-loo](Tests#t-est-backtest-loo) | requirement | CHK-1 | Given three finished goals, when the backtest leaves each out, then every candidate's prediction and the score equal the values worked out by hand without that goal. | not run |
| [est-accuracy-line](Tests#t-est-accuracy-line) | requirement | CHK-1 | Given 12 finished goals, when the board is shown, then the line under the finish time names the model in use and its typical whole-goal error; under 10 goals it says the error is not known yet. | not run |
| [est-backtest-fails](Tests#t-est-backtest-fails) | requirement | CHK-1 | Given a backtest that raises an error, when the board is shown, then it still renders with the size rule, says the backtest failed, and prints the traceback to stderr. | not run |
| [est-stall-floor](Tests#t-est-stall-floor) | requirement | CHK-1 | Given a step with a 2-minute estimate, when it has run 10 minutes, then it is not stalled, and at 16 minutes it is. | not run |
| [est-held-idle](Tests#t-est-held-idle) | requirement | CHK-1 | Given a held goal, or a log with a hold or free entry, when step time is counted, then held time adds nothing until the goal resumes, and its time left is the same an hour later. | not run |
| [est-module-size](Tests#t-est-module-size) | requirement | CHK-1 | Given the board's estimate code split into modules, when they are loaded, then each is under 19,000 bytes and every name readers use still resolves from board_status. | not run |
| [est-backtest-speed](Tests#t-est-backtest-speed) | requirement | CHK-1 | Given 100 finished goals, when the backtest runs, then it takes under 3 CPU seconds (measured 0.08), and the board over 300 finished goals renders in under 5 CPU seconds. | not run |
| [est-steps-monotone](Tests#t-est-steps-monotone) | requirement | CHK-1 | Given the step medians and blend models, when a larger goal is estimated, then it gets a strictly longer estimate, even past a size with no time. | not run |
| [est-recompute](Tests#t-est-recompute) | requirement | CHK-1 | Given the same finished runs, when the board is shown twice, then the backtest is reused; when one more run finishes, then it is worked out again (a running goal's change also recomputes it). | not run |
| [est-pool-unread-stall](Tests#t-est-pool-unread-stall) | requirement | CHK-1 | Given the session pool can't be read and a goal's log ends in a hold entry, when the board is shown, then the goal is not listed as stalled. | not run |
| [mon14-repo-blocks](Tests#t-mon14-repo-blocks) | requirement | CHK-1 | Given a cross-repo dependency, when the check-in prints, then it is listed between headed repo blocks. | PASS 2026-11-12 |
| [est-time-order-mon4](Tests#t-est-time-order-mon4) | requirement | CHK-1 | Given goals that finished before, exactly when, during and after a goal started, and one with inverted stamps, when the board backtests, then each goal is predicted only from goals that finished strictly before it started and never from itself. | not run |
| [mon14-reply-repo-blocks](Tests#t-mon14-reply-repo-blocks) | requirement | CHK-1 | Given a check-in reply whose Dependencies section has no == repo == block, when the reply hook checks it, then it flags the missing repo block. | not run |
| [mon14-reply-deps-whole](Tests#t-mon14-reply-deps-whole) | requirement | CHK-1 | Given a check-in reply whose Dependencies section leaves out a running goal of the board, when the reply hook checks it, then it names that goal, and a reply that draws every goal passes. | not run |
| [mon-stray-runs](Tests#t-mon-stray-runs) | requirement | CHK-1 | Given a file in loop/runs that is not a run record, when report or dashboard runs, then it is skipped and the board prints. | PASS 2026-11-14 |
| [mon14-map-finish](Tests#t-mon14-map-finish) | requirement | CHK-1 | Given live goals with past runs to estimate from, when the check-in draws Dependencies, then each repo block ends with its expected finish. | not run |
| [mon14-map-arrows](Tests#t-mon14-map-arrows) | requirement | CHK-1 | Given a goal that waits on another, when the check-in draws Dependencies, then the wait is drawn as an arrow. | not run |
| [mon14-map-live-only](Tests#t-mon14-map-live-only) | requirement | CHK-1 | Given a record with no goal, a stopped goal, a left goal and a worker held at pr, when the check-in draws Dependencies, then only live goals show and the held one reads holding. | not run |
| [mon14-map-times](Tests#t-mon14-map-times) | requirement | CHK-1 | Given live goals with past runs to estimate from, when the check-in draws Dependencies, then each goal shows its time left. | not run |
| [machine-local-checkin](Tests#t-machine-local-checkin) | requirement | CHK-1 | Given proofs owed to another machine, when the check-in is written, then they are listed under Coming up as off-machine to-dos, not as blockers. | not run |
| [held-time-session-hold](Tests#t-held-time-session-hold) | requirement | CHK-1 | Given a goal held by a session report, when its time budget is read, then the held time counts nothing. | PASS 2026-11-14 |
| [roadmap-closed-drops](Tests#t-roadmap-closed-drops) | requirement | CHK-1 | Given a Roadmap row for an issue that is closed, when batch.py roadmap runs, then the row is not on the page. | PASS 2026-11-15 |
| [roadmap-status-values](Tests#t-roadmap-status-values) | requirement | CHK-1 | Given a running goal that names an issue and a goal in queue.md, when batch.py roadmap runs, then their rows read in flight and queued and any other row reads open. | not run |
| [roadmap-backlog-apart](Tests#t-roadmap-backlog-apart) | requirement | CHK-1 | Given an open issue on a Backlog milestone, when batch.py roadmap runs, then it is listed under After v1.0 and in no v1.0.0 group. | not run |
| [roadmap-priority-empty](Tests#t-roadmap-priority-empty) | requirement | CHK-1 | Given the v1.0.0 group rows, when batch.py roadmap runs, then each row's Priority cell is empty for the owner to fill. | not run |
| [roadmap-unreviewed-listed](Tests#t-roadmap-unreviewed-listed) | requirement | CHK-1 | Given a wiki page with an Unreviewed requirement, when batch.py roadmap runs, then the page and requirement are listed. | not run |
| [roadmap-todos-apart](Tests#t-roadmap-todos-apart) | requirement | CHK-1 | Given an open To-do issue, when batch.py roadmap runs, then it is listed under off-machine to-dos and in no group. | not run |
| [roadmap-hand-backlog-once](Tests#t-roadmap-hand-backlog-once) | requirement | CHK-1 | Given a hand row for an issue on a Backlog milestone or a To-do issue, when batch.py roadmap runs, then the issue is listed once, apart, and not in a v1.0.0 group. | not run |
| [roadmap-finished-not-queued](Tests#t-roadmap-finished-not-queued) | requirement | CHK-1 | Given a goal still named in queue.md whose run record is done, when batch.py roadmap runs, then an issue it names reads open, not queued. | not run |
| [roadmap-paths-scrubbed](Tests#t-roadmap-paths-scrubbed) | requirement | CHK-1 | Given a run record whose goal text holds a home folder path, when batch.py roadmap runs, then the page shows no user name or path. | not run |
| [roadmap-odd-input-ok](Tests#t-roadmap-odd-input-ok) | requirement | CHK-1 | Given a null issues file, an issue with no title and an --out folder that does not exist, when batch.py roadmap runs, then it finishes without a traceback and still writes the page. | not run |
| [budget-fair-base-moved](Tests#t-budget-fair-base-moved) | requirement | CHK-1 | Given five pr lanes that each end BASE_MOVED (a refused merge, or main moved), when the time budget is read, then none of that lane time is charged: only the 30 minutes of steps count, and neither a 60 minute budget nor a 400 minute one with 24 lost lanes is stopped (#4261). | PASS 2026-11-15 |
| [budget-fair-failed-stays](Tests#t-budget-fair-failed-stays) | requirement | CHK-1 | Given a pr lane that really failed, when the time budget is read, then its time is still charged. | PASS 2026-11-15 |
| [budget-fair-held-time](Tests#t-budget-fair-held-time) | requirement | CHK-1 | Given a goal held in the pr queue, on a hold, on an owner answer or after a stop, when the time budget is read, then that time is never charged, and a goal that truly runs past its budget is still stopped (#3878). | PASS 2026-11-15 |
| [mon14-merged-since-once](Tests#t-mon14-merged-since-once) | requirement | CHK-1 | Given a goal merged since the previous check-in, when the check-in draws Dependencies, then it is listed once as [x]. | not run |
| [mon14-merged-before-dropped](Tests#t-mon14-merged-before-dropped) | requirement | CHK-1 | Given a goal merged before the previous check-in, when the check-in draws and checks Dependencies, then it is neither drawn nor required. | not run |
| [mon5-pr-merged-closes](Tests#t-mon5-pr-merged-closes) | requirement | CHK-1 | Given a done run whose pull request merged on GitHub before the last check-in, when the check-in prints, then the goal is gone from the graph and the check. | not run |
| [mon5-merged-pr-retires](Tests#t-mon5-merged-pr-retires) | requirement | CHK-1 | Given a running record whose pull request merged, when it is retired with --pr, then it closes for good; with no merged pull request it is still refused. | not run |
| [mon17-this-pod-only](Tests#t-mon17-this-pod-only) | requirement | CHK-1 | Given goals of two pods, when the check-in is written, then only this pod's goals are listed and the other pod gets one line. | not run |
| [review-board-shows-wait](Tests#t-review-board-shows-wait) | requirement | CHK-1 | Given a goal held by review_hold, when the live board lists its Issues, then it says merge waiting on review and names the review.py command. | not run |
| [machine-guide-monitoring](Tests#t-machine-guide-monitoring) | requirement | CHK-1 | Given the operation guide, when it is read, then it holds the check-in layout, full-auto rules, decision log and held-line conventions, and the check-in routine file is only a pointer to it. | not run |
| [mon5-checkin-machine-line](Tests#t-mon5-checkin-machine-line) | requirement | CHK-1 | Given a check-in reply with no Machine line, when the reply hook checks it, then it flags it, and a reply with the Machine line and every goal line passes; and given an All sessions row whose for cell is only a slug or issue number, then it flags that row. | PASS 2026-11-16 |
| [mon14-checkin-goal-lines](Tests#t-mon14-checkin-goal-lines) | requirement | CHK-1 | Given a Dependencies goal with no status marker, time left or machine, when the reply hook checks the check-in, then it flags the goal by name. | PASS 2026-11-16 |
| [mon14-release-eta](Tests#t-mon14-release-eta) | requirement | CHK-1 | Given a check-in whose release header has no release ETA, when the reply hook checks it, then it flags it, and a header with the ETA and its counts passes. | PASS 2026-11-16 |
| [eta-checkin-table](Tests#t-eta-checkin-table) | requirement | CHK-1 | Given goals with and without an ETA, when the check-in's All sessions table is built, then each goal's time left cell also shows its ETA clock time, ETA passed, or no ETA (a goal frozen before ETAs reads no ETA until the owner gives it one; hard ETA, DEL-17). | not run |
| [held-charge-pauses](Tests#t-held-charge-pauses) | requirement | CHK-1 | Given a goal that runs 30 minutes, is paused 300 minutes (goal.py wait, or a session report that says waiting or paused) and runs 20 more, when the minute budget is read through fit.budget_stop, then it is charged 50, and the same goal running 350 minutes with no pause is charged 350 and stopped by a smaller budget. | not run |
| [notify-new-events](Tests#t-notify-new-events) | requirement | CHK-1 | Given a fake mailer and notification settings, when notification runs, then each new event names its goal and owner action once, repeated or disabled events send nothing, the first run only records a baseline, no address is printed or kept, and the private setting defaults off. | PASS 2026-11-18 |
| [notify-operate-runs](Tests#t-notify-operate-runs) | requirement | CHK-1 | Given an operation pass, when it prints the check-in, then it saves it and runs notify.py send. | not run |
| [notify-one-mail-per-event](Tests#t-notify-one-mail-per-event) | requirement | CHK-1 | Given a stopped goal that also shows under Needs you, when notify runs, then one mail goes out for it, not two. | not run |
| [held-stale-next](Tests#t-held-stale-next) | defect | [#102](https://github.com/jcl2018/agent-workflow-template/issues/102) closed (2026-11-10) | Given a session goal with an old failure report and a newer session report, when the live board prints, then its next line is the newer report. | PASS 2026-11-10 |
| [held-shows-held](Tests#t-held-shows-held) | defect | [#102](https://github.com/jcl2018/agent-workflow-template/issues/102) closed (2026-11-10) | Given a running goal with no worker (session reassigned, worktree kept), when the live board prints, then it is listed as held, not running and not as a background worker. | PASS 2026-11-10 |
| [held-freezing](Tests#t-held-freezing) | defect | [#102](https://github.com/jcl2018/agent-workflow-template/issues/102) closed (2026-11-10) | Given a goal handed to a worker session before it is frozen, when the live board prints, then it shows at once under that session with step freezing. | PASS 2026-11-10 |
| [held-off-flow](Tests#t-held-off-flow) | defect | [#102](https://github.com/jcl2018/agent-workflow-template/issues/102) closed (2026-11-10) | Given a goal whose step is outside the flow, such as checks, when the live board prints, then it keeps its last known flow step, not idea 0%. | PASS 2026-11-10 |
| [reply-hook-checkin-123](Tests#t-reply-hook-checkin-123) | defect | [#123](https://github.com/jcl2018/agent-workflow-template/issues/123) closed (2026-11-10) | Given a check-in reply that lacks the one headline, the All sessions table, the Dependencies graph, numbered Needs you or Coming up last, when it is checked, then each missing piece is named, and a reply in the issue 123 layout passes. | PASS 2026-11-10 |
| [est-stalled](Tests#t-est-stalled) | defect | [#37](https://github.com/jcl2018/agent-workflow-template/issues/37) closed (2026-11-11) | Given a running step past three times its estimate, when the board is shown, then the goal shows under Issues as stalled, naming the step and how long it has run. | not run |
| [est-issue-96](Tests#t-est-issue-96) | defect | [#96](https://github.com/jcl2018/agent-workflow-template/issues/96) closed (2026-11-11) | Given two queued goals of different sizes, when the board is shown, then they get different estimates, each inside the range of their similar past goals. | not run |
| [est-offflow-done](Tests#t-est-offflow-done) | defect | [#37](https://github.com/jcl2018/agent-workflow-template/issues/37) closed (2026-11-11) | Given a goal at an off-flow step after a step's done entry, when the board is shown, then it sits at the next step, that step's time counts, and it stalls past three times its estimate. | not run |
| [deps-graph-94](Tests#t-deps-graph-94) | defect | [#94](https://github.com/jcl2018/agent-workflow-template/issues/94) closed (2026-11-11) | Given chained goals, when the board is printed, then Dependencies is a top-to-bottom graph at most 60 columns wide with markers and a legend. | PASS 2026-11-10 |
| [issues-phone-97](Tests#t-issues-phone-97) | defect | [#97](https://github.com/jcl2018/agent-workflow-template/issues/97) closed (2026-11-11) | Given four goals stopped by one usage limit, when the board is printed, then Issues shows one short line with no raw agent output and the finish says paused. | PASS 2026-11-10 |
| [report-held-111](Tests#t-report-held-111) | defect | [#111](https://github.com/jcl2018/agent-workflow-template/issues/111) closed (2026-11-11) | Given a held goal and a freezing goal, when report and the board digest are printed, then both list them. | PASS 2026-11-10 |
| [state-shared-113](Tests#t-state-shared-113) | defect | [#113](https://github.com/jcl2018/agent-workflow-template/issues/113) closed (2026-11-11) | Given running, held and waiting goals, when graph and the live board judge them, then they agree and a held goal holds no slot. | PASS 2026-11-10 |
| [held-time-115](Tests#t-held-time-115) | defect | [#115](https://github.com/jcl2018/agent-workflow-template/issues/115) closed (2026-11-11) | Given a goal held for three hours, when the board is printed, then it shows the held time, not the time since its last change. | PASS 2026-11-10 |
| [reply-checkin-321](Tests#t-reply-checkin-321) | defect | [#321](https://github.com/jcl2018/agent-workflow-template/issues/321) closed (2026-11-11) | Given a scheduled check-in prompt in the operation session and a one-line reply, when the reply hook runs, then it blocks the reply and names the missing parts. | PASS 2026-11-10 |
| [monitor-stray-runs-3862](Tests#t-monitor-stray-runs-3862) | defect | [#3862](https://github.com/jcl2018/agent-workflow-template/issues/3862) closed (2026-11-14) | Given a JSON file in loop/runs that is not a run record, when monitor.py report or dashboard runs, then it skips the file and prints (issue 3862; fixed by v0.28.51, closed with this row). | PASS 2026-11-14 |
