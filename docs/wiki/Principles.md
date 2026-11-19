<!-- workflow-docs -->
<!-- workflow-docs guide -->
# Principles

Eight principles sit above the features. Health gives one verdict for each, red when any of its groups fails, and each is made true by the requirements it names. Each table lists the requirements that enforce its principle: the requirement, its feature, the release that introduced it, a one-line summary and a link to the feature's flow diagram. A row marked v2.1 (planned) is a feature on the v2.1 roadmap that has no requirement ID yet. The README shows the same eight in short; this page has each in full, with its diagram and requirements.

![How principles, health and features fit](principles-overview.svg)

## 1. Documentation-driven

Nothing is built that a Reviewed requirement doesn't ask for, and the PRD changes only by your words.

![Documentation-driven](principle-01-documentation-driven.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [DOC-2 The PRD is mine](Documentation) | Documentation | v0.1.2 | Only I mark a page or a requirement Reviewed, in my own recorded words | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DOC-20 Reviewed text is revised, never rewritten](Documentation) | Documentation | v1.0.67 | A change to a Reviewed requirement is a new revision with its date, reason and my approval; earlier… | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DOC-22 The PRD is read-only while a goal builds](Documentation) | Documentation | v1.0.67 | A goal never edits a Reviewed requirement while it builds, and a page has one writer at a time on any… | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DEL-2 Done lines are frozen](Delivery) | Delivery | v0.1.2 | Done lines can't change once the goal starts; a change means a new goal | [Delivery flow](How-to-use-Delivery#system-diagram) |
| [DEL-18 Everything goes through a goal](Delivery) | Delivery | v1.0.70 | Every change to a repo's main branch arrives through a goal: its pull request and its release commit | [Delivery flow](How-to-use-Delivery#system-diagram) |
| [DEL-19 Every goal serves a requirement](Delivery) | Delivery | v1.0.70 | A goal is frozen only when it names the Reviewed requirement it builds, fixes or keeps true | [Delivery flow](How-to-use-Delivery#system-diagram) |
| [REG-1 Three kinds of tests](Regression) | Regression | v0.1.2 | Every Reviewed requirement has at least one requirement test, every whole flow has an end-to-end… | [Regression flow](How-to-use-Regression#system-diagram) |
| plan-red-team (planned) | Delivery | v2.1 (planned) | The plan is challenged against the PRD before build | [Delivery flow](How-to-use-Delivery#system-diagram) |

## 2. The loop and coverage

Every requirement is enforced and proven, and whatever falls short, conflicts or has no owner becomes work until it is fixed or the PRD is revised.

![The loop and coverage](principle-02-the-loop-and-coverage.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [REG-1 Three kinds of tests](Regression) | Regression | v0.1.2 | Every Reviewed requirement has at least one requirement test, every whole flow has an end-to-end… | [Regression flow](How-to-use-Regression#system-diagram) |
| [REG-6 Every fixed issue leaves a test](Regression) | Regression | v0.1.2 | A goal that fixes an issue adds that issue's defect test, seen failing on the old code and passing on… | [Regression flow](How-to-use-Regression#system-diagram) |
| [REG-9 Honest results](Regression) | Regression | v0.1.3 | Every test has been seen failing once, or shows as unproven | [Regression flow](How-to-use-Regression#system-diagram) |
| [REG-10 Tests a machine can't run](Regression) | Regression | v0.27.46 | A test this machine can't run is skipped with its reason and never counted as seen failing | [Regression flow](How-to-use-Regression#system-diagram) |
| [REG-15 Coverage is measured in one place](Regression) | Regression | v1.0.74 | Each requirement's coverage step, from Stated to Fresh, is computed from the latest full run on main and… | [Regression flow](How-to-use-Regression#system-diagram) |
| [REG-16 Coverage never drops silently](Regression) | Regression | v1.0.74 | A goal that would remove the only proof of a Reviewed requirement is refused at qa, and a release that… | [Regression flow](How-to-use-Regression#system-diagram) |
| [DOC-3 Tests follow on their own](Documentation) | Documentation | v0.1.2 | Once I review a PRD, the loop writes Given/When/Then tests for each requirement, links each to a… | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [HLT-4 Findings become issues](Health) | Health | v0.1.2 | Each finding is one GitHub issue tagged with its group and its feature | [Health flow](How-to-use-Health#system-diagram) |
| [HLT-6 Every rule can fire](Health) | Health | v0.1.2 | Every health rule has a negative control that proves it can fire | [Health flow](How-to-use-Health#system-diagram) |
| [HLT-12 A filed finding becomes work](Health) | Health | v1.0.75 | When the next goals are planned, the open defect and backlog issues are read by feature and goals are… | [Health flow](How-to-use-Health#system-diagram) |
| [GRD-9 Health proves every guardrail](Guardrails) | Guardrails | v0.27.1 | Each guardrail has a health rule that reads whether it is present and working, and each rule has a… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [DEL-14 Every goal feeds back what it found](Delivery) | Delivery | v0.28.14 | When a goal ships, each finding it did not fix is filed once: a break of a Reviewed requirement as an… | [Delivery flow](How-to-use-Delivery#system-diagram) |
| ops-findings (planned) | Operation | v2.1 (planned) | What the operation finds while releasing becomes tracked work | [Operation flow](How-to-use-Operation#system-diagram) |

## 3. The docs are true

The pages agree with each other and with the code: one ID, one name for each command, and no two requirements that contradict.

![The docs are true](principle-03-the-docs-are-true.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [DOC-1 PRD template](Documentation) | Documentation | v0.1.2 | One template defines every feature page: Problem written from the user's side, Requirements as ID'd… | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DOC-6 Each skill's commands are documented](Documentation) | Documentation | v0.1.2 | Each skill's command map names every command, and its command reference gives each command's exact… | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DOC-12 Fast check](Documentation) | Documentation | v0.22.0 | The docs check finishes in under 30 seconds on this repo, every time | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DOC-13 Same answer every time](Documentation) | Documentation | v0.22.0 | The docs check is deterministic: the same pages and tests give the same result, with no AI judgment | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DOC-20 Reviewed text is revised, never rewritten](Documentation) | Documentation | v1.0.67 | A change to a Reviewed requirement is a new revision with its date, reason and my approval; earlier… | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [DOC-21 A code change alone never un-reviews a page](Documentation) | Documentation | v1.0.74 | A change to code or settings a page describes never needs my words when none of the page's own text… | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [HLT-5 Repo review](Health) | Health | v0.1.2 | A reviewer, separate from the rules and never part of the verdict, reads every page, issue, test and the… | [Health flow](How-to-use-Health#system-diagram) |
| [HLT-13 Conflicts and orphans are findings](Health) | Health | v1.0.75 | Health flags two requirements that conflict or repeat, and any test, script or goal that names no… | [Health flow](How-to-use-Health#system-diagram) |
| [REL-10 Every goal ends with a release](Release) | Release | v1.0.70 | With auto_merge on, a finished goal is merged and released automatically: version bump, release note… | [Release flow](How-to-use-Release#system-diagram) |
| [INT-2 The repo stays the source of truth](Integrations) | Integrations | v1.0.74 | Every check, test and publish reads the repo's own copy and never the outside system | [Integrations flow](How-to-use-Integrations#system-diagram) |
| [INT-3 A difference is a delta, never a silent overwrite](Integrations) | Integrations | v1.0.74 | Where both sides can change the same thing, sync compares them with what they last agreed on | [Integrations flow](How-to-use-Integrations#system-diagram) |

## 4. Nothing stale or left over

The tests ran today, merged work is released, and no stale branch, idle session, old finding or question to you is left behind.

![Nothing stale or left over](principle-04-nothing-stale-or-left-over.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [AUT-2 Regression on a schedule](Automation) | Automation | v0.20.0 | The full regression suite runs on the schedule set in the repo's settings, every 4 hours by default, and… | [Automation flow](How-to-use-Automation#system-diagram) |
| [AUT-3 Health on a schedule](Automation) | Automation | v0.20.0 | Health runs on my always-on machine on the schedule, after the latest finished regression run, with all… | [Automation flow](How-to-use-Automation#system-diagram) |
| [REG-4 When tests run](Regression) | Regression | v0.1.2 | In the loop a goal runs only the tests its change affects plus its own new ones, and they run again on… | [Regression flow](How-to-use-Regression#system-diagram) |
| [REL-9 The merge's wiki check refuses only for what the goal changed](Release) | Release | v0.1.2 | merge.py refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts… | [Release flow](How-to-use-Release#system-diagram) |
| [REL-1 A version number says what changed](Release) | Release | v0.1.2 | A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone | [Release flow](How-to-use-Release#system-diagram) |
| [REL-5 A candidate admits only gate fixes](Release) | Release | v0.1.2 | From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not… | [Release flow](How-to-use-Release#system-diagram) |
| [REL-6 Promotion tags, snapshots and reports](Release) | Release | v0.1.2 | Promoting a major runs only from the operation session with my record naming that version and every gate… | [Release flow](How-to-use-Release#system-diagram) |
| [REL-7 A major can be reverted](Release) | Release | v0.1.2 | revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a… | [Release flow](How-to-use-Release#system-diagram) |
| [OPS-6 Clean up after every goal](Operation) | Operation | v0.1.2 | When a goal merges, its worker session is given the next ready goal or archived, and its worktree and… | [Operation flow](How-to-use-Operation#system-diagram) |
| [OPS-8 No silent worker](Operation) | Operation | v0.1.2 | A worker with no report for 30 minutes shows under Needs you | [Operation flow](How-to-use-Operation#system-diagram) |
| [HLT-8 Triage](Health) | Health | v0.22.0 | Open findings are shown per feature with their kind, age and count | [Health flow](How-to-use-Health#system-diagram) |
| [HLT-12 A filed finding becomes work](Health) | Health | v1.0.75 | When the next goals are planned, the open defect and backlog issues are read by feature and goals are… | [Health flow](How-to-use-Health#system-diagram) |
| [CHK-7 Blockers first](Check-in-and-board) | Check in and board | v1.0.75 | Each item under Needs you says what it holds up and whether it is on the critical path to the next… | [Check in and board flow](How-to-use-Check-in-and-board#system-diagram) |
| release-readiness (planned) | Release | v2.1 (planned) | A goal's release readiness is said before the merge | [Release flow](How-to-use-Release#system-diagram) |

## 5. Fast, cheap and small

Goals, tests and health stay inside their time and token limits, and scripts, pages and the package stay inside their size limits, including Agensi's.

![Fast, cheap and small](principle-05-fast-cheap-and-small.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [GRD-2 Budgets and caps stop a runaway](Guardrails) | Guardrails | v0.27.1 | Time, token and test budgets stop a goal or a step before it runs away | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-7 CI spends minutes only on runs that matter](Guardrails) | Guardrails | v0.27.1 | A newer run of the same workflow on the same branch cancels the one it replaces, and a heavy job is… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-8 A step far past its usual is flagged while it runs](Guardrails) | Guardrails | v0.27.1 | A step whose tokens or time pass a set multiple of that step's usual is flagged on the board and in the… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-19 A page stays small enough to review](Guardrails) | Guardrails | v1.0.75 | A feature page holds at most the number of requirements one setting allows, and health's Size group… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-20 The package always passes Agensi's rules](Guardrails) | Guardrails | v1.0.75 | No release is cut unless the built package passes every rule Agensi publishes: the file, size and… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-21 Our package limits are never looser than Agensi's](Guardrails) | Guardrails | v1.0.75 | One table on this page states each package limit: Agensi's figure, ours, and the date Agensi's page was… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-22 A goal learns at qa that it doesn't fit](Guardrails) | Guardrails | v1.0.75 | A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [DEL-17 A goal's ETA is a hard limit](Delivery) | Delivery | v1.0.70 | Every goal records an ETA when it is frozen | [Delivery flow](How-to-use-Delivery#system-diagram) |
| [REG-7 Fast in the loop](Regression) | Regression | v0.1.2 | Every in-loop test run stays within a time budget, 15 minutes by default and never lower | [Regression flow](How-to-use-Regression#system-diagram) |
| [REG-11 Preparation is budgeted too](Regression) | Regression | v1.0.74 | The work before a lane's first test, preparing, planning and waiting for a slot, has its own budget, 15… | [Regression flow](How-to-use-Regression#system-diagram) |
| [REG-14 Caps on tests and suite time](Regression) | Regression | v1.0.74 | The number of tests and the full-suite time are capped by settings | [Regression flow](How-to-use-Regression#system-diagram) |
| [AUT-7 Bounded cost](Automation) | Automation | v0.22.0 | A round finishes within 45 minutes, and each report shows how long the round took | [Automation flow](How-to-use-Automation#system-diagram) |
| [HLT-11 Health keeps the repo lean](Health) | Health | v1.0.75 | Health flags an in-loop test run over its time budget, naming the slowest tests to move to the full… | [Health flow](How-to-use-Health#system-diagram) |
| [SET-3 Shipped as a versioned package](Setup) | Setup | v0.1.3 | The template ships as one versioned package of separate skills that works out of the box with a built-in… | [Setup flow](How-to-use-Setup#system-diagram) |
| release-eta (planned) | Release | v2.1 (planned) | A release says when it will land and flags a slip | [Release flow](How-to-use-Release#system-diagram) |
| merge-queue (planned) | Release | v2.1 (planned) | Ready pull requests merge in batches: one CI run, one release | [Release flow](How-to-use-Release#system-diagram) |

## 6. Nothing private escapes

No private name, path, address or key leaves the machine, and automation gets only the access it needs.

![Nothing private escapes](principle-06-nothing-private-escapes.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [GRD-3 Nothing private is committed](Guardrails) | Guardrails | v0.27.1 | Every commit, push and pull request passes the private-name scan, and local settings and private values… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-4 A worker writes only its own goal's work](Guardrails) | Guardrails | v0.27.1 | A worker can't widen its own goal's touched files, resume itself or change its own budget, and it… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-5 Nothing is written to GitHub without --live](Guardrails) | Guardrails | v0.27.1 | Every command that writes issues, comments, milestones or releases previews by default and writes only… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [GRD-16 No commit skips the hooks](Guardrails) | Guardrails | v1.0.75 | A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [AUT-6 Private address](Automation) | Automation | v0.22.0 | The email address and the mail key live only in one local secrets file outside git, shared by both… | [Automation flow](How-to-use-Automation#system-diagram) |
| [AUT-9 Every routine declares what it may do](Automation) | Automation | v0.28.59 | Each routine has allow and deny rules in the repo for the commands, files and sites its runbook needs | [Automation flow](How-to-use-Automation#system-diagram) |
| [INT-4 Nothing leaves without my say](Integrations) | Integrations | v1.0.74 | An integration reads by default | [Integrations flow](How-to-use-Integrations#system-diagram) |
| [MCH-6 Phone-first: starting a worker never needs the desktop app](Machines) | Machines | v1.0.65 | When no app session can start, a worker starts as a background process through agent_command (the… | [Machines flow](How-to-use-Machines#system-diagram) |

## 7. It works installed fresh

A repo that adopts the template gets the same loop, checks and guardrails, with nothing rebuilt there.

![It works installed fresh](principle-07-it-works-installed-fresh.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [SET-1 One command adopts a repo](Setup) | Setup | v0.1.3 | One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled… | [Setup flow](How-to-use-Setup#system-diagram) |
| [SET-6 Adoption is proven](Setup) | Setup | v0.22.0 | Adoption is proven on test repos shaped like real ones, and every adoption defect found in a real repo… | [Setup flow](How-to-use-Setup#system-diagram) |
| [SET-16 One command judges a repo fully migrated](Setup) | Setup | v1.0.28 | One read-only command lists every gap between a repo and the current template, each with a one-line fix… | [Setup flow](How-to-use-Setup#system-diagram) |
| [SET-21 Adopted repos build on the template, not copies of it](Setup) | Setup | v1.0.70 | An adopted repo holds only its own settings, pages, tests and data | [Setup flow](How-to-use-Setup#system-diagram) |
| [GRD-10 Setup installs the whole set](Guardrails) | Guardrails | v0.27.1 | Adopting a repo installs every guardrail on this page with its default setting and lists each one… | [Guardrails flow](How-to-use-Guardrails#system-diagram) |
| [MCH-1 One command sets a machine up](Machines) | Machines | v1.0.26 | A second Mac or Windows machine reaches this one's setup from a git clone and one command: a dry run… | [Machines flow](How-to-use-Machines#system-diagram) |
| [MCH-7 Prerequisites first](Machines) | Machines | v1.0.70 | Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh… | [Machines flow](How-to-use-Machines#system-diagram) |
| develop-staging (planned) | Release | v2.1 (planned) | Changes land on a develop branch and reach main as a tested release | [Release flow](How-to-use-Release#system-diagram) |

## 8. It stops for you only when it must

It asks you only for what is yours to decide: anything destructive, costly or private, and any change to the PRD. Everything else it decides, tells you, and lets you reverse.

![It stops for you only when it must](principle-08-it-stops-for-you-only-when-it-must.svg)

| Requirement | Feature | Release | Summary | Flow |
|---|---|---|---|---|
| [DEL-3 It only stops for me when it must](Delivery) | Delivery | v0.1.2 | A decision that is mine waits under Needs you, or is auto-approved and logged where the repo allows | [Delivery flow](How-to-use-Delivery#system-diagram) |
| [DEL-17 A goal's ETA is a hard limit](Delivery) | Delivery | v1.0.70 | Every goal records an ETA when it is frozen | [Delivery flow](How-to-use-Delivery#system-diagram) |
| [OPS-11 Full auto mode](Operation) | Operation | v0.1.2 | Full auto is off in a new repo until I turn it on | [Operation flow](How-to-use-Operation#system-diagram) |
| [OPS-18 I say it once](Operation) | Operation | v0.1.3 | One standing instruction to merge, recorded once for named goals or all, replaces a go per merge, and a… | [Operation flow](How-to-use-Operation#system-diagram) |
| [MCH-8 A goal started on another machine can be adopted](Machines) | Machines | v1.0.70 | A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open… | [Machines flow](How-to-use-Machines#system-diagram) |
| [REL-11 A merge is never refused late or left half done](Release) | Release | v1.0.70 | A merge is refused only for a page the goal's own change made stale, and the pull-request checks catch… | [Release flow](How-to-use-Release#system-diagram) |
| [REL-8 Promotion and waivers are my words](Release) | Release | v0.1.2 | Only the operation session promotes or reverts, and a waiver counts only when its owner record exists… | [Release flow](How-to-use-Release#system-diagram) |
| [DOC-2 The PRD is mine](Documentation) | Documentation | v0.1.2 | Only I mark a page or a requirement Reviewed, in my own recorded words | [Documentation flow](How-to-use-Documentation#system-diagram) |
| [CHK-7 Blockers first](Check-in-and-board) | Check in and board | v1.0.75 | Each item under Needs you says what it holds up and whether it is on the critical path to the next… | [Check in and board flow](How-to-use-Check-in-and-board#system-diagram) |
| [CHK-9 I can answer and steer from my phone or mail](Check-in-and-board) | Check in and board | v1.0.75 | I can answer any question under Needs you by replying to its mail or from my phone, with the same words… | [Check in and board flow](How-to-use-Check-in-and-board#system-diagram) |
