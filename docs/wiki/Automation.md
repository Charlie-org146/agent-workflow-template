<!-- workflow-docs -->
# Automation

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/10

Review: **Unreviewed**

How to use: [How-to-use-Automation](How-to-use-Automation)

## Problem
- Things break between my sessions, and I only find out when I next open one; the important checks should run on their own.
- Every few hours I want the full regression suite and the health check to run, and every problem they find to become an issue tagged with its group, and with its feature when feature_labels is on.
- I want one email to my address after each round that tells me what ran, what broke, what got fixed and what to ask the agent, without opening GitHub.

## Requirements

### Functional
- AUT-1: **Unreviewed** Routines run on schedule, by runbook
  - Health and regression run on schedule wherever they can run fully. [AUT-1]
  - They report where they ran and what they skipped, catch up missed runs, and follow runbooks. [AUT-1]

  - Feature markers v1
  - Reference: GitHub Actions `schedule`: adopted; Google SRE on-call playbooks: adapted
  - Line 1: metric missing; test 12 linked rows, see Tests
  - Line 2: metric missing; test 12 linked rows, see Tests


### Non-functional
- AUT-5: **Unreviewed** Routines and publishing stay under my control
  - Each routine turns off or reschedules with one setting and writes nothing without secrets. [AUT-5]
  - Publishing never deletes or overwrites pages it didn't write, and it can be undone. [AUT-5]

  - Feature markers v1
  - Reference: GitHub environments with required reviewers: own
  - Line 1: metric missing; test 4 linked rows, see Tests
  - Line 2: metric missing; test 4 linked rows, see Tests

## Non-goals
- The scheduled routines never push, merge or release; they only write issues, labels, comments, run reports (an Actions run summary or a local report on my Mac) and the digest email.
- No chat or webhook notifications; email and GitHub only.

## Success metrics
- After each scheduled round, one digest email arrives and every failing test or finding has exactly one open issue tagged with its feature.
- With a routine set to off, its runs write no issue, label, comment or email.

## Revisions

### Retired

- AUT-10: moved to DEL-3
- AUT-2: moved to AUT-1
- AUT-3: moved to AUT-1
- AUT-4: moved to CHK-1
- AUT-6: moved to DEL-9
- AUT-7: moved to DEL-17
- AUT-8: moved to AUT-1
- AUT-9: moved to GRD-4

### AUT-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Routines run on schedule, by runbook <br> Health and regression run on schedule wherever they can run fully. [AUT-1] <br> They report where they ran and what they skipped, catch up missed runs, and follow runbooks. [AUT-1] | readme-six: the owner-approved final README (o514) | o573: "yes build it" |
| r3 | 2026-11-19 | Routines run on schedule, by runbook <br> Health runs on my always-on machine for every repo; regression runs in GitHub Actions for a public repo and on that machine for a private one. Each report says where it ran, and a routine missed while the machine was off runs once at the next tick and says it was missed. [AUT-1] <br> The full regression suite runs on the schedule set in the repo's settings, every 4 hours by default, and on every release tag; I can also start it by hand. The report names every test it skipped and why. [AUT-2] <br> Health runs on my always-on machine on the schedule, after the latest finished regression run, with all its rule groups and the repo review. It uses my own login, and when the login has expired the report says so and the next round tries again. [AUT-3] <br> A page that owns a routine has a Runbook for it, saying what an agent told only "run routine X" must read and do, and a scheduled run follows it exactly. The docs check fails a registered routine with no runbook or a missing field. A runbook is not locked by my review. [DOC-16] | consolidation (TOP-DECISION 89) | o218: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Routines run where they can run fully <br> Health runs on my always-on machine for every repo; regression runs in GitHub Actions for a public repo and on that machine for a private one. Each report says where it ran, and a routine missed while the machine was off runs once at the next tick and says it was missed. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Routines run where they can run fully <br> Health runs on my always-on machine (the Mac through its launch agent, or a Windows PC through its own scheduled task) for every repo. Regression runs in GitHub Actions for a public repo and on that machine for a private one. <br> Each routine runs on a schedule set in the repo's config (every 4 hours by default), and I can also start it by hand. <br> A routine missed while that machine is asleep or off runs once at the next tick, and the digest says it was missed. <br> Each run's report says whether it ran on my Mac or in GitHub Actions. <br> A long issue body or comment is passed to gh in a file (`--body-file`), never on the command line, so a routine writes the same on native Windows. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Regression on a schedule <br> The full regression suite runs on the schedule set in the repo's settings, every 4 hours by default, and on every release tag; I can also start it by hand. The report names every test it skipped and why. | consolidation (TOP-DECISION 89): absorbed into AUT-1 | o219: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Regression on a schedule <br> The full regression suite runs on the schedule set in the repo's settings, every 4 hours by default, and on every release tag; I can also start it by hand. The report names every test it skipped and why. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Regression every few hours <br> The full regression suite runs on the schedule (every 4 hours by default), in GitHub Actions for a public repo (which also runs it on every release tag) and on my Mac for a private one; the report names every test it skipped and why. <br> A push or pull request runs only the tests its change affects (Regression, REG-4), in the same place as the full suite. <br> No GitHub Actions check this tool writes is needed to merge a private repo; where its ruleset requires named checks, the pull request lane posts them as commit statuses itself, success when the lane passes and failure when it fails, so a failing lane holds that merge and a passing one releases it. <br> A failing test opens or updates one issue labeled defect, tagged with the feature it guards when feature_labels is on, naming the test and the requirement; it closes by itself when the test passes again. <br> The CI suite runs in eight shards with one combined summary: each row is given the time left, the suite-time line counts the rows skipped for time (the unrun rows), and a newer run on the same ref cancels the older. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Health on a schedule <br> Health runs on my always-on machine on the schedule, after the latest finished regression run, with all its rule groups and the repo review. It uses my own login, and when the login has expired the report says so and the next round tries again. | consolidation (TOP-DECISION 89): absorbed into AUT-1 | o220: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Health on a schedule <br> Health runs on my always-on machine on the schedule, after the latest finished regression run, with all its rule groups and the repo review. It uses my own login, and when the login has expired the report says so and the next round tries again. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Health every few hours <br> Health never runs in GitHub Actions: it runs on my always-on machine on the schedule (every 4 hours by default), after the latest finished regression run, with all its rule groups; its report names that run with its commit and age, or says none finished, and says when health last ran. <br> The repo review always runs, using my own login on that machine, with no API key secret; when the login has expired or can't be reached, the report says which and the next round tries again. <br> Every finding becomes one issue tagged with its group and, when feature_labels is on, its feature, updated, closed or reopened as things change, never duplicated. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | A digest by email <br> After each round, one email goes to the address I set: what ran, its results, and the new, still-open and fixed issues grouped by feature, each with its link and the request to give the agent. The same digest is posted on a pinned issue. | consolidation (TOP-DECISION 89): absorbed into MCH-5 | o336: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A digest by email <br> After each round, one email goes to the address I set: what ran, its results, and the new, still-open and fixed issues grouped by feature, each with its link and the request to give the agent. The same digest is posted on a pinned issue. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-10 | A digest by email <br> After each round, one email goes to the address I set: what ran and its results, then the new, still-open and fixed issues grouped by feature, each with its link and the request to give the agent to fix it. <br> The same digest is also posted as one comment on a pinned Automation digest issue. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Routines and publishing stay under my control <br> Each routine turns off or reschedules with one setting and writes nothing without secrets. [AUT-5] <br> Publishing never deletes or overwrites pages it didn't write, and it can be undone. [AUT-5] | readme-six: the owner-approved final README (o514) | o588: "yes build it" |
| r3 | 2026-11-19 | Routines and publishing stay under my control <br> Each routine can be turned off or rescheduled in one setting. Without the secrets it needs, a routine runs, writes nothing and says what is missing. [AUT-5] <br> Publishing never deletes a wiki page and never overwrites one it didn't write unless I name it. The last publish can be undone. [DOC-11] | consolidation (TOP-DECISION 89) | o346: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Under my control <br> Each routine can be turned off or rescheduled in one setting. Without the secrets it needs, a routine runs, writes nothing and says what is missing. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Under my control <br> Each routine can be turned off or rescheduled in one setting. It writes to GitHub only with `--live` (the scheduled workflows pass it), and without the secrets it needs a routine runs but writes nothing and says what is missing. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Private address <br> The email address and the mail key live only in one local secrets file outside git, shared by both mailers and read only by the local runner. They never appear in the repo, logs, issues or the digest, and mail goes only to the one address I set. | consolidation (TOP-DECISION 89): absorbed into DEL-9 | o291: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Private address <br> The email address and the mail key live only in one local secrets file outside git, shared by both mailers and read only by the local runner. They never appear in the repo, logs, issues or the digest, and mail goes only to the one address I set. | v2 rewrite (prd-rewrite-to-10): changed: one file for both mailers (your decision, o39). | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Private address <br> The email address and the mail key live only in a local secrets file outside git, kept where the repo review cannot reach it, read only by the local runner; never in the repo, logs, issues or the digest comment, and never printed. The same holds for the GitHub token the Mac uses. <br> The mail file is `mail.env` in the schedule home, or the file `LOOP_MAIL_ENV` names (a shared file on a synced folder); on a machine with file modes a mail.env others can read sends nothing, and on Windows, which has no modes, that check is skipped. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Bounded cost <br> A round finishes within 45 minutes, and each report shows how long the round took. | consolidation (TOP-DECISION 89): absorbed into HLT-7 | o272: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Bounded cost <br> A round finishes within 45 minutes, and each report shows how long the round took. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Bounded cost <br> A round finishes within 45 minutes (the 30-minute regression budget of Regression REG-7 plus 15 for health and the digest, health starting when regression has finished, not at a fixed offset), and each report shows the round's wall time and its pass and fail counts, plus its Actions minutes when it ran in GitHub Actions, so I can slow the schedule if it costs too much. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Every routine has a runbook an agent follows exactly <br> Each routine is listed in the routine registry with the feature page that owns it (health-round on Health, regression-round on Regression), and that page's Runbook section says what a full run is, the one output, the forbidden shortcuts and how to check the run was real. <br> An automation prompt for a routine reduces to "read the <page> Runbook and follow it exactly"; a scheduled run never sends a dry run, a fixture or a test mail in place of the real output. | v2 rewrite (prd-rewrite-to-10): moved DOC-16 | o155: "start regroup 3 and 4" |
| r1 | 2026-11-13 | Every routine has a runbook an agent follows exactly <br> Each routine is listed in the routine registry with the feature page that owns it (health-round on Health, regression-round on Regression), and that page's Runbook section says what a full run is, the one output, the forbidden shortcuts and how to check the run was real. <br> An automation prompt for a routine reduces to "read the <page> Runbook and follow it exactly"; a scheduled run never sends a dry run, a fixture or a test mail in place of the real output. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Automation runs with declared, least access <br> Each routine has allow and deny rules in the repo for the commands, files and sites its runbook needs. Setup writes them into the repo's project settings, so a scheduled run on a fresh machine stops at no approval prompt, and the docs check fails a routine with missing or contradicting rules. [AUT-9] <br> Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing. [MCH-11] <br> When no app session can start, a worker starts as a background process through `agent_command` (the owner's `workers: app` rule still keeps a goal waiting for a bound session), and the start goes through one function other goals can extend. [MCH-6] <br> `setup.py desk` lists every desk-only step (trusting folders, permission modes, tool pre-approvals, the private-names file, mail.env, the Codex login), prints each open step once, records each as done, and `desk check` ends with DESK OK only when nothing is left at the desk and a phone-only start works. [MCH-6] | readme-six: absorbed into GRD-4 (o514) | o606: "yes build it" |
| r3 | 2026-11-19 | Automation runs with declared, least access <br> Each routine has allow and deny rules in the repo for the commands, files and sites its runbook needs. Setup writes them into the repo's project settings, so a scheduled run on a fresh machine stops at no approval prompt, and the docs check fails a routine with missing or contradicting rules. [AUT-9] <br> Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing. [MCH-11] <br> When no app session can start, a worker starts as a background process through `agent_command` (the owner's `workers: app` rule still keeps a goal waiting for a bound session), and the start goes through one function other goals can extend. [MCH-6] <br> `setup.py desk` lists every desk-only step (trusting folders, permission modes, tool pre-approvals, the private-names file, mail.env, the Codex login), prints each open step once, records each as done, and `desk check` ends with DESK OK only when nothing is left at the desk and a phone-only start works. [MCH-6] | consolidation (TOP-DECISION 89) | o299: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Every routine declares what it may do <br> Each routine has allow and deny rules in the repo for the commands, files and sites its runbook needs. Setup writes them into the repo's project settings, so a scheduled run on a fresh machine stops at no approval prompt, and the docs check fails a routine with missing or contradicting rules. | v2 rewrite (prd-rewrite-to-10) | o155: "start regroup 3 and 4" |
| r1 | 2026-11-14 | Every routine declares what it may do, in its repo. <br> Each routine in the registry has rows in `.loop/permissions.tsv` (routine, allow or deny, rule, why): the commands, file paths and sites its Runbook needs, and the denies its Never field states. The repo owns its list; the template owns the rule, the command that writes it and the check. <br> Setup writes the rows into the repo's committed project settings (`.claude/settings.json`, keeping every other rule), so a scheduled run on a fresh machine stops at no approval prompt for what its Runbook says it does; nothing private is written there. <br> The docs check fails a routine with no rows, a row missing from the project settings, a command or site the Runbook names that no allow row covers, and an allow that a deny contradicts. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### AUT-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A private repo needs no Actions check to merge <br> No GitHub Actions check this tool writes is needed to merge a private repo. Where the repo's rules require named checks, the pull-request checks post them as commit statuses. | consolidation (TOP-DECISION 89): absorbed into REL-12 | o345: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-14 | A private repo needs no Actions check to merge <br> No GitHub Actions check this tool writes is needed to merge a private repo. Where the repo's rules require named checks, the pull-request checks post them as commit statuses. | migration r1; date from the Review line | o155: "start regroup 3 and 4" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [ci-summary](Tests#t-ci-summary) | requirement | AUT-1 | Given the nightly run, when it ends, then it writes a results table to the job summary. | PASS 2026-11-27 |
| [schedule-setting](Tests#t-schedule-setting) | requirement | AUT-1 | Given a changed schedule setting, when the workflow is rewritten, then the Actions schedule changes. | PASS 2026-11-27 |
| [aut-defect-issue](Tests#t-aut-defect-issue) | requirement | AUT-1 | Given AUT-1, when test-automation.sh runs its 2 cases, then each passes: it prints every PASS line the 3 merged rows checke; the issue gains the defect label. | PASS 2026-11-27 |
| [ls-private-tick](Tests#t-ls-private-tick) | requirement | AUT-1 | Given AUT-1, when test-local-schedule.sh runs its 3 cases, then each passes: health runs, the regression runs live, one issue i; health runs, no regression runs the tick says REGR; it says Last ran and MISSED, a recent last run say. | PASS 2026-11-27 |
| [st-pass](Tests#t-st-pass) | requirement | AUT-1 | Given AUT-1, when test-statuses.sh runs its 2 cases, then each passes: one success per required check is posted with a de; only failure is posted, only for a head already on. | not run |
| [aut-email-file](Tests#t-aut-email-file) | requirement | AUT-1 | Given AUT-1, when test-automation-email.sh runs its 2 cases, then each passes: each is tagged with its group on no milestone (and; its defect issue is filed with no milestone read,. | PASS 2026-11-27 |
| [runbook-good](Tests#t-runbook-good) | requirement | AUT-1 | Given AUT-1, when test-runbook.sh runs its 4 cases, then each passes: it passes, and a Runbook placed before Problem is; each is refused naming the page, the routine and t; the page is neither locked nor marked changed; each routine in the registry has every field, says. | PASS 2026-11-27 |
| [runbook-registry](Tests#t-runbook-registry) | requirement | AUT-1 | Given a routine in the routine registry whose page has no runbook for it, or a registry row naming no page, when the docs check runs, then it fails; it passes once the page carries the runbook, and with no registry file. | FAIL 2026-11-27 |
| [runbook-output-names-row](Tests#t-runbook-output-names-row) | requirement | AUT-1 | Given a Runbook whose Output names a Deployments row that does not exist, when the docs check runs, then it is refused naming the row; an existing row passes. | not run |
| [aut-routine-block](Tests#t-aut-routine-block) | requirement | AUT-1 | Given the AUT-1 cases of test-automation-routines.py, when it runs once, then it prints every PASS line the 3 merged rows checked and no FAIL line. | PASS 2026-11-27 |
| [health-register-no-launchd](Tests#t-health-register-no-launchd) | requirement | AUT-1 | Given a machine that is not a Mac, when local register runs, then the repo is in the schedule registry, a second run keeps one entry, and no launch agent is written. | PASS 2026-11-14 |
| [perms-docs-check](Tests#t-perms-docs-check) | requirement | AUT-1 | Given a routine with no declared permissions, when docs.py check runs, then it prints a PERMISSIONS finding (the same check as audit.py permissions check, run inside docs.py check). | not run |
| [refuse-replace](Tests#t-refuse-replace) | requirement | AUT-5 | Given AUT-5, when test-docs.sh runs its 2 cases, then each passes: that page is never overwritten; the original page is back. | PASS 2026-11-27 |
| [bad-schedule-refused](Tests#t-bad-schedule-refused) | requirement | AUT-5 | Given a schedule setting that is not a cron time, when it is applied, then it is refused. | PASS 2026-11-27 |
| [aut-regression-off](Tests#t-aut-regression-off) | requirement | AUT-5 | Given AUT-5, when test-automation.sh runs its 2 cases, then each passes: it prints every PASS line the 5 merged rows checke; it prints every PASS line the 3 merged rows checke. | PASS 2026-11-27 |
| [publish-tables-regen](Tests#t-publish-tables-regen) | requirement | AUT-5 | Given the AUT-5 cases of test-publish-tables.py, when it runs once, then it prints every PASS line the 2 merged rows checked and no FAIL line. | PASS 2026-11-13 |
| [capture-row-ci](Tests#t-capture-row-ci) | defect | [#3789](https://github.com/jcl2018/agent-workflow-template/issues/3789) closed (2026-11-13) | Given a failing row that ends in grep -q and prints nothing, when the scheduled workflow files its issue, then the body holds the row's last 40 output lines, not an empty block (#3789). | PASS 2026-11-27 |
| [automation-table-health](Tests#t-automation-table-health) | defect | [#3857](https://github.com/jcl2018/agent-workflow-template/issues/3857) closed (2026-11-13) | Given a repo with health on and no health workflow file, when the Automation table renders, then health and the digest email read the Mac's local schedule and owe no health.yml. | PASS 2026-11-27 |
