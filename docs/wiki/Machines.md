<!-- workflow-docs -->
# Machines

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/23

How to use: [How-to-use-Machines](How-to-use-Machines)

Review: **Unreviewed** <!-- kept prd-revisions@71f2d8b1 -->


## Problem
- A second machine, a Mac or a Windows PC, should reach the same working setup as the one I run on from a git clone and one command, because much of what the operation relies on lives only on one machine: the skill install, the hooks, the private-names file, the check-in prompt, the routines and the mailer.
- I said it for Windows too: "that command should capture windows" (owner, 2026-11-11), so every item has a Windows form, or is named in the checklist as not yet possible, never skipped silently.
- A machine that has drifted, a skills checkout two days behind or a clone with no hooks, should say so in one line per gap, without anyone having to notice.

## Requirements

### Functional
- MCH-1: **Unreviewed** One command sets a machine up
  - A second Mac or Windows machine reaches this one's setup from a git clone and one command: a dry run lists everything first, then apply installs the skill links, the hooks and the empty private files.
  - Every item has a Windows form or is named as not yet possible.
- MCH-2: **Unreviewed** A new machine or account reaches a working operation session and its peer link from one command
  - Given a fresh clone on a new machine, when `machine.py apply` runs (setup machine), then the operation session (its start routine and task, and the reply and govern hooks in the repo's machine-local settings), its scheduled tasks and the peer link (`~/.workflow-loop/peer.json`, holding this machine's and its peer's labels only; `--peer NAME`, default the other platform) exist, and `check` names any that is missing. The output ends with only the owner-only items left: the mail files, the private-names lists, account logins, the permission mode and registering tasks in the app; they are named, never created or copied.
- MCH-3: **Unreviewed** Backup and restore are commands
  - `machine.py backup DIR` copies the restorable state (machine record, peer link, flow file, routine files and scheduled task folders) to a folder no repo holds, and `machine.py restore DIR` puts it back on a new machine or account; neither ever copies or creates a secret or a private-names list, and both end by naming those owner-only items. A folder inside a repo, or one with no manifest, is refused.
- MCH-4: **Unreviewed** Prerequisites first
  - Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh signed in as me, real symlinks and a supported platform, each marked present or missing with its fix.
- MCH-5: **Unreviewed** A goal started on another machine can be adopted
  - A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open pull request; qa, ship and the pull request run again here before release.
  - A branch that isn't pushed, or a goal with no done line or pull request, is refused.
- MCH-6: **Unreviewed** A machine keeps its private data to itself
  - Each machine's private files, the private-name lists, mail settings, secrets and local overrides, stay outside the repo and are never copied to another machine, a log or a report.
  - A new machine gets empty private files and asks me to fill them.
- MCH-7: **Unreviewed** A drifted machine says so
  - The machine check lists one line per gap between this machine and the expected setup, such as a skills checkout that is behind or a clone with no hooks.
- MCH-8: **Unreviewed** No routine stops to ask
  - Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing.

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

### MCH-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | One command sets a machine up <br> A second Mac or Windows machine reaches this one's setup from a git clone and one command: a dry run lists everything first, then apply installs the skill links, the hooks and the empty private files. <br> Every item has a Windows form or is named as not yet possible. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-18 | A second machine reaches this one's setup from a git clone and one command <br> A second Mac or Windows machine reaches this one's setup from a git clone and one command, `machine.py`: a dry run lists everything first, `apply` installs the skill links, the commit and private-name hooks, the empty private-names file, the operation check-in (a pointer to the operation guide, whose layout shows each goal's time left and ETA) and one scheduled task per adopted repo named `<repo>-health-regression`, every 4 hours with staggered starts, running health and the full regression for public and private repos alike (it replaces local-schedule's launch agent, so no repo has two 4-hourly runs); `check` lists every gap with a one-line fix and writes nothing, and health's Adoption group runs it. A repo's own routine or custom item (`machine_setup` in its config) applies only when that repo is adopted on the machine. What setup cannot do (secrets files, logins, connectors, the permission mode, registering a task in the app) is a numbered owner checklist; anything not yet possible on Windows is named in it, never skipped silently. <br> No routine stops to ask: each task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing (a note you record, not the app's own setting). <br> Routine emails go through a local SMTP send script that reads its credentials only from a local secrets file, never prints them and sends only to the one configured owner address; nothing private is committed, and setup refuses a text with a secret, address or home path. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A new machine or account reaches a working operation session and its peer link from one command <br> Given a fresh clone on a new machine, when `machine.py apply` runs (setup machine), then the operation session (its start routine and task, and the reply and govern hooks in the repo's machine-local settings), its scheduled tasks and the peer link (`~/.workflow-loop/peer.json`, holding this machine's and its peer's labels only; `--peer NAME`, default the other platform) exist, and `check` names any that is missing. The output ends with only the owner-only items left: the mail files, the private-names lists, account logins, the permission mode and registering tasks in the app; they are named, never created or copied. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Backup and restore are commands <br> `machine.py backup DIR` copies the restorable state (machine record, peer link, flow file, routine files and scheduled task folders) to a folder no repo holds, and `machine.py restore DIR` puts it back on a new machine or account; neither ever copies or creates a secret or a private-names list, and both end by naming those owner-only items. A folder inside a repo, or one with no manifest, is refused. | migration r1; date from the run day | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### MCH-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Prerequisites first <br> Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh signed in as me, real symlinks and a supported platform, each marked present or missing with its fix. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A goal started on another machine can be adopted <br> A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open pull request; qa, ship and the pull request run again here before release. <br> A branch that isn't pushed, or a goal with no done line or pull request, is refused. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A machine keeps its private data to itself <br> Each machine's private files, the private-name lists, mail settings, secrets and local overrides, stay outside the repo and are never copied to another machine, a log or a report. <br> A new machine gets empty private files and asks me to fill them. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A drifted machine says so <br> The machine check lists one line per gap between this machine and the expected setup, such as a skills checkout that is behind or a clone with no hooks. | migration r1; date from the run day | o47: "Yes, start it end." |

### MCH-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | No routine stops to ask <br> Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing. | migration r1; date from the run day | o47: "Yes, start it end." |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [machine-apply-installs](Tests#t-machine-apply-installs) | requirement | MCH-1 | Given a clone and a toy home, when machine plan runs, then it writes nothing, and when apply runs, then it links the skills and writes the private-names file, the mailer, the hooks and the tasks. | not run |
| [machine-operation-guide](Tests#t-machine-operation-guide) | requirement | MCH-1 | Given the operation guide, when it is read, then it holds the check-in layout, full-auto rules, decision log and held lines, and the check-in routine file is only a pointer. | not run |
| [machine-new-machine-docs](Tests#t-machine-new-machine-docs) | requirement | MCH-1 | Given the Machines page and README, when read, then the New machine steps are there and linked from the README and SET-11 and SET-12 are Unreviewed. | PASS 2026-11-16 |
| [machine-rows-listed](Tests#t-machine-rows-listed) | requirement | MCH-1 | Given the machine rows, when the Setup Tests table is read, then every row is listed. | not run |
| [machine-windows](Tests#t-machine-windows) | requirement | MCH-1 | Given a Windows-shaped toy home, when machine plan, apply and check run for Windows, then it passes beside the Mac form and a fresh Windows home fails. | not run |
| [machine-task-layout](Tests#t-machine-task-layout) | requirement | MCH-1 | Given two repos, when apply runs, then each has a <repo>-health-regression task every 4 hours with staggered starts, and no repo keeps a second launch agent run. | PASS 2026-11-17 FLAKY |
| [machine-custom-items](Tests#t-machine-custom-items) | requirement | MCH-1 | Given a repo with allow, routine and secret custom items, when apply and check run, then they are applied, listed and checked, and a repo without items gets nothing. | not run |
| [machine-mailer](Tests#t-machine-mailer) | requirement | MCH-1 | Given the mailer, when it runs, then it reads only the local files, prints no secret, sends only to the one configured address and refuses any other. | not run |
| [machine-caps](Tests#t-machine-caps) | requirement | MCH-1 | Given the package, when scripts are measured, then machine.py is under the byte cap and stays out of the package: it lives in dev/, never under skills/ (other goals may add their own scripts there). | PASS 2026-11-16 |
| [machine-operation-peer](Tests#t-machine-operation-peer) | requirement | MCH-2 | Given a fresh clone and toy home, when machine apply runs, then the operation session, its tasks and the peer link exist, check names them when missing, and the output names only the owner-only items left. | PASS 2026-11-17 |
| [machine-backup-restore](Tests#t-machine-backup-restore) | requirement | MCH-3 | Given a set-up home, when machine backup and restore run, then restorable state moves to a new home, no secret or private-names list is copied, a folder inside a repo or without a manifest is refused. | PASS 2026-11-17 |
| [adopt-prerequisites](Tests#t-adopt-prerequisites) | requirement | MCH-4 | Given a machine where gh is not signed in, when setup runs, then it prints one checklist before writing with the exact fix for each gap. | not run |
| - | requirement | MCH-4 | no passing test | not enforced |
| [adopt-record-qa](Tests#t-adopt-record-qa) | requirement | MCH-5 | Given a goal pushed from another machine with an open pull request, when goal.py adopt runs on its branch, then a run record exists at step qa with the pull request, idea, plan and review done on another machine and qa, ship and pr not recorded. | PASS 2026-11-16 FLAKY |
| [adopt-refuses-unpushed](Tests#t-adopt-refuses-unpushed) | requirement | MCH-5 | Given a branch that is not on origin, when goal.py adopt runs, then it is refused in one line and no run record is written. | not run |
| [adopt-replaces-stale](Tests#t-adopt-replaces-stale) | requirement | MCH-5 | Given a run record here that is running with no pid and no recorded step, when goal.py adopt runs, then it replaces the record and logs it; given a record with a pid, then adopt refuses and leaves it unchanged. | PASS 2026-11-16 FLAKY |
| [machine-no-private](Tests#t-machine-no-private) | requirement | MCH-6 | Given a repo routine holding an address or home path, when apply runs, then it refuses naming the line and kind, writes nothing and never echoes the value. | PASS 2026-11-17 FLAKY |
| [machine-check-gaps](Tests#t-machine-check-gaps) | requirement | MCH-7 | Given a fresh toy home, when machine check runs, then it names every gap with a fix and writes nothing, and a set-up home prints MACHINE OK. | not run |
| - | requirement | MCH-7 | no passing test | not enforced |
| [machine-no-prompt-mode](Tests#t-machine-no-prompt-mode) | requirement | MCH-8 | Given a task with no recorded mode or a prompting one, when machine check runs, then it fails, and a no-prompt mode passes. | not run |
| - | requirement | MCH-8 | no passing test | not enforced |
