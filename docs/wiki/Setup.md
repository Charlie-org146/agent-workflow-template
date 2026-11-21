<!-- workflow-docs -->
# Setup

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/9

Review: **Reviewed 2026-11-20** <!-- prd P=7f1b1066 R=665f5e1f N=9c385754 M=471a58c6 U=03828777 -->

How to use: [How-to-use-Setup](How-to-use-Setup)

## Problem
- I want this toolset to be a workspace I can drop into any repo, for any agent: one install gives Claude Code, Codex or any agent that reads skills the same loop, docs, monitoring and settings, in the right format for each.
- Adopting a repo should never block: it should look at what is there, borrow what fits, learn from a repo I've already set up, and list what doesn't fit instead of refusing.
- Any new session should see the design logic, the docs and every command at once, and an improvement in one repo, or in the template, should reach the others.

## Requirements

### Functional
- SET-1: **Reviewed 2026-11-21** Any repo adopts the template, stays current, and is proven by replay <!-- reviewed b83b3caa -->
  - One safe, idempotent command adopts any repo byte for byte. [SET-1]
  - Adopted repos hold only their own data, record their template version, take updates, flag lag, and send fixes upstream. [SET-1]
  - Adoption is proven by a step-by-step replay against the golden result. [SET-1]
  - **Updates arrive by themselves:** every repo made from the template or adopting it gets each template release as an automatic pull request that it reviews and merges through its own checks, never by hand. [SET-1]
- SET-2: **Reviewed 2026-11-20** Layered settings and a generated entry page <!-- reviewed 129441cc -->
  - Settings come in layers (template, repo, private), each with a default and an explanation. [SET-2]
  - Every repo has one entry page generated from committed settings only, and two pull requests that each change a setting do not conflict in it. [SET-2]
- SET-10: **Unreviewed** One versioned template; every agent runs one loop
  - **The template is the only way the loop ships:** a GitHub template repository, versioned by its release tags, whose skills work out of the box in Claude Code and Codex in every repo made from it or adopting it. No separate skills package is built or uploaded. [SET-10]
  - Steps map to agents, with a warned fallback and recorded tokens. A private setting maps each step and goal size to an agent profile. [SET-10]

### Non-functional

None

## Non-goals
- It never commits private settings or values.
- An update never overwrites a repo's own config, requirements, docs or local settings.
- It doesn't rewrite a page that has its own sections; that page is listed for a person.

## Success metrics
- One command adopts a fresh or existing repo with no blocking step, and the health check run right after it is green or names every gap with its fix.
- A new session in an adopted repo can name every feature and how to use it from the entry point alone.
- A template update reaches every governed repo without losing any repo setting or page.

## Revisions

### Retired

- SET-11: moved to SET-1
- SET-12: moved to SET-1
- SET-13: moved to OPS-16
- SET-14: moved to SET-1
- SET-15: moved to DEL-9
- SET-16: moved to SET-1
- SET-17: moved to HLT-4
- SET-18: moved to SET-1
- SET-19: moved to SET-1
- SET-20: moved to SET-1
- SET-21: moved to SET-1
- SET-3: moved to SET-10
- SET-4: moved to SET-1
- SET-5: moved to SET-2
- SET-6: moved to SET-1
- SET-7: moved to SET-1
- SET-8: moved to DEL-9
- SET-9: moved to SET-1

### SET-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r6 | 2026-11-21 | Any repo adopts the template, stays current, and is proven by replay <br> One safe, idempotent command adopts any repo byte for byte. [SET-1] <br> Adopted repos hold only their own data, record their template version, take updates, flag lag, and send fixes upstream. [SET-1] <br> Adoption is proven by a step-by-step replay against the golden result. [SET-1] <br> **Updates arrive by themselves:** every repo made from the template or adopting it gets each template release as an automatic pull request that it reviews and merges through its own checks, never by hand. [SET-1] | TD554: the loop ships only as the template (owner o677, item 5 of operation-top's pending folds, as drafted) | o677: "So I'm thinking about making it template only. Add this decision to" |
| r5 | 2026-11-20 | Any repo adopts the template, stays current, and is proven by replay <br> One safe, idempotent command adopts any repo byte for byte. [SET-1] <br> Adopted repos hold only their own data, record their template version, take updates, flag lag, and send fixes upstream. [SET-1] <br> Adoption is proven by a step-by-step replay against the golden result. [SET-1] | readme-six: the owner-approved final README (o514) | o584: "yes build it" |
| r4 | 2026-11-19 | Any repo adopts the template; its own files are adapted <br> Files the template owns install exactly, byte for byte; the repo's own files are adapted, never overwritten. The adopted repo's README shows the template's principles and design logic as written, plus its own product principles if it has any. (Owner rule 2026-11-19, o192; resolves the DOC-23 conflict.) [SET-1] <br> Conflict SET-1 vs SET-7 resolved by the owner, 2026-11-19 (o192). [SET-7] <br> One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. [SET-1] <br> A dry run lists everything before any write; running setup twice changes nothing the second time; nothing of the repo's own is overwritten. [SET-7] <br> Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. [SET-9] <br> Adopting a repo installs every guardrail on the Guardrails page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. [GRD-10] <br> Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. A health check runs before and after, and the one after is green or names each gap with its fix. [SET-18] <br> For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. [SET-14] <br> From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. It ends with the board showing exactly the repos I chose. [SET-12] | consolidation (TOP-DECISION 89): second revision (TOP-DECISIONs 91, 94, 95) | o362: "I want to merge the 2.1 into 2.0 ... (owner ~01:35, o355)" |
| r3 | 2026-11-19 | Any repo adopts the template byte for byte <br> Any repo adopts the template cleanly, byte for byte: every file the template installs matches the template's copy exactly, and the adopted repo's README shows the template's principles and design logic as written, byte for byte, plus its own product principles if it has any. (Owner rule 2026-11-19; resolves the DOC-23 conflict.) [SET-1] <br> Files the template owns install exactly; the repo's own files are adapted, never overwritten. (Owner rule 2026-11-19 01:40, o192; resolves the SET-1 vs SET-7 conflict.) [SET-1] <br> One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. [SET-1] <br> A dry run lists everything before any write; running setup twice changes nothing the second time; nothing of the repo's own is overwritten. [SET-7] <br> Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. [SET-9] <br> Adopting a repo installs every guardrail on the Guardrails page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. [GRD-10] <br> Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. A health check runs before and after, and the one after is green or names each gap with its fix. [SET-18] <br> For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. [SET-14] <br> From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. It ends with the board showing exactly the repos I chose. [SET-12] | consolidation (TOP-DECISION 89) | o316: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | One command adopts a repo <br> One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. <br> It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-13 | One command adopts a repo <br> One command sets up a new or existing repo: the loop config, PRD feature pages in the docs format, the Home table and README How to use, the nightly regression in GitHub Actions, the health groups, and every setting with its default. <br> It shows what it found and would change first, then applies it on a branch through the loop, adapting what is there instead of overwriting. <br> It never blocks: what doesn't fit is listed and filed as issues tagged with the right feature, and the rest is adopted. <br> Health is the first and last step: before adopting, a health check records where the repo starts; after adopting, the full health check (every group, Adoption included) must come back green or name each gap with its fix, and that verdict is the adoption result, because if health works, the rest works. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Layered settings and a generated entry page <br> Settings come in layers (template, repo, private), each with a default and an explanation. [SET-2] <br> Every repo has one entry page generated from committed settings only, and two pull requests that each change a setting do not conflict in it. [SET-2] | readme-six: the owner-approved final README (o514) | o585: "yes build it" |
| r3 | 2026-11-19 | Layered settings and a generated entry page <br> Settings come in three layers: the template's defaults, the repo's committed settings, and my private local settings; a later layer overrides an earlier one. Every setting has a default and a one-line explanation, and I can see each value and its layer. [SET-2] <br> Every adopted repo has one entry page any new session reads first: how the parts fit together, which features exist and how to use them. It is generated from the feature pages and the committed settings only, so it is never stale and never carries one machine's local values. [SET-5] | consolidation (TOP-DECISION 89) | o330: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Layered settings <br> Settings come in three layers: the template's defaults, the repo's committed settings, and my private local settings; a later layer overrides an earlier one. <br> Every setting has a default and a one-line explanation, and I can see each value and its layer. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-10 | Layered settings <br> Settings come in three layers: the template's defaults, the repo's settings (committed and shared), and my local settings (private, outside the repo); a later layer overrides an earlier one. <br> Every setting has a default and a one-line explanation; I can see each setting's value and which layer it came from, and change any of them at any time. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Shipped as a versioned package <br> The template ships as one versioned package of separate skills that works out of the box with a built-in default flow, and is proven to run in both Claude Code and Codex. <br> The rules the package must pass are Guardrails' (GRD-20 to GRD-22). | consolidation (TOP-DECISION 89): absorbed into SET-10 | o306: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Shipped as a versioned package <br> The template ships as one versioned package of separate skills that works out of the box with a built-in default flow, and is proven to run in both Claude Code and Codex. <br> The rules the package must pass are Guardrails' (GRD-20 to GRD-22). | v2 rewrite: changed: the Agensi rules move to Guardrails. | o47: "Yes, start it end." |
| r1 | 2026-11-13 | Shipped as a versioned package. <br> The template ships as one versioned package of separate skills in the Agensi format, every script self-contained and under 20 KB. It works out of the box with a built-in default flow, and is proven to run in both Claude Code and Codex on a clean test repo with no private settings. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r5 | 2026-11-20 | Repos build on the template and stay current <br> An adopted repo holds only its own settings, pages, tests and data. The loop's code lives once per machine in the installed template, so a fix or feature in the template reaches every repo through an update, never by rebuilding it there. [SET-21] <br> An adopted repo can see what is new in the template and update to it, keeping its own settings, pages, rules and local settings. A repo running an older template version is flagged. [SET-4] <br> A repo records the template version it is on, and one with none counts as behind. A session that starts in a repo behind the installed template is told so in one line; the cases where a new goal is refused are in How-to. [SET-20] <br> One read-only command lists every gap between a repo and the current template, each with a one-line fix, and succeeds only when none remain. Health's Adoption group runs the same check. [SET-16] <br> A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. [SET-19] <br> (v2.0 planned) develop-staging: a develop or staging branch runs ahead of main, so updates are proven before they reach main and adopted repos (named only). | readme-six: absorbed into SET-1 (o514) | o609: "yes build it" |
| r4 | 2026-11-19 | Repos build on the template and stay current <br> An adopted repo holds only its own settings, pages, tests and data. The loop's code lives once per machine in the installed template, so a fix or feature in the template reaches every repo through an update, never by rebuilding it there. [SET-21] <br> An adopted repo can see what is new in the template and update to it, keeping its own settings, pages, rules and local settings. A repo running an older template version is flagged. [SET-4] <br> A repo records the template version it is on, and one with none counts as behind. A session that starts in a repo behind the installed template is told so in one line; the cases where a new goal is refused are in How-to. [SET-20] <br> One read-only command lists every gap between a repo and the current template, each with a one-line fix, and succeeds only when none remain. Health's Adoption group runs the same check. [SET-16] <br> A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. [SET-19] <br> (v2.0 planned) develop-staging: a develop or staging branch runs ahead of main, so updates are proven before they reach main and adopted repos (named only). | consolidation (TOP-DECISION 89): second revision (TOP-DECISIONs 91, 94, 95) | o363: "I want to merge the 2.1 into 2.0 ... (owner ~01:35, o355)" |
| r3 | 2026-11-19 | Repos build on the template and stay current <br> An adopted repo holds only its own settings, pages, tests and data. The loop's code lives once per machine in the installed template, so a fix or feature in the template reaches every repo through an update, never by rebuilding it there. [SET-21] <br> An adopted repo can see what is new in the template and update to it, keeping its own settings, pages, rules and local settings. A repo running an older template version is flagged. [SET-4] <br> A repo records the template version it is on, and one with none counts as behind. A session that starts in a repo behind the installed template is told so in one line; the cases where a new goal is refused are in How-to. [SET-20] <br> One read-only command lists every gap between a repo and the current template, each with a one-line fix, and succeeds only when none remain. Health's Adoption group runs the same check. [SET-16] <br> A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. [SET-19] <br> (v2.1 planned) develop-staging: a develop or staging branch runs ahead of main, so updates are proven before they reach main and adopted repos (named only). | consolidation (TOP-DECISION 89) | o323: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Updates reach every repo <br> An adopted repo can see what is new in the template and update to it, keeping its own settings, pages, rules and local settings. <br> A repo running an older template version is flagged. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-10 | Updates flow both ways <br> An adopted repo can check for a newer template version, see what's new and update, keeping its own config, pages, rules and local settings. <br> The operation session flags any governed repo running an older template version. <br> A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | A self-describing workspace <br> Every adopted repo has one entry page any new session reads first: how the parts fit together, which features exist and how to use them. <br> It is generated from the feature pages and the committed settings only, so it is never stale and never carries one machine's local values. | consolidation (TOP-DECISION 89): absorbed into SET-2 | o331: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A self-describing workspace <br> Every adopted repo has one entry page any new session reads first: how the parts fit together, which features exist and how to use them. <br> It is generated from the feature pages and the committed settings only, so it is never stale and never carries one machine's local values. | v2 rewrite: "committed settings only" is new. | o47: "Yes, start it end." |
| r1 | 2026-11-10 | A self-describing workspace <br> Every adopted repo has one entry point that any new session reads first: how the loop, release, operation and workers, docs, regression, health and settings fit together, and which features exist and how to use them. <br> It is generated from the PRD pages and settings, so it is never stale. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-20 | Adoption is proven by strict replay <br> Adoption is proven on test repos shaped like real ones, and every adoption defect found in a real repo adds a test repo that reproduces it. [SET-6] <br> Adoption replays the first run step by step against the recorded good result in `dev/toy/adoption-golden.tsv`. It stops at the first mismatch, says what differs and asks me, and never passes a step it cannot observe. [SET-11] <br> (v2.0) ci-trace-matrix: the 1,188-command adoption replay runs across about 16 CI jobs within the time limit. | readme-six: absorbed into SET-1 (o514) | o610: "yes build it" |
| r3 | 2026-11-19 | Adoption is proven by strict replay <br> Adoption is proven on test repos shaped like real ones, and every adoption defect found in a real repo adds a test repo that reproduces it. [SET-6] <br> Adoption replays the first run step by step against the recorded good result in `dev/toy/adoption-golden.tsv`. It stops at the first mismatch, says what differs and asks me, and never passes a step it cannot observe. [SET-11] <br> (v2.0) ci-trace-matrix: the 1,188-command adoption replay runs across about 16 CI jobs within the time limit. | consolidation (TOP-DECISION 89) | o328: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Adoption is proven <br> Adoption is proven on test repos shaped like real ones, and every adoption defect found in a real repo adds a test repo that reproduces it. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-10 | Adoption is proven <br> Adoption is proven on test repos shaped like real ones (existing checks, CI tests, a blocking .gitignore, a bare agent command, features that aren't folders), and every adoption defect found in a real repo adds a test repo that reproduces it. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Safe and repeatable <br> A dry run lists everything before any write; running setup twice changes nothing the second time; nothing existing is overwritten. | consolidation (TOP-DECISION 89): absorbed into SET-1 | o321: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-10 | Safe and repeatable <br> A dry run lists everything before any write; running setup twice changes nothing the second time; nothing existing is overwritten. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Private stays private <br> Local settings and private values are never written into the repo, and setup refuses to commit a file that holds one. | moved by the v2 regroup to GRD-3 | o89: "Yes, I want you to handle all of the questions except the" |
| r1 | 2026-11-10 | Private stays private <br> Local settings and private values are never written into the repo, and setup refuses to commit a file that holds one. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Learn from a repo already set up <br> Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. | consolidation (TOP-DECISION 89): absorbed into SET-1 | o322: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Learn from a repo already set up <br> Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-10 | Learn from a repo already set up <br> Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules (never private values) and adapts them to the new repo. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r6 | 2026-11-21 | One versioned template; every agent runs one loop <br> **The template is the only way the loop ships:** a GitHub template repository, versioned by its release tags, whose skills work out of the box in Claude Code and Codex in every repo made from it or adopting it. No separate skills package is built or uploaded. [SET-10] <br> Steps map to agents, with a warned fallback and recorded tokens. A private setting maps each step and goal size to an agent profile. [SET-10] | TD554: the loop ships only as the template (owner o677, item 5 of operation-top's pending folds, as drafted) | o677: "So I'm thinking about making it template only. Add this decision to" |
| r5 | 2026-11-20 | One versioned package; every agent runs one loop <br> One versioned skills package works out of the box in Claude Code and Codex. [SET-10] <br> Steps map to agents, with a warned fallback and recorded tokens. A private setting maps each step and goal size to an agent profile. [SET-10] | TD439, restored under delegation (DOC-2, o486): dropped by omission; its row guards it | o662: "Then I want u to fix this merge time issuee first. I" |
| r4 | 2026-11-20 | One versioned package; every agent runs one loop <br> One versioned skills package works out of the box in Claude Code and Codex. [SET-10] <br> Steps map to agents, with a warned fallback and recorded tokens. [SET-10] | readme-six: the owner-approved final README (o514) | o582: "yes build it" |
| r3 | 2026-11-19 | One versioned package; every agent runs one loop <br> The template ships as one versioned package of separate skills that works out of the box with a built-in default flow, and is proven to run in both Claude Code and Codex. The size and listing rules the package must pass are Guardrails' (GRD-20 to GRD-22, principle 3). [SET-3] <br> The same skills are wired into each agent's own entry files, so Claude Code, Codex and other skill-reading agents run the same loop the same way. [SET-10] <br> A private setting maps each step and goal size to an agent profile. A missing or signed-out agent falls back to the default with a warning. The run record names the agent, model and tokens of every step. [DEL-16] | consolidation (TOP-DECISION 89) | o304: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | The right format for every agent <br> The same skills are wired into each agent's own entry files, so Claude Code, Codex and other skill-reading agents run the same loop the same way. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-10 | The right format for every agent <br> The same skills are wired into each agent's own entry files (for example CLAUDE.md and AGENTS.md), so Claude Code, Codex and other SKILL.md agents run the same loop the same way. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-19 | A strict replay of the first adoption <br> Adoption replays the first run step by step against the recorded good result in `dev/toy/adoption-golden.tsv`. <br> It stops at the first mismatch, says what differs and asks me, and never passes a step it cannot observe. | consolidation (TOP-DECISION 89): absorbed into SET-6 | o329: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r3 | 2026-11-18 | A strict replay of the first adoption <br> Adoption replays the first run step by step against the recorded good result in `dev/toy/adoption-golden.tsv`. <br> It stops at the first mismatch, says what differs and asks me, and never passes a step it cannot observe. | adoption-golden: SET-11 names its fixture file again, so the test finds the fixture and the stop rule (operation-mac, 2026-11-18) | o48: "Do ur choice" |
| r2 | 2026-11-18 | A strict replay of the first adoption <br> Adoption replays the first run step by step against a recorded good result. <br> It stops at the first mismatch, says what differs and asks me, and never passes a step it cannot observe. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-17 | Prerequisites first, then a strict replay of the first adoption <br> Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh installed and signed in as me, real symlinks, and a supported platform (no crash on a missing POSIX call, and the qa lane runs on this platform instead of hanging). Each line that fails carries its exact fix, for example the install command, or `gh auth login` run with a device code I can enter from my phone instead of a prompt waiting at the PC. <br> Adoption then replays the first run step by step against its golden result (`dev/toy/adoption-golden.tsv`, eight steps from prerequisites to the first check-in). It stops at the first mismatch, says what differs and asks me to do the exact step that fixes it; it never accepts a looser equivalent. <br> Setup prints that checklist at the start of every run; `unattended.py prerequisites`, `replay` and `connectors` run each part alone (the replay stops at the first mismatch and never passes a step it cannot observe), and `board.py repos adopt` is the one-pass adoption of SET-12. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-12

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Adopt all my repos in one pass <br> From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. <br> It ends with the board showing exactly the repos I chose. | consolidation (TOP-DECISION 89): absorbed into SET-1 | o318: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Adopt all my repos in one pass <br> From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. <br> It ends with the board showing exactly the repos I chose. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-17 | Adopt all my repos in one pass <br> From the operation session, one flow lists my GitHub repos by last push, private ones included, lets me choose which to follow, clones them into one folder, registers each with the board and updates each to the current template version. <br> It ends with the board showing exactly the repos I chose and none of them on an unknown or older template version. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-13

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Workers are app sessions I can see <br> When I've chosen app sessions, a goal never falls back to a background worker: it waits for a free session and says so, including when the app refuses to start one because my message came over Remote Control. <br> The pool is kept at `pool_size` sessions (MON-12): it asks me to fill it only when it runs low, and never starts more than that. <br> Worker and pool sessions start on the model one setting names, and the operation session sets it on every session it starts or reuses. <br> The reply and govern hooks are installed exactly once each, however many times setup or either hook command runs. | moved by the v2 regroup to OPS-12 | o89: "Yes, I want you to handle all of the questions except the" |
| r1 | 2026-11-17 | Workers are app sessions I can see <br> When I've chosen app sessions, a goal never falls back to a background worker: it waits for a free session and says so, including when the app refuses to start one because my message came over Remote Control. <br> The pool is kept at `pool_size` sessions (MON-12): it asks me to fill it only when it runs low, and never starts more than that. <br> Worker and pool sessions start on the model one setting names, and the operation session sets it on every session it starts or reuses. <br> The reply and govern hooks are installed exactly once each, however many times setup or either hook command runs. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-14

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | The connectors each repo needs are checked <br> For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. <br> It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. | consolidation (TOP-DECISION 89): absorbed into SET-1 | o319: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | The connectors each repo needs are checked <br> For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. <br> It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-17 | The connectors each repo needs are checked <br> For each followed repo, setup reads which connectors its PRDs need (mail accounts, a calendar, a file store, a notification channel) and probes each with a read-only call. <br> It prints each as connected, needs sign-in or missing, with the fix, and names the owner-written files a repo needs that don't exist yet. It never attaches or enables a connector itself: I do, with the narrowest access. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-15

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | One private-name list that fits every repo <br> When setup seeds the private-name list, it explains that the list covers every repo on this machine, so a private repo's own name, or a contact it cites on purpose, would block that repo's own commits. <br> A pattern can be scoped, for example to public repos only or to named repos, so a private repo can hold what a public one must never show. <br> The checklist notes a missing list and says how to scope a line (`@public`, `@repos=a,b`). | moved by the v2 regroup to GRD-3 | o89: "Yes, I want you to handle all of the questions except the" |
| r1 | 2026-11-17 | One private-name list that fits every repo <br> When setup seeds the private-name list, it explains that the list covers every repo on this machine, so a private repo's own name, or a contact it cites on purpose, would block that repo's own commits. <br> A pattern can be scoped, for example to public repos only or to named repos, so a private repo can hold what a public one must never show. <br> The checklist notes a missing list and says how to scope a line (`@public`, `@repos=a,b`). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-16

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | One command judges a repo fully migrated <br> One read-only command lists every gap between a repo and the current template, each with a one-line fix, and succeeds only when none remain. <br> Health's Adoption group runs the same check. | consolidation (TOP-DECISION 89): absorbed into SET-4 | o324: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | One command judges a repo fully migrated <br> One read-only command lists every gap between a repo and the current template, each with a one-line fix, and succeeds only when none remain. <br> Health's Adoption group runs the same check. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-13 | A repo is judged fully migrated by one command <br> One read-only command lists every gap between a repo and the current template, each with a one-line fix, and exits 0 only when none remain; it writes nothing, and health's Adoption group runs the same check. <br> A repo carries `template_version` (set by update) and one with none counts as behind; a session that starts in a repo behind the installed template is told so in one line and never blocked, except that a new goal is refused when the major version differs. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-17

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | The Backlog milestones exist after adoption <br> Adoption creates one milestone "Backlog: <Feature>" for each feature page and "Backlog: Other", and creates none that already exists. Health's Adoption group warns for each one that is missing. | moved by the v2 regroup to HLT-10 | o89: "Yes, I want you to handle all of the questions except the" |
| r1 | 2026-11-13 | The Backlog milestones exist after adoption <br> Adoption creates one milestone "Backlog: <Feature>" for each feature page and "Backlog: Other", and creates none that already exists. Health's Adoption group warns for each one that is missing. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-18

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Adoption never blocks, and health judges it <br> Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. <br> A health check runs before and after, and the one after is green or names each gap with its fix. | consolidation (TOP-DECISION 89): absorbed into SET-1 | o320: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-17 | Adoption never blocks, and health judges it <br> Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. <br> A health check runs before and after, and the one after is green or names each gap with its fix. | migration r1; date from the Review line | o47: "Yes, start it end." |

### SET-19

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Fixes flow back to the template <br> A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. | consolidation (TOP-DECISION 89): absorbed into SET-4 | o325: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-17 | Fixes flow back to the template <br> A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. | migration r1; date from the Review line | o47: "Yes, start it end." |

### SET-20

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A repo behind the template says so <br> A repo records the template version it is on, and one with none counts as behind. <br> A session that starts in a repo behind the installed template is told so in one line; the cases where a new goal is refused are in How-to. | consolidation (TOP-DECISION 89): absorbed into SET-4 | o326: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-17 | A repo behind the template says so <br> A repo records the template version it is on, and one with none counts as behind. <br> A session that starts in a repo behind the installed template is told so in one line; the cases where a new goal is refused are in How-to. | migration r1; date from the Review line | o47: "Yes, start it end." |

### SET-21

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Adopted repos build on the template, not copies of it <br> An adopted repo holds only its own settings, pages, tests and data. <br> The loop's code lives once per machine in the installed template, so a fix or feature in the template reaches every repo through an update, never by rebuilding it there. | consolidation (TOP-DECISION 89): absorbed into SET-4 | o327: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-17 | Adopted repos build on the template, not copies of it <br> An adopted repo holds only its own settings, pages, tests and data. <br> The loop's code lives once per machine in the installed template, so a fix or feature in the template reaches every repo through an update, never by rebuilding it there. | migration r1; date from the Review line | o47: "Yes, start it end." |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [adopt-set-1](Tests#t-adopt-set-1) | requirement | SET-1 | Given SET-1, when test-adopt.sh runs its 4 cases, then each passes: it holds; apply, when the toy adopt-and-update test runs, th; check shows the change, apply keeps the repo's dat; the skills update, the repo half lands on workflow. | FAIL 2026-11-12 |
| [setup-both-halves](Tests#t-setup-both-halves) | requirement | SET-1 | Given a repo, when setup runs, then it writes the repo half and, outside the repo, the private half. | PASS 2026-11-12 |
| [migration-clean](Tests#t-migration-clean) | requirement | SET-1 | Given SET-1, when test-migration.sh runs its 6 cases, then each passes: each prints MIGRATION OK and exits 0; migration-check names it by code with a Fix line,; migration-check names each state gap by code, neve; each exits as specified (0, 1, 2 or 4), the last l; the tree, index, branches, stash, git files, home; it prints the same gap codes through the migration. | not run |
| [migration-base-config](Tests#t-migration-base-config) | requirement | SET-1 | Given SET-1, when test-migration.sh runs its 5 cases, then each passes: it reports the base branch's config and never says; it warns and goes on, refuses a differing major wi; its README and Home hold both blocks and the READM; each gets exactly one migrate-<repo> goal line, a; mac is kept, no DRIFT line prints and only origin/. | not run |
| [migration-robustness](Tests#t-migration-robustness) | requirement | SET-1 | Given SET-1, when test-migration.sh runs its 2 cases, then each passes: each ends with a verdict line and no traceback, an; it prints the exact version line, nothing for a cu. | not run |
| [sync-check-preview](Tests#t-sync-check-preview) | requirement | SET-1 | Given SET-1, when test-sync-update.sh runs its 5 cases, then each passes: it shows the installed and available versions, the; it lists that repo under Issues with the fix; it still finds the template through the installed; it refuses rather than read another repo's release; it shows as a local fix, is kept, and --propose --. | not run |
| [set1-health-bracket](Tests#t-set1-health-bracket) | requirement | SET-1 | Given SET-1, when test-setup-adopt.sh runs its 6 cases, then each passes: HEALTH START comes before the first write line, AD; it adopts and commits with exit 0, names each gap,; one findings line lists both and one issue tagged; for real, then the dry run writes nothing anywhere; it prints NO CHANGE, adds no commit, leaves a clea; it borrows the portable settings and page shape, h. | not run |
| [set1-docs-format](Tests#t-set1-docs-format) | requirement | SET-1 | Given SET-1, when test-setup-adopt.sh runs its 2 cases, then each passes: no Home, front door, requirement or problem format; the value is skipped and appears in no output and. | not run |
| [adopt-fixture-existing-checks](Tests#t-adopt-fixture-existing-checks) | requirement | SET-1 | Given SET-1, when test-adopt-fixtures.sh runs its 4 cases, then each passes: the written config keeps every check and the seede; the exception lines are written, the loop files ar; it adopts with exit 0, names the gap with its fix; they become pages and no milestone is made or read. | not run |
| [setup-fit](Tests#t-setup-fit) | requirement | SET-1 | Given a repo with CI tests, a bare agent command, its own feature list and a blocking .gitignore, when setup adopts it, then it adopts with gaps, and an older setup.py beside the new modules still works. | not run |
| [adoption-golden](Tests#t-adoption-golden) | requirement | SET-1 | Given the golden first adoption, when its fixture is read, then it holds steps 1 to 8 in order, each with a check, golden result and fix, and no machine path or account (the replay against it, stopping at the first mismatch, is adopt-replay-strict). | PASS 2026-11-13 |
| [grd10-install-hooks](Tests#t-grd10-install-hooks) | requirement | SET-1 | Given a repo being adopted, when setup runs by default, then it installs the three private-name hooks after its commit. | not run |
| [migration-v1](Tests#t-migration-v1) | requirement | SET-1 | Given a toy repo missing a feature the template carries (Usage dropped, .loop/health-rules.json, routine Runbook pointers, hooks once, a node or python the repo asks for), when migration-check runs, then it names each with its code and fix, or an OWNER STEP with the exact install command, and exits 1 only for a gap; with everything present it exits 0. | PASS 2026-11-16 |
| [repo-rules-setup](Tests#t-repo-rules-setup) | requirement | SET-1 | Given a repo adopted or updated by setup, when settings fill-repo runs, then an empty commented .loop/health-rules.json exists once and an edited one is kept. | not run |
| [matrix-health-rule](Tests#t-matrix-health-rule) | requirement | SET-1 | Given SET-1, when test-matrix.py runs its 3 cases, then each passes: a cell with no pass in 7 days reads not proven (WA; it appends a dated line with agent, OS, machine, c; it reads WARN pending: no run recorded and never F. | PASS 2026-11-13 |
| [adopt-stamps-version](Tests#t-adopt-stamps-version) | requirement | SET-1 | Given SET-1, when test-adoption-proof.py runs its 4 cases, then each passes: its config holds the installed template_version; it stops at the first mismatch naming what differs; each is connected, needs sign-in or missing from a; both are cloned into one folder, followed and set. | not run |
| [setup-owner-words-up-front](Tests#t-setup-owner-words-up-front) | requirement | SET-1 | Given a repo, when setup runs, then its first output says that un-reviewing a locked requirement needs the owner's own sentence, not a relayed letter or an agent (#2874). | PASS 2026-11-15 |
| [test-caps-settings](Tests#t-test-caps-settings) | requirement | SET-1 | Given settings.py, when the settings are read, then max_regression_rows and max_suite_seconds are repo settings with defaults the template passes today. | PASS 2026-11-16 |
| [private-checks-run-local](Tests#t-private-checks-run-local) | requirement | SET-1 | Given the SET-1 cases of test-private-checks.py, when it runs once, then it prints every PASS line the 3 merged rows checked and no FAIL line. | not run |
| [settings-reference](Tests#t-settings-reference) | requirement | SET-2 | Given SET-2, when test-settings.sh runs its 4 cases, then each passes: each is listed with its default and a one-line exp; it means unlimited, and it is the default; it takes effect; criteria_max is a repo setting with default 10 and. | PASS 2026-11-12 |
| [adopt-set-5](Tests#t-adopt-set-5) | requirement | SET-2 | Given SET-2, when test-adopt.sh runs its 2 cases, then each passes: the design guide is installed and setup's .loop/ST; .loop/START.md holds the first-five-minutes list a. | FAIL 2026-11-19 |
| [depth-setup](Tests#t-depth-setup) | requirement | SET-2 | Given the SET-2 cases of test-review-depth.sh, when it runs once, then it prints every PASS line the 3 merged rows checked and no FAIL line. | PASS 2026-11-10 |
| [entry-stale](Tests#t-entry-stale) | requirement | SET-2 | Given an adopted repo, when a PRD page's Problem changes, then the entry point check and the docs check fail STALE until docs.py audit regenerates it. | PASS 2026-11-12 |
| [set2-layers-show](Tests#t-set2-layers-show) | requirement | SET-2 | Given a default, a repo and a local setting, when settings show runs, then each value shows the layer it came from, a local key in the committed config is flagged, and private values are withheld. | not run |
| [topics-in-reference](Tests#t-topics-in-reference) | requirement | SET-2 | Given SET-2, when settings.py runs its 2 cases, then each passes: it lists topics with its default; machine_setup is listed with its default and one-l. | PASS 2026-11-13 |
| [review-hold-setting-listed](Tests#t-review-hold-setting-listed) | requirement | SET-2 | Given the settings table, when review_hold is read, then it is a repo setting that is off by default. | not run |
| [goal-pr-regenerates-start](Tests#t-goal-pr-regenerates-start) | requirement | SET-2 | Given a goal whose START.md inputs changed after the last commit, when goal.py pr runs, then it commits the regenerated START.md before the push and the entry check is OK. | not run |
| [adopt-set-3](Tests#t-adopt-set-3) | requirement | SET-10 | Given SET-3, when the toy adopt-and-update test runs, then it holds. | FAIL 2026-11-19 |
| [skill-kept](Tests#t-skill-kept) | requirement | SET-10 | Given detail moved out of the workflow-delivery and workflow-docs SKILL.md files, when their references are read, then every moved sentence is there word for word and SKILL.md points to it. | PASS 2026-11-19 |
| [agents-wire](Tests#t-agents-wire) | requirement | SET-10 | Given a repo, when setup or agents.py wire runs, then CLAUDE.md and AGENTS.md hold the same workflow-loop block, text outside it is kept, and a second run changes nothing. | PASS 2026-11-12 |
| [codex-ro-home](Tests#t-codex-ro-home) | requirement | SET-10 | Given SET-10, when test-codex.sh runs its 4 cases, then each passes: it says the private settings were not written and; no goal or binding is lost, a repeated slug is ref; the run records it as SKIPPED, never PASS, opens n; setup adopts, go freezes the goal, the live board. | not run |
| [agent-routing](Tests#t-agent-routing) | workflow | SET-10 | Given a config that routes build to Codex and review to Claude, when a small goal runs, then build runs through the Codex command, review stays on Claude, the run record names both agents with their tokens, and a missing or write-blocked Codex falls back to Claude with one warning line. | not run |
| [setup-zero-tests-119](Tests#t-setup-zero-tests-119) | defect | [#127](https://github.com/jcl2018/agent-workflow-template/issues/119 https://github.com/jcl2018/agent-workflow-template/issues/127) state unknown | Given SET-1, when test-setup-adopt.sh runs its 2 cases, then each passes: the command finds at least one test, and with no p; the ignore is exempted by a written line and the h. | not run |
| [pr-statuses-only-lane-3840](Tests#t-pr-statuses-only-lane-3840) | defect | [#3840](https://github.com/jcl2018/agent-workflow-template/issues/3840) closed (2026-11-14) | Given required checks whose jobs do more than the lane, or that no workflow job names, when goal.py pr posts statuses, then only a check whose job runs only the lane's regression command gets one and each other is printed as BLOCKS (issue 3840). | PASS 2026-11-14 |
| [migration-runs](Tests#t-migration-runs) | defect | 3821 | Given a public repo (actions, regression.yml present) and a private repo (mac), when migration-check runs, then only the wrong settings and a private repo's leftover regression.yml are gaps. | not run |
| [skill-size-116](Tests#t-skill-size-116) | defect | [#141](https://github.com/jcl2018/agent-workflow-template/issues/116 https://github.com/jcl2018/agent-workflow-template/issues/139 https://github.com/jcl2018/agent-workflow-template/issues/141) state unknown | Given SET-10, when test-defect.sh runs its 3 cases, then each passes: every one is under 150 lines, so test-board passes; neither file warns and every moved name resolves t; neither file fails (warn at 19,000, fail at 20,480. | PASS 2026-11-19 |
| [codex-key-commands](Tests#t-codex-key-commands) | defect | [#38](https://github.com/jcl2018/agent-workflow-template/issues/38) closed (2026-11-11) | Given a clean toy repo with no private settings and a Codex that is installed, signed in and able to answer, when Codex runs setup, go, the live board, health check and regression run, then each runs and leaves what it should; where Codex is not available the row exits 77 and is SKIPPED, never PASS. | not run |
