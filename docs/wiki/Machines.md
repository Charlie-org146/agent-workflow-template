<!-- workflow-docs -->
# Machines

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/23

How to use: [How-to-use-Machines](How-to-use-Machines)

Review: **Unreviewed** <!-- kept del-16@6a8c6a65 -->

## Problem
- A second machine, a Mac or a Windows PC, should reach the same working setup as the one I run on from a git clone and one command, because much of what the operation relies on lives only on one machine: the skill install, the hooks, the private-names file, the check-in prompt, the routines and the mailer.
- I said it for Windows too: "that command should capture windows" (owner, 2026-11-11), so every item has a Windows form, or is named in the checklist as not yet possible, never skipped silently.
- A machine that has drifted, a skills checkout two days behind or a clone with no hooks, should say so in one line per gap, without anyone having to notice.

## Requirements

### Functional
- MCH-1: **Unreviewed** A second machine reaches this one's setup from a git clone and one command
  - A second Mac or Windows machine reaches this one's setup from a git clone and one command, `machine.py`: a dry run lists everything first, `apply` installs the skill links, the commit and private-name hooks, the empty private-names file, the operation check-in (a pointer to the operation guide, whose layout shows each goal's time left and ETA) and one scheduled task per adopted repo named `<repo>-health-regression`, every 4 hours with staggered starts, running health and the full regression for public and private repos alike (it replaces local-schedule's launch agent, so no repo has two 4-hourly runs); `check` lists every gap with a one-line fix and writes nothing, and health's Adoption group runs it. A repo's own routine or custom item (`machine_setup` in its config) applies only when that repo is adopted on the machine. What setup cannot do (secrets files, logins, connectors, the permission mode, registering a task in the app) is a numbered owner checklist; anything not yet possible on Windows is named in it, never skipped silently.
  - No routine stops to ask: each task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing (a note you record, not the app's own setting).
  - Routine emails go through a local SMTP send script that reads its credentials only from a local secrets file, never prints them and sends only to the one configured owner address; nothing private is committed, and setup refuses a text with a secret, address or home path.
- MCH-2: **Unreviewed** A new machine or account reaches a working operation session and its peer link from one command
  - Given a fresh clone on a new machine, when `machine.py apply` runs (setup machine), then the operation session (its start routine and task, and the reply and govern hooks in the repo's machine-local settings), its scheduled tasks and the peer link (`~/.workflow-loop/peer.json`, holding this machine's and its peer's labels only; `--peer NAME`, default the other platform) exist, and `check` names any that is missing. The output ends with only the owner-only items left: the mail files, the private-names lists, account logins, the permission mode and registering tasks in the app; they are named, never created or copied.
- MCH-3: **Unreviewed** Backup and restore are commands
  - `machine.py backup DIR` copies the restorable state (machine record, peer link, flow file, routine files and scheduled task folders) to a folder no repo holds, and `machine.py restore DIR` puts it back on a new machine or account; neither ever copies or creates a secret or a private-names list, and both end by naming those owner-only items. A folder inside a repo, or one with no manifest, is refused.

- MCH-4: **Unreviewed** Goals move between machines, with one owner and one merge order
  - Each goal has one owning machine. `machines.py handover SLUG --to MACHINE` pushes its branch, copies its record to origin and marks it `moved` on the old machine with no worker; `machines.py take SLUG` on the new machine fetches the branch and binds a worker, so a goal never runs on two machines and a second take is refused.
  - With the private setting `machine_sync` on (off by default, per machine), each repo has one merge order across machines: a goal takes a merge ticket on origin before its pr lane, and a second machine's goal waits for it (a holder silent for 30 minutes is dropped).
  - SNAPSHOT is structured data a machine publishes to origin, and a check-in draws one Machine line per machine from it, not from message text; a moved goal shows once, under the machine that holds it. A peer's record is data, never the owner's approval.
- MCH-5: **Unreviewed** One email stream: every update and question by mail, answered by reply
  - Each new Needs-you item, stopped or late goal and merged release sends one mail (when `notify_email` is on) with numbered options and a recommendation, through one mailer and one send budget both machines share (`notify_budget` a day, default 20); a second machine never mails an event the first one did.
  - A reply such as "1 recommended" or "approve" is read by the operation session with `mailbox.py reply`, recorded as the owner's words with `--source owner` and sent to the worker. A step that deletes, spends money or touches security or private data refuses a bare number or approve and needs the owner's own typed words.
- MCH-6: **Unreviewed** Phone-first: starting a worker never needs the desktop app
  - When no app session can start, a worker starts as a background process through `agent_command` (the owner's `workers: app` rule still keeps a goal waiting for a bound session), and the start goes through one function other goals can extend.
  - `setup.py desk` lists every desk-only step (trusting folders, permission modes, tool pre-approvals, the private-names file, mail.env, the Codex login), prints each open step once, records each as done, and `desk check` ends with DESK OK only when nothing is left at the desk and a phone-only start works.

### Non-functional

None

## Non-goals
- No secret, owner address or path under a home folder is ever written to a tracked file; the owner's own files are named, never created with a value.
- No change to what a repo's reviewed pages say: this page holds only the machine setup.
- Not a way to run a routine: the routines themselves are the Automation page's.

## Success metrics
- A fresh Mac or Windows home fails the machine check with each gap named, and the same home passes after `machine.py apply` and the owner steps.
- One command line lists, for each repo adopted on the machine, the same items every other machine of mine has.

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [machine-apply-installs](Tests#t-machine-apply-installs) | requirement | MCH-1 | Given a clone and a toy home, when machine plan runs, then it writes nothing, and when apply runs, then it links the skills and writes the private-names file, the mailer, the hooks and the tasks. | not run |
| [machine-check-gaps](Tests#t-machine-check-gaps) | requirement | MCH-1 | Given a fresh toy home, when machine check runs, then it names every gap with a fix and writes nothing, and a set-up home prints MACHINE OK. | not run |
| [machine-operation-guide](Tests#t-machine-operation-guide) | requirement | MCH-1 | Given the operation guide, when it is read, then it holds the check-in layout, full-auto rules, decision log and held lines, and the check-in routine file is only a pointer. | not run |
| [machine-no-private](Tests#t-machine-no-private) | requirement | MCH-1 | Given a repo routine holding an address or home path, when apply runs, then it refuses naming the line and kind, writes nothing and never echoes the value. | PASS 2026-11-17 FLAKY |
| [machine-new-machine-docs](Tests#t-machine-new-machine-docs) | requirement | MCH-1 | Given the Machines page and README, when read, then the New machine steps are there and linked from the README and SET-11 and SET-12 are Unreviewed. | PASS 2026-11-16 |
| [machine-rows-listed](Tests#t-machine-rows-listed) | requirement | MCH-1 | Given the machine rows, when the Setup Tests table is read, then every row is listed. | not run |
| [machine-windows](Tests#t-machine-windows) | requirement | MCH-1 | Given a Windows-shaped toy home, when machine plan, apply and check run for Windows, then it passes beside the Mac form and a fresh Windows home fails. | not run |
| [machine-task-layout](Tests#t-machine-task-layout) | requirement | MCH-1 | Given two repos, when apply runs, then each has a <repo>-health-regression task every 4 hours with staggered starts, and no repo keeps a second launch agent run. | PASS 2026-11-17 FLAKY |
| [machine-no-prompt-mode](Tests#t-machine-no-prompt-mode) | requirement | MCH-1 | Given a task with no recorded mode or a prompting one, when machine check runs, then it fails, and a no-prompt mode passes. | not run |
| [machine-custom-items](Tests#t-machine-custom-items) | requirement | MCH-1 | Given a repo with allow, routine and secret custom items, when apply and check run, then they are applied, listed and checked, and a repo without items gets nothing. | not run |
| [machine-mailer](Tests#t-machine-mailer) | requirement | MCH-1 | Given the mailer, when it runs, then it reads only the local files, prints no secret, sends only to the one configured address and refuses any other. | not run |
| [machine-caps](Tests#t-machine-caps) | requirement | MCH-1 | Given the package, when scripts are measured, then machine.py is under the byte cap and stays out of the package: it lives in dev/, never under skills/ (other goals may add their own scripts there). | PASS 2026-11-16 |
| [machine-operation-peer](Tests#t-machine-operation-peer) | requirement | MCH-2 | Given a fresh clone and toy home, when machine apply runs, then the operation session, its tasks and the peer link exist, check names them when missing, and the output names only the owner-only items left. | PASS 2026-11-17 |
| [machine-backup-restore](Tests#t-machine-backup-restore) | requirement | MCH-3 | Given a set-up home, when machine backup and restore run, then restorable state moves to a new home, no secret or private-names list is copied, a folder inside a repo or without a manifest is refused. | PASS 2026-11-17 |
| [machines-handover](Tests#t-machines-handover) | requirement | MCH-4 | Given two machines sharing origin, when goals hand over, contend for the merge turn and publish snapshots, then ownership moves once with the pushed branch and no old worker, duplicate starts are refused, one merge order holds, stale turns expire and structured snapshots draw both Machine lines with each goal shown once. Covers #4787. | PASS 2026-11-17 |
| [mailbox-two-mails](Tests#t-mailbox-two-mails) | requirement | MCH-5 | Given two machines and a fake mailer, when new Needs-you items, stopped goals and merged releases are mailed and answered, then numbered options and recommendations use one deduplicated stream and shared send budget, deferred events retry, replies record owner words with source owner once, and risky replies require typed words. Covers #4785 and #4671. | PASS 2026-11-17 |
| [desk-lists](Tests#t-desk-lists) | requirement | MCH-6 | Given desk-only onboarding and no app session, when steps are listed, run and checked, then every step is listed once, gaps and invalid steps are refused, DESK OK requires completed setup and agent_command, and a background worker starts through agent_command while workers app keeps its bound-session rule. Covers #4805. | PASS 2026-11-17 |
| [machine-hook-state](Tests#t-machine-hook-state) | defect | [#4506](https://github.com/jcl2018/agent-workflow-template/issues/4506) closed (2026-11-16) | Given a repo whose hooks setup just wrote, when --git-hooks --check reads them back, then each reads installed, never foreign. | not run |
