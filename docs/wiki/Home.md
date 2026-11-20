<!-- workflow-docs -->
# agent-workflow-template

The features, how to use each one, the settings and what runs by itself are on the wiki pages below. The sections after the System design are the project's principles, each with the requirements that enforce it, then every requirement by topic and feature.

## What this is

The loop's steps are: ask, frozen goal, worker build in its own worktree, tests, CI and the merge queue, merge, release from a tag, then health and the reviewer, whose findings become the next goal. Everything in the repo is part of one of those steps or keeps them running. Main changes only through a goal's pull request. A goal freezes only when it names a Reviewed requirement and the step of the loop it changes; a goal that serves no step is refused. Done lines never change after the freeze. "What this is" is generated from this text.

## System design

How the loop sits between its owner, its parts and the outside systems it uses; every principle below is judged against it.

![System design, by principle: how many of each principle's requirements are on each feature](system-design-by-principle.svg)

![System design, by feature: how many of each principle's requirements are on each feature](system-design-by-feature.svg)

## 1. Guided: documentation-driven and standard

The principles and requirements are my guardrails and the only part I write, and each one follows a named industry standard, adopted wherever one can run. The agents implement the code, tests and pages from them, so I never deal with implementation details. Nothing is built that a Reviewed requirement doesn't ask for, and tests come from the requirements.

| Requirement | Summary | Follows | Feature | Adoption | Confidence |
|---|---|---|---|---|---|
| [DOC-2 Only I write the principles and requirements; the repo copy is the PRD (absorbs DOC-22, DOC-20, INT-7, INT-2)](Documentation) ([DOC-2 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DOC-2.svg)) | Each principle's sentence, its table and every requirement's text are written only by me. An agent may draft and propose; only my own words make it the text, and only my words mark it Reviewed. Goals never edit Reviewed text while building. A change is a dated, approved revision; old revisions are kept and IDs are never reused. The repo copy is the PRD: an outside document may sync into it but never overrides it, and checks read only the repo. | GitHub CODEOWNERS with required review; OpenGitOps: adapted | Documentation (Docs), Integrations (Other) | 0% |  |
| [DEL-19 Every change is a goal inside the loop, serving a requirement (absorbs DEL-2, DEL-18)](Delivery) ([DEL-19 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DEL-19.svg)) | The loop's steps are: ask, frozen goal, worker build in its own worktree, tests, CI and the merge queue, merge, release from a tag, then health and the reviewer, whose findings become the next goal. Everything in the repo is part of one of those steps or keeps them running. Main changes only through a goal's pull request. A goal freezes only when it names a Reviewed requirement and the step of the loop it changes; a goal that serves no step is refused. Done lines never change after the freeze. "What this is" is generated from this text. | GitHub closing keywords linking a PR to an issue; Conventional Commits 1.0.0: adapted | Delivery (Build loop) | 0% |  |
| [DOC-25 Every page has the same fixed sections, and README and Home match (absorbs DOC-1's page shapes)](Documentation) ([DOC-25 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DOC-25.svg)) | The README and the wiki Home have exactly these sections, in order: What this is, System design, one section per principle, Requirements by feature. Every principle table has the columns shown here, including Adoption and Confidence, and each principle's heading shows both for the whole principle. Health generates the two scores; no one types them. Every wiki page has the sections of its kind. Every requirement row links to its own workflow figure. Generated sections stay current. | markdownlint MD043; Diátaxis; C4 system context diagram: adapted | Documentation (Docs) | 0% |  |
| [DOC-26 Each principle has at most five requirements, each dense and fully covering (new)](Documentation) ([DOC-26 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DOC-26.svg)) | A new need is written into an existing requirement before a new one is added. Health fails a principle with more than five, and a goal that would add a sixth is refused at freeze. | Google re:Work OKR guide, three to five objectives (checked at build): adapted | Documentation (Docs) | 0% |  |
| [DEL-21 Every requirement names what it follows and adopts a standard tool by default, scored (absorbs DOC-24)](Delivery) ([DEL-21 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DEL-21.svg)) | Every requirement names a specific tool, standard or production system, links its source, and gives each one a tag: adopted, adapted or own. General guidance is not a reference. A drop-in tool is used as it is; adapted names the design it copies and why. The adoption score is shown per requirement, per principle and overall. The target is 50%, and I set it. Every goal that adds or rewrites a requirement first checks whether a tool can be adopted. A change that lowers the score needs my words. | MADR decision records; OpenSSF Scorecard: adapted | Delivery (Build loop), Documentation (Docs), Health (Quality) | 0% |  |

Adoption: 0% (the average of this principle's rows).

**How it works:** I write or approve the text and nothing else can change it. A goal must name a Reviewed requirement and its step of the loop, or the freeze refuses it. The docs check runs on every pull request and fails wrong sections, a row with no figure, a sixth row, or scores that differ from health's latest run.

## 2. Sensed: enforced, verified and honest

Every principle and requirement is enforced by the loop's own machinery, and everything the loop says is verified. Tests, health, CI, the merge queue, the routines and a fresh-context reviewer check each one. Every claim carries its evidence and clock time. Every ETA is a commitment, and a miss stays recorded with its cause. Whatever falls short becomes tracked work until it is fixed.

| Requirement | Summary | Follows | Feature | Adoption | Confidence |
|---|---|---|---|---|---|
| [REG-4 Every requirement has its tests, written and run one way, with honest results (absorbs REG-1, REG-9 and their folded rows)](Regression) ([REG-4 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/REG-4.svg)) | Every Reviewed requirement, whole flow and fixed issue has its kind of test: requirement, flow or defect. A requirement with no passing test shows "not enforced". One format, and one command runs them everywhere. **The table has one row per test script and requirement, and at most 600 rows**; a row runs every case of its script for that requirement. A test counts as proven only after it was seen failing. A flaky test is marked, never silently retried. A fix leaves a defect test behind. Coverage comes from main's full run and never drops silently. | Gherkin; Nx `affected`; Google flaky-test handling: adapted | Regression (Quality), Documentation (Docs) | 0% |  |
| [HLT-2 Health checks every rule, every principle and every page (absorbs HLT-1, DOC-13, HLT-3, HLT-6, GRD-9, HLT-13, GRD-1, DOC-1's checks)](Health) ([HLT-2 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/HLT-2.svg)) | Health is deterministic and read-only: twelve fixed rule groups, each rule proven able to fire, one report with a verdict per principle; what it couldn't read is never shown green. It checks each page's template, each principle's row count, every requirement's reference and tag, and every claim, ETA and correction. The scheduled health routine computes the Adoption and Confidence scores, and the docs render writes them into the tables. A fresh-context reviewer is a gate, not a report: it checks the live operation on a fixed cadence, every plan before build, and every report that claims done. | OpenSSF Scorecard; Open Policy Agent; IEEE 1012 independent verification: adapted | Health (Quality), Documentation (Docs), Guardrails (Quality), Operation (Build loop) | 0% |  |
| [HLT-4 Every finding is one tracked issue until settled (absorbs REG-5, DEL-14, HLT-5, HLT-8, HLT-9, HLT-10, HLT-12)](Health) ([HLT-4 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/HLT-4.svg)) | Each finding, failing test and unfixed goal finding is one evidenced issue on its feature's Backlog milestone, triaged with my words and planned into goals. A wrong statement, a missed ETA or a skipped gate is a finding too: corrected where it was made, logged with what was said, what was true, the cause and the action. Health counts them. | GitHub Issues and milestones; Google SRE postmortem action items: adopted | Health (Quality), Regression (Quality), Delivery (Build loop) | 100% |  |
| [DEL-1 One sentence runs unattended to a release, and a major ships only through the gate (absorbs DEL-4, REL-9 to REL-11, REL-14, REL-3 and its folded rows)](Delivery) ([DEL-1 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DEL-1.svg)) | A sentence and its done lines run unattended to a recorded pull request and a release made from a tag. A merge is refused only for the goal's own findings, never left half done. A major exists only after the gate: milestone closed, full suite run, health green, everything Reviewed. Promotion and revert need the operation session and my words. | GitHub merge queue, tag release workflow, Semantic Versioning: adopted; SonarQube quality gates: adapted; the sentence-to-PR pipeline: own | Delivery (Build loop), Release (Other) | 33% |  |
| [AUT-1 Routines run on schedule, by runbook (absorbs AUT-2, AUT-3, DOC-16)](Automation) ([AUT-1 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/AUT-1.svg)) | Health and regression run on schedule wherever they can run fully. They report where they ran and what they skipped, catch up missed runs, and follow runbooks. | GitHub Actions `schedule`: adopted; Google SRE on-call playbooks: adapted | Automation (Operations), Documentation (Docs) | 50% |  |

Adoption: 37% (the average of this principle's rows).

**How it works:** every pull request runs its affected tests in CI. The merge queue runs a fixed smoke on the merged result before main moves; it took 11 seconds on its first run at 03:17 (the Mac's reading). Health runs on schedule and before every release, opens one issue per finding, and writes the scores. The reviewer runs every 15 minutes and on every plan and done claim.

## 3. Fast, cheap and small

Every change runs on one clock from my ask to main, with a limit and a token budget for each step, and sizes stay inside their limits.

| Requirement | Summary | Follows | Feature | Adoption | Confidence |
|---|---|---|---|---|---|
| [DEL-17 Every change runs on one clock, from my ask to main (absorbs REG-7, GRD-7, GRD-8, REL-13, REL-15)](Delivery) ([DEL-17 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DEL-17.svg)) | **Normal goal:** freeze to build takes the goal's own ETA; then one local lane (5 minutes, only the tests the change reaches, reused by later steps), push and PR CI (5 minutes, one run per push, parallel jobs), and ready to main (5 minutes: the merge queue tests the merged result, merges, and the release is made from a tag). **Small fix:** 2 minutes to edit and push, 2 for the lane, 3 for CI, 3 for the queue: 10 minutes from my ask. **Tokens:** each step has a budget from its measured usual; past twice that it is flagged; waiting is done in a script. **Every ETA is a commitment:** it records who made it, when, and on what basis; a passed one shows as missed with its cause and stays visible. A merge never makes another ready pull request re-run. Test count and suite time stay capped. | GitHub merge queue: adopted; DORA lead time: adapted | Delivery (Build loop), Regression (Quality), Release (Other), Guardrails (Quality) | 50% |  |
| [HLT-7 Checks, check-ins and instructions answer fast](Health) ([HLT-7 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/HLT-7.svg)) | Health under 60 seconds, docs under 30, the board under 10, rounds under 45 minutes. A worker's turn ends at least every 5 minutes, so an instruction reaches it within 5. | DORA four keys: adapted | Health (Quality), Check in and board (Build loop), Operation (Build loop) | 0% |  |
| [GRD-20 Sizes are one table, enforced on main, never met by reformatting (absorbs HLT-11)](Guardrails) ([GRD-20 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/GRD-20.svg)) | One table holds every size limit: Agensi's package rules, kept as they are; scripts warn at 19,000 bytes and fail at 20,000; pages, requirements per page, test rows and file count. No script on main is over its fail line. Reformatting a whole file only to fit is refused. | Agensi packaging rules: adopted; ESLint `max-lines`: adapted | Guardrails (Quality), Health (Quality) | 50% |  |
| [OPS-16 Every ready goal starts within capacity limits](Operation) ([OPS-16 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/OPS-16.svg)) | Every ready goal gets its own worker at once unless a capacity limit holds it. The memory floor is measured per machine. | Kubernetes ResourceQuota; Kanban WIP limits: adapted | Operation (Build loop), Guardrails (Quality) | 0% |  |

Adoption: 25% (the average of this principle's rows).

**How it works:** the merge queue enforces "ready to main" today: four merges tonight took between 50 seconds and 2 min 39 s. The 5-minute CI is being built now. Health prints each step's time and tokens for the last 20 changes and fails a step over its limit.

## 4. Private and guarded

No private name, path, address or key leaves the machine, and automation gets only the access it needs.

| Requirement | Summary | Follows | Feature | Adoption | Confidence |
|---|---|---|---|---|---|
| [DEL-9 Nothing private is committed, shipped or copied (absorbs GRD-3, AUT-6, MCH-9)](Delivery) ([DEL-9 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DEL-9.svg)) | Every commit, push and pull request passes the scoped private-name scan. Private files, the mail address and keys stay local and are never copied. | gitleaks; GitHub push protection; GitGuardian on the organization: adopted | Delivery (Build loop), Guardrails (Quality), Automation (Operations), Machines (Operations) | 100% |  |
| [GRD-4 Every session and automation gets least access (absorbs OPS-7, AUT-9, MCH-11, MCH-6)](Guardrails) ([GRD-4 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/GRD-4.svg)) | A worker touches only its own goal's state and cannot widen its files or budget, or resume itself. Check-ins never edit, commit or push. Each routine declares allow and deny rules and keeps its prompt locally. | GitHub Actions `permissions`: adopted; NIST SP 800-53 AC-6, Kubernetes RBAC: adapted | Guardrails (Quality), Operation (Build loop), Automation (Operations), Machines (Operations) | 50% |  |
| [GRD-5 Nothing is written outside without explicit say (absorbs INT-4)](Guardrails) ([GRD-5 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/GRD-5.svg)) | GitHub writes preview by default and need `--live`. Integrations read by default and write only behind a switch and an accepted delta. I attach connectors myself. | GitHub environments with required reviewers: adapted | Guardrails (Quality), Integrations (Other) | 0% |  |
| [GRD-6 Base branch and hooks cannot be bypassed (absorbs GRD-16)](Guardrails) ([GRD-6 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/GRD-6.svg)) | The base branch refuses direct and force pushes and merges only through the merge queue on required checks, with no bypass. Hook-skipping commits are refused and flagged. | GitHub rulesets with merge queue and required checks; pre-commit: adopted | Guardrails (Quality) | 100% |  |

Adoption: 62% (the average of this principle's rows).

**How it works:** GitHub enforces these, not our code. The ruleset "Main" refuses direct pushes, and GitGuardian and push protection scan every push. The private-name scan runs in the pre-commit hook and in CI.

## 5. Reproducible, portable and adoptable

The same inputs give the same result on any machine, in any repo and on any agent. Any repo adopts the template cleanly, plugs into other systems through adapters, and survives a failure without losing work.

| Requirement | Summary | Follows | Feature | Adoption | Confidence |
|---|---|---|---|---|---|
| [SET-10 One versioned package; every agent runs one loop (absorbs DEL-16, SET-3)](Setup) ([SET-10 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/SET-10.svg)) | One versioned skills package works out of the box in Claude Code and Codex. Steps map to agents, with a warned fallback and recorded tokens. | Semantic Versioning 2.0.0; Agent Skills format: adopted | Setup (Operations), Delivery (Build loop) | 100% |  |
| [MCH-1 Any machine sets up identically, and work moves between them safely (absorbs MCH-2, MCH-10, MCH-7, DEL-12, GRD-18, MCH-4, MCH-8, OPS-15, DEL-7, MCH-3)](Machines) ([MCH-1 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/MCH-1.svg)) | A fresh clone, the checklist, a dry run and an apply reach a working operation session on a Mac or on Windows. Each goal has one owning machine; handover and adoption move it safely. Failed steps retry three times and then stop with a reason; crashed goals resume. Backup and restore move state, never secrets. | Dev Containers; chezmoi; Kubernetes Lease; Temporal durable execution: adapted | Machines (Operations), Delivery (Build loop), Guardrails (Quality), Operation (Build loop) | 0% |  |
| [SET-1 Any repo adopts the template, stays current, and is proven by replay (absorbs SET-4, SET-6 and their folded rows)](Setup) ([SET-1 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/SET-1.svg)) | One safe, idempotent command adopts any repo byte for byte. Adopted repos hold only their own data, record their template version, take updates, flag lag, and send fixes upstream. Adoption is proven by a step-by-step replay against the golden result. | Copier; GitHub template repositories; Renovate; Jest snapshots: adapted | Setup (Operations), Guardrails (Quality) | 0% |  |
| [SET-2 Layered settings and a generated entry page (absorbs SET-5)](Setup) ([SET-2 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/SET-2.svg)) | Settings come in layers (template, repo, private), each with a default and an explanation. Every repo has one entry page generated from committed settings only, and two pull requests that each change a setting do not conflict in it. | Twelve-Factor App, factor III Config: adapted | Setup (Operations) | 0% |  |
| [INT-1 Every integration is a declared, visible adapter (absorbs INT-6, INT-5)](Integrations) ([INT-1 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/INT-1.svg)) | Outside systems are opt-in integrations in one registry, added as adapters without changes to the loop's code, with state and deltas shown and counted. | Model Context Protocol: adopted | Integrations (Other) | 100% |  |

Adoption: 40% (the average of this principle's rows).

**How it works:** the package is one versioned zip that update.py installs the same way on any machine. Adoption is one command, proven by the replay tests in CI.

## 6. Autonomous and human-friendly

It runs by itself across machines and stops for me only when a decision is truly mine. At any moment I can see where everything stands, on one board and in one check-in layout, in plain words that read on a phone. When it needs me, it asks one clear question with a recommendation.

| Requirement | Summary | Follows | Feature | Adoption | Confidence |
|---|---|---|---|---|---|
| [DEL-3 It stops only for decisions that are mine, and asks them clearly (absorbs OPS-11, OPS-18, REL-12, AUT-10)](Delivery) ([DEL-3 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/DEL-3.svg)) | My decisions wait for me or are auto-approved where allowed. Full auto applies everything except the safety classes. Merges wait only on gates I set. Every question to me is one decision in plain words, with a recommendation, the exact words or button that answers it, and what happens if I don't answer. Questions are numbered and never asked twice. What was decided for me is listed. | GitHub auto-merge with required checks: adopted; GitHub environments required reviewers: adapted | Delivery (Build loop), Operation (Build loop), Release (Other), Automation (Operations) | 50% |  |
| [CHK-1 One live board and one check-in layout show where everything stands (absorbs CHK-2, CHK-5, CHK-6, MCH-5, CHK-3, CHK-9, AUT-4)](Check-in-and-board) ([CHK-1 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/CHK-1.svg)) | **The board** has these sections, in order, each collapsible: Your move (only my items); Red team (bottlenecks now, planning suggestions with taken or why not, the biggest risk, a verdict per principle); Release goals (short: one line, one bar, an ETA, at most five steps); Task queue (every open task by expected time on main, with a state and whose ETA it is); Workers; Shipped. **Every item is a card;** no tables and no plain lists. **The check-in** follows the same order and opens with what slipped. Text is plain and reads on a phone. Every claim carries what it was read from and its clock time. One email stream, which I answer by reply. | GitHub Projects; PagerDuty: own today, both marked "replace" | Check in and board (Build loop), Machines (Operations), Automation (Operations) | 0% |  |
| [OPS-1 One operation session governs the loop for me (absorbs OPS-2, OPS-6, OPS-8, OPS-10, OPS-23, CHK-7)](Operation) ([OPS-1 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/OPS-1.svg)) | **Layers:** top, one session per machine, workers; top only governs. **Relay:** my words go to the machines word for word, on fixed message forms; a machine's message is never my approval. **Full auto:** top decides process choices and numbers each decision; the safety classes wait for my typed words. **Red team:** every 15 minutes a fresh reviewer reports the bottlenecks, planning suggestions and the biggest risk; top verifies each, changes the plan or writes why not, and shows it all on the board. **Active:** top acts at once on a green pull request left unmerged, a stuck head, an idle worker or a stale STATUS. **Delays:** every wait has a named cause and an owner; every limit that can pause a session is counted. **Setup:** one command starts it from files in the repo, the same way on any machine. | Kubernetes controller reconcile loop; Google SRE incident command: adapted | Operation (Build loop), Check in and board (Build loop) | 0% |  |
| [AUT-5 Routines and publishing stay under my control (absorbs DOC-11)](Automation) ([AUT-5 flow](https://github.com/jcl2018/agent-workflow-template/blob/main/docs/wiki/flows/AUT-5.svg)) | Each routine turns off or reschedules with one setting and writes nothing without secrets. Publishing never deletes or overwrites pages it didn't write, and it can be undone. | GitHub environments with required reviewers: own today, marked "replace" | Automation (Operations), Documentation (Docs) | 0% |  |

Adoption: 12% (the average of this principle's rows).

**How it works:** the operation session reads every machine each check-in and posts the board. Questions reach me only for the safety classes and for overrides of my own requirements. Everything else is decided, logged and listed.

## Requirements by feature

Every requirement with its complete text, grouped by topic and feature (read from each feature's page); a requirement that serves several features is listed under each.

### Build loop

#### Delivery

[How to use Delivery](How-to-use-Delivery)

| Requirement | Complete text |
|---|---|
| [DEL-1 One sentence runs unattended to a release, and a major ships only through the gate](Delivery) | A sentence and its done lines run unattended to a recorded pull request and a release made from a tag. [DEL-1]<br>A merge is refused only for the goal's own findings, never left half done. [DEL-1]<br>A major exists only after the gate: milestone closed, full suite run, health green, everything Reviewed. [DEL-1]<br>Promotion and revert need the operation session and my words. [DEL-1] |
| [DEL-3 It stops only for decisions that are mine, and asks them clearly](Delivery) | My decisions wait for me or are auto-approved where allowed. [DEL-3]<br>Full auto applies everything except the safety classes. [DEL-3]<br>Merges wait only on gates I set. [DEL-3]<br>Every question to me is one decision in plain words, with a recommendation, the exact words or button that answers it, and what happens if I don't answer. [DEL-3]<br>Questions are numbered and never asked twice. [DEL-3]<br>What was decided for me is listed. [DEL-3] |
| [DEL-17 Every change runs on one clock, from my ask to main](Delivery) | **Normal goal:** freeze to build takes the goal's own ETA; then one local lane (5 minutes, only the tests the change reaches, reused by later steps), push and PR CI (5 minutes, one run per push, parallel jobs), and ready to main (5 minutes: the merge queue tests the merged result, merges, and the release is made from a tag). [DEL-17]<br>**Small fix:** 2 minutes to edit and push, 2 for the lane, 3 for CI, 3 for the queue: 10 minutes from my ask. [DEL-17]<br>**Tokens:** each step has a budget from its measured usual; past twice that it is flagged; waiting is done in a script. [DEL-17]<br>**Every ETA is a commitment:** it records who made it, when, and on what basis; a passed one shows as missed with its cause and stays visible. [DEL-17]<br>A merge never makes another ready pull request re-run. [DEL-17]<br>Test count and suite time stay capped. [DEL-17] |
| [DEL-19 Every change is a goal inside the loop, serving a requirement](Delivery) | The loop's steps are: ask, frozen goal, worker build in its own worktree, tests, CI and the merge queue, merge, release from a tag, then health and the reviewer, whose findings become the next goal. [DEL-19]<br>Everything in the repo is part of one of those steps or keeps them running. [DEL-19]<br>Main changes only through a goal's pull request. [DEL-19]<br>A goal freezes only when it names a Reviewed requirement and the step of the loop it changes; a goal that serves no step is refused. [DEL-19]<br>Done lines never change after the freeze. [DEL-19]<br>"What this is" is generated from this text. [DEL-19] |
| [DEL-21 Every requirement names what it follows and adopts a standard tool by default, scored](Delivery) | Every requirement names a specific tool, standard or production system, links its source, and gives each one a tag: adopted, adapted or own. [DEL-21]<br>General guidance is not a reference. [DEL-21]<br>A drop-in tool is used as it is; adapted names the design it copies and why. [DEL-21]<br>The adoption score is shown per requirement, per principle and overall. [DEL-21]<br>The target is 50%, and I set it. [DEL-21]<br>Every goal that adds or rewrites a requirement first checks whether a tool can be adopted. [DEL-21]<br>A change that lowers the score needs my words. [DEL-21] |
| [DEL-9 Nothing private is committed, shipped or copied](Delivery) | Every commit, push and pull request passes the scoped private-name scan. [DEL-9]<br>Private files, the mail address and keys stay local and are never copied. [DEL-9] |

#### Operation

[How to use Operation](How-to-use-Operation)

| Requirement | Complete text |
|---|---|
| [OPS-1 One operation session governs the loop for me](Operation) | **Layers:** top, one session per machine, workers; top only governs. [OPS-1]<br>**Relay:** my words go to the machines word for word, on fixed message forms; a machine's message is never my approval. [OPS-1]<br>**Full auto:** top decides process choices and numbers each decision; the safety classes wait for my typed words. [OPS-1]<br>**Red team:** every 15 minutes a fresh reviewer reports the bottlenecks, planning suggestions and the biggest risk; top verifies each, changes the plan or writes why not, and shows it all on the board. [OPS-1]<br>**Active:** top acts at once on a green pull request left unmerged, a stuck head, an idle worker or a stale STATUS. [OPS-1]<br>**Delays:** every wait has a named cause and an owner; every limit that can pause a session is counted. [OPS-1]<br>**Setup:** one command starts it from files in the repo, the same way on any machine. [OPS-1] |
| [OPS-2 Live communication on a fixed protocol](Operation) | A worker reports each change of step or status as it happens, and its result when it ends; the operation session sends a worker its answer or a follow-up. [OPS-2]<br>Background processes are used only when a session can't be started or reached, and the board says so. [OPS-2]<br>Messages and fields. STATUS (machine to top, on change and every 30 minutes) carries main per repo, PR numbers, running, parked and idle sessions with reasons, and worker lines; PR per goal; merges; needs-owner with the exact words to answer and a recommendation. ASK, OWNER-WORDS and PRIORITY go between top and machine; MERGE-REQUEST and MERGE-GO go machine to machine, copied to top. A worker never talks to top or to another machine. [OPS-2]<br>(v2.0 planned) Any limit that can pause a session's messages is counted and reported with every STATUS (used, remaining, what resets it); from three quarters used the session says so first; a capped session keeps working and sends its log after the reset. [OPS-2] |
| [OPS-16 Every ready goal starts within capacity limits](Operation) | Every ready goal gets its own worker at once unless a capacity limit holds it. [OPS-16]<br>The memory floor is measured per machine. [OPS-16] |

#### Check in and board

[How to use Check in and board](How-to-use-Check-in-and-board)

| Requirement | Complete text |
|---|---|
| [CHK-1 One live board and one check-in layout show where everything stands](Check-in-and-board) | **The board** has these sections, in order, each collapsible: Your move (only my items); Red team (bottlenecks now, planning suggestions with taken or why not, the biggest risk, a verdict per principle); Release goals (short: one line, one bar, an ETA, at most five steps); Task queue (every open task by expected time on main, with a state and whose ETA it is); Workers; Shipped. [CHK-1]<br>**Every item is a card;** no tables and no plain lists. [CHK-1]<br>**The check-in** follows the same order and opens with what slipped. [CHK-1]<br>Text is plain and reads on a phone. [CHK-1]<br>Every claim carries what it was read from and its clock time. [CHK-1]<br>One email stream, which I answer by reply. [CHK-1] |

### Quality

#### Regression

[How to use Regression](How-to-use-Regression)

| Requirement | Complete text |
|---|---|
| [REG-4 Every requirement has its tests, written and run one way, with honest results](Regression) | Every Reviewed requirement, whole flow and fixed issue has its kind of test: requirement, flow or defect. [REG-4]<br>A requirement with no passing test shows "not enforced". [REG-4]<br>One format, and one command runs them everywhere. [REG-4]<br>**The table has one row per test script and requirement, and at most 600 rows**; a row runs every case of its script for that requirement. [REG-4]<br>A test counts as proven only after it was seen failing. [REG-4]<br>A flaky test is marked, never silently retried. [REG-4]<br>A fix leaves a defect test behind. [REG-4]<br>Coverage comes from main's full run and never drops silently. [REG-4] |

#### Health

[How to use Health](How-to-use-Health)

| Requirement | Complete text |
|---|---|
| [HLT-2 Health checks every rule, every principle and every page](Health) | Health is deterministic and read-only: twelve fixed rule groups, each rule proven able to fire, one report with a verdict per principle; what it couldn't read is never shown green. [HLT-2]<br>It checks each page's template, each principle's row count, every requirement's reference and tag, and every claim, ETA and correction. [HLT-2]<br>The scheduled health routine computes the Adoption and Confidence scores, and the docs render writes them into the tables. [HLT-2]<br>A fresh-context reviewer is a gate, not a report: it checks the live operation on a fixed cadence, every plan before build, and every report that claims done. [HLT-2] |
| [HLT-4 Every finding is one tracked issue until settled](Health) | Each finding, failing test and unfixed goal finding is one evidenced issue on its feature's Backlog milestone, triaged with my words and planned into goals. [HLT-4]<br>A wrong statement, a missed ETA or a skipped gate is a finding too: corrected where it was made, logged with what was said, what was true, the cause and the action. [HLT-4]<br>Health counts them. [HLT-4] |
| [HLT-7 Checks, check-ins and instructions answer fast](Health) | Health under 60 seconds, docs under 30, the board under 10, rounds under 45 minutes. [HLT-7]<br>A worker's turn ends at least every 5 minutes, so an instruction reaches it within 5. [HLT-7] |

#### Guardrails

[How to use Guardrails](How-to-use-Guardrails)

| Requirement | Complete text |
|---|---|
| [GRD-4 Every session and automation gets least access](Guardrails) | A worker touches only its own goal's state and cannot widen its files or budget, or resume itself. [GRD-4]<br>Check-ins never edit, commit or push. [GRD-4]<br>Each routine declares allow and deny rules and keeps its prompt locally. [GRD-4] |
| [GRD-5 Nothing is written outside without explicit say](Guardrails) | GitHub writes preview by default and need `--live`. [GRD-5]<br>Integrations read by default and write only behind a switch and an accepted delta. [GRD-5]<br>I attach connectors myself. [GRD-5] |
| [GRD-6 Base branch and hooks cannot be bypassed](Guardrails) | The base branch refuses direct and force pushes and merges only through the merge queue on required checks, with no bypass. [GRD-6]<br>Hook-skipping commits are refused and flagged. [GRD-6] |
| [GRD-20 Sizes are one table, enforced on main, never met by reformatting](Guardrails) | One table holds every size limit: Agensi's package rules, kept as they are; scripts warn at 19,000 bytes and fail at 20,000; pages, requirements per page, test rows and file count. [GRD-20]<br>No script on main is over its fail line. [GRD-20]<br>Reformatting a whole file only to fit is refused. [GRD-20] |

### Operations

#### Automation

[How to use Automation](How-to-use-Automation)

| Requirement | Complete text |
|---|---|
| [AUT-1 Routines run on schedule, by runbook](Automation) | Health and regression run on schedule wherever they can run fully. [AUT-1]<br>They report where they ran and what they skipped, catch up missed runs, and follow runbooks. [AUT-1] |
| [AUT-5 Routines and publishing stay under my control](Automation) | Each routine turns off or reschedules with one setting and writes nothing without secrets. [AUT-5]<br>Publishing never deletes or overwrites pages it didn't write, and it can be undone. [AUT-5] |

#### Setup

[How to use Setup](How-to-use-Setup)

| Requirement | Complete text |
|---|---|
| [SET-1 Any repo adopts the template, stays current, and is proven by replay](Setup) | One safe, idempotent command adopts any repo byte for byte. [SET-1]<br>Adopted repos hold only their own data, record their template version, take updates, flag lag, and send fixes upstream. [SET-1]<br>Adoption is proven by a step-by-step replay against the golden result. [SET-1] |
| [SET-2 Layered settings and a generated entry page](Setup) | Settings come in layers (template, repo, private), each with a default and an explanation. [SET-2]<br>Every repo has one entry page generated from committed settings only, and two pull requests that each change a setting do not conflict in it. [SET-2] |
| [SET-10 One versioned package; every agent runs one loop](Setup) | One versioned skills package works out of the box in Claude Code and Codex. [SET-10]<br>Steps map to agents, with a warned fallback and recorded tokens. [SET-10] |

#### Machines

[How to use Machines](How-to-use-Machines)

| Requirement | Complete text |
|---|---|
| [MCH-1 Any machine sets up identically, and work moves between them safely](Machines) | A fresh clone, the checklist, a dry run and an apply reach a working operation session on a Mac or on Windows. [MCH-1]<br>Each goal has one owning machine; handover and adoption move it safely. [MCH-1]<br>Failed steps retry three times and then stop with a reason; crashed goals resume. [MCH-1]<br>Backup and restore move state, never secrets. [MCH-1] |

### Docs

#### Documentation

[How to use Documentation](How-to-use-Documentation)

| Requirement | Complete text |
|---|---|
| [DOC-1 Every page follows its template and stays checked](Documentation) | One template defines every feature page: Problem written from the user's side, Requirements as ID'd bullets under Functional and Non-functional, Non-goals, Success metrics and a generated Tests table. Nothing else goes on the page except the generated Deployments and Runbook sections. [DOC-1]<br>A feature that ships a page people open or a delivery people receive lists it in a Deployments section: its link or channel, who can open or receives it, what it shows or sends, and its live status. Recipients are named as a group, never an address. [DOC-14]<br>Home carries the same sections as the README, in the same order, and nothing else (DOC-25): the System design, the principles' tables, then every requirement by topic and feature, and each feature's How-to-use link sits under its name. A repo that ships no principle list keeps one features table with four columns: Feature, What it does, How to use and Milestone, and may lead with an optional Topic column. A version milestone stays optional and free form; nothing requires an issue or pull request to have one. [DOC-4]<br>The Setup How-to-use page gives, under How to reach or run it, each setting's name, what it means, how to set it, its default and this repo's value, marked overridden only when it differs from the default. [DOC-15]<br>The Automation How-to-use page gives, under Automations and schedules, each routine on or off, what it does, its cadence in plain words, where it runs, its last run when known (live, from `docs.py automation`, so the page does not change with every run) and any step still owed by the owner; health and regression are built in and a repo adds a routine with one entry in its config, with no code change. [DOC-15]<br>The README names and links the template repo the loop came from, never a local path, and the adoption entry points to all three. The docs check says STALE when a setting, a workflow file or a value changes, and render or publish refreshes them. [DOC-15] entry.py renders START.md from the committed .loop/config.json when a local skip-worktree edit holds the file. [DOC-15]<br>The code that renders the blocks stays readable and under health's size warning: `counting.py` holds the Automation block code and `render.py` the rest, so the text a config renders is the same wherever the code sits (issue 1402). Health and the digest email run on the Mac's local schedule, never in GitHub Actions, so the Automation table owes no health workflow; the digest's keys go in the schedule's mail.env on the Mac, outside git. [DOC-15]<br>The README holds only its title, one link to the wiki Home and the principles in two parts. Part 1 has, for each principle, its one-sentence statement, its diagram and a table with one row per requirement under it: the requirement's ID and title, a summary that names any requirements it absorbs, its feature and topic, the version that introduced it (v2.0 (planned) for work with no requirement ID yet) and its own flow diagram. Part 2 lists every requirement with its complete text, one row each, grouped by topic and then feature, a requirement that serves several features listed under each; everything else it once held is on Home or a How-to-use page. The Principles page shows Part 1. [DOC-23]<br>`docs.py check` fails a README, and a Home in a repo that ships the list, with any other section, a principle sentence that differs by a word from the list health uses (the list in workflow-health's commands reference), a table with other columns, a requirement that appears in no row of Part 2, a Part 2 row with no text, a cited requirement that neither exists nor is v2.0 planned, a Flow link that points to no existing diagram file, and on Home a feature with no How-to-use link; a repo that adopts the template shows the template's principles as written, plus its own product principles if it has any. [DOC-23]<br>Every feature has a How-to-use page `docs/wiki/How-to-use-<Feature>.md`, titled "# How to use <Feature>", with these sections in order, leaving out any that do not apply: What it's for, How to reach or run it, URLs and deployments, Automations and schedules, Runbooks, Links (the PRD page and "Backlog: <Feature>"). The feature page links it in one line in its head, between its title and its first section: "How to use: [How-to-use-<Feature>](How-to-use-<Feature>)", and nothing else may sit there. A routine's runbook may sit under "Runbooks" on this page instead of the PRD. [DOC-18]<br>`docs.py check` reports a feature page with no How-to-use page, one off that skeleton, or a feature page that does not link it (a page whose PRD is a link needs no link line); a How-to-use page has no `.loop/docs.tsv` row of its own and is mapped to its feature's paths, so it goes stale and publishes with it, and `audit.py restamp` re-stamps a stale one whose text is as committed; one whose feature has no page is an orphan, reported unmapped. [DOC-18]<br>Home links each feature's How-to-use page, and the README holds only the principles and the requirements by topic and feature (the README rule above); what to say, and any URLs, deployments and schedules, live on the How-to-use page. [DOC-18]<br>Each How-to-use page has one item for every functional requirement of its feature, showing how it is delivered: a command and its output, an example, or a file or page it produces. The docs check fails a missing or unknown item. [DOC-19]<br>A repo's own published sites (listed in `scripts/public-origins.json` or as `public_origins` in `.loop/config.json`) and its README count as inside the repo: a page may link to them, and the docs check and the merge's wiki check do not report them. [DOC-19]<br>Each skill's command map names every command, and its command reference gives each command's exact syntax, what it prints on success, and each refusal with its message and exit code. [DOC-6]<br>A change to code or settings a page describes never needs my words when none of the page's own text changed, and a comments-only change doesn't make the page stale. [DOC-21]<br>Conflict note: the DOC-23 rule that an adopting repo keeps its own README is resolved by the owner (2026-11-19): an adopted repo's README shows the template's principles as written, byte for byte, plus its own product principles if it has any (see SET-1, principle 5). [DOC-23] |
| [DOC-2 Only I write the principles and requirements; the repo copy is the PRD](Documentation) | Each principle's sentence, its table and every requirement's text are written only by me. [DOC-2]<br>An agent may draft and propose; only my own words make it the text, and only my words mark it Reviewed. [DOC-2]<br>Goals never edit Reviewed text while building. [DOC-2]<br>A change is a dated, approved revision; old revisions are kept and IDs are never reused. [DOC-2]<br>The repo copy is the PRD: an outside document may sync into it but never overrides it, and checks read only the repo. [DOC-2] |
| [DOC-24 Every requirement names what it follows](Documentation) | Every requirement names what it follows: a specific tool, published standard or production system with a proven record, a link to its source, and a verdict, adopted or adapted. General guidance is not a reference. [DOC-24] |
| [DOC-25 Every page has the same fixed sections, and README and Home match](Documentation) | The README and the wiki Home have exactly these sections, in order: What this is, System design, one section per principle, Requirements by feature. [DOC-25]<br>Every principle table has the columns shown here, including Adoption and Confidence, and each principle's heading shows both for the whole principle. [DOC-25]<br>Health generates the two scores; no one types them. [DOC-25]<br>Every wiki page has the sections of its kind. [DOC-25]<br>Every requirement row links to its own workflow figure. [DOC-25]<br>Generated sections stay current. [DOC-25] |
| [DOC-26 Each principle has at most five requirements, each dense and fully covering](Documentation) | A new need is written into an existing requirement before a new one is added. [DOC-26]<br>Health fails a principle with more than five, and a goal that would add a sixth is refused at freeze. [DOC-26] |

### Other

#### Integrations

[How to use Integrations](How-to-use-Integrations)

| Requirement | Complete text |
|---|---|
| [INT-1 Every integration is a declared, visible adapter](Integrations) | Outside systems are opt-in integrations in one registry, added as adapters without changes to the loop's code, with state and deltas shown and counted. [INT-1] |

#### Release

[How to use Release](How-to-use-Release)

| Requirement | Complete text |
|---|---|
| [REL-15 A ready pull request is on main within 5 minutes](Release) | From the moment a pull request is ready (reviewed, its own checks green on its head) to its commit on main takes 5 minutes or less, and a merge of one pull request never makes another ready one re-run its lane or CI. [REL-15]<br>The affected run on the pull request's head counts for the rest of the checks: the merge_group run is a fixed small tier that finishes within 5 minutes, and a pushed pull-request branch starts one CI run, not two. The wiki publish after the merge is outside the 5 minutes. [REL-15]<br>With the merge_queue setting on, merge.py leaves a moved base to GitHub's merge queue, and prints MERGED only after gh reports the pull request merged; with it off the moved-base refusal is unchanged. [REL-15]<br>(v2.0 planned) Health prints the median and slowest of the last 20 merges and fails one over 5 minutes. [REL-15] |
