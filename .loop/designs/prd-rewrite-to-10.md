# PRDs rewritten so every requirement can score 10

A draft built from the review in prd-review-all-features.md. Nothing in the repo was changed, and no requirement was marked Reviewed.

## What a rewrite can and cannot do

- **Size (3 points) and Scope (3 points) come from the text.** Every requirement below is rewritten as one promise, in the right feature, in 12 to 80 words. A script checked the word counts. All 153 requirements score 3 and 3.
- **Proof (4 points) comes from tests passing.** Rewriting cannot earn it. For each requirement the last column says what is still needed to reach 10.
- So today, after this rewrite, 24 of 153 requirements would score 10. The rest score 6 to 9 until their tests exist and pass.

## The work left to make every score 10

| Work | How much |
|---|---|
| Run tests that exist but show no result | 433 tests |
| Fix flaky tests | 8 |
| Write tests for requirements that have none | 19 requirements (18 of them new) |
| Assign existing tests to a requirement split out of a larger one | 34 requirements |

The "not run" count is taken from the Tests tables as published. Some of those tests may pass as soon as they are run; I did not run any.

## What changed in the rewrite

- **114 requirements became 153.** Bundled requirements were split into single promises, and repeats were merged. The average length fell from 109 words to 42.
- **Nine features became twelve.** Release and Integrations are new, and Monitoring is split into Operation and Check-in and board, because rewritten as single promises it would hold 22 requirements against a page limit of 19.
- **Detail moved, not deleted.** Script names, file layouts, defaults and check rules that were inside requirements are to be moved word for word to each feature's How-to-use page when this is applied.
- **Every old requirement is accounted for.** The "From" column names the requirement each one came from. Old requirements that no longer stand alone: none.
- **18 requirements are new, and eighteen existing ones gain or change a sentence.** Each is marked in italics. They come from today's failures or from your answers, and they need your approval like any new requirement.

## Principles

Eight principles sit above the features. The README would hold only these (DOC-23), and health gives one verdict for each (HLT-2). Diagrams and today's standing are in principles-draft.html.

| # | Principle | In one sentence | Health groups | Enforced by |
|---|---|---|---|---|
| 1 | **Documentation-driven** | Nothing is built that a Reviewed requirement doesn't ask for, and the PRD changes only by your words. | Traceability | DOC-2, DOC-20, DOC-22, DEL-2, DEL-18, DEL-19, REG-1 |
| 2 | **The loop and coverage** | Every requirement is enforced and proven, and whatever falls short, conflicts or has no owner becomes work until it is fixed or the PRD is revised. | Requirements, Tests, Controls | REG-1, REG-6, REG-9, REG-10, REG-15, REG-16, DOC-3, HLT-4, HLT-6, HLT-12, GRD-9, DEL-14 |
| 3 | **The docs are true** | The pages agree with each other and with the code: one ID, one name for each command, and no two requirements that contradict. | Consistency, Docs | DOC-1, DOC-6, DOC-12, DOC-13, DOC-20, DOC-21, HLT-5, HLT-13, REL-10, INT-2, INT-3 |
| 4 | **Nothing stale or left over** | The tests ran today, merged work is released, and no stale branch, idle session, old finding or question to you is left behind. | Freshness, Hygiene | AUT-2, AUT-3, REG-4, REL-9, REL-1, REL-5, REL-6, REL-7, MON-6, MON-8, HLT-8, HLT-12, CHK-7 |
| 5 | **Fast, cheap and small** | Goals, tests and health stay inside their time and token limits, and scripts, pages and the package stay inside their size limits, including Agensi's. | Performance, Size | GRD-2, GRD-7, GRD-8, GRD-19, GRD-20, GRD-21, GRD-22, DEL-17, REG-7, REG-11, REG-14, AUT-7, HLT-11, SET-3 |
| 6 | **Nothing private escapes** | No private name, path, address or key leaves the machine, and automation gets only the access it needs. | Security and privacy | GRD-3, GRD-4, GRD-5, GRD-16, AUT-6, AUT-9, INT-4, MCH-6 |
| 7 | **It works installed fresh** | A repo that adopts the template gets the same loop, checks and guardrails, with nothing rebuilt there. | Adoption | SET-1, SET-6, SET-16, SET-21, GRD-10, MCH-1, MCH-2 |
| 8 | **It stops for you only when it must** | It asks you only for what is yours to decide: anything destructive, costly or private, and any change to the PRD. Everything else it decides, tells you, and lets you reverse. | Attention (new; Docs folds into Consistency) | DEL-3, DEL-17, MON-11, MON-18, MCH-3, REL-11, REL-8, DOC-2, CHK-7, CHK-9 |

## Summary by feature

| Feature | Requirements | Already 10 | Text score | 
|---|---|---|---|
| Delivery | 10 | 1 | 6 of 6 |
| Release (new) | 13 | 0 | 6 of 6 |
| Setup | 17 | 1 | 6 of 6 |
| Regression | 16 | 3 | 6 of 6 |
| Automation | 9 | 4 | 6 of 6 |
| Documentation | 19 | 7 | 6 of 6 |
| Integrations (new) | 8 | 0 | 6 of 6 |
| Guardrails | 19 | 0 | 6 of 6 |
| Health | 13 | 2 | 6 of 6 |
| Machines | 6 | 0 | 6 of 6 |
| Operation (was Monitoring, part 1) | 14 | 4 | 6 of 6 |
| Check-in and board (was Monitoring, part 2) | 9 | 2 | 6 of 6 |
| **All** | **153** | **24** | 6 of 6 |

## Delivery

Problem: The loop: one sentence in, a reviewed pull request out, and every run feeds back what it found.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| DEL-1 | **The loop.** I give one sentence and its done lines, and a worker runs it unattended through freeze, idea, plan, build, review, qa, ship, pull request and release. Each step maps to a skill I choose. It won't start until the flow is set up. Review is the only gate a person has to pass. | DEL-1 | 55 | 3 | 3 | 3 | Run 1 test not run yet |
| DEL-18 | **Everything goes through a goal.** Every change to a repo's main branch arrives through a goal: its pull request and its release commit. Nothing else writes to main, and health's Traceability group flags a commit on main that no goal accounts for. *NEW: your rule, 2026-11-17.* | new | 42 | 3 | 3 | 0 | Write its tests (new requirement) |
| DEL-19 | **Every goal serves a requirement.** A goal is frozen only when it names the Reviewed requirement it builds, fixes or keeps true. Work that no requirement covers starts as a goal that changes the PRD, with the new text in its done lines and my approval; the build follows as a second goal. A goal that names none is refused at freeze, and health's Traceability group flags any that slipped through. *NEW: your rule, 2026-11-17: requirement-driven; today most goals show under "no feature".* | new | 71 | 3 | 3 | 0 | Write its tests (new requirement) |
| DEL-2 | **Done lines are frozen.** Done lines can't change once the goal starts; a change means a new goal. | DEL-2 | 18 | 3 | 3 | 4 | Nothing: already proven |
| DEL-14 | **Every goal feeds back what it found.** When a goal ships, each finding it did not fix is filed once: a break of a Reviewed requirement as an issue labelled defect, and an improvement, idea or saving as an issue labelled backlog on its feature's Backlog milestone. | DEL-14 | 47 | 3 | 3 | 2 | Run 1 test not run yet; fix 1 flaky |
| DEL-3 | **It only stops for me when it must.** A decision that is mine waits under Needs you, or is auto-approved and logged where the repo allows. Plan and review run at full depth unless the repo or I choose condensed. Tests never shrink. | DEL-3, DEL-6 | 43 | 3 | 3 | 3 | Run 4 tests not run yet |
| DEL-7 | **It survives failure.** A failed step is retried, and after three failed tries the goal stops with a reason. A stopped or crashed goal resumes from its last recorded step. Past its time or token budget a goal starts no new step and waits under Needs you; only my recorded words raise a limit. A step that fails because its session or tool is unusable restarts in a fresh session with its notes. *changed: last sentence is new (the planning-tool risk).* | DEL-7, DEL-8, DEL-1 | 73 | 3 | 3 | 1 | Run 16 tests not run yet |
| DEL-17 | **A goal's ETA is a hard limit.** Every goal records an ETA when it is frozen. Past it, the goal finishes its current step, starts no new one, and I choose: ship now, extend once, or defer. Decisions a goal can foresee are asked once, up front, each with a recommendation. Time spent waiting for a queue, for memory or for me does not count. *changed: last sentence is new (the budget risk).* | GRD-14 | 65 | 3 | 3 | 0 | Run 9 tests not run yet |
| DEL-4 | **The pull request is the record.** Every pull request carries the done lines, the plan, how to verify by hand, and each step's result. | DEL-4 | 24 | 3 | 3 | 3 | Run 1 test not run yet |
| DEL-16 | **Each step runs on the agent I pick.** A private setting maps each step and goal size to an agent profile. A missing or signed-out agent falls back to the default with a warning. The run record names the agent, model and tokens of every step. | DEL-16 | 46 | 3 | 3 | 0 | Write a test |

## Release (new)

Problem: A finished pull request merges, gets a version and is published, one at a time across machines, without one stuck goal holding up the rest.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| REL-1 | **A version number says what changed.** A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. A goal's release never bumps a major; a major exists only after the gate passes. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-1 | 41 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-2 | **A major's milestone is closed out.** Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-2 | 29 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-3 | **The full suite passes on the candidate.** The gate runs the whole nightly suite on the release candidate. Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-3 | 41 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-4 | **Health, review and pages pass on the candidate.** The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-4 | 35 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-5 | **A candidate admits only gate fixes.** From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-5 | 33 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-6 | **Promotion tags, snapshots and reports.** Promoting a major runs only from the operation session with my record naming that version and every gate check passing. It tags the major, keeps a snapshot branch, and mails a state report as the release notes. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-6 | 42 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-7 | **A major can be reverted.** revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-7 | 28 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-8 | **Promotion and waivers are my words.** Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject. *on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44).* | REL-8 | 27 | 3 | 3 | to assign | Assign its tests when the source is split |
| REL-9 | **Every goal ends with a release.** With auto_merge on, a finished goal is merged and released automatically: version bump, release note, published release and wiki. With auto_merge off it makes a draft release and merges nothing. Any failure shows under Needs you. *renumbered from the draft's REL-1 because main's Release page (v1.0.61) already uses REL-1 to REL-8.* | DEL-5 | 42 | 3 | 3 | 2 | Run 13 tests not run yet |
| REL-10 | **A merge is never refused late or left half done.** A merge is refused only for a page the goal's own change made stale, and the pull-request checks catch that before a merge slot is spent. If the merge lands but the release fails, the goal reads "merged, release owed", and a second run finishes it without merging twice. *NEW: from today's failures (#4903, #4852, #4924); renumbered from the draft's REL-2 because main's Release page (v1.0.61) already uses REL-1 to REL-8.* | DEL-5 | 59 | 3 | 3 | 0 | Write its tests (new requirement) |
| REL-11 | **A review hold before auto merge.** Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows the merge waiting on review. *renumbered from the draft's REL-3 because main's Release page (v1.0.61) already uses REL-1 to REL-8.* | DEL-13 | 37 | 3 | 3 | 0 | Run 4 tests not run yet |
| REL-12 | **Fast merge queue.** Pull requests merge one at a time per repo, across machines. A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together. When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next. *"yields its place" and the last sentence are new (the merge-queue risk); renumbered from the draft's REL-4 because main's Release page (v1.0.61) already uses REL-1 to REL-8.* | DEL-15, MON-15 | 65 | 3 | 3 | 0 | Run 2 tests not run yet |
| REL-13 | **Every release is noted.** Every release has a release note that says what changed and lists the issues it fixed; the test that proves each fix is Regression's (REG-6). *tests to split from DOC-10; renumbered from the draft's REL-5 because main's Release page (v1.0.61) already uses REL-1 to REL-8.* | DOC-10, REG-6 | 29 | 3 | 3 | to assign | Assign its tests when the source is split |

## Setup

Problem: One install makes any repo a workspace for any agent, without blocking and without overwriting.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| SET-1 | **One command adopts a repo.** One command sets up a new or existing repo: the loop settings, feature pages, Home, the scheduled regression and the health groups. It shows what it would change first, applies it on a branch through the loop, and adapts what is there instead of overwriting. | SET-1 | 50 | 3 | 3 | 1 | Run 10 tests not run yet |
| SET-18 | **Adoption never blocks, and health judges it.** Adoption never blocks: what doesn't fit is listed and filed as issues on the right feature, and the rest is adopted. A health check runs before and after, and the one after is green or names each gap with its fix. *split from SET-1; tests to split.* | SET-1 | 48 | 3 | 3 | to assign | Assign its tests when the source is split |
| SET-21 | **Adopted repos build on the template, not copies of it.** An adopted repo holds only its own settings, pages, tests and data. The loop's code lives once per machine in the installed template, so a fix or feature in the template reaches every repo through an update, never by rebuilding it there. *NEW: your rule, 2026-11-17; this is how it works today, but no requirement says so.* | new | 52 | 3 | 3 | 0 | Write its tests (new requirement) |
| SET-2 | **Layered settings.** Settings come in three layers: the template's defaults, the repo's committed settings, and my private local settings; a later layer overrides an earlier one. Every setting has a default and a one-line explanation, and I can see each value and its layer. | SET-2 | 44 | 3 | 3 | 3 | Run 3 tests not run yet |
| SET-4 | **Updates reach every repo.** An adopted repo can see what is new in the template and update to it, keeping its own settings, pages, rules and local settings. A repo running an older template version is flagged. | SET-4 | 37 | 3 | 3 | 0 | Run 7 tests not run yet |
| SET-19 | **Fixes flow back to the template.** A fix made in an adopted repo that belongs in the template is proposed back to the template as an issue. *split from SET-4; tests to split.* | SET-4 | 27 | 3 | 3 | to assign | Assign its tests when the source is split |
| SET-5 | **A self-describing workspace.** Every adopted repo has one entry page any new session reads first: how the parts fit together, which features exist and how to use them. It is generated from the feature pages and the committed settings only, so it is never stale and never carries one machine's local values. *"committed settings only" is new.* | SET-5 | 52 | 3 | 3 | 1 | Run 2 tests not run yet |
| SET-6 | **Adoption is proven.** Adoption is proven on test repos shaped like real ones, and every adoption defect found in a real repo adds a test repo that reproduces it. | SET-6 | 29 | 3 | 3 | 1 | Run 6 tests not run yet |
| SET-9 | **Learn from a repo already set up.** Setup can take an adopted repo as its model: it borrows that repo's settings shape, flow, milestone layout and private rules, never private values, and adapts them to the new repo. | SET-9 | 38 | 3 | 3 | 0 | Run 2 tests not run yet |
| SET-10 | **The right format for every agent.** The same skills are wired into each agent's own entry files, so Claude Code, Codex and other skill-reading agents run the same loop the same way. | SET-10 | 32 | 3 | 3 | 4 | Nothing: already proven |
| SET-11 | **A strict replay of the first adoption.** Adoption replays the first run step by step against a recorded good result. It stops at the first mismatch, says what differs and asks me, and never passes a step it cannot observe. | SET-11 | 40 | 3 | 3 | 1 | Run 2 tests not run yet |
| SET-12 | **Adopt all my repos in one pass.** From the operation session, one flow lists my GitHub repos by last push, lets me choose which to follow, clones and registers them, and updates each to the current template. It ends with the board showing exactly the repos I chose. | SET-12, MON-13 | 48 | 3 | 3 | 0 | Run 1 test not run yet |
| SET-14 | **The connectors each repo needs are checked.** For each followed repo, setup reads which connectors its feature pages need and probes each with a read-only call. It reports each as connected, needs sign-in or missing, with the fix, and never attaches or enables one itself. | SET-14 | 45 | 3 | 3 | 0 | Run 1 test not run yet |
| SET-16 | **One command judges a repo fully migrated.** One read-only command lists every gap between a repo and the current template, each with a one-line fix, and succeeds only when none remain. Health's Adoption group runs the same check. | SET-16 | 38 | 3 | 3 | 1 | Run 14 tests not run yet |
| SET-20 | **A repo behind the template says so.** A repo records the template version it is on, and one with none counts as behind. A session that starts in a repo behind the installed template is told so in one line; the cases where a new goal is refused are in How-to. *split from SET-16; tests to split.* | SET-16 | 51 | 3 | 3 | to assign | Assign its tests when the source is split |
| SET-3 | **Shipped as a versioned package.** The template ships as one versioned package of separate skills that works out of the box with a built-in default flow, and is proven to run in both Claude Code and Codex. The rules the package must pass are Guardrails' (GRD-20 to GRD-22). *changed: the Agensi rules move to Guardrails.* | SET-3 | 48 | 3 | 3 | 1 | Run 8 tests not run yet; fix 1 flaky |
| SET-7 | **Safe and repeatable.** A dry run lists everything before any write; running setup twice changes nothing the second time; nothing existing is overwritten. | SET-7 | 23 | 3 | 3 | 0 | Run 2 tests not run yet |

## Regression

Problem: Every requirement and every fix is proven by a test, fast in the loop and in full on a schedule.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| REG-1 | **Three kinds of tests.** Every Reviewed requirement has at least one requirement test, every whole flow has an end-to-end workflow test on a toy repo, and every fixed issue has a defect test. A requirement with no passing test shows as not enforced. | REG-1 | 43 | 3 | 3 | 2 | Run 5 tests not run yet |
| REG-2 | **Test format.** Every test is listed in one fixed format, grouped by feature, wherever tests are shown: its kind, what it guards, what it checks and its last result. | REG-2 | 29 | 3 | 3 | 3 | Run 3 tests not run yet |
| REG-3 | **One command, three places.** One command runs the suite the same way for me, the loop and GitHub Actions. | REG-3 | 19 | 3 | 3 | 4 | Nothing: already proven |
| REG-4 | **When tests run.** In the loop a goal runs only the tests its change affects plus its own new ones, and they run again on the merged result before a pull request merges. The full suite runs on the schedule and on every release, never on every goal, and I can run any part at any time. | REG-4 | 57 | 3 | 3 | 3 | Run 5 tests not run yet |
| REG-5 | **Failures go to GitHub.** Each failing test has one labelled issue, updated while it fails and closed when it passes. Known failures don't block, and nothing is written without --live. | REG-5 | 30 | 3 | 3 | 2 | Run 5 tests not run yet |
| REG-6 | **Every fixed issue leaves a test.** A goal that fixes an issue adds that issue's defect test, seen failing on the old code and passing on the fix, before the issue closes. A reopened issue's test is marked failing until it passes again. | REG-6 | 43 | 3 | 3 | 4 | Nothing: already proven |
| REG-7 | **Fast in the loop.** Every in-loop test run stays within a time budget, 15 minutes by default and never lower. A run that would go past it runs what fits and defers the rest to the full suite, naming how many. It is the only time limit on a lane. *changed: one lane limit (your decision, o39).* | REG-7 | 50 | 3 | 3 | 1 | Run 20 tests not run yet |
| REG-11 | **Preparation is budgeted too.** The work before a lane's first test, preparing, planning and waiting for a slot, has its own budget, 15 minutes by default and never lower. A lane that reaches it stops, says which part ran long, and can be rerun. *split from REG-7; tests to split.* | REG-7, GRD-2 | 44 | 3 | 3 | to assign | Assign its tests when the source is split |
| REG-8 | **Controllable.** Which tests run where, the schedule, the time limits and how many test lanes run at once are settings. | REG-8 | 20 | 3 | 3 | 2 | Run 2 tests not run yet; fix 1 flaky |
| REG-12 | **Lanes don't disturb each other.** Test lanes running side by side never share files or ports or time each other out, and a lane over its limit says so. *split from REG-8; tests to split.* | REG-8 | 29 | 3 | 3 | to assign | Assign its tests when the source is split |
| REG-9 | **Honest results.** Every test has been seen failing once, or shows as unproven. A test that fails then passes on the same commit is marked flaky, never silently retried. | REG-9 | 29 | 3 | 3 | 2 | Run 1 test not run yet |
| REG-10 | **Tests a machine can't run.** A test this machine can't run is skipped with its reason and never counted as seen failing. Its failing proof is recorded as owed, runs on a machine that can, and is written back with that machine and commit. An owed proof never blocks the goal, its merge or the release. | REG-10, GRD-11 | 56 | 3 | 3 | 1 | Run 9 tests not run yet |
| REG-13 | **One machine's failure is not the goal's failure.** A test that fails on one machine but passes on CI is filed as an issue and is not counted as a failure of the goal. *NEW: from #4921.* | new | 34 | 3 | 3 | 0 | Write its tests (new requirement) |
| REG-14 | **Caps on tests and suite time.** The number of tests and the full-suite time are capped by settings. A goal that takes the repo over a cap is refused at qa unless it removes or merges as many tests as it adds, or I raise the cap in my own words. The suite time is measured from the latest full run. *last sentence is new (#4920).* | GRD-13 | 61 | 3 | 3 | 4 | Nothing: already proven |
| REG-15 | **Coverage is measured in one place.** Each requirement's coverage step, from Stated to Fresh, is computed from the latest full run on main and shown beside it on its page. One test may prove several requirements. Nothing else is a source. *NEW: your rule, 2026-11-17 (o34): the coverage principle.* | new | 41 | 3 | 3 | 0 | Write its tests (new requirement) |
| REG-16 | **Coverage never drops silently.** A goal that would remove the only proof of a Reviewed requirement is refused at qa, and a release that lowers coverage needs my words. *NEW: your rule, 2026-11-17: the coverage principle.* | new | 29 | 3 | 3 | 0 | Write its tests (new requirement) |

## Automation

Problem: The important checks run on their own between my sessions and tell me by email.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| AUT-1 | **Routines run where they can run fully.** Health runs on my always-on machine for every repo; regression runs in GitHub Actions for a public repo and on that machine for a private one. Each report says where it ran, and a routine missed while the machine was off runs once at the next tick and says it was missed. | AUT-1 | 59 | 3 | 3 | 2 | Run 3 tests not run yet |
| AUT-2 | **Regression on a schedule.** The full regression suite runs on the schedule set in the repo's settings, every 4 hours by default, and on every release tag; I can also start it by hand. The report names every test it skipped and why. | AUT-2 | 43 | 3 | 3 | 2 | Run 2 tests not run yet |
| AUT-10 | **A private repo needs no Actions check to merge.** No GitHub Actions check this tool writes is needed to merge a private repo. Where the repo's rules require named checks, the pull-request checks post them as commit statuses. *split from AUT-2; tests to split.* | AUT-2 | 38 | 3 | 3 | to assign | Assign its tests when the source is split |
| AUT-3 | **Health on a schedule.** Health runs on my always-on machine on the schedule, after the latest finished regression run, with all its rule groups and the repo review. It uses my own login, and when the login has expired the report says so and the next round tries again. | AUT-3 | 49 | 3 | 3 | 4 | Nothing: already proven |
| AUT-4 | **A digest by email.** After each round, one email goes to the address I set: what ran, its results, and the new, still-open and fixed issues grouped by feature, each with its link and the request to give the agent. The same digest is posted on a pinned issue. | AUT-4 | 49 | 3 | 3 | 4 | Nothing: already proven |
| AUT-9 | **Every routine declares what it may do.** Each routine has allow and deny rules in the repo for the commands, files and sites its runbook needs. Setup writes them into the repo's project settings, so a scheduled run on a fresh machine stops at no approval prompt, and the docs check fails a routine with missing or contradicting rules. | AUT-9 | 59 | 3 | 3 | 1 | Run 7 tests not run yet |
| AUT-5 | **Under my control.** Each routine can be turned off or rescheduled in one setting. Without the secrets it needs, a routine runs, writes nothing and says what is missing. | AUT-5 | 29 | 3 | 3 | 4 | Nothing: already proven |
| AUT-6 | **Private address.** The email address and the mail key live only in one local secrets file outside git, shared by both mailers and read only by the local runner. They never appear in the repo, logs, issues or the digest, and mail goes only to the one address I set. *changed: one file for both mailers (your decision, o39).* | AUT-6, MCH-1 | 50 | 3 | 3 | 4 | Nothing: already proven |
| AUT-7 | **Bounded cost.** A round finishes within 45 minutes, and each report shows how long the round took. | AUT-7 | 17 | 3 | 3 | 1 | Run 3 tests not run yet |

## Documentation

Problem: Every feature page says what the feature does and how to use it, in one format, and my approved text stays as I wrote it.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| DOC-1 | **PRD template.** One template defines every feature page: Problem written from the user's side, Requirements as ID'd bullets under Functional and Non-functional, Non-goals, Success metrics and a generated Tests table. Nothing else goes on the page except the generated Deployments and Runbook sections. | DOC-1, DOC-7, DOC-8 | 43 | 3 | 3 | 3 | Run 10 tests not run yet |
| DOC-2 | **The PRD is mine.** Only I mark a page or a requirement Reviewed, in my own recorded words. After that its text does not change unless I un-review it, and a recorded message counts only for the pages or IDs it lists. | DOC-2 | 42 | 3 | 3 | 2 | Run 13 tests not run yet |
| DOC-20 | **Reviewed text is revised, never rewritten.** A change to a Reviewed requirement is a new revision with its date, reason and my approval; earlier revisions stay on the page. I review only the changed requirement, and no other requirement loses its review. IDs are never reused, and a dropped requirement stays, marked Retired. A requirement that moves without a change of text keeps its Reviewed mark. *NEW: the revision format.* | new | 66 | 3 | 3 | 0 | Write its tests (new requirement) |
| DOC-21 | **A code change alone never un-reviews a page.** A change to code or settings a page describes never needs my words when none of the page's own text changed, and a comments-only change doesn't make the page stale. *split from DOC-2; tests to split.* | DOC-2 | 38 | 3 | 3 | to assign | Assign its tests when the source is split |
| DOC-22 | **The PRD is read-only while a goal builds.** A goal never edits a Reviewed requirement while it builds, and a page has one writer at a time on any machine. A gap is filed as a finding on the feature's Backlog milestone and becomes a revision only when I approve it. A goal that changes a requirement states the new text in its done lines, approved before it starts. *NEW: your rule, 2026-11-17; replaces the standing un-review in MON-11.* | new | 69 | 3 | 3 | 0 | Write its tests (new requirement) |
| DOC-3 | **Tests follow on their own.** Once I review a PRD, the loop writes Given/When/Then tests for each requirement, links each to a regression test, and keeps them in step when a requirement changes. I never write or manage tests. | DOC-3 | 39 | 3 | 3 | 4 | Nothing: already proven |
| DOC-4 | **Home is one table.** Home holds one table with four columns: Feature, What it does, How to use and Milestone, and may lead with an optional Topic column. Below it Home carries only the generated Settings and Automation sections. *changed: optional Topic column (your decision, o39).* | DOC-4 | 39 | 3 | 3 | 3 | Run 2 tests not run yet; fix 1 flaky |
| DOC-18 | **Every feature has a How-to-use page.** Every feature has a How-to-use page for its users, in one fixed section order, and the docs check reports a feature without one. Home links each feature's How-to-use page. *changed: the README no longer links them (DOC-23).* | DOC-18, DOC-5 | 35 | 3 | 3 | 4 | Nothing: already proven |
| DOC-19 | **One How-to item per functional requirement.** Each How-to-use page has one item for every functional requirement of its feature, showing how it is delivered: a command and its output, an example, or a file or page it produces. The docs check fails a missing or unknown item. | DOC-19 | 47 | 3 | 3 | 4 | Nothing: already proven |
| DOC-6 | **Each skill's commands are documented.** Each skill's command map names every command, and its command reference gives each command's exact syntax, what it prints on success, and each refusal with its message and exit code. | DOC-6 | 35 | 3 | 3 | 2 | Run 1 test not run yet |
| DOC-9 | **Tests are a table.** Each page's Tests section is a table: Test, Kind, Guards, Checks, Last result. Every requirement and every defect has at least one row, and each test links to its entry on the full Tests page. | DOC-9 | 39 | 3 | 3 | 4 | Nothing: already proven |
| DOC-10 | **One Tests page.** One full Tests page is generated, listing every test with its latest result. | DOC-10 | 16 | 3 | 3 | 3 | Run 3 tests not run yet |
| DOC-14 | **A feature page lists what it ships.** A feature that ships a page people open or a delivery people receive lists it in a Deployments section: its link or channel, who can open or receives it, what it shows or sends, and its live status. Recipients are named as a group, never an address. | DOC-14 | 54 | 3 | 3 | 4 | Nothing: already proven |
| DOC-16 | **A runbook for each routine.** A page that owns a routine has a Runbook for it, saying what an agent told only "run routine X" must read and do, and a scheduled run follows it exactly. The docs check fails a registered routine with no runbook or a missing field. A runbook is not locked by my review. | DOC-16, AUT-8 | 58 | 3 | 3 | 0 | Run 10 tests not run yet |
| DOC-15 | **Home shows the setup and what runs by itself.** Home shows each setting with its meaning, default and this repo's value, and each routine with whether it is on, what it does, its cadence and where it runs. The docs check says stale when a setting or a workflow changes. *changed: the README no longer carries this (DOC-23).* | DOC-15 | 50 | 3 | 3 | 2 | Run 5 tests not run yet |
| DOC-11 | **Safe publish.** Publishing never deletes a wiki page and never overwrites one it didn't write unless I name it. The last publish can be undone. | DOC-11 | 25 | 3 | 3 | 4 | Nothing: already proven |
| DOC-12 | **Fast check.** The docs check finishes in under 30 seconds on this repo, every time. | DOC-12 | 15 | 3 | 3 | 4 | Nothing: already proven |
| DOC-13 | **Same answer every time.** The docs check is deterministic: the same pages and tests give the same result, with no AI judgment. | DOC-13 | 22 | 3 | 3 | 2 | Run 1 test not run yet |
| DOC-23 | **The README is the principles.** The README holds only its title, the principles, each with its diagram and the requirements that enforce it, and one link to Home. The docs check fails a README with any other section, and one whose principles differ from health's by a word. *NEW: your rule, 2026-11-17.* | new | 48 | 3 | 3 | 0 | Write its tests (new requirement) |

## Integrations (new)

Problem: The loop works with systems outside the repo, such as documents, trackers, mail, chat, agents and deploy targets, through one contract, so a new system plugs in without rebuilding anything and nothing outside can break or silently change the repo.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| INT-1 | **One contract for every integration.** Anything outside the repo that the loop works with, a document, a tracker, a mailbox, a chat, an agent or a deploy target, is an integration declared in one registry: what it carries, which way it flows, where its secrets live and the health rule that proves it is connected. It is opt-in per repo or page. *NEW: your generalization, 2026-11-17.* | DOC-17, SET-14 | 62 | 3 | 3 | 0 | Write its tests (new requirement) |
| INT-2 | **The repo stays the source of truth.** Every check, test and publish reads the repo's own copy and never the outside system. An integration that can't be reached says not connected, changes nothing and never breaks the loop. *tests to split from DOC-17.* | DOC-17 | 38 | 3 | 3 | to assign | Assign its tests when the source is split |
| INT-3 | **A difference is a delta, never a silent overwrite.** Where both sides can change the same thing, sync compares them with what they last agreed on. Each difference is a delta naming what changed and on which side, and it stays open until someone accepts one side's text. It is posted on the feature's Backlog milestone. *changed: where a delta is posted (your decision, o39).* | DOC-17 | 56 | 3 | 3 | 0 | Run 42 tests not run yet |
| INT-4 | **Nothing leaves without my say.** An integration reads by default. It writes outside only behind an explicit switch and, for shared text, an accepted delta. I attach each connector myself with the narrowest access, and its secrets live outside the repo. *tests to split from DOC-17 and SET-14.* | DOC-17, SET-14, GRD-5 | 41 | 3 | 3 | to assign | Assign its tests when the source is split |
| INT-5 | **Every integration is visible.** The board shows each integration's connection state and its open deltas as waiting on me, with the words to accept either side, and health counts an open delta or an unreadable integration as a finding, never as passing. *tests to split from MON-3 and HLT-2.* | MON-3, HLT-2 | 42 | 3 | 3 | to assign | Assign its tests when the source is split |
| INT-6 | **A new system is an adapter, not a rewrite.** Adding a system means one reader or writer, one registry row and one How-to page. No loop code changes, and an adopted repo gets it by declaring it, not by building it. *NEW: your generalization, 2026-11-17.* | new | 41 | 3 | 3 | 0 | Write its tests (new requirement) |
| INT-7 | **PRDs kept in an outside document.** A PRD lives in the repo by default. A page can opt in to keep step with an outside document, in Notion or behind a link, under this contract; the repo's copy stays the one every check reads. *first adapter; tests to split from DOC-17.* | DOC-1, DOC-17 | 44 | 3 | 3 | to assign | Assign its tests when the source is split |
| INT-8 | **Milestones kept in step with an outside page.** A repo can keep its GitHub milestones in step with an outside Milestones page under this contract, opt-in by one setting. *second adapter; tests to split from DOC-17.* | DOC-17 | 29 | 3 | 3 | to assign | Assign its tests when the source is split |

Already-built integrations register under this contract and keep their own requirements: the mail digest (AUT-4, AUT-6), connector checks (SET-14), agent profiles (DEL-16, SET-10) and deploy targets (DOC-14). GitHub itself is the one system the loop assumes.

## Guardrails

Problem: One visible set of protections, each pointing to the feature that owns it, proven on by health.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| GRD-1 | **One visible set of guardrails.** This page lists every guardrail with what it protects against, where it is enforced, the setting that controls it and the health rule that proves it is on. It points to the requirement that owns each one and restates none of the owner's text. | GRD-1 | 49 | 3 | 3 | 2 | Run 1 test not run yet |
| GRD-2 | **Budgets and caps stop a runaway.** Time, token and test budgets stop a goal or a step before it runs away. Goal budgets and the ETA are Delivery's (DEL-7, DEL-17); test-run and preparation budgets and the test caps are Regression's (REG-7, REG-11, REG-14). *index only.* | GRD-2 | 43 | 3 | 3 | 1 | Run 17 tests not run yet |
| GRD-15 | **Token counts are real or say unread.** Each step's tokens are read from its session record when the step is recorded. A goal with no token count shows "unread", never 0, so an unread count is never mistaken for an unspent budget. *split from GRD-2; tests to split.* | GRD-2 | 42 | 3 | 3 | to assign | Assign its tests when the source is split |
| GRD-3 | **Nothing private is committed.** Every commit, push and pull request passes the private-name scan, and local settings and private values are never written into a repo. A line in the list may be scoped to public repos or to named repos; an unscoped line applies everywhere. | GRD-3, DEL-9, SET-8, SET-15 | 46 | 3 | 3 | 1 | Run 11 tests not run yet |
| GRD-16 | **No commit skips the hooks.** A commit or push that skips the repo's hooks is refused by the loop's own commands and flagged by health. *split from GRD-3; tests to split.* | GRD-3 | 25 | 3 | 3 | to assign | Assign its tests when the source is split |
| GRD-4 | **A worker writes only its own goal's work.** A worker can't widen its own goal's touched files, resume itself or change its own budget, and it changes shared loop state only for its own goal through the goal's commands. Only the operation session can do the rest. | GRD-4 | 47 | 3 | 3 | 1 | Run 4 tests not run yet |
| GRD-5 | **Nothing is written to GitHub without --live.** Every command that writes issues, comments, milestones or releases previews by default and writes only behind an explicit --live switch; a token in the environment does not turn writing on. | GRD-5 | 37 | 3 | 3 | 0 | Run 4 tests not run yet |
| GRD-6 | **The base branch is protected.** The base branch refuses direct and force pushes, and a pull request merges only when the repo's required checks pass. I set those rules on the platform; setup never edits them, and health reads that they are set. | GRD-6 | 43 | 3 | 3 | 0 | Run 1 test not run yet |
| GRD-7 | **CI spends minutes only on runs that matter.** A newer run of the same workflow on the same branch cancels the one it replaces, and a heavy job is skipped for a change that touches no code. | GRD-7 | 37 | 3 | 3 | 0 | Run 1 test not run yet |
| GRD-17 | **Too many CI runs raise an alarm.** Runs or minutes per day past a set limit raise one alarm, and each round shows the Actions minutes it used. *split from GRD-7; tests to split.* | GRD-7 | 28 | 3 | 3 | to assign | Assign its tests when the source is split |
| GRD-8 | **A step far past its usual is flagged while it runs.** A step whose tokens or time pass a set multiple of that step's usual is flagged on the board and in the check-in while it runs. | GRD-8 | 37 | 3 | 3 | 0 | Run 1 test not run yet |
| GRD-9 | **Health proves every guardrail.** Each guardrail has a health rule that reads whether it is present and working, and each rule has a negative control run against a deliberately broken copy. A guardrail its rule can't read shows as unread, never as passing. | GRD-9 | 43 | 3 | 3 | 0 | Run 4 tests not run yet |
| GRD-10 | **Setup installs the whole set.** Adopting a repo installs every guardrail on this page with its default setting and lists each one installed, and health judges a freshly adopted repo on the same rules as the template. | GRD-10 | 37 | 3 | 3 | 0 | Run 1 test not run yet |
| GRD-12 | **Nothing starts under the memory floor.** No goal or test lane starts while free memory is below one setting, 3 GB by default and stated here only. A machine may set its own value locally. A lane already running is never stopped. *changed: 3 GB default (your decision, o39).* | GRD-12, REG-7, MON-12 | 42 | 3 | 3 | 0 | Run 1 test not run yet |
| GRD-18 | **Windows-safe.** A pull request that adds a POSIX-only call without its guard fails its checks, and long text for an issue, comment, pull request or release note is always passed to gh in a file, so nothing breaks on native Windows. | DEL-12, REG-7, AUT-1, HLT-4, DOC-10 | 41 | 3 | 3 | 0 | Run 1 test not run yet |
| GRD-19 | **A page stays small enough to review.** A feature page holds at most the number of requirements one setting allows, and health's Size group reports a page over it. *split from GRD-9; tests to split.* | GRD-9 | 29 | 3 | 3 | to assign | Assign its tests when the source is split |
| GRD-20 | **The package always passes Agensi's rules.** No release is cut unless the built package passes every rule Agensi publishes: the file, size and text-only limits of both upload routes, what a buyer's agent is sent, scripts that each run alone, the eight security checks and the listing limits. A failure names the rule and the file. *your hard requirement, 2026-11-17; split from SET-3; tests to split.* | SET-3 | 56 | 3 | 3 | to assign | Assign its tests when the source is split |
| GRD-21 | **Our package limits are never looser than Agensi's.** One table on this page states each package limit: Agensi's figure, ours, and the date Agensi's page was last read. Ours may be tighter, never looser. Raising one of ours takes my own words, and health warns when the last read is over 30 days old. *NEW: your hard requirement, 2026-11-17; the repo's table missed one Agensi limit and misstates another.* | new | 54 | 3 | 3 | 0 | Write its tests (new requirement) |
| GRD-22 | **A goal learns at qa that it doesn't fit.** A goal that adds a shipped file or grows a script past a package limit is refused at qa, not at release, unless it frees as much room as it takes. The refusal says how much room is left and what would free it. *NEW: from prd-revisions today, which found at design review that the package is full.* | new | 53 | 3 | 3 | 0 | Write its tests (new requirement) |

### Agensi's rules, as Agensi publishes them (read 2026-11-17)

This is the table GRD-21 asks for. Source: Agensi's own docs pages Package your skill, Submit from your agent, Review and approval, and How agents load skills. "Package today" is main at v1.0.57.

| Rule | Agensi's figure | Kind | Our gate today | Package today |
|---|---|---|---|---|
| Upload on the website | 1,000 files, 50 MB ZIP | Hard | Not used | 100 files, 1.81 MB |
| Upload from an agent | 100 files, 5 MB, text only | Hard, for that route only | 100 files, 5 MB | **100 of 100: full** |
| What a buyer's agent is sent | Every SKILL.md, plus up to 200 other text files, within 6 million characters per listing. Anything beyond is not delivered | Hard | **Not checked, and not in the repo's rule table** | 93 other files, 1.9 million characters |
| Skills per pack | 50 | Hard | Not checked | 7 |
| Script size | "Keep the logic in each script under 20 KB so it stays easy to review." Data inside the script doesn't count | Guideline | Stricter: the whole file under 20,480 bytes, data included; health warns over 19,000 | None over; 72 of 82 scripts are over 18,000 bytes |
| Scripts run alone | Each is written to a temporary file, run and removed, so it can't read another package file | Hard: it is how delivery works | Checked: each script is run alone | Passes; one helper is copied into three skills because of it |
| File types | Text and code. Executables fail. No bundled dependencies. Images and PDFs are allowed but never delivered | Hard | Checked | Passes |
| Security scan | Eight checks; each failed check takes 20 points off a score of 100, and a person decides | Scored | Six of eight checked. shell=True prints a note and does not fail (3 scripts have it). Environment harvesting and network-with-local-data are not checked | Would lose points for shell=True |
| Listing | Name up to 60 characters and unique; summary up to 300; 10 tags, 10 keywords, 8 use cases; up to 3 categories | Hard | Summary, tags, keywords and use cases checked; name length and categories not checked | Summary 292; 8 tags, 8 keywords, 7 use cases |
| Updates | Version higher than the last; changelog up to 2,000 characters | Hard | Not verified | Not verified |
| Nothing installed on the buyer's machine | Plugins, hooks and slash commands can't be sold, and agents are told never to save a skill's scripts into project or skill folders | Policy | Not checked | **Open question:** setup installs Claude hooks and git hooks, which need a script that stays on disk. I did not test how that behaves for a buyer |

**Package structure (your words, o38, replacing o37): not split for now.** The template stays one package at 100 files, and a goal that needs room frees it first (GRD-22). Splitting stays an option for later.


## Health

Problem: A reviewer and fixed checks tell me, per feature, where the repo falls short of its own PRDs, and what they find becomes work.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| HLT-2 | **The rules.** Health checks twelve fixed rule groups, each from a stated angle, and each belongs to one of the principles the README shows. The report gives one verdict for each principle, red when any of its groups fails, and every principle has at least one rule that can fail. Adding a group means retiring one. Each group's rules are listed in How-to. *changed: the groups roll up to principles; Docs folds into Consistency and a new group, Attention, checks principle 8 (your rule, 2026-11-17).* | HLT-2 | 63 | 3 | 3 | 2 | Run 14 tests not run yet |
| HLT-3 | **Formal report with one findings table.** The report lists every group it ran, then one findings table sorted by feature, then each rule marked pass, warn, fail or unread with its fix, then one verdict. A rule that can't read its data is never shown as passing. | HLT-3 | 47 | 3 | 3 | 4 | Nothing: already proven |
| HLT-4 | **Findings become issues.** Each finding is one GitHub issue tagged with its group and its feature. A preview lists what would be opened, updated, closed or reopened, and nothing is written until I confirm. A repeat updates its issue, a fix closes it and a return reopens it, never a duplicate. | HLT-4 | 51 | 3 | 3 | 2 | Run 8 tests not run yet |
| HLT-8 | **Triage.** Open findings are shown per feature with their kind, age and count. When I close a batch, each is closed with my words as the reason, and it isn't refiled unless the evidence changes. | HLT-8 | 35 | 3 | 3 | 2 | Run 1 test not run yet |
| HLT-10 | **Every feature has a Backlog milestone.** Every feature has one standing Backlog milestone, and "Backlog: Other" holds what fits no feature. Adoption creates the missing ones, and health warns for each that is absent. | SET-17, DOC-10 | 34 | 3 | 3 | 0 | Run 3 tests not run yet |
| HLT-12 | **A filed finding becomes work.** When the next goals are planned, the open defect and backlog issues are read by feature and goals are proposed from them, most blocking first, so a filed finding is picked up or closed with my words, never left unseen. *NEW: the missing link in the improvement loop; needs your decision.* | new | 45 | 3 | 3 | 0 | Write its tests (new requirement) |
| HLT-5 | **Repo review.** A reviewer, separate from the rules and never part of the verdict, reads every page, issue, test and the code, feature by feature, and reports conflicts, gaps, drift, weak tests and savings, ending with ranked next steps per feature. Wording changes it suggests are applied only by me. | HLT-5 | 50 | 3 | 3 | 2 | Run 3 tests not run yet |
| HLT-6 | **Every rule can fire.** Every health rule has a negative control that proves it can fire. | HLT-6 | 16 | 3 | 3 | 3 | Run 1 test not run yet |
| HLT-11 | **Health keeps the repo lean.** Health flags an in-loop test run over its time budget, naming the slowest tests to move to the full suite, and flags stale worktrees and branches, printing the commands that remove them without running them. It warns on a script over 19,000 bytes and fails one at 20 KB. *split from HLT-6; tests to split; size rule (your decision, o39).* | HLT-6 | 54 | 3 | 3 | to assign | Assign its tests when the source is split |
| HLT-1 | **Deterministic and read-only.** The rule check gives the same answer twice on an unchanged repo and changes nothing; it writes only reports and GitHub issues. | HLT-1 | 25 | 3 | 3 | 2 | Run 1 test not run yet |
| HLT-7 | **Fast check.** The rule check, run without its controls, finishes in under 60 seconds on this repo. | HLT-7 | 17 | 3 | 3 | 4 | Nothing: already proven |
| HLT-9 | **Evidence or nothing.** Every review finding names its feature and cites its evidence: a page and requirement ID, a file and line, a test or an issue. A finding without evidence is dropped, and nothing is filed twice. | HLT-9 | 38 | 3 | 3 | 1 | Run 2 tests not run yet |
| HLT-13 | **Conflicts and orphans are findings.** Health flags two requirements that conflict or repeat, and any test, script or goal that names no requirement. Each is settled by a revision that merges, retires or rewords, or by a removal. *NEW: your rule, 2026-11-17: the coverage principle, across and up.* | new | 38 | 3 | 3 | 0 | Write its tests (new requirement) |

## Machines

Problem: A second machine reaches the same working setup from a clone and one command, and a machine that has drifted says so.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| MCH-1 | **One command sets a machine up.** A second Mac or Windows machine reaches this one's setup from a git clone and one command: a dry run lists everything first, then apply installs the skill links, the hooks and the empty private files. Every item has a Windows form or is named as not yet possible. | MCH-1 | 55 | 3 | 3 | 1 | Run 8 tests not run yet; fix 2 flaky |
| MCH-2 | **A drifted machine says so.** The machine check lists one line per gap between this machine and the expected setup, such as a skills checkout that is behind or a clone with no hooks. *split from MCH-1; tests to split.* | MCH-1 | 34 | 3 | 3 | to assign | Assign its tests when the source is split |
| MCH-3 | **No routine stops to ask.** Each scheduled task keeps its full prompt in a local routine file, and the machine check fails a task whose recorded permission mode would prompt or is missing. *split from MCH-1; tests to split.* | MCH-1 | 33 | 3 | 3 | to assign | Assign its tests when the source is split |
| MCH-4 | **Prerequisites first.** Before it writes anything, setup prints one checklist of what this machine needs: git, python3, gh signed in as me, real symlinks and a supported platform, each marked present or missing with its fix. *tests to split from SET-11.* | SET-11 | 36 | 3 | 3 | to assign | Assign its tests when the source is split |
| MCH-5 | **A goal started on another machine can be adopted.** A goal started on another machine can be adopted here from its pushed branch, frozen goal file and open pull request; qa, ship and the pull request run again here before release. A branch that isn't pushed, or a goal with no done line or pull request, is refused. | DEL-10, DEL-11 | 58 | 3 | 3 | 2 | Run 1 test not run yet; fix 2 flaky |
| MCH-6 | **A machine keeps its private data to itself.** Each machine's private files, the private-name lists, mail settings, secrets and local overrides, stay outside the repo and are never copied to another machine, a log or a report. A new machine gets empty private files and asks me to fill them. *NEW: your rule, 2026-11-17 (o44), from the PC's mapping (J37).* | new | 50 | 3 | 3 | 0 | Write its tests (new requirement) |

## Operation (was Monitoring, part 1)

Problem: One session governs: it starts every ready goal in its own worker, passes my answers along, runs unattended and never builds.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| MON-1 | **One command starts the operation session.** One command starts the operation session and drives the whole process the same way every time. It governs only: it never builds. | MON-1 | 28 | 3 | 3 | 4 | Nothing: already proven |
| MON-20 | **Every ready goal gets its own worker.** The operation session plans queued goals as a dependency graph and gives every goal whose dependencies are met its own worker session, in parallel. A goal waits only on goals it truly depends on; sharing files is not a reason to wait. *split from MON-1; tests to split.* | MON-1 | 49 | 3 | 3 | to assign | Assign its tests when the source is split |
| MON-2 | **Live communication.** A worker reports each change of step or status as it happens, and its result when it ends; the operation session sends a worker its answer or a follow-up. Background processes are used only when a session can't be started or reached, and the board says so. | MON-2 | 49 | 3 | 3 | 3 | Run 1 test not run yet |
| MON-6 | **Clean up after every goal.** When a goal merges, its worker session is given the next ready goal or archived, and its worktree and branch are removed. | MON-6 | 27 | 3 | 3 | 4 | Nothing: already proven |
| MON-10 | **Re-plan at every check-in.** At each check-in the operation session re-reads every goal's progress and re-plans to finish soonest: it merges goals that do the same thing, splits a goal that blocks others, and puts the critical path first. It never stops a running goal to re-plan, and every change is logged with its reason. | MON-10 | 55 | 3 | 3 | 4 | Nothing: already proven |
| MON-11 | **Full auto mode.** Full auto is off in a new repo until I turn it on. With it on, the operation session applies every recommendation without asking, except a safety class: destructive, money, security, private data, a merge on another machine, or anything that contradicts my words. Those wait for me. A safety class is judged by what the action does, not by a word in its name. *first and last sentences are new (off by default: your decision, o39; today's misjudged questions).* | MON-11 | 68 | 3 | 3 | 4 | Nothing: already proven |
| MON-12 | **Session pool.** The operation session keeps a pool of idle worker sessions, sized by one setting, and hands each ready goal one from the pool. When the pool runs low it asks me to fill it, at the desktop. When I've chosen app sessions, a goal never falls back to a background worker: it waits and says so. | MON-12, SET-13 | 58 | 3 | 3 | 2 | Run 1 test not run yet |
| MON-13 | **Two layers per pod.** One operation session governs every repo in its pod directly and talks to each worker, with no per-repo operation session. Several pods may run at once, independently. | MON-13 | 31 | 3 | 3 | 2 | Run 1 test not run yet |
| MON-15 | **Pods coordinate through shared state.** Every goal records the pod that owns it, and only that pod starts, answers, merges or resumes it; other pods see it read-only. | MON-15 | 28 | 3 | 3 | 1 | Run 5 tests not run yet |
| MON-16 | **Fill every free slot at once.** When goals are ready and slots, sessions and memory are free, every one starts in the same pass; budgets still hold. A ready goal waits while live goals, weekly plan usage or free memory are past their limits, and the check-in names the limit. | MON-16, MON-12 | 50 | 3 | 3 | 1 | Run 3 tests not run yet |
| MON-18 | **I say it once.** One standing instruction to merge, recorded once for named goals or all, replaces a go per merge, and a worker accepts an owner record the operation session names without asking me again. A record covers only the IDs it lists. | MON-18 | 44 | 3 | 3 | 0 | Run 5 tests not run yet |
| MON-23 | **The operation session keeps itself running.** On start the operation session runs a self-check and lists what is missing, each with its fix. It re-creates its check-in timer before the timer expires, and warns before the app's limit on unanswered messages is reached. *split from MON-18; tests to split.* | MON-18 | 43 | 3 | 3 | to assign | Assign its tests when the source is split |
| MON-7 | **Govern only.** A check-in never edits code, commits or pushes from the operation session; only merges and the post-merge steps change the repo. | MON-7 | 23 | 3 | 3 | 1 | Run 2 tests not run yet |
| MON-8 | **No silent worker.** A worker with no report for 30 minutes shows under Needs you. | MON-8 | 15 | 3 | 3 | 2 | Run 1 test not run yet |

## Check-in and board (was Monitoring, part 2)

Problem: I can see what is running, stuck or waiting on me, the same way every time, without opening each session.

| ID | Requirement | From | Words | Size | Scope | Proof today | To reach 10 |
|---|---|---|---|---|---|---|---|
| CHK-1 | **Live board.** Report, dashboard and "where do things stand?" print the live board in one fixed layout: issues first with their fix, then running goals with progress and time left, then queued goals and dependencies. Merged work and history are left out, and a stuck worker stays at the top until I answer. | MON-3, MON-4 | 53 | 3 | 3 | 2 | Run 40 tests not run yet |
| CHK-2 | **A check-in on a cadence, in one layout.** The operation session checks in on a set cadence, 30 minutes by default, and at once when a worker reports something new. Every full check-in has the same layout: headline, machine line, all sessions, dependencies, needs you, coming up. A hook blocks a reply that doesn't follow it. *changed: "full" check-in (your decision, o39).* | MON-5 | 56 | 3 | 3 | 2 | Run 15 tests not run yet |
| CHK-3 | **Notify me by mail.** When notification is on for this machine, each check-in mails me once per new event, such as a new Needs you item or a goal that stopped or passed its ETA. *split from MON-5; tests to split.* | MON-5 | 35 | 3 | 3 | to assign | Assign its tests when the source is split |
| CHK-4 | **A check-in with nothing new costs nothing.** A scheduled check-in that is the same as the last full one, apart from its machine line and numbers, is one line, printed without a model turn, for at most two hours in a row. Each check-in logs the tokens the operation session spent. *split from MON-5; tests to split; one line allowed (your decision, o39).* | MON-5 | 51 | 3 | 3 | to assign | Assign its tests when the source is split |
| CHK-5 | **Dependency map.** The check-in's dependency map is grouped by repo, then by release. Each goal shows its status, expected time left and machine; each release shows its expected time and how many goals haven't started; only live goals are drawn. | MON-14 | 40 | 3 | 3 | 1 | Run 8 tests not run yet |
| CHK-6 | **What a check-in shows of other machines.** A check-in lists this machine's goals in full and, for every other machine, one row per goal with its agent, step and status from that machine's latest report. It never asks me another machine's questions. *CHANGED to match your both-machines table (o9); needs your decision.* | MON-17 | 42 | 3 | 3 | 0 | Run 1 test not run yet |
| CHK-7 | **Blockers first.** Each item under Needs you says what it holds up and whether it is on the critical path to the next release, and items are sorted with the one holding up the most goals first. | MON-19 | 37 | 3 | 3 | 4 | Nothing: already proven |
| CHK-8 | **Fast board.** The live board builds and prints in under 10 seconds on this repo. | MON-9 | 15 | 3 | 3 | 4 | Nothing: already proven |
| CHK-9 | **I can answer and steer from my phone or mail.** I can answer any question under Needs you by replying to its mail or from my phone, with the same words a typed answer takes, and start, stop or reorder goals the same way. A reply counts as my words only when it comes from my own address or signed-in session. *NEW: your rule, 2026-11-17 (o44), from the PC's mapping: #4785, #4805.* | new | 61 | 3 | 3 | 0 | Write its tests (new requirement) |

## What I did not check

- I rewrote from each requirement's text. Where a long bullet's detail was cut for length, I kept the promise and left the detail for How-to; I did not read the code to confirm each promise is built.
- "Proof today" adds up the tests of the requirements each one came from. After a split or merge the tests need to be re-linked, so these are estimates.
- Scope 3 is my judgment that each is one promise in the right place. It is the part to challenge.
- Applying this changes Reviewed text, so it needs your un-review words for the pages it touches, and it is a goal of its own.
