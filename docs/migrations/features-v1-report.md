# Feature migration report (features-v1)

Written by `docs/migrations/features-v1.py run`; it holds no run date, so a re-run writes the same bytes.

## Features

| ID | Page | Text hash before | Text hash after | Lines | Metric | Test rows | Reference |
|---|---|---|---|---|---|---|---|
| AUT-1 | Automation | 9a051430018d | 9a051430018d | 2 | missing | 12 | GitHub Actions `schedule`: adopted; Google SRE on-call playbooks: adapted |
| AUT-5 | Automation | 65c39feec341 | 65c39feec341 | 2 | missing | 4 | GitHub environments with required reviewers: own |
| CHK-1 | Check-in-and-board | 150673e5b449 | 150673e5b449 | 8 | missing | 39 | GitHub Projects: own; PagerDuty: own |
| DEL-1 | Delivery | 248f04935abe | 248f04935abe | 4 | missing | 27 | GitHub merge queue, tag release workflow, Semantic Versioning: adopted; SonarQube quality gates: adapted; the sentence-to-PR pipeline: own |
| DEL-3 | Delivery | 3b27fdd3bca7 | 3b27fdd3bca7 | 6 | missing | 10 | GitHub auto-merge with required checks: adopted; GitHub environments required reviewers: adapted |
| DEL-17 | Delivery | 896e67888270 | 896e67888270 | 7 | missing | 23 | GitHub merge queue: adopted; DORA lead time: adapted |
| DEL-19 | Delivery | 5a4ac9d17f0f | 5a4ac9d17f0f | 6 | missing | 5 | GitHub closing keywords linking a PR to an issue: adapted; Conventional Commits 1.0.0: adapted |
| DEL-21 | Delivery | ef308e97f103 | ef308e97f103 | 7 | missing | 1 | MADR decision records: adapted; OpenSSF Scorecard: adapted |
| DEL-9 | Delivery | 0dc04849af9b | 0dc04849af9b | 2 | missing | 11 | gitleaks: adopted; GitHub push protection: adopted; GitGuardian on the organization: adopted |
| DOC-2 | Documentation | 9f2097eacc80 | 9f2097eacc80 | 5 | missing | 13 | GitHub CODEOWNERS with required review: adapted; OpenGitOps: adapted |
| DOC-25 | Documentation | 46d994b01e19 | 46d994b01e19 | 6 | missing | 32 | markdownlint MD043: adapted; Diátaxis: adapted; C4 system context diagram: adapted |
| DOC-26 | Documentation | af57ae9a117d | af57ae9a117d | 2 | missing | 0 | Google re:Work OKR guide, three to five objectives (checked at build): adapted |
| GRD-4 | Guardrails | f512fc7a24be | f512fc7a24be | 3 | missing | 12 | GitHub Actions `permissions`: adopted; NIST SP 800-53 AC-6, Kubernetes RBAC: adapted |
| GRD-5 | Guardrails | 7768a462623a | 7768a462623a | 3 | missing | 3 | GitHub environments with required reviewers: adapted |
| GRD-6 | Guardrails | f10526d8f8e2 | f10526d8f8e2 | 2 | missing | 1 | GitHub rulesets with merge queue and required checks: adopted; pre-commit: adopted |
| GRD-20 | Guardrails | 63506cf642c1 | 63506cf642c1 | 3 | missing | 1 | Agensi packaging rules: adopted; ESLint `max-lines`: adapted |
| HLT-2 | Health | ef3237d01be5 | ef3237d01be5 | 5 | missing | 28 | OpenSSF Scorecard: adapted; Open Policy Agent: adapted; IEEE 1012 independent verification: adapted; GitHub required status checks: adopted |
| HLT-4 | Health | 96107e281663 | 96107e281663 | 3 | missing | 17 | GitHub Issues and milestones: adopted; Google SRE postmortem action items: adopted |
| HLT-7 | Health | 4d5ccf9b3760 | 4d5ccf9b3760 | 2 | missing | 5 | DORA four keys: adapted |
| INT-1 | Integrations | 3c5b7f190b14 | 3c5b7f190b14 | 1 | missing | 0 | Model Context Protocol: adopted |
| MCH-1 | Machines | f19da8fbac3a | f19da8fbac3a | 5 | missing | 27 | Dev Containers: adapted; chezmoi: adapted; Kubernetes Lease: adapted; Temporal durable execution: adapted; macOS launchd; Claude Code cloud sessions: adopted |
| OPS-1 | Operation | ab9cf90ec303 | ab9cf90ec303 | 13 | missing | 18 | Kubernetes controller reconcile loop: adapted; Google SRE incident command: adapted |
| OPS-16 | Operation | 1dd4088f2cee | 1dd4088f2cee | 8 | missing | 5 | Kubernetes ResourceQuota: adapted; Kanban WIP limits: adapted |
| REG-4 | Regression | 1d032279ba83 | 1d032279ba83 | 9 | missing | 49 | Gherkin: adapted; Nx `affected`: adapted; Google flaky-test handling; pytest `xfail(strict=True)`: adapted |
| SET-1 | Setup | 73ee3f3676fc | 73ee3f3676fc | 3 | missing | 19 | Copier: adapted; GitHub template repositories: adapted; Renovate: adapted; Jest snapshots: adapted |
| SET-2 | Setup | eb8b2329764a | eb8b2329764a | 2 | missing | 9 | Twelve-Factor App, factor III Config: adapted |
| SET-10 | Setup | bbe552a4bcce | bbe552a4bcce | 2 | missing | 8 | Semantic Versioning 2.0.0: adopted; Agent Skills format: adopted |

## Old marks cleared

| Kind | Page | ID | Date | Seal or lock | Review-log row (context only, not proof) |
|---|---|---|---|---|---|
| entry | Automation | AUT-1 | 2026-11-20 | 6aac93e4 | 2026-11-20 o617 |
| entry | Automation | AUT-5 | 2026-11-20 | bd5f6128 | 2026-11-20 o632 |
| page | Automation | - | 2026-11-20 | prd P=a45649a4 R=e1b516f0 N=e081872e M=4670eeeb U=03828777 | 2026-11-20 o658 |
| entry | Check-in-and-board | CHK-1 | 2026-11-20 | e1ba8975 | 2026-11-20 o673 |
| entry | Delivery | DEL-1 | 2026-11-20 | 8a6cfd0a | 2026-11-20 o616 |
| entry | Delivery | DEL-3 | 2026-11-20 | e3b04ded | 2026-11-20 o631 |
| entry | Delivery | DEL-17 | 2026-11-20 | 01f97e9e | 2026-11-20 o672 |
| entry | Delivery | DEL-19 | 2026-11-20 | 24b6865a | 2026-11-20 o614 |
| entry | Delivery | DEL-21 | 2026-11-20 | b530df14 | 2026-11-20 o634 |
| entry | Delivery | DEL-9 | 2026-11-20 | 753012f1 | 2026-11-20 o622 |
| entry | Documentation | DOC-2 | 2026-11-20 | 22a8ca15 | 2026-11-20 o613 |
| entry | Documentation | DOC-25 | 2026-11-20 | 45ba875e | 2026-11-20 o633 |
| entry | Documentation | DOC-26 | 2026-11-20 | a075bf15 | 2026-11-20 o595 |
| entry | Guardrails | GRD-4 | 2026-11-20 | 9110aaad | 2026-11-20 o623 |
| entry | Guardrails | GRD-5 | 2026-11-20 | f7806e3b | 2026-11-20 o624 |
| entry | Guardrails | GRD-6 | 2026-11-20 | 361f1915 | 2026-11-20 o625 |
| entry | Guardrails | GRD-20 | 2026-11-20 | 2ecb9a54 | 2026-11-20 o655 |
| entry | Health | HLT-2 | 2026-11-20 | 58360fd7 | 2026-11-20 o666 |
| entry | Health | HLT-4 | 2026-11-20 | e97cc230 | 2026-11-20 o636 |
| entry | Health | HLT-7 | 2026-11-20 | 2060d7f7 | 2026-11-20 o619 |
| entry | Integrations | INT-1 | 2026-11-20 | 2f1e2663 | 2026-11-20 o630 |
| entry | Machines | MCH-1 | 2026-11-20 | 5820cfff | 2026-11-20 o666 |
| entry | Operation | OPS-1 | 2026-11-20 | 5ee683ee | 2026-11-20 o653 |
| entry | Operation | OPS-16 | 2026-11-20 | dada51c6 | 2026-11-20 o651 |
| entry | Regression | REG-4 | 2026-11-20 | 05626ff1 | 2026-11-20 o666 |
| page | Regression | - | 2026-11-20 | prd P=14b68802 R=94b657f1 N=f86bd012 M=d4d1a48b U=03828777 | 2026-11-20 o659 |
| entry | Setup | SET-1 | 2026-11-20 | e36ea742 | 2026-11-20 o628 |
| entry | Setup | SET-2 | 2026-11-20 | 129441cc | 2026-11-20 o629 |
| page | Setup | - | 2026-11-20 | prd P=7f1b1066 R=c8e485ef N=9c385754 M=471a58c6 U=03828777 | 2026-11-20 o660 |

## To split (more than five lines)

- OPS-1 (Operation): 13 lines
- REG-4 (Regression): 9 lines
- CHK-1 (Check-in-and-board): 8 lines
- OPS-16 (Operation): 8 lines
- DEL-17 (Delivery): 7 lines
- DEL-21 (Delivery): 7 lines
- DEL-3 (Delivery): 6 lines
- DEL-19 (Delivery): 6 lines
- DOC-25 (Documentation): 6 lines

## Skipped (added in the new format by a later goal)

- DOC-27, DOC-28 (skipped if present; nothing is required if absent, the goal that adds them lands later)

## Totals

- features migrated: 27
- requirement marks cleared: 26
- page-level marks cleared: 3
- features to split: 9
- lines: 121
- lines with metric missing, by line: 121, by ID: 27
- lines with test missing, by line: 3, by ID: 2
- features with reference missing: 0

## Original mark lines (read by the check)

```text
entry	Automation	AUT-1	2026-11-20	6aac93e4	2026-11-20 o617	- AUT-1: **Reviewed 2026-11-20** Routines run on schedule, by runbook <!-- reviewed 6aac93e4 -->
entry	Automation	AUT-5	2026-11-20	bd5f6128	2026-11-20 o632	- AUT-5: **Reviewed 2026-11-20** Routines and publishing stay under my control <!-- reviewed bd5f6128 -->
page	Automation	-	2026-11-20	prd P=a45649a4 R=e1b516f0 N=e081872e M=4670eeeb U=03828777	2026-11-20 o658	Review: **Reviewed 2026-11-20** <!-- prd P=a45649a4 R=e1b516f0 N=e081872e M=4670eeeb U=03828777 --> <!-- kept fast-3min@d0a4c4b38 -->
entry	Check-in-and-board	CHK-1	2026-11-20	e1ba8975	2026-11-20 o673	- CHK-1: **Reviewed 2026-11-20** One live board and one check-in layout show where everything stands <!-- reviewed e1ba8975 -->
entry	Delivery	DEL-1	2026-11-20	8a6cfd0a	2026-11-20 o616	- DEL-1: **Reviewed 2026-11-20** One sentence runs unattended to a release, and a major ships only through the gate <!-- reviewed 8a6cfd0a -->
entry	Delivery	DEL-3	2026-11-20	e3b04ded	2026-11-20 o631	- DEL-3: **Reviewed 2026-11-20** It stops only for decisions that are mine, and asks them clearly <!-- reviewed e3b04ded -->
entry	Delivery	DEL-17	2026-11-20	01f97e9e	2026-11-20 o672	- DEL-17: **Reviewed 2026-11-20** Every change runs on one clock, from my ask to main <!-- reviewed 01f97e9e -->
entry	Delivery	DEL-19	2026-11-20	24b6865a	2026-11-20 o614	- DEL-19: **Reviewed 2026-11-20** Every change is a goal inside the loop, serving a requirement <!-- reviewed 24b6865a -->
entry	Delivery	DEL-21	2026-11-20	b530df14	2026-11-20 o634	- DEL-21: **Reviewed 2026-11-20** Every requirement names what it follows and adopts a standard tool by default, scored <!-- reviewed b530df14 -->
entry	Delivery	DEL-9	2026-11-20	753012f1	2026-11-20 o622	- DEL-9: **Reviewed 2026-11-20** Nothing private is committed, shipped or copied <!-- reviewed 753012f1 -->
entry	Documentation	DOC-2	2026-11-20	22a8ca15	2026-11-20 o613	- DOC-2: **Reviewed 2026-11-20** Only I write the principles and requirements; the repo copy is the PRD <!-- reviewed 22a8ca15 -->
entry	Documentation	DOC-25	2026-11-20	45ba875e	2026-11-20 o633	- DOC-25: **Reviewed 2026-11-20** Every page has the same fixed sections, and README and Home match <!-- reviewed 45ba875e -->
entry	Documentation	DOC-26	2026-11-20	a075bf15	2026-11-20 o595	- DOC-26: **Reviewed 2026-11-20** Each principle has at most five requirements, each dense and fully covering <!-- reviewed a075bf15 -->
entry	Guardrails	GRD-4	2026-11-20	9110aaad	2026-11-20 o623	- GRD-4: **Reviewed 2026-11-20** Every session and automation gets least access <!-- reviewed 9110aaad -->
entry	Guardrails	GRD-5	2026-11-20	f7806e3b	2026-11-20 o624	- GRD-5: **Reviewed 2026-11-20** Nothing is written outside without explicit say <!-- reviewed f7806e3b -->
entry	Guardrails	GRD-6	2026-11-20	361f1915	2026-11-20 o625	- GRD-6: **Reviewed 2026-11-20** Base branch and hooks cannot be bypassed <!-- reviewed 361f1915 -->
entry	Guardrails	GRD-20	2026-11-20	2ecb9a54	2026-11-20 o655	- GRD-20: **Reviewed 2026-11-20** Sizes are one table, enforced on main, never met by reformatting <!-- reviewed 2ecb9a54 -->
entry	Health	HLT-2	2026-11-20	58360fd7	2026-11-20 o666	- HLT-2: **Reviewed 2026-11-20** Health checks every rule, every principle and every page <!-- reviewed 58360fd7 -->
entry	Health	HLT-4	2026-11-20	e97cc230	2026-11-20 o636	- HLT-4: **Reviewed 2026-11-20** Every finding is one tracked issue until settled <!-- reviewed e97cc230 -->
entry	Health	HLT-7	2026-11-20	2060d7f7	2026-11-20 o619	- HLT-7: **Reviewed 2026-11-20** Checks, check-ins and instructions answer fast <!-- reviewed 2060d7f7 -->
entry	Integrations	INT-1	2026-11-20	2f1e2663	2026-11-20 o630	- INT-1: **Reviewed 2026-11-20** Every integration is a declared, visible adapter <!-- reviewed 2f1e2663 -->
entry	Machines	MCH-1	2026-11-20	5820cfff	2026-11-20 o666	- MCH-1: **Reviewed 2026-11-20** Any machine sets up identically, and work moves between them safely <!-- reviewed 5820cfff -->
entry	Operation	OPS-1	2026-11-20	5ee683ee	2026-11-20 o653	- OPS-1: **Reviewed 2026-11-20** One operation session governs the loop for me <!-- reviewed 5ee683ee -->
entry	Operation	OPS-16	2026-11-20	dada51c6	2026-11-20 o651	- OPS-16: **Reviewed 2026-11-20** Every ready goal starts within capacity limits <!-- reviewed dada51c6 -->
entry	Regression	REG-4	2026-11-20	05626ff1	2026-11-20 o666	- REG-4: **Reviewed 2026-11-20** Every requirement has its tests, written and run one way, with honest results <!-- reviewed 05626ff1 -->
page	Regression	-	2026-11-20	prd P=14b68802 R=94b657f1 N=f86bd012 M=d4d1a48b U=03828777	2026-11-20 o659	Review: **Reviewed 2026-11-20** <!-- prd P=14b68802 R=94b657f1 N=f86bd012 M=d4d1a48b U=03828777 -->
entry	Setup	SET-1	2026-11-20	e36ea742	2026-11-20 o628	- SET-1: **Reviewed 2026-11-20** Any repo adopts the template, stays current, and is proven by replay <!-- reviewed e36ea742 -->
entry	Setup	SET-2	2026-11-20	129441cc	2026-11-20 o629	- SET-2: **Reviewed 2026-11-20** Layered settings and a generated entry page <!-- reviewed 129441cc -->
page	Setup	-	2026-11-20	prd P=7f1b1066 R=c8e485ef N=9c385754 M=471a58c6 U=03828777	2026-11-20 o660	Review: **Reviewed 2026-11-20** <!-- prd P=7f1b1066 R=c8e485ef N=9c385754 M=471a58c6 U=03828777 -->
```
