<!-- workflow-docs -->
# Setup

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/9

Review: **Reviewed 2026-11-17** <!-- prd P=7f1b1066 R=98612a96 N=9c385754 M=471a58c6 U=03828777 --> <!-- kept principle-7-readme@2bdb6a4ef -->

How to use: [How-to-use-Setup](How-to-use-Setup)

## Problem
- I want this toolset to be a workspace I can drop into any repo, for any agent: one install gives Claude Code, Codex or any agent that reads skills the same loop, docs, monitoring and settings, in the right format for each.
- Adopting a repo should never block: it should look at what is there, borrow what fits, learn from a repo I've already set up, and list what doesn't fit instead of refusing.
- Any new session should see the design logic, the docs and every command at once, and an improvement in one repo, or in the template, should reach the others.

## Requirements

### Functional
- SET-1: **Reviewed 2026-11-19** Any repo adopts the template; its own files are adapted <!-- reviewed f2232bf0 -->
  - Files the template owns install exactly, byte for byte; the repo's own files are adapted, never overwritten. The adopted repo's README shows the template's principles and design logic as written, plus its own product principles if it has any. (Owner rule 2026-11-19, o192; resolves the DOC-23 conflict.) [SET-1]
  - Conflict SET-1 vs SET-7 resolved by the owner, 2026-11-19 (o192). [SET-7]
  - One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. [SET-1]
  - A dry run lists everything before any write; running setup twice changes nothing the second time; nothing of the repo's own is overwritten. [SET-7]
  - Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. [SET-9]
  - Adopting a repo installs every guardrail on the Guardrails page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. [GRD-10]
  - Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. A health check runs before and after, and the one after is green or names each gap with its fix. [SET-18]
  - For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. [SET-14]
  - From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. It ends with the board showing exactly the repos I chose. [SET-12]
- SET-2: **Reviewed 2026-11-19** Layered settings and a generated entry page <!-- reviewed 0fc34db4 -->
  - Settings come in three layers: the template's defaults, the repo's committed settings, and my private local settings; a later layer overrides an earlier one. Every setting has a default and a one-line explanation, and I can see each value and its layer. [SET-2]
  - Every adopted repo has one entry page any new session reads first: how the parts fit together, which features exist and how to use them. It is generated from the feature pages and the committed settings only, so it is never stale and never carries one machine's local values. [SET-5]
- SET-4: **Reviewed 2026-11-19** Repos build on the template and stay current <!-- reviewed 37028201 -->
  - An adopted repo holds only its own settings, pages, tests and data. The loop's code lives once per machine in the installed template, so a fix or feature in the template reaches every repo through an update, never by rebuilding it there. [SET-21]
  - An adopted repo can see what is new in the template and update to it, keeping its own settings, pages, rules and local settings. A repo running an older template version is flagged. [SET-4]
  - A repo records the template version it is on, and one with none counts as behind. A session that starts in a repo behind the installed template is told so in one line; the cases where a new goal is refused are in How-to. [SET-20]
  - One read-only command lists every gap between a repo and the current template, each with a one-line fix, and succeeds only when none remain. Health's Adoption group runs the same check. [SET-16]
  - A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. [SET-19]
  - (v2.0 planned) develop-staging: a develop or staging branch runs ahead of main, so updates are proven before they reach main and adopted repos (named only).
- SET-6: **Reviewed 2026-11-19** Adoption is proven by strict replay <!-- reviewed 340ffece -->
  - Adoption is proven on test repos shaped like real ones, and every adoption defect found in a real repo adds a test repo that reproduces it. [SET-6]
  - Adoption replays the first run step by step against the recorded good result in `dev/toy/adoption-golden.tsv`. It stops at the first mismatch, says what differs and asks me, and never passes a step it cannot observe. [SET-11]
  - (v2.0) ci-trace-matrix: the 1,188-command adoption replay runs across about 16 CI jobs within the time limit.
- SET-10: **Reviewed 2026-11-19** One versioned package; every agent runs one loop <!-- reviewed ada09efb -->
  - The template ships as one versioned package of separate skills that works out of the box with a built-in default flow, and is proven to run in both Claude Code and Codex. The size and listing rules the package must pass are Guardrails' (GRD-20 to GRD-22, principle 3). [SET-3]
  - The same skills are wired into each agent's own entry files, so Claude Code, Codex and other skill-reading agents run the same loop the same way. [SET-10]
  - A private setting maps each step and goal size to an agent profile. A missing or signed-out agent falls back to the default with a warning. The run record names the agent, model and tokens of every step. [DEL-16]

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

- SET-11: moved to SET-6
- SET-12: moved to SET-1
- SET-13: moved to OPS-16
- SET-14: moved to SET-1
- SET-15: moved to DEL-9
- SET-16: moved to SET-4
- SET-17: moved to HLT-4
- SET-18: moved to SET-1
- SET-19: moved to SET-4
- SET-20: moved to SET-4
- SET-21: moved to SET-4
- SET-3: moved to SET-10
- SET-5: moved to SET-2
- SET-7: moved to SET-1
- SET-8: moved to DEL-9
- SET-9: moved to SET-1

### SET-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r4 | 2026-11-19 | Any repo adopts the template; its own files are adapted <br> Files the template owns install exactly, byte for byte; the repo's own files are adapted, never overwritten. The adopted repo's README shows the template's principles and design logic as written, plus its own product principles if it has any. (Owner rule 2026-11-19, o192; resolves the DOC-23 conflict.) [SET-1] <br> Conflict SET-1 vs SET-7 resolved by the owner, 2026-11-19 (o192). [SET-7] <br> One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. [SET-1] <br> A dry run lists everything before any write; running setup twice changes nothing the second time; nothing of the repo's own is overwritten. [SET-7] <br> Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. [SET-9] <br> Adopting a repo installs every guardrail on the Guardrails page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. [GRD-10] <br> Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. A health check runs before and after, and the one after is green or names each gap with its fix. [SET-18] <br> For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. [SET-14] <br> From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. It ends with the board showing exactly the repos I chose. [SET-12] | consolidation (TOP-DECISION 89): second revision (TOP-DECISIONs 91, 94, 95) | o362: "I want to merge the 2.1 into 2.0 ... (owner ~01:35, o355)" |
| r3 | 2026-11-19 | Any repo adopts the template byte for byte <br> Any repo adopts the template cleanly, byte for byte: every file the template installs matches the template's copy exactly, and the adopted repo's README shows the template's principles and design logic as written, byte for byte, plus its own product principles if it has any. (Owner rule 2026-11-19; resolves the DOC-23 conflict.) [SET-1] <br> Files the template owns install exactly; the repo's own files are adapted, never overwritten. (Owner rule 2026-11-19 01:40, o192; resolves the SET-1 vs SET-7 conflict.) [SET-1] <br> One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. [SET-1] <br> A dry run lists everything before any write; running setup twice changes nothing the second time; nothing of the repo's own is overwritten. [SET-7] <br> Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. [SET-9] <br> Adopting a repo installs every guardrail on the Guardrails page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. [GRD-10] <br> Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. A health check runs before and after, and the one after is green or names each gap with its fix. [SET-18] <br> For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. [SET-14] <br> From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. It ends with the board showing exactly the repos I chose. [SET-12] | consolidation (TOP-DECISION 89) | o316: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | One command adopts a repo <br> One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. <br> It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-13 | One command adopts a repo <br> One command sets up a new or existing repo: the loop config, PRD feature pages in the docs format, the Home table and README How to use, the nightly regression in GitHub Actions, the health groups, and every setting with its default. <br> It shows what it found and would change first, then applies it on a branch through the loop, adapting what is there instead of overwriting. <br> It never blocks: what doesn't fit is listed and filed as issues tagged with the right feature, and the rest is adopted. <br> Health is the first and last step: before adopting, a health check records where the repo starts; after adopting, the full health check (every group, Adoption included) must come back green or name each gap with its fix, and that verdict is the adoption result, because if health works, the rest works. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### SET-2

| rev | date | text | why | approved |
|---|---|---|---|---|
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
| [adopt-set-1](Tests#t-adopt-set-1) | requirement | SET-1 | Given SET-1, when the toy adopt-and-update test runs, then it holds. | FAIL 2026-11-12 |
| [adopt-set-2](Tests#t-adopt-set-2) | requirement | SET-1 | Given SET-1 with suggest then apply, when the toy adopt-and-update test runs, then it holds. | FAIL 2026-11-12 |
| [setup-both-halves](Tests#t-setup-both-halves) | requirement | SET-1 | Given a repo, when setup runs, then it writes the repo half and, outside the repo, the private half. | PASS 2026-11-12 |
| [set1-health-bracket](Tests#t-set1-health-bracket) | requirement | SET-1 | Given an adoption, when setup runs, then HEALTH START comes before the first write line, ADOPTION VERDICT is the last line, and a verdict that is not green lists each gap with its fix. | not run |
| [set1-never-blocks](Tests#t-set1-never-blocks) | requirement | SET-1 | Given a bare agent_command and an ignored *.tsv, when setup runs, then it adopts and commits with exit 0, names each gap, writes the exception line, and a failed step after the commit is a note and a gap. | not run |
| [set1-no-fit-filed](Tests#t-set1-no-fit-filed) | requirement | SET-1 | Given two pages with their own sections, when setup runs, then one findings line lists both and one issue tagged adoption is filed through the stand-in, matching preview, and a second run files none. | not run |
| [set1-docs-format](Tests#t-set1-docs-format) | requirement | SET-1 | Given a fresh adoption, when the docs check runs, then no Home, front door, requirement or problem format gap and no broken link remains, only pages still to be written. | not run |
| [set7-dry-run-lists-all](Tests#t-set7-dry-run-lists-all) | requirement | SET-1 | Given a repo, when setup runs dry and then for real, then the dry run writes nothing anywhere and lists every file the real commit holds. | not run |
| [set7-second-run-nothing](Tests#t-set7-second-run-nothing) | requirement | SET-1 | Given an adopted repo with a working config nobody committed, when setup runs again, then it prints NO CHANGE, adds no commit, leaves a clean tree and keeps the config's own values. | not run |
| [set9-from-borrows](Tests#t-set9-from-borrows) | requirement | SET-1 | Given an adopted repo as the model, when setup runs with --from, then it borrows the portable settings and page shape, holds auto_merge and reply_hook until --allow, keeps its own base and agent command, changes nothing on a second run and never writes to the model. | not run |
| [set9-from-no-values](Tests#t-set9-from-no-values) | requirement | SET-1 | Given a model value holding a home path or an email, when setup runs with --from, then the value is skipped and appears in no output and no written file. | not run |
| [grd10-install-hooks](Tests#t-grd10-install-hooks) | requirement | SET-1 | Given a repo being adopted, when setup runs by default, then it installs the three private-name hooks after its commit. | not run |
| [repo-rules-setup](Tests#t-repo-rules-setup) | requirement | SET-1 | Given a repo adopted or updated by setup, when settings fill-repo runs, then an empty commented .loop/health-rules.json exists once and an edited one is kept. | not run |
| [adopt-connectors-probed](Tests#t-adopt-connectors-probed) | requirement | SET-1 | Given followed repos whose PRDs name connectors, when the connectors are listed, then each is connected, needs sign-in or missing from a read-only probe, and nothing is enabled. | not run |
| [adopt-many-one-pass](Tests#t-adopt-many-one-pass) | requirement | SET-1 | Given two GitHub repos chosen from the recent list, when repos adopt runs, then both are cloned into one folder, followed and set up, each reporting its template_version. | not run |
| [setup-owner-words-up-front](Tests#t-setup-owner-words-up-front) | requirement | SET-1 | Given a repo, when setup runs, then its first output says that un-reviewing a locked requirement needs the owner's own sentence, not a relayed letter or an agent (#2874). | PASS 2026-11-15 |
| [test-caps-settings](Tests#t-test-caps-settings) | requirement | SET-1 | Given settings.py, when the settings are read, then max_regression_rows and max_suite_seconds are repo settings with defaults the template passes today. | PASS 2026-11-16 |
| [private-checks-run-local](Tests#t-private-checks-run-local) | requirement | SET-1 | Given a required check whose job is plain run steps, when the pr step posts statuses, then it runs those steps here and posts the check with the regression one (#4537). | not run |
| [private-checks-fail-not-green](Tests#t-private-checks-fail-not-green) | requirement | SET-1 | Given a plain job whose step fails, when the pr step posts statuses, then that check is never posted green and is named, as is a third-party-action check (#4537). | not run |
| [private-checks-control](Tests#t-private-checks-control) | requirement | SET-1 | Given a repo requiring only the regression check, when the pr step runs, then nothing is named or stopped, as before (negative control, #4537). | not run |
| [adopt-set-5](Tests#t-adopt-set-5) | requirement | SET-2 | Given SET-5, when the toy adopt test runs, then the design guide is installed and setup's .loop/START.md holds the opener and every part. | FAIL 2026-11-19 |
| [settings-reference](Tests#t-settings-reference) | requirement | SET-2 | Given every repo and private setting, when the reference is read, then each is listed with its default and a one-line explanation. | PASS 2026-11-12 |
| [parallel-unlimited](Tests#t-parallel-unlimited) | requirement | SET-2 | Given parallel is 0, when goals run, then it means unlimited, and it is the default. | PASS 2026-11-12 |
| [settings-read-fresh](Tests#t-settings-read-fresh) | requirement | SET-2 | Given a changed setting, when the next run happens, then it takes effect. | PASS 2026-11-12 |
| [criteria-max-setting](Tests#t-criteria-max-setting) | requirement | SET-2 | Given the repo settings, when they are read, then criteria_max is a repo setting with default 10 and a one-line explanation. | PASS 2026-11-12 |
| [depth-setup](Tests#t-depth-setup) | requirement | SET-2 | Given a new repo, when setup runs, then it writes review_depth full with a one-line explanation. | PASS 2026-11-10 |
| [depth-reference](Tests#t-depth-reference) | requirement | SET-2 | Given the settings reference, when it is generated, then it lists review_depth with its default. | PASS 2026-11-10 |
| [depth-fill-repo-help](Tests#t-depth-fill-repo-help) | requirement | SET-2 | Given a config that already has its _help explanations, when fill-repo runs, then it fills without error. | PASS 2026-11-10 |
| [entry-stale](Tests#t-entry-stale) | requirement | SET-2 | Given an adopted repo, when a PRD page's Problem changes, then the entry point check and the docs check fail STALE until docs.py audit regenerates it. | PASS 2026-11-12 |
| [entry-adopt](Tests#t-entry-adopt) | requirement | SET-2 | Given a repo, when setup adopts it, then .loop/START.md holds the first-five-minutes list and every part: loop, release, operation and workers, docs, regression, health, settings and features. | SKIPPED 2026-11-16 |
| [set2-layers-show](Tests#t-set2-layers-show) | requirement | SET-2 | Given a default, a repo and a local setting, when settings show runs, then each value shows the layer it came from, a local key in the committed config is flagged, and private values are withheld. | not run |
| [repo-rules-threshold](Tests#t-repo-rules-threshold) | requirement | SET-2 | Given health_script_bytes set in .loop/config.json, when health checks the Size group, then that number is the script cap and the default stays 20480. | not run |
| [topics-in-reference](Tests#t-topics-in-reference) | requirement | SET-2 | Given the settings reference, when it is generated, then it lists topics with its default. | PASS 2026-11-13 |
| [review-hold-setting-listed](Tests#t-review-hold-setting-listed) | requirement | SET-2 | Given the settings table, when review_hold is read, then it is a repo setting that is off by default. | not run |
| [machine-setting-listed](Tests#t-machine-setting-listed) | requirement | SET-2 | Given the settings reference, when it is printed, then machine_setup is listed with its default and one-line explanation. | PASS 2026-11-16 |
| [adopt-set-4](Tests#t-adopt-set-4) | requirement | SET-4 | Given SET-4, when the toy adopt-and-update test runs, then check shows the change, apply keeps the repo's data and lands the repo half on its branch. | FAIL 2026-11-12 |
| [migration-clean](Tests#t-migration-clean) | requirement | SET-4 | Given a clean private repo and a clean public repo, both recorded mac with the task registered, when migration-check runs, then each prints MIGRATION OK and exits 0. | not run |
| [migration-gaps-pr](Tests#t-migration-gaps-pr) | requirement | SET-4 | Given a clean toy repo, when each kind of pull-request-closable gap is made (version, settings, entries, stale START.md, bookkeeping files, workflow files, land row, blocks, Runbook, stale page), then migration-check names it by code with a Fix line, and with regression off it names no regression gap. | not run |
| [migration-gaps-state](Tests#t-migration-gaps-state) | requirement | SET-4 | Given a clean toy repo with a bare wiki, when the task is misnamed, 6-hourly or missing, or the wiki holds an orphan, a stale page, hostile page names, no wiki, an unreadable origin or an ext:: origin, then migration-check names each state gap by code, never deletes, runs no command from a page name, and a repo with no docs.tsv gets no wiki gap. | not run |
| [migration-flags](Tests#t-migration-flags) | requirement | SET-4 | Given a repo whose only gaps are state gaps, when migration-check runs with --pr, --offline, --repo, an unknown flag, no workflow-health, an injected exception, a credential in the origin URL or a clone that hangs, then each exits as specified (0, 1, 2 or 4), the last line says what was skipped, no credential is printed and the hang ends at 30 seconds. | not run |
| [migration-writes-nothing](Tests#t-migration-writes-nothing) | requirement | SET-4 | Given a repo with gaps and a published orphan page, when migration-check runs in full, with --pr and with --offline, then the tree, index, branches, stash, git files, home folder and temp folder are identical before and after. | not run |
| [migration-health-same](Tests#t-migration-health-same) | requirement | SET-4 | Given a repo with no template_version and an unknown setting, when health check runs the Adoption group, then it prints the same gap codes through the migration rule and the template-version row, stays green, previews WOULD open for both, and the migration rule's negative control fires. | not run |
| [migration-base-config](Tests#t-migration-base-config) | requirement | SET-4 | Given an adopted repo, when update --check runs from a branch cut before setup, with no local main, from a fresh clone, with a default branch that is neither main nor master, or with a stale local main, then it reports the base branch's config and never says it has none. | not run |
| [migration-robustness](Tests#t-migration-robustness) | requirement | SET-4 | Given a linked worktree, a subdirectory, a missing or malformed config, a corrupt regression.tsv, an unparseable docs.tsv, an unprintable wiki page name and two runs at once, when migration-check runs, then each ends with a verdict line and no traceback, and no temp folder is left. | not run |
| [migration-lag-line](Tests#t-migration-lag-line) | requirement | SET-4 | Given a repo behind the installed template, when entry.py lag runs through a fake install folder and through the test override, then it prints the exact version line, nothing for a current or newer repo or a tree that holds the skills, and a differing major refuses a new goal unless its slug starts with migrate-. | PASS 2026-11-18 |
| [migration-major-refused](Tests#t-migration-major-refused) | requirement | SET-4 | Given a repo behind the installed template, when goal.py new starts a goal, then it warns and goes on, refuses a differing major with exit 2 and no goal state, lets a migrate- slug through, and only notes a missing entry.py. | not run |
| [migration-blocks-inserted](Tests#t-migration-blocks-inserted) | requirement | SET-4 | Given a repo adopted before the Settings and Automation blocks existed, when update --apply runs, then its README and Home hold both blocks and the README line, its config holds template_version and the three routines, and the repo is no longer behind. | not run |
| [migration-queue](Tests#t-migration-queue) | requirement | SET-4 | Given followed repos app, app.v2 and app-api all behind the template, when the operation session's pass runs, then each gets exactly one migrate-<repo> goal line, a second or concurrent pass adds none, a finished goal for this version is an Issues line, an older one allows a version-suffixed slug, and a repo on another branch or with a modified queue file is skipped with its reason. | not run |
| [migration-mac-kept](Tests#t-migration-mac-kept) | requirement | SET-4 | Given a public repo recorded regression_runs mac, when setup re-runs and the tick runs, then mac is kept, no DRIFT line prints and only origin/<base> is fetched. | not run |
| [sync-check-preview](Tests#t-sync-check-preview) | requirement | SET-4 | Given a newer template release, when update --check runs, then it shows the installed and available versions, the repo's version, what is new and each changed file, writes nothing, and never offers a downgrade. | not run |
| [sync-apply-keeps](Tests#t-sync-apply-keeps) | requirement | SET-4 | Given an adopted repo, when update applies a newer version, then the skills update, the repo half lands on workflow-update-vX with template_version stamped, and config values, pages and private settings are kept. | not run |
| [sync-default-source](Tests#t-sync-default-source) | requirement | SET-4 | Given an update from the template's release source archive, when the next default check runs, then it still finds the template through the installed stamp. | SKIPPED 2026-11-16 |
| [sync-template-redirect](Tests#t-sync-template-redirect) | requirement | SET-4 | Given a committed template_repo that differs from the installed stamp's repo, when update runs, then it refuses rather than read another repo's releases. | SKIPPED 2026-11-16 |
| [sync-propose](Tests#t-sync-propose) | requirement | SET-4 | Given a skill file fixed in an adopted repo, when update runs, then it shows as a local fix, is kept, and --propose --file-issue files one issue on the template with its diff and no repo name. | SKIPPED 2026-11-16 |
| [sync-board-lag](Tests#t-sync-board-lag) | requirement | SET-4 | Given a governed repo on an older template version, when the live board renders, then it lists that repo under Issues with the fix. | not run |
| [migration-v1](Tests#t-migration-v1) | requirement | SET-4 | Given a toy repo missing a feature the template carries (Usage dropped, .loop/health-rules.json, routine Runbook pointers, hooks once, a node or python the repo asks for), when migration-check runs, then it names each with its code and fix, or an OWNER STEP with the exact install command, and exits 1 only for a gap; with everything present it exits 0. | PASS 2026-11-16 |
| [adopt-stamps-version](Tests#t-adopt-stamps-version) | requirement | SET-4 | Given a repo set up from an installed package, when setup finishes, then its config holds the installed template_version. | not run |
| [adopt-fixture-existing-checks](Tests#t-adopt-fixture-existing-checks) | requirement | SET-6 | Given a repo whose config lists its own checks (pull request 83), when setup adopts it, then the written config keeps every check and the seeded row runs all of them. | not run |
| [adopt-fixture-ci-gitignore](Tests#t-adopt-fixture-ci-gitignore) | requirement | SET-6 | Given CI tests and a .gitignore blocking *.tsv, when setup adopts the repo, then the exception lines are written, the loop files are committed and the check comes from CI. | not run |
| [adopt-fixture-bare-agent](Tests#t-adopt-fixture-bare-agent) | requirement | SET-6 | Given a bare agent_command and no CI, when setup adopts the repo, then it adopts with exit 0, names the gap with its fix and leaves the agent command alone. | not run |
| [adopt-fixture-feature-milestones](Tests#t-adopt-fixture-feature-milestones) | requirement | SET-6 | Given features that are roadmap milestones and not folders, when setup adopts the repo, then they become pages and no milestone is made or read. | not run |
| [setup-fit](Tests#t-setup-fit) | requirement | SET-6 | Given a repo with CI tests, a bare agent command, its own feature list and a blocking .gitignore, when setup adopts it, then it adopts with gaps, and an older setup.py beside the new modules still works. | not run |
| [adoption-golden](Tests#t-adoption-golden) | requirement | SET-6 | Given the golden first adoption, when its fixture and SET-11 are read, then the fixture holds steps 1 to 8 in order, each with a check, golden result and fix, no machine path or account, and SET-11 names it and its first-mismatch stop. | PASS 2026-11-13 |
| [matrix-health-rule](Tests#t-matrix-health-rule) | requirement | SET-6 | Given a record of smoke runs, when health checks, then a cell with no pass in 7 days reads not proven (WARN) and a V1-required cell with none is a FAIL. | PASS 2026-11-13 |
| [matrix-smoke-record](Tests#t-matrix-smoke-record) | requirement | SET-6 | Given a smoke run, when it ends, then it appends a dated line with agent, OS, machine, commit and result that health reads as proof of that cell. | PASS 2026-11-13 |
| [matrix-never-run-warns](Tests#t-matrix-never-run-warns) | requirement | SET-6 | Given a cell of the agent-by-machine matrix that has never run, when health checks, then it reads WARN pending: no run recorded and never FAIL; only a cell that ran and failed, or whose last run is too old, fails. | not run |
| [adopt-replay-strict](Tests#t-adopt-replay-strict) | requirement | SET-6 | Given a machine that differs from the golden first adoption, when the replay runs, then it stops at the first mismatch naming what differs and never passes a step it cannot observe (the live check-in, step 8, is reported as not observed). | not run |
| [adopt-set-3](Tests#t-adopt-set-3) | requirement | SET-10 | Given SET-3, when the toy adopt-and-update test runs, then it holds. | FAIL 2026-11-19 |
| [skill-kept](Tests#t-skill-kept) | requirement | SET-10 | Given detail moved out of the workflow-delivery and workflow-docs SKILL.md files, when their references are read, then every moved sentence is there word for word and SKILL.md points to it. | PASS 2026-11-19 |
| [agents-wire](Tests#t-agents-wire) | requirement | SET-10 | Given a repo, when setup or agents.py wire runs, then CLAUDE.md and AGENTS.md hold the same workflow-loop block, text outside it is kept, and a second run changes nothing. | PASS 2026-11-12 |
| [codex-ro-home](Tests#t-codex-ro-home) | requirement | SET-10 | Given a Codex sandbox that leaves the home folder read-only, when setup adopts a clean toy repo, then it says the private settings were not written and still adopts the repo, with no crash. | not run |
| [codex-pods-collide](Tests#t-codex-pods-collide) | requirement | SET-10 | Given a Codex pod and a Claude Code pod that know nothing of each other, when they queue goals, bind workers and run lanes in the same toy repos at once, then no goal or binding is lost, a repeated slug is refused, the lanes share one slot pool and take turns, and their private flow files stay apart. | not run |
| [codex-skip-77](Tests#t-codex-skip-77) | requirement | SET-10 | Given a regression row that cannot run on this machine, when it exits 77, then the run records it as SKIPPED, never PASS, opens no issue, and a later lane runs it again. | not run |
| [codex-harness](Tests#t-codex-harness) | requirement | SET-10 | Given a stand-in for codex that runs the prompt's commands, when the Codex harness runs them on a clean toy repo with no private settings, then setup adopts, go freezes the goal, the live board lists it, health check prints its verdict and regression run prints its result. | not run |
| [package-gate-head](Tests#t-package-gate-head) | requirement | SET-10 | Given the merged head of a pull request, when package.py's file and script checks run on its tracked files, then the lane fails if a script is over 20,480 bytes, the package has over 100 files, or a script is not standalone; it runs on Windows too. | FAIL 2026-11-16 |
| [package-headroom-held](Tests#t-package-headroom-held) | requirement | SET-10 | Given the shipped package, when rules.py, lane.py, goal.py, actions.py or report.py passes 19,000 bytes or the package passes 100 files, then the check fails; today all five are at most 19,000 and the package has 100 files. | FAIL 2026-11-15 |
| [package-rows-tracked](Tests#t-package-rows-tracked) | requirement | SET-10 | Given untracked files such as __pycache__ in a checkout, when package.py walks it, then only the files git tracks are counted, and a package row that fails prints its reason. | FAIL 2026-11-15 |
| [agent-routing](Tests#t-agent-routing) | workflow | SET-10 | Given a config that routes build to Codex and review to Claude, when a small goal runs, then build runs through the Codex command, review stays on Claude, the run record names both agents with their tokens, and a missing or write-blocked Codex falls back to Claude with one warning line. | not run |
| [setup-zero-tests-119](Tests#t-setup-zero-tests-119) | defect | [#119](https://github.com/jcl2018/agent-workflow-template/issues/119) closed (2026-11-13) | Given a repo whose tests are named *_test.py, when setup picks its check, then the command finds at least one test, and with no proof it is no fit with a finding. | not run |
| [setup-tsv-guard-127](Tests#t-setup-tsv-guard-127) | defect | [#127](https://github.com/jcl2018/agent-workflow-template/issues/127) closed (2026-11-13) | Given a .gitignore blocking *.tsv and a hook that rejects tracked .tsv files, when setup runs, then the ignore is exempted by a written line and the hook is named with its exemption and never edited. | not run |
| [pr-statuses-only-lane-3840](Tests#t-pr-statuses-only-lane-3840) | defect | [#3840](https://github.com/jcl2018/agent-workflow-template/issues/3840) closed (2026-11-14) | Given required checks whose jobs do more than the lane, or that no workflow job names, when goal.py pr posts statuses, then only a check whose job runs only the lane's regression command gets one and each other is printed as BLOCKS (issue 3840). | PASS 2026-11-14 |
| [migration-runs](Tests#t-migration-runs) | defect | 3821 | Given a public repo (actions, regression.yml present) and a private repo (mac), when migration-check runs, then only the wrong settings and a private repo's leftover regression.yml are gaps. | not run |
| [skill-size-116](Tests#t-skill-size-116) | defect | [#116](https://github.com/jcl2018/agent-workflow-template/issues/116) closed (2026-11-10) | Given the package's skills, when each SKILL.md is counted, then every one is under 150 lines, so test-board passes. | PASS 2026-11-19 |
| [size-139](Tests#t-size-139) | defect | [#139](https://github.com/jcl2018/agent-workflow-template/issues/139) closed (2026-11-19) | Given criteria.py's page rules moved into deployments.py by a pure move, when health's size rule and the split checks run, then neither file warns and every moved name resolves the same on criteria. | PASS 2026-11-12 |
| [size-140](Tests#t-size-140) | defect | [#140](https://github.com/jcl2018/agent-workflow-template/issues/140) closed (2026-11-19) | Given docs.py's page map moved into counting.py by a pure move, when health's size rule and the split checks run, then neither file warns and every moved name resolves the same on docs. | PASS 2026-11-12 |
| [size-141](Tests#t-size-141) | defect | [#141](https://github.com/jcl2018/agent-workflow-template/issues/141) closed (2026-11-19) | Given regression.py's row and page readers moved into runs.py by a pure move, when health's size rule and the split checks run, then neither file warns and every moved name resolves the same on regression. | PASS 2026-11-12 |
| [codex-key-commands](Tests#t-codex-key-commands) | defect | [#38](https://github.com/jcl2018/agent-workflow-template/issues/38) closed (2026-11-11) | Given a clean toy repo with no private settings and a Codex that is installed, signed in and able to answer, when Codex runs setup, go, the live board, health check and regression run, then each runs and leaves what it should; where Codex is not available the row exits 77 and is SKIPPED, never PASS. | not run |
| [package-passes-3800](Tests#t-package-passes-3800) | defect | [#3800](https://github.com/jcl2018/agent-workflow-template/issues/3800) closed (2026-11-15) | Given the shipped tree, when dev/package.py runs, then it passes: no script over 20,480 bytes, at most 100 files, no Safety or Disclosure failure (issue 3800). | not run |
