<!-- workflow-docs -->
# Automation

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/10

Review: **Reviewed 2026-11-14** <!-- prd P=a45649a4 R=bde75618 N=e081872e M=4670eeeb U=03828777 --> <!-- kept gap-cheap-fixes@3f6ccd9e -->

How to use: [How-to-use-Automation](How-to-use-Automation)

## Problem
- Things break between my sessions, and I only find out when I next open one; the important checks should run on their own.
- Every few hours I want the full regression suite and the health check to run, and every problem they find to become an issue tagged with its group, and with its feature when feature_labels is on.
- I want one email to my address after each round that tells me what ran, what broke, what got fixed and what to ask the agent, without opening GitHub.

## Requirements

### Functional
- AUT-1: **Reviewed 2026-11-19** Routines run on schedule, by runbook <!-- reviewed 6bea60c3 -->
  - Health runs on my always-on machine for every repo; regression runs in GitHub Actions for a public repo and on that machine for a private one. Each report says where it ran, and a routine missed while the machine was off runs once at the next tick and says it was missed. [AUT-1]
  - The full regression suite runs on the schedule set in the repo's settings, every 4 hours by default, and on every release tag; I can also start it by hand. The report names every test it skipped and why. [AUT-2]
  - Health runs on my always-on machine on the schedule, after the latest finished regression run, with all its rule groups and the repo review. It uses my own login, and when the login has expired the report says so and the next round tries again. [AUT-3]
  - A page that owns a routine has a Runbook for it, saying what an agent told only "run routine X" must read and do, and a scheduled run follows it exactly. The docs check fails a registered routine with no runbook or a missing field. A runbook is not locked by my review. [DOC-16]

- AUT-9: **Reviewed 2026-11-19** Automation runs with declared, least access <!-- reviewed 44fb8c0c -->
  - Each routine has allow and deny rules in the repo for the commands, files and sites its runbook needs. Setup writes them into the repo's project settings, so a scheduled run on a fresh machine stops at no approval prompt, and the docs check fails a routine with missing or contradicting rules. [AUT-9]
  - Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing. [MCH-11]
  - When no app session can start, a worker starts as a background process through `agent_command` (the owner's `workers: app` rule still keeps a goal waiting for a bound session), and the start goes through one function other goals can extend. [MCH-6]
  - `setup.py desk` lists every desk-only step (trusting folders, permission modes, tool pre-approvals, the private-names file, mail.env, the Codex login), prints each open step once, records each as done, and `desk check` ends with DESK OK only when nothing is left at the desk and a phone-only start works. [MCH-6]

### Non-functional
- AUT-5: **Reviewed 2026-11-19** Routines and publishing stay under my control <!-- reviewed ec03824d -->
  - Each routine can be turned off or rescheduled in one setting. Without the secrets it needs, a routine runs, writes nothing and says what is missing. [AUT-5]
  - Publishing never deletes a wiki page and never overwrites one it didn't write unless I name it. The last publish can be undone. [DOC-11]

## Non-goals
- The scheduled routines never push, merge or release; they only write issues, labels, comments, run reports (an Actions run summary or a local report on my Mac) and the digest email.
- No chat or webhook notifications; email and GitHub only.

## Success metrics
- After each scheduled round, one digest email arrives and every failing test or finding has exactly one open issue tagged with its feature.
- With a routine set to off, its runs write no issue, label, comment or email.

## Revisions

### Retired

- AUT-10: moved to REL-12
- AUT-2: moved to AUT-1
- AUT-3: moved to AUT-1
- AUT-4: moved to MCH-5
- AUT-6: moved to DEL-9
- AUT-7: moved to HLT-7
- AUT-8: moved to AUT-1

### AUT-1

| rev | date | text | why | approved |
|---|---|---|---|---|
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
| [ci-summary](Tests#t-ci-summary) | requirement | AUT-1 | Given the nightly run, when it ends, then it writes a results table to the job summary. | PASS 2026-11-19 |
| [schedule-setting](Tests#t-schedule-setting) | requirement | AUT-1 | Given a changed schedule setting, when the workflow is rewritten, then the Actions schedule changes. | PASS 2026-11-12 |
| [aut-defect-issue](Tests#t-aut-defect-issue) | requirement | AUT-1 | Given a failing test, when the scheduled regression runs, then one issue labelled defect opens, naming the test, the feature and the requirement it guards. | PASS 2026-11-12 |
| [aut-old-issue-relabel](Tests#t-aut-old-issue-relabel) | requirement | AUT-1 | Given an open failing-test issue without the defect label, when the test fails again, then the issue gains the defect label. | PASS 2026-11-12 |
| [aut-issue-list-fails](Tests#t-aut-issue-list-fails) | requirement | AUT-1 | Given a page of the open regression issues cannot be read, when the scheduled regression runs, then it changes no issue rather than open duplicates. | PASS 2026-11-12 |
| [ls-private-tick](Tests#t-ls-private-tick) | requirement | AUT-1 | Given a toy repo whose regression_runs is mac and one failing row, when the tick runs, then health runs, the regression runs live, one issue is filed for the failing row, the digest is posted and the tick says REGRESSION: runs on the Mac. | not run |
| [ls-public-tick](Tests#t-ls-public-tick) | requirement | AUT-1 | Given a toy repo whose regression_runs is actions, when the tick runs, then health runs, no regression runs the tick says REGRESSION: runs in GitHub Actions and the newest suite-time artifact is fetched into the git common dir. | not run |
| [ls-missed-run](Tests#t-ls-missed-run) | requirement | AUT-1 | Given a registry whose last run is older than the interval plus an hour, when the digest is composed, then it says Last ran and MISSED, a recent last run says no MISSED, a repo whose tick started 20 minutes after another's is still due at the next fire, a run id of 12 digits not starting 20 is an Actions id, and one coalesced fire after sleep makes every overdue repo due. | not run |
| [st-pass](Tests#t-st-pass) | requirement | AUT-1 | Given a private repo whose rules require two checks and a lane that passed, when the pr lane posts, then one success per required check is posted with a description naming the local run and no target_url. | not run |
| [st-fail-never-success](Tests#t-st-fail-never-success) | requirement | AUT-1 | Given a lane that failed, when it posts, then only failure is posted, only for a head already on the remote, never success, and an unpushed head posts nothing. | not run |
| [aut-regression-schedule-mismatch](Tests#t-aut-regression-schedule-mismatch) | requirement | AUT-1 | Given a regression schedule that differs from the config, when the routine runs, then it names the difference and the command that fixes it. | PASS 2026-11-12 |
| [aut-email-file](Tests#t-aut-email-file) | requirement | AUT-1 | Given health findings, when the scheduled health run files them, then each is tagged with its group on no milestone (and with its feature when feature_labels is on), no open issue is duplicated, and an issue the owner put on a milestone stays. | PASS 2026-11-12 |
| [aut-email-regression](Tests#t-aut-email-regression) | requirement | AUT-1 | Given a failing test, when the scheduled regression runs, then its defect issue is filed with no milestone read, made or set, tagged with its feature when feature_labels is on, the suite runs every 4 hours and on every release tag, and a failed filing fails the run. | PASS 2026-11-12 |
| [runbook-good](Tests#t-runbook-good) | requirement | AUT-1 | Given a feature page with a well-formed Runbook section after its Problem, when the docs check runs, then it passes, and a Runbook placed before Problem is refused as out of order. | not run |
| [runbook-refused](Tests#t-runbook-refused) | requirement | AUT-1 | Given a Runbook missing its Full run or Output field, with a field too short, an unknown field, loose prose, no routine heading or a bad routine name, when the docs check runs, then each is refused naming the page, the routine and the field. | not run |
| [runbook-registry](Tests#t-runbook-registry) | requirement | AUT-1 | Given a routine in the routine registry whose page has no runbook for it, or a registry row naming no page, when the docs check runs, then it fails; it passes once the page carries the runbook, and with no registry file. | not run |
| [runbook-not-locked](Tests#t-runbook-not-locked) | requirement | AUT-1 | Given a Reviewed feature page that gains a Runbook section, when the docs check runs, then the page is neither locked nor marked changed. | not run |
| [runbook-repo](Tests#t-runbook-repo) | requirement | AUT-1 | Given this repo's Health and Regression pages, when their Runbook sections are read, then each routine in the registry has every field, says a full run is live, and names a fixture or dry run as forbidden. | not run |
| [runbook-output-names-row](Tests#t-runbook-output-names-row) | requirement | AUT-1 | Given a Runbook whose Output names a Deployments row that does not exist, when the docs check runs, then it is refused naming the row; an existing row passes. | not run |
| [aut-routine-block](Tests#t-aut-routine-block) | requirement | AUT-1 | Given a routine added to the config's automation list, when the Automation block renders, then it has a row for the routine with its schedule and where it runs. | not run |
| [aut-routine-runbook-owed](Tests#t-aut-routine-runbook-owed) | requirement | AUT-1 | Given a routine in the config's automation list whose page has no Runbook section for it, when the docs check runs, then it reports the missing Runbook. | not run |
| [aut-routine-prompt](Tests#t-aut-routine-prompt) | requirement | AUT-1 | Given a routine in the registry, when docs.py prompts runs, then it prints one line saying to fast-forward to origin/main and follow the repo's Runbook section for the routine. | not run |
| [health-register-no-launchd](Tests#t-health-register-no-launchd) | requirement | AUT-1 | Given a machine that is not a Mac, when local register runs, then the repo is in the schedule registry, a second run keeps one entry, and no launch agent is written. | PASS 2026-11-14 |
| [perms-docs-check](Tests#t-perms-docs-check) | requirement | AUT-1 | Given a routine with no declared permissions, when docs.py check runs, then it prints a PERMISSIONS finding (the same check as audit.py permissions check, run inside docs.py check). | not run |
| [machine-no-prompt-mode](Tests#t-machine-no-prompt-mode) | requirement | AUT-9 | Given a task with no recorded mode or a prompting one, when machine check runs, then it fails, and a no-prompt mode passes. | not run |
| [perms-undeclared](Tests#t-perms-undeclared) | requirement | AUT-9 | Given a routine in the registry with no rows in .loop/permissions.tsv, when permissions.py check runs, then it prints UNDECLARED and exits 1. | not run |
| [perms-not-written](Tests#t-perms-not-written) | requirement | AUT-9 | Given declared rows the project settings lack, when permissions.py check runs, then each is NOT WRITTEN and it exits 1. | not run |
| [perms-uncovered](Tests#t-perms-uncovered) | requirement | AUT-9 | Given a Runbook that names a command and a site no allow row covers, when permissions.py check runs, then each is UNCOVERED. | not run |
| [perms-conflict](Tests#t-perms-conflict) | requirement | AUT-9 | Given an allow rule that a deny rule covers, when permissions.py check runs, then it prints CONFLICT. | not run |
| [perms-private-refused](Tests#t-perms-private-refused) | requirement | AUT-9 | Given a row holding a home path, when permissions.py write runs, then it is refused and no settings file is written. | PASS 2026-11-17 |
| [perms-write-keeps](Tests#t-perms-write-keeps) | requirement | AUT-9 | Given a settings file with other keys and rules, when permissions.py write runs, then they are all kept. | not run |
| [perms-repo-ok](Tests#t-perms-repo-ok) | requirement | AUT-9 | Given this repo, when permissions.py check runs, then its routines are declared, written and covered. | not run |
| [perms-settings-tracked](Tests#t-perms-settings-tracked) | requirement | AUT-9 | Given a fresh checkout, when the permissions check runs, then .claude/settings.json is in it, because it is tracked and not ignored. | PASS 2026-11-15 |
| [perms-no-repo-deny](Tests#t-perms-no-repo-deny) | requirement | AUT-9 | Given the committed .claude/settings.json, when it is read, then it holds allow rules only, because a deny would apply to every session in the repo. | not run |
| [desk-lists](Tests#t-desk-lists) | requirement | AUT-9 | Given desk-only onboarding and no app session, when steps are listed, run and checked, then every step is listed once, gaps and invalid steps are refused, DESK OK requires completed setup and agent_command, and a background worker starts through agent_command while workers app keeps its bound-session rule. Covers #4805. | PASS 2026-11-18 |
| [refuse-replace](Tests#t-refuse-replace) | requirement | AUT-5 | Given a wiki page the tool did not write, when the tool writes pages, then that page is never overwritten. | PASS 2026-11-19 |
| [bad-schedule-refused](Tests#t-bad-schedule-refused) | requirement | AUT-5 | Given a schedule setting that is not a cron time, when it is applied, then it is refused. | PASS 2026-11-12 |
| [publish-restore](Tests#t-publish-restore) | requirement | AUT-5 | Given a publish that adopted a page someone else wrote, when restore runs, then the original page is back. | PASS 2026-11-19 |
| [aut-regression-off](Tests#t-aut-regression-off) | requirement | AUT-5 | Given regression_cron off, when the regression workflow runs, then it writes nothing and says the routine is off. | PASS 2026-11-12 |
| [aut-off-by-hand](Tests#t-aut-off-by-hand) | requirement | AUT-5 | Given regression_cron off, when its workflow is written, then it has no schedule and can still be started by hand. | PASS 2026-11-12 |
| [aut-digest-no-token](Tests#t-aut-digest-no-token) | requirement | AUT-5 | Given no token in the digest step, when it runs in Actions, then it says what is missing and writes nothing. | PASS 2026-11-12 |
| [aut-no-push](Tests#t-aut-no-push) | requirement | AUT-5 | Given the scheduled workflows, when they are written, then neither pushes nor has write access to the repo's contents. | PASS 2026-11-12 |
| [aut-by-hand-runs](Tests#t-aut-by-hand-runs) | requirement | AUT-5 | Given regression_cron off, when someone starts the regression run by hand, then it still runs. | PASS 2026-11-12 |
| [aut-digest-dry-run](Tests#t-aut-digest-dry-run) | requirement | AUT-5 | Given no token outside Actions, when the digest runs, then it prints the comment, says it is a dry run and writes nothing. | PASS 2026-11-12 |
| [aut-off-push-runs](Tests#t-aut-off-push-runs) | requirement | AUT-5 | Given regression_cron off, when a release tag is pushed, then the regression run still runs the rows. | PASS 2026-11-12 |
| [aut-off-dispatch-runs](Tests#t-aut-off-dispatch-runs) | requirement | AUT-5 | Given regression_cron off, when someone starts the regression run by hand, then it still runs the rows. | PASS 2026-11-12 |
| [publish-tables-regen](Tests#t-publish-tables-regen) | requirement | AUT-5 | Given a merged head whose generated Tests tables are stale, when the wiki publish prepares its tree, then it re-renders them and the Tests page is no longer stale. | PASS 2026-11-13 |
| [publish-tables-handwritten](Tests#t-publish-tables-handwritten) | requirement | AUT-5 | Given a stale hand-written page, when the wiki publish re-renders the generated tables, then that page is still reported stale and the publish still refuses. | PASS 2026-11-13 |
| [capture-row-ci](Tests#t-capture-row-ci) | defect | [#3789](https://github.com/jcl2018/agent-workflow-template/issues/3789) closed (2026-11-13) | Given a failing row that ends in grep -q and prints nothing, when the scheduled workflow files its issue, then the body holds the row's last 40 output lines, not an empty block (#3789). | FAIL 2026-11-13 |
| [automation-table-health](Tests#t-automation-table-health) | defect | [#3857](https://github.com/jcl2018/agent-workflow-template/issues/3857) closed (2026-11-13) | Given a repo with health on and no health workflow file, when the Automation table renders, then health and the digest email read the Mac's local schedule and owe no health.yml. | not run |
| [desk-lists-4805](Tests#t-desk-lists-4805) | defect | [#4805](https://github.com/jcl2018/agent-workflow-template/issues/4805) closed (2026-11-18) | Given the missing desk onboarding and background worker fallback, when its full fixture runs, then every promised behavior is required and fails without the implementation. | PASS 2026-11-18 |
