<!-- workflow-docs -->
# Machines

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/23

How to use: [How-to-use-Machines](How-to-use-Machines)

Review: **Unreviewed** <!-- kept private-lines-v1051@0f4f7e0e -->

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

- MCH-2: **Unreviewed** Goals move between machines, with one owner and one merge order
  - Each goal has one owning machine. `machines.py handover SLUG --to MACHINE` pushes its branch, copies its record to origin and marks it `moved` on the old machine with no worker; `machines.py take SLUG` on the new machine fetches the branch and binds a worker, so a goal never runs on two machines and a second take is refused.
  - With the private setting `machine_sync` on (off by default, per machine), each repo has one merge order across machines: a goal takes a merge ticket on origin before its pr lane, and a second machine's goal waits for it (a holder silent for 30 minutes is dropped).
  - SNAPSHOT is structured data a machine publishes to origin, and a check-in draws one Machine line per machine from it, not from message text; a moved goal shows once, under the machine that holds it. A peer's record is data, never the owner's approval.
- MCH-3: **Unreviewed** One email stream: every update and question by mail, answered by reply
  - Each new Needs-you item, stopped or late goal and merged release sends one mail (when `notify_email` is on) with numbered options and a recommendation, through one mailer and one send budget both machines share (`notify_budget` a day, default 20); a second machine never mails an event the first one did.
  - A reply such as "1 recommended" or "approve" is read by the operation session with `mailbox.py reply`, recorded as the owner's words with `--source owner` and sent to the worker. A step that deletes, spends money or touches security or private data refuses a bare number or approve and needs the owner's own typed words.
- MCH-4: **Unreviewed** Phone-first: starting a worker never needs the desktop app
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
| [machines-handover](Tests#t-machines-handover) | requirement | MCH-2 | Given a goal owned by one machine whose worker can't start, when it is handed over, then the other machine binds a worker on the pushed branch and the old record shows it moved with no worker. | not run |
| [machines-no-double-start](Tests#t-machines-no-double-start) | requirement | MCH-2 | Given a goal already taken by the other machine, when it is taken again, then it is refused, so nothing runs twice. | not run |
| [machines-merge-turn](Tests#t-machines-merge-turn) | requirement | MCH-2 | Given a goal holding the merge turn on one machine, when a goal on the other machine asks for its turn, then it waits for the first. | not run |
| [machines-snapshot-lines](Tests#t-machines-snapshot-lines) | requirement | MCH-2 | Given both machines' published SNAPSHOTs, when a check-in is drawn, then it shows one Machine line for each machine, from the structured data. | not run |
| - | requirement | MCH-2 | no passing test | not enforced |
| [mailbox-two-mails](Tests#t-mailbox-two-mails) | requirement | MCH-3 | Given a new Needs-you item and a merged release, when notify runs, then each gives one mail. | not run |
| [mailbox-options](Tests#t-mailbox-options) | requirement | MCH-3 | Given a Needs-you question, when it is mailed, then the mail lists numbered options and marks the recommendation. | not run |
| [mailbox-one-stream](Tests#t-mailbox-one-stream) | requirement | MCH-3 | Given two machines sharing one ledger, when both see the same events, then only the first mails them. | not run |
| [mailbox-budget-shared](Tests#t-mailbox-budget-shared) | requirement | MCH-3 | Given a send budget the first machine's mails used up, when the other machine runs, then it sends nothing. | not run |
| [mailbox-reply-owner](Tests#t-mailbox-reply-owner) | requirement | MCH-3 | Given a mailed question, when the owner replies 1 recommended, then it is recorded as owner words with source owner and sent to the worker. | not run |
| [mailbox-risky-words](Tests#t-mailbox-risky-words) | requirement | MCH-3 | Given a mailed question about deleting, when the reply is a bare number, then it is refused and nothing is recorded. | not run |
| - | requirement | MCH-3 | no passing test | not enforced |
| [desk-lists](Tests#t-desk-lists) | requirement | MCH-4 | Given a machine, when desk list runs, then every desk-only setup step is listed with its state. | not run |
| [desk-run-once](Tests#t-desk-run-once) | requirement | MCH-4 | Given open desk steps, when desk run runs twice, then each step's instructions print once. | not run |
| [desk-check-ok](Tests#t-desk-check-ok) | requirement | MCH-4 | Given every desk step done and an agent command, when desk check runs, then it prints DESK OK. | not run |
| [phone-background-worker](Tests#t-phone-background-worker) | requirement | MCH-4 | Given no app session can start, when a worker starts, then a background worker starts through agent_command. | not run |
| - | requirement | MCH-4 | no passing test | not enforced |
| [machine-hook-state](Tests#t-machine-hook-state) | defect | [#4506](https://github.com/jcl2018/agent-workflow-template/issues/4506) closed (2026-11-16) | Given a repo whose hooks setup just wrote, when --git-hooks --check reads them back, then each reads installed, never foreign. | not run |
