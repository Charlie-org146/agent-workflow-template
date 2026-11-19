<!-- workflow-docs -->
# Machines

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/23

How to use: [How-to-use-Machines](How-to-use-Machines)

Review: **Unreviewed** <!-- kept merge-private-lane-import@836ead18 -->


## Problem
- A second machine, a Mac or a Windows PC, should reach the same working setup as the one I run on from a git clone and one command, because much of what the operation relies on lives only on one machine: the skill install, the hooks, the private-names file, the check-in prompt, the routines and the mailer.
- I said it for Windows too: "that command should capture windows" (owner, 2026-11-11), so every item has a Windows form, or is named in the checklist as not yet possible, never skipped silently.
- A machine that has drifted, a skills checkout two days behind or a clone with no hooks, should say so in one line per gap, without anyone having to notice.

## Requirements

### Functional
- MCH-1: **Reviewed 2026-11-19** Any Mac or Windows machine sets up identically <!-- reviewed 81e3aa40 -->
  - Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh signed in as me, real symlinks and a supported platform, each marked present or missing with its fix. [MCH-7]
  - A second Mac or Windows machine reaches this one's setup from a git clone and one command: a dry run lists everything first, then apply installs the skill links, the hooks and the empty private files. Every item has a Windows form or is named as not yet possible. [MCH-1]
  - Given a fresh clone on a new machine, when `machine.py apply` runs (setup machine), then the operation session (its start routine and task, and the reply and govern hooks in the repo's machine-local settings), its scheduled tasks and the peer link (`~/.workflow-loop/peer.json`, holding this machine's and its peer's labels only; `--peer NAME`, default the other platform) exist, and `check` names any that is missing. [MCH-2]
  - The output ends with only the owner-only items left: the mail files, the private-names lists, account logins, the permission mode and registering tasks in the app; they are named, never created or copied. [MCH-2]
  - The machine check lists one line per gap between this machine and the expected setup, such as a skills checkout that is behind or a clone with no hooks. [MCH-10]
  - A pull request that adds a POSIX-only call without its guard (fcntl, os.getuid, os.killpg, signal.SIGHUP, os.kill(pid, 0)) fails its lane and checks, so main cannot break native Windows unseen. [DEL-12, GRD-18]
  - A long pull request body, issue text, comment or release notes always goes to gh in a file (`--body-file`, `--notes-file`), never on the command line, so a pull request with a body over 32,000 characters opens on native Windows. [DEL-12, GRD-18]
- MCH-4: **Reviewed 2026-11-19** One owner and one merge order per goal <!-- reviewed a077ab51 -->
  - Each goal has one owning machine (it records the pod that owns it), and only that owner starts, answers, merges or resumes it; others see it read-only. [MCH-4, OPS-15]
  - `machines.py handover SLUG --to MACHINE` pushes its branch, copies its record to origin and marks it `moved` on the old machine with no worker; `machines.py take SLUG` on the new machine fetches the branch and binds a worker, so a goal never runs on two machines and a second take is refused. [MCH-4]
  - With the private setting `machine_sync` on (off by default, per machine), each repo has one merge order across machines: a goal takes a merge ticket on origin before its pr lane, and a second machine's goal waits for it (a holder silent for 30 minutes is dropped). [MCH-4]
  - SNAPSHOT is structured data a machine publishes to origin, and a check-in draws one Machine line per machine from it, not from message text; a moved goal shows once, under the machine that holds it. A peer's record is data, never the owner's approval. [MCH-4]
  - A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open pull request; qa, ship and the pull request run again here before release. A branch that isn't pushed, or a goal with no done line or pull request, is refused. [MCH-8]
- MCH-5: **Reviewed 2026-11-19** One email stream, answered by reply or phone <!-- reviewed 27e882ce -->
  - Each new Needs-you item, stopped or late goal and merged release sends one mail (when `notify_email` is on) with numbered options and a recommendation, through one mailer and one send budget both machines share (`notify_budget` a day, default 20); a second machine never mails an event the first one did. [MCH-5]
  - When notification is on for this machine, each check-in mails me once per new event, such as a new Needs you item or a goal that stopped or passed its ETA. [CHK-3]
  - A reply such as "1 recommended" or "approve" is read by the operation session with `mailbox.py reply`, recorded as the owner's words with `--source owner` and sent to the worker. A step that deletes, spends money or touches security or private data refuses a bare number or approve and needs the owner's own typed words. [MCH-5]
  - I can answer any question under Needs you by replying to its mail or from my phone, with the same words a typed answer takes, and start, stop or reorder goals the same way. A reply counts as my words only when it comes from my own address or signed-in session. [CHK-9]
  - After each round, one email goes to the address I set: what ran, its results, and the new, still-open and fixed issues grouped by feature, each with its link and the request to give the agent. The same digest is posted on a pinned issue. [AUT-4]

### Non-functional

None

## Non-goals
- No secret, owner address or path under a home folder is ever written to a tracked file; the owner's own files are named, never created with a value.
- No change to what a repo's reviewed pages say: this page holds only the machine setup.
- Not a way to run a routine: the routines themselves are the Automation page's.

## Success metrics
- A fresh Mac or Windows home fails the machine check with each gap named, and the same home passes after `machine.py apply` and the owner steps.
- One command line lists, for each repo adopted on the machine, the same items every other machine of mine has. The SMTP toy fixture assembles its credential values at runtime and checks that the mailer output never reveals them.

## Revisions

### Retired

- MCH-10: moved to MCH-1
- MCH-11: moved to AUT-9
- MCH-2: moved to MCH-1
- MCH-3: moved to DEL-7
- MCH-6: moved to AUT-9
- MCH-7: moved to MCH-1
- MCH-8: moved to MCH-4
- MCH-9: moved to DEL-9

### MCH-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Any Mac or Windows machine sets up identically <br> Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh signed in as me, real symlinks and a supported platform, each marked present or missing with its fix. [MCH-7] <br> A second Mac or Windows machine reaches this one's setup from a git clone and one command: a dry run lists everything first, then apply installs the skill links, the hooks and the empty private files. Every item has a Windows form or is named as not yet possible. [MCH-1] <br> Given a fresh clone on a new machine, when `machine.py apply` runs (setup machine), then the operation session (its start routine and task, and the reply and govern hooks in the repo's machine-local settings), its scheduled tasks and the peer link (`~/.workflow-loop/peer.json`, holding this machine's and its peer's labels only; `--peer NAME`, default the other platform) exist, and `check` names any that is missing. [MCH-2] <br> The output ends with only the owner-only items left: the mail files, the private-names lists, account logins, the permission mode and registering tasks in the app; they are named, never created or copied. [MCH-2] <br> The machine check lists one line per gap between this machine and the expected setup, such as a skills checkout that is behind or a clone with no hooks. [MCH-10] <br> A pull request that adds a POSIX-only call without its guard (fcntl, os.getuid, os.killpg, signal.SIGHUP, os.kill(pid, 0)) fails its lane and checks, so main cannot break native Windows unseen. [DEL-12, GRD-18] <br> A long pull request body, issue text, comment or release notes always goes to gh in a file (`--body-file`, `--notes-file`), never on the command line, so a pull request with a body over 32,000 characters opens on native Windows. [DEL-12, GRD-18] | consolidation (TOP-DECISION 89) | o307: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | One command sets a machine up <br> A second Mac or Windows machine reaches this one's setup from a git clone and one command: a dry run lists everything first, then apply installs the skill links, the hooks and the empty private files. <br> Every item has a Windows form or is named as not yet possible. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-18 | A second machine reaches this one's setup from a git clone and one command <br> A second Mac or Windows machine reaches this one's setup from a git clone and one command, `machine.py`: a dry run lists everything first, `apply` installs the skill links, the commit and private-name hooks, the empty private-names file, the operation check-in (a pointer to the operation guide, whose layout shows each goal's time left and ETA) and one scheduled task per adopted repo named `<repo>-health-regression`, every 4 hours with staggered starts, running health and the full regression for public and private repos alike (it replaces local-schedule's launch agent, so no repo has two 4-hourly runs); `check` lists every gap with a one-line fix and writes nothing, and health's Adoption group runs it. A repo's own routine or custom item (`machine_setup` in its config) applies only when that repo is adopted on the machine. What setup cannot do (secrets files, logins, connectors, the permission mode, registering a task in the app) is a numbered owner checklist; anything not yet possible on Windows is named in it, never skipped silently. <br> No routine stops to ask: each task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing (a note you record, not the app's own setting). <br> Routine emails go through a local SMTP send script that reads its credentials only from a local secrets file, never prints them and sends only to the one configured owner address; nothing private is committed, and setup refuses a text with a secret, address or home path. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A new machine or account reaches a working operation session and its peer link from one command <br> Given a fresh clone on a new machine, when `machine.py apply` runs (setup machine), then the operation session (its start routine and task, and the reply and govern hooks in the repo's machine-local settings), its scheduled tasks and the peer link (`~/.workflow-loop/peer.json`, holding this machine's and its peer's labels only; `--peer NAME`, default the other platform) exist, and `check` names any that is missing. The output ends with only the owner-only items left: the mail files, the private-names lists, account logins, the permission mode and registering tasks in the app; they are named, never created or copied. | consolidation (TOP-DECISION 89): absorbed into MCH-1 | o309: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A new machine or account reaches a working operation session and its peer link from one command <br> Given a fresh clone on a new machine, when `machine.py apply` runs (setup machine), then the operation session (its start routine and task, and the reply and govern hooks in the repo's machine-local settings), its scheduled tasks and the peer link (`~/.workflow-loop/peer.json`, holding this machine's and its peer's labels only; `--peer NAME`, default the other platform) exist, and `check` names any that is missing. The output ends with only the owner-only items left: the mail files, the private-names lists, account logins, the permission mode and registering tasks in the app; they are named, never created or copied. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Backup and restore are commands <br> `machine.py backup DIR` copies the restorable state (machine record, peer link, flow file, routine files and scheduled task folders) to a folder no repo holds, and `machine.py restore DIR` puts it back on a new machine or account; neither ever copies or creates a secret or a private-names list, and both end by naming those owner-only items. A folder inside a repo, or one with no manifest, is refused. | consolidation (TOP-DECISION 89): absorbed into DEL-7 | o303: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Backup and restore are commands <br> `machine.py backup DIR` copies the restorable state (machine record, peer link, flow file, routine files and scheduled task folders) to a folder no repo holds, and `machine.py restore DIR` puts it back on a new machine or account; neither ever copies or creates a secret or a private-names list, and both end by naming those owner-only items. A folder inside a repo, or one with no manifest, is refused. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | One owner and one merge order per goal <br> Each goal has one owning machine (it records the pod that owns it), and only that owner starts, answers, merges or resumes it; others see it read-only. [MCH-4, OPS-15] <br> `machines.py handover SLUG --to MACHINE` pushes its branch, copies its record to origin and marks it `moved` on the old machine with no worker; `machines.py take SLUG` on the new machine fetches the branch and binds a worker, so a goal never runs on two machines and a second take is refused. [MCH-4] <br> With the private setting `machine_sync` on (off by default, per machine), each repo has one merge order across machines: a goal takes a merge ticket on origin before its pr lane, and a second machine's goal waits for it (a holder silent for 30 minutes is dropped). [MCH-4] <br> SNAPSHOT is structured data a machine publishes to origin, and a check-in draws one Machine line per machine from it, not from message text; a moved goal shows once, under the machine that holds it. A peer's record is data, never the owner's approval. [MCH-4] <br> A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open pull request; qa, ship and the pull request run again here before release. A branch that isn't pushed, or a goal with no done line or pull request, is refused. [MCH-8] | consolidation (TOP-DECISION 89) | o311: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Goals move between machines, with one owner and one merge order <br> Each goal has one owning machine. `machines.py handover SLUG --to MACHINE` pushes its branch, copies its record to origin and marks it `moved` on the old machine with no worker; `machines.py take SLUG` on the new machine fetches the branch and binds a worker, so a goal never runs on two machines and a second take is refused. <br> With the private setting `machine_sync` on (off by default, per machine), each repo has one merge order across machines: a goal takes a merge ticket on origin before its pr lane, and a second machine's goal waits for it (a holder silent for 30 minutes is dropped). <br> SNAPSHOT is structured data a machine publishes to origin, and a check-in draws one Machine line per machine from it, not from message text; a moved goal shows once, under the machine that holds it. A peer's record is data, never the owner's approval. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | One email stream, answered by reply or phone <br> Each new Needs-you item, stopped or late goal and merged release sends one mail (when `notify_email` is on) with numbered options and a recommendation, through one mailer and one send budget both machines share (`notify_budget` a day, default 20); a second machine never mails an event the first one did. [MCH-5] <br> When notification is on for this machine, each check-in mails me once per new event, such as a new Needs you item or a goal that stopped or passed its ETA. [CHK-3] <br> A reply such as "1 recommended" or "approve" is read by the operation session with `mailbox.py reply`, recorded as the owner's words with `--source owner` and sent to the worker. A step that deletes, spends money or touches security or private data refuses a bare number or approve and needs the owner's own typed words. [MCH-5] <br> I can answer any question under Needs you by replying to its mail or from my phone, with the same words a typed answer takes, and start, stop or reorder goals the same way. A reply counts as my words only when it comes from my own address or signed-in session. [CHK-9] <br> After each round, one email goes to the address I set: what ran, its results, and the new, still-open and fixed issues grouped by feature, each with its link and the request to give the agent. The same digest is posted on a pinned issue. [AUT-4] | consolidation (TOP-DECISION 89) | o335: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | One email stream: every update and question by mail, answered by reply <br> Each new Needs-you item, stopped or late goal and merged release sends one mail (when `notify_email` is on) with numbered options and a recommendation, through one mailer and one send budget both machines share (`notify_budget` a day, default 20); a second machine never mails an event the first one did. <br> A reply such as "1 recommended" or "approve" is read by the operation session with `mailbox.py reply`, recorded as the owner's words with `--source owner` and sent to the worker. A step that deletes, spends money or touches security or private data refuses a bare number or approve and needs the owner's own typed words. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Phone-first: starting a worker never needs the desktop app <br> When no app session can start, a worker starts as a background process through `agent_command` (the owner's `workers: app` rule still keeps a goal waiting for a bound session), and the start goes through one function other goals can extend. <br> `setup.py desk` lists every desk-only step (trusting folders, permission modes, tool pre-approvals, the private-names file, mail.env, the Codex login), prints each open step once, records each as done, and `desk check` ends with DESK OK only when nothing is left at the desk and a phone-only start works. | consolidation (TOP-DECISION 89): absorbed into AUT-9 | o301: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Phone-first: starting a worker never needs the desktop app <br> When no app session can start, a worker starts as a background process through `agent_command` (the owner's `workers: app` rule still keeps a goal waiting for a bound session), and the start goes through one function other goals can extend. <br> `setup.py desk` lists every desk-only step (trusting folders, permission modes, tool pre-approvals, the private-names file, mail.env, the Codex login), prints each open step once, records each as done, and `desk check` ends with DESK OK only when nothing is left at the desk and a phone-only start works. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Prerequisites first <br> Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh signed in as me, real symlinks and a supported platform, each marked present or missing with its fix. | consolidation (TOP-DECISION 89): absorbed into MCH-1 | o310: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Prerequisites first <br> Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh signed in as me, real symlinks and a supported platform, each marked present or missing with its fix. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A goal started on another machine can be adopted <br> A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open pull request; qa, ship and the pull request run again here before release. <br> A branch that isn't pushed, or a goal with no done line or pull request, is refused. | consolidation (TOP-DECISION 89): absorbed into MCH-4 | o312: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A goal started on another machine can be adopted <br> A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open pull request; qa, ship and the pull request run again here before release. <br> A branch that isn't pushed, or a goal with no done line or pull request, is refused. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A machine keeps its private data to itself <br> Each machine's private files, the private-name lists, mail settings, secrets and local overrides, stay outside the repo and are never copied to another machine, a log or a report. <br> A new machine gets empty private files and asks me to fill them. | consolidation (TOP-DECISION 89): absorbed into DEL-9 | o292: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A machine keeps its private data to itself <br> Each machine's private files, the private-name lists, mail settings, secrets and local overrides, stay outside the repo and are never copied to another machine, a log or a report. <br> A new machine gets empty private files and asks me to fill them. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A drifted machine says so <br> The machine check lists one line per gap between this machine and the expected setup, such as a skills checkout that is behind or a clone with no hooks. | consolidation (TOP-DECISION 89): absorbed into MCH-1 | o308: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A drifted machine says so <br> The machine check lists one line per gap between this machine and the expected setup, such as a skills checkout that is behind or a clone with no hooks. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | No routine stops to ask <br> Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing. | consolidation (TOP-DECISION 89): absorbed into AUT-9 | o300: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | No routine stops to ask <br> Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing. | migration r1; date from the run day | o47: "Yes, start it end." |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [machine-apply-installs](Tests#t-machine-apply-installs) | requirement | MCH-1 | Given a clone and a toy home, when machine plan runs, then it writes nothing, and when apply runs, then it links the skills and writes the private-names file, the mailer, the hooks and the tasks. | not run |
| [machine-check-gaps](Tests#t-machine-check-gaps) | requirement | MCH-1 | Given a fresh toy home, when machine check runs, then it names every gap with a fix and writes nothing, and a set-up home prints MACHINE OK. | not run |
| [machine-operation-guide](Tests#t-machine-operation-guide) | requirement | MCH-1 | Given the operation guide, when it is read, then it holds the check-in layout, full-auto rules, decision log and held lines, and the check-in routine file is only a pointer. | not run |
| [machine-new-machine-docs](Tests#t-machine-new-machine-docs) | requirement | MCH-1 | Given the Machines page and README, when read, then the New machine steps are there and linked from the README and SET-11 and SET-12 are Unreviewed. | PASS 2026-11-16 |
| [machine-rows-listed](Tests#t-machine-rows-listed) | requirement | MCH-1 | Given the machine rows, when the Setup Tests table is read, then every row is listed. | not run |
| [machine-windows](Tests#t-machine-windows) | requirement | MCH-1 | Given a Windows-shaped toy home, when machine plan, apply and check run for Windows, then it passes beside the Mac form and a fresh Windows home fails. | not run |
| [machine-task-layout](Tests#t-machine-task-layout) | requirement | MCH-1 | Given two repos, when apply runs, then each has a <repo>-health-regression task every 4 hours with staggered starts, and no repo keeps a second launch agent run. | PASS 2026-11-17 FLAKY |
| [machine-custom-items](Tests#t-machine-custom-items) | requirement | MCH-1 | Given a repo with allow, routine and secret custom items, when apply and check run, then they are applied, listed and checked, and a repo without items gets nothing. | not run |
| [machine-mailer](Tests#t-machine-mailer) | requirement | MCH-1 | Given the mailer, when it runs, then it reads only the local files, prints no secret, sends only to the one configured address and refuses any other. | not run |
| [machine-caps](Tests#t-machine-caps) | requirement | MCH-1 | Given the package, when scripts are measured, then machine.py is under the byte cap and stays out of the package: it lives in dev/, never under skills/ (other goals may add their own scripts there). | PASS 2026-11-16 |
| [windows-safe-posix-names](Tests#t-windows-safe-posix-names) | requirement | MCH-1 | Given a script under skills/*/scripts, when it names fcntl outside the lock shim, os.getuid, os.killpg, os.getpgrp, os.O_NOFOLLOW, signal.SIGHUP, os.kill(pid, 0) or os.WNOHANG with no guard, then the lane fails naming its file and line, and the real tree passes (issue 2871). | not run |
| [adopt-prerequisites](Tests#t-adopt-prerequisites) | requirement | MCH-1 | Given a machine where gh is not signed in, when setup runs, then it prints one checklist before writing with the exact fix for each gap. | not run |
| [machine-operation-peer](Tests#t-machine-operation-peer) | requirement | MCH-1 | Given a fresh clone and toy home, when machine apply runs, then the operation session, its tasks and the peer link exist, check names them when missing, and the output names only the owner-only items left. | PASS 2026-11-17 |
| [mon15-pod-owner](Tests#t-mon15-pod-owner) | requirement | MCH-4 | Given another pod's goal, when a pod acts on it, then it is refused naming the owner and shown owned by that pod. | PASS 2026-11-12 |
| [mon15-merge-lock](Tests#t-mon15-merge-lock) | requirement | MCH-4 | Given two pods merging into one main, when they run together, then the lock serializes them. | PASS 2026-11-12 |
| [adopt-record-qa](Tests#t-adopt-record-qa) | requirement | MCH-4 | Given a goal pushed from another machine with an open pull request, when goal.py adopt runs on its branch, then a run record exists at step qa with the pull request, idea, plan and review done on another machine and qa, ship and pr not recorded. | PASS 2026-11-16 FLAKY |
| [adopt-refuses-unpushed](Tests#t-adopt-refuses-unpushed) | requirement | MCH-4 | Given a branch that is not on origin, when goal.py adopt runs, then it is refused in one line and no run record is written. | PASS 2026-11-18 FLAKY |
| [adopt-replaces-stale](Tests#t-adopt-replaces-stale) | requirement | MCH-4 | Given a run record here that is running with no pid and no recorded step, when goal.py adopt runs, then it replaces the record and logs it; given a record with a pid, then adopt refuses and leaves it unchanged. | PASS 2026-11-16 FLAKY |
| [resume-ask-prompt](Tests#t-resume-ask-prompt) | requirement | MCH-4 | Given a goal set to ask and auto_merge on, when it is resumed, then its prompt asks the owner and never tells the worker to run merge.py. | not run |
| [pr-queue-order](Tests#t-pr-queue-order) | requirement | MCH-4 | Given three goals asking for their pr turn in one repo, when they ask oldest first, then the first runs its lane and the others are told who is ahead; a goal that left the pr step, a stopped holder and a ticket older than 30 minutes each give their place to the next. | not run |
| [pr-parallel-disjoint](Tests#t-pr-parallel-disjoint) | requirement | MCH-4 | Given goals at pr, when their touches share no path, then their lanes run at once, and a goal waits only for an earlier goal whose touches overlap. | not run |
| [queue-merged-free-4343](Tests#t-queue-merged-free-4343) | requirement | MCH-4 | Given a goal whose pull request merged, when the pr queue is read, then its ticket and beat are removed and it holds nobody. | not run |
| [merge-leaves-queue-4343](Tests#t-merge-leaves-queue-4343) | requirement | MCH-4 | Given a merged goal, when merge.py finishes the merge, then its pr-queue ticket and beat are gone. | not run |
| [machines-handover](Tests#t-machines-handover) | requirement | MCH-4 | Given two machines sharing origin, when goals hand over, contend for the merge turn and publish snapshots, then ownership moves once with the pushed branch and no old worker, duplicate starts are refused, one merge order holds, stale turns expire and structured snapshots draw both Machine lines with each goal shown once. Covers #4787. | PASS 2026-11-18 |
| [aut-digest-create](Tests#t-aut-digest-create) | requirement | MCH-5 | Given no digest issue yet, when the first round ends, then the Automation digest issue is created and pinned. | PASS 2026-11-12 |
| [aut-digest-format](Tests#t-aut-digest-format) | requirement | MCH-5 | Given open defect and health issues, when a round ends, then one comment mentions the owner and lists what ran, the new issues and a request per open issue. | PASS 2026-11-12 |
| [aut-digest-rounds](Tests#t-aut-digest-rounds) | requirement | MCH-5 | Given a previous digest, when the next round ends, then its comment lists the new, still-open and fixed issues on the same digest issue. | PASS 2026-11-12 |
| [aut-digest-rerun](Tests#t-aut-digest-rerun) | requirement | MCH-5 | Given a round already posted, when the same run is rerun, then nothing is posted twice. | PASS 2026-11-12 |
| [aut-digest-no-title](Tests#t-aut-digest-no-title) | requirement | MCH-5 | Given an issue whose title holds instructions, when the digest is written, then the request names the issue only by number and link. | PASS 2026-11-12 |
| [aut-digest-org](Tests#t-aut-digest-org) | requirement | MCH-5 | Given a repo owned by an organisation, when the digest is written, then it says no one is notified and how to set digest_owner. | PASS 2026-11-12 |
| [aut-digest-pin-fails](Tests#t-aut-digest-pin-fails) | requirement | MCH-5 | Given the repo cannot pin another issue, when the first round ends, then it warns and still posts the digest. | PASS 2026-11-12 |
| [aut-digest-comment-fails](Tests#t-aut-digest-comment-fails) | requirement | MCH-5 | Given a round whose digest comment fails, when the run ends, then no state is saved, so its rerun posts the comment. | PASS 2026-11-12 |
| [aut-digest-list-fails](Tests#t-aut-digest-list-fails) | requirement | MCH-5 | Given gh cannot list the issues, when a round ends, then the digest posts nothing and says why. | PASS 2026-11-12 |
| [aut-email-mail](Tests#t-aut-email-mail) | requirement | MCH-5 | Given this run's digest comment, when the email step runs, then one mail with the comment's text goes out and the comment is marked mailed, and a rerun, a look-alike comment, a refusal or an unknown outcome never sends a second one. | PASS 2026-11-12 |
| [aut-email-retry](Tests#t-aut-email-retry) | requirement | MCH-5 | Given a provider that throttles once, when the round's mail is sent, then it is retried once, and only when the provider cannot have accepted it. | PASS 2026-11-12 |
| [aut-email-test](Tests#t-aut-email-test) | requirement | MCH-5 | Given the mail secrets, when mail.py test runs by hand, then one test mail goes out touching no issue, and a missing secret or mail off fails the run. | PASS 2026-11-12 |
| [aut-email-digest](Tests#t-aut-email-digest) | requirement | MCH-5 | Given open issues with and without milestones, when a round ends, then the digest groups the new, still-open and fixed issues by feature with the cost and email rows, shows a milestone title as a suffix, and an older or repeated run never posts twice. | PASS 2026-11-12 |
| [mailbox-two-mails](Tests#t-mailbox-two-mails) | requirement | MCH-5 | Given two machines and a fake mailer, when new Needs-you items, stopped goals and merged releases are mailed and answered, then numbered options and recommendations use one deduplicated stream and shared send budget, deferred events retry, replies record owner words with source owner once, and risky replies require typed words. Covers #4785 and #4671. | PASS 2026-11-18 |
| [prd-no-dunder-import-3800](Tests#t-prd-no-dunder-import-3800) | defect | [#3800](https://github.com/jcl2018/agent-workflow-template/issues/3800) closed (2026-11-15) | Given the scripts under skills/*/scripts (prd.py and render.py relock and render through importlib), when the package Safety rule scans them, then none holds __import__ (issue 3800). | PASS 2026-11-16 |
| [pr-order-one-queue](Tests#t-pr-order-one-queue) | defect | [#3922](https://github.com/jcl2018/agent-workflow-template/issues/3922) closed (2026-11-14) | Given three goals retrying their pr turn in a loop, when each asks, then every goal sees one order by first-join time, a retry touches only the heartbeat, and no goal without a readable ticket counts as first. | not run |
| [machines-handover-4787](Tests#t-machines-handover-4787) | defect | [#4787](https://github.com/jcl2018/agent-workflow-template/issues/4787) closed (2026-11-18) | Given the missing machine ownership, handover, merge order and structured snapshots, when its full fixture runs, then every promised behavior is required and fails without the implementation. | PASS 2026-11-18 |
| [mailbox-two-mails-4785](Tests#t-mailbox-two-mails-4785) | defect | [#4785](https://github.com/jcl2018/agent-workflow-template/issues/4785) closed (2026-11-18) | Given the missing one shared mail stream, send budget, numbered recommendations and owner replies, when its full fixture runs, then every promised behavior is required and fails without the implementation. | PASS 2026-11-18 |
| [mailbox-two-mails-4671](Tests#t-mailbox-two-mails-4671) | defect | [#4671](https://github.com/jcl2018/agent-workflow-template/issues/4671) closed (2026-11-18) | Given the missing one shared mail stream, send budget, numbered recommendations and owner replies, when its full fixture runs, then every promised behavior is required and fails without the implementation. | PASS 2026-11-18 |
