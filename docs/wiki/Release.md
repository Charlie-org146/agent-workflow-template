<!-- workflow-docs -->
# Release

Review: **Unreviewed** <!-- kept merge-queue-ci@2b2c3a54a -->

How to use: [How-to-use-Release](How-to-use-Release)

## Problem

- Goals keep landing fixes while a release is being deployed, so quality drifts and I can't say what a version really holds.
- Nothing stops a milestone shipping with open issues, a red test, a failing health check, requirements I never reviewed or stale docs.
- When a release goes wrong I have no snapshot to go back to, so a bad release is repaired forward.

## Requirements

### Functional

None

### Non-functional

None

## Non-goals

- Staging, release-candidate tags and the promotion of a minor or a patch belong to release-channels (Delivery); this page covers only a major.
- The gate never fixes a failure and never moves an issue itself except one the owner waived by name.

## Success metrics

- No major ships with an open milestone issue, a red unwaived row, a failing health check, an Unreviewed requirement or a stale page.
- Every major leaves a `vX.0.0` tag, a `release/vX` branch and a state report, and `revert vX` can put main back.

## Revisions

### Retired

- REL-1: moved to DEL-1
- REL-10: moved to DEL-1
- REL-11: moved to DEL-1
- REL-12: moved to DEL-3
- REL-13: moved to DEL-17
- REL-14: moved to DEL-1
- REL-15: moved to DEL-17
- REL-2: moved to DEL-1
- REL-3: moved to DEL-1
- REL-4: moved to DEL-1
- REL-5: moved to DEL-1
- REL-6: moved to DEL-1
- REL-7: moved to DEL-1
- REL-8: moved to DEL-1
- REL-9: moved to DEL-1

### REL-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | A version number says what changed <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. <br> A goal's release never bumps a major; a major exists only after the gate passes. | consolidation (TOP-DECISION 89): absorbed into REL-3 | o229: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A version number says what changed <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. <br> A goal's release never bumps a major; a major exists only after the gate passes. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | A version number says what changed, and a major ships only through the gate <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. <br> A goal's release never bumps a major: `release.py` refuses it, naming `review.py promote`, so a major version exists only after the gate passed. | migration r1; date from the run day | o51: "Yes to both" |

### REL-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | A major's milestone is closed out <br> Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue. | consolidation (TOP-DECISION 89): absorbed into REL-3 | o230: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A major's milestone is closed out <br> Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Every issue on the milestone is closed, or the owner moved it by name <br> `review.py gate vX` lists the open issues of milestone `vX.0` and refuses each one, naming its number. <br> An issue passes only with a release waiver of kind `moved` whose owner-words record names the issue; a record that does not name it, or does not exist, waives nothing. | migration r1; date from the run day | o51: "Yes to both" |

### REL-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r6 | 2026-11-20 | A major ships only through the gate <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. A goal's release never bumps a major; a major exists only after the gate passes. [REL-1] <br> Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue. [REL-2] <br> The gate runs the whole nightly suite on the release candidate. Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. [REL-3] <br> The suite may instead come from a GitHub Actions run of the regression workflow (review.py gate or promote with --suite-from RUN), but only a run on the candidate's commit that completed with every shard reported, nothing UNRUN and every land or nightly row logged; any other run refuses "suite run does not cover the candidate", and the run id is recorded with the gate result. [REL-3] <br> The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails. [REL-4] <br> From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals. [REL-5] <br> Promoting a major runs only from the operation session with my record naming that version and every gate check passing. It tags the major, keeps a snapshot branch, and mails a state report as the release notes. [REL-6] <br> Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject. [REL-8] <br> revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it. [REL-7] <br> (v2.0 planned) release-readiness: a release-readiness check runs before the gate (named only). | readme-six: absorbed into DEL-1 (o514) | o600: "yes build it" |
| r5 | 2026-11-19 | A major ships only through the gate <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. A goal's release never bumps a major; a major exists only after the gate passes. [REL-1] <br> Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue. [REL-2] <br> The gate runs the whole nightly suite on the release candidate. Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. [REL-3] <br> The suite may instead come from a GitHub Actions run of the regression workflow (review.py gate or promote with --suite-from RUN), but only a run on the candidate's commit that completed with every shard reported, nothing UNRUN and every land or nightly row logged; any other run refuses "suite run does not cover the candidate", and the run id is recorded with the gate result. [REL-3] <br> The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails. [REL-4] <br> From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals. [REL-5] <br> Promoting a major runs only from the operation session with my record naming that version and every gate check passing. It tags the major, keeps a snapshot branch, and mails a state report as the release notes. [REL-6] <br> Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject. [REL-8] <br> revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it. [REL-7] <br> (v2.0 planned) release-readiness: a release-readiness check runs before the gate (named only). | consolidation (TOP-DECISION 89): second revision (TOP-DECISIONs 91, 94, 95) | o361: "I want to merge the 2.1 into 2.0 ... (owner ~01:35, o355)" |
| r4 | 2026-11-19 | A major ships only through the gate <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. A goal's release never bumps a major; a major exists only after the gate passes. [REL-1] <br> Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue. [REL-2] <br> The gate runs the whole nightly suite on the release candidate. Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. [REL-3] <br> The suite may instead come from a GitHub Actions run of the regression workflow (review.py gate or promote with --suite-from RUN), but only a run on the candidate's commit that completed with every shard reported, nothing UNRUN and every land or nightly row logged; any other run refuses "suite run does not cover the candidate", and the run id is recorded with the gate result. [REL-3] <br> The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails. [REL-4] <br> From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals. [REL-5] <br> Promoting a major runs only from the operation session with my record naming that version and every gate check passing. It tags the major, keeps a snapshot branch, and mails a state report as the release notes. [REL-6] <br> Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject. [REL-8] <br> revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it. [REL-7] <br> (v2.1 planned) release-readiness: a release-readiness check runs before the gate (named only). | consolidation (TOP-DECISION 89) | o228: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r3 | 2026-11-19 | The full suite passes on the candidate <br> The gate runs the whole nightly suite on the release candidate. <br> Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. <br> The suite may instead come from a GitHub Actions run of the regression workflow (review.py gate or promote with --suite-from RUN), but only a run on the candidate's commit that completed with every shard reported, nothing UNRUN and every land or nightly row logged; any other run refuses "suite run does not cover the candidate", and the run id is recorded with the gate result. | a CI run of the regression workflow is an accepted suite source for the gate (TOP-DECISION 36) | o191: "TOP-DECISION 36 under the owner's delegation (o168), ~18:12: freeze gate-ci-suite on a" |
| r2 | 2026-11-18 | The full suite passes on the candidate <br> The gate runs the whole nightly suite on the release candidate. <br> Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | The full regression suite passes on the release candidate, and each known-red row is fixed or waived with an issue <br> The gate runs the whole nightly suite on a checkout of the candidate, not the goal lane. <br> A row that fails, could not run or is on the known-red list refuses, naming the row, unless a `red` waiver gives its issue and its owner record names the row; a suite that did not run refuses. <br> A suite that runs past `max_suite_seconds` is not itself a refusal (health reports that cap); the gate waits up to four hours (`LOOP_GATE_SECONDS`), and a run a time budget stopped with rows left refuses, since rows that did not run prove nothing. | migration r1; date from the run day | o51: "Yes to both" |

### REL-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Health, review and pages pass on the candidate <br> The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails. | consolidation (TOP-DECISION 89): absorbed into REL-3 | o231: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Health, review and pages pass on the candidate <br> The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Health passes, every requirement is Reviewed by the owner, and no wiki page is stale <br> The gate runs the health check on the candidate and refuses unless it prints `HEALTH: green`. <br> It refuses each requirement on a feature page that is still Unreviewed, naming the requirement and its page, and each page the docs audit calls stale. | migration r1; date from the run day | o51: "Yes to both" |

### REL-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | A candidate admits only gate fixes <br> From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals. | consolidation (TOP-DECISION 89): absorbed into REL-3 | o232: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A candidate admits only gate fixes <br> From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Once the release candidate is cut, only fixes for gate failures enter staging <br> From a major's `vX.0.0-rc.N` tag until the `vX.0.0` tag exists, `merge.py` refuses a goal with `frozen for vX.0.0`. <br> A goal passes only when its goal file names a subject of the last gate run's refusals: an issue, a row, a requirement, a page or `health`; before any gate run, none passes. | migration r1; date from the run day | o51: "Yes to both" |

### REL-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Promotion tags, snapshots and reports <br> Promoting a major runs only from the operation session with my record naming that version and every gate check passing. <br> It tags the major, keeps a snapshot branch, and mails a state report as the release notes. | consolidation (TOP-DECISION 89): absorbed into REL-3 | o233: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Promotion tags, snapshots and reports <br> Promoting a major runs only from the operation session with my record naming that version and every gate check passing. <br> It tags the major, keeps a snapshot branch, and mails a state report as the release notes. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Promoting a major tags it, keeps a snapshot branch and sends a state report <br> `review.py promote vX --owner-record ID` runs only in the operation session, only when that owner-words record names `vX.0.0`, and only when every gate check passes; a refusal makes no tag, branch or release. <br> It moves main to the candidate by fast-forward, tags `vX.0.0`, keeps branch `release/vX`, and moves waived issues to the milestone the waiver names. <br> The state report (review state of each page, test results, health, closed issues, changes since the last major) is the release's notes and is mailed; a machine with no mail secrets prints `EMAIL not sent` and the report path, and the tag stays. | migration r1; date from the run day | o51: "Yes to both" |

### REL-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | A major can be reverted <br> revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it. | consolidation (TOP-DECISION 89): absorbed into REL-3 | o234: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | A major can be reverted <br> revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | `revert vX` puts main back on the snapshot through a pull request <br> It pushes a branch whose tree is `release/vX`'s on top of the base, and opens a pull request to the base; it never pushes the base itself. <br> It refuses when `release/vX` does not exist, and a worker cannot run it. | migration r1; date from the run day | o51: "Yes to both" |

### REL-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | Promotion and waivers are my words <br> Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject. | consolidation (TOP-DECISION 89): absorbed into REL-3 | o235: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | Promotion and waivers are my words <br> Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Promotion and every waiver are the owner's words, never a worker's or a peer session's <br> Only the operation session runs `promote` or `revert`; a worker is refused with `REVIEW_ROLE`. <br> A waiver counts only when its owner-words record exists and names its subject, and the record id is kept beside the waiver in the git folder, outside the repo. | migration r1; date from the run day | o51: "Yes to both" |

### REL-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | The merge's wiki check refuses only for what the goal changed <br> `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it, and a page only merge.py's own re-render of the Tests tables changed counts as left alone. <br> Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so. <br> On the base branch itself every finding counts. | consolidation (TOP-DECISION 89): absorbed into DEL-1 | o227: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r2 | 2026-11-18 | The merge's wiki check refuses only for what the goal changed <br> `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it, and a page only merge.py's own re-render of the Tests tables changed counts as left alone. <br> Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so. <br> On the base branch itself every finding counts. | merge.py re-renders other pages Tests tables on the goal branch; those pages are not the goal pages | o56: "Yes, start it" |
| r1 | 2026-11-18 | The merge's wiki check refuses only for what the goal changed <br> `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it. <br> Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so. <br> On the base branch itself every finding counts. | migration r1; date from the run day | o51: "Yes to both" |

### REL-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Every goal ends with a release <br> With auto_merge on, a finished goal is merged and released automatically: version bump, release note, published release and wiki. <br> With auto_merge off it makes a draft release and merges nothing. <br> Any failure shows under Needs you. | consolidation (TOP-DECISION 89): absorbed into DEL-1 | o224: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Every goal ends with a release <br> With auto_merge on, a finished goal is merged and released automatically: version bump, release note, published release and wiki. <br> With auto_merge off it makes a draft release and merges nothing. <br> Any failure shows under Needs you. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A merge is never refused late or left half done <br> A merge is refused only for a page the goal's own change made stale, and the pull-request checks catch that before a merge slot is spent. <br> If the merge lands but the release fails, the goal reads "merged, release owed", and a second run finishes it without merging twice. | consolidation (TOP-DECISION 89): absorbed into DEL-1 | o225: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A merge is never refused late or left half done <br> A merge is refused only for a page the goal's own change made stale, and the pull-request checks catch that before a merge slot is spent. <br> If the merge lands but the release fails, the goal reads "merged, release owed", and a second run finishes it without merging twice. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-12

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-20 | Merges wait only on gates I set <br> Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows the merge waiting on review. [REL-12] <br> No GitHub Actions check this tool writes is needed to merge a private repo. Where the repo's rules require named checks, the pull-request checks post them as commit statuses. [AUT-10] | readme-six: absorbed into DEL-3 (o514) | o611: "yes build it" |
| r2 | 2026-11-19 | Merges wait only on gates I set <br> Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows the merge waiting on review. [REL-12] <br> No GitHub Actions check this tool writes is needed to merge a private repo. Where the repo's rules require named checks, the pull-request checks post them as commit statuses. [AUT-10] | consolidation (TOP-DECISION 89) | o344: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A review hold before auto merge <br> Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows the merge waiting on review. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-13

| rev | date | text | why | approved |
|---|---|---|---|---|
| r5 | 2026-11-20 | Fast merge queue <br> Pull requests merge one at a time per repo, across machines. [REL-13] <br> A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together. [REL-13] <br> When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next. [REL-13] <br> (v2.0 planned) merge-queue: a merge queue (named only). <br> (v2.0 planned) A commit that moves only stamp files (the version, the changelog, the regression run and issue records) is tree-equal modulo stamps: a pass recorded for the tested tree carries to it, with no fresh CI run. [REL-13] | readme-six: absorbed into DEL-17 (o514) | o604: "yes build it" |
| r4 | 2026-11-19 | Fast merge queue <br> Pull requests merge one at a time per repo, across machines. [REL-13] <br> A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together. [REL-13] <br> When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next. [REL-13] <br> (v2.0 planned) merge-queue: a merge queue (named only). <br> (v2.0 planned) A commit that moves only stamp files (the version, the changelog, the regression run and issue records) is tree-equal modulo stamps: a pass recorded for the tested tree carries to it, with no fresh CI run. [REL-13] | merge-queue-b stamp bullet (TOP-DECISION 113) | o419: "approved by operation-top under owner delegation (DOC-2, o371); TOP-DECISION 113: add the" |
| r3 | 2026-11-19 | Fast merge queue <br> Pull requests merge one at a time per repo, across machines. [REL-13] <br> A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together. [REL-13] <br> When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next. [REL-13] <br> (v2.0 planned) merge-queue: a merge queue (named only). | consolidation (TOP-DECISION 89): second revision (TOP-DECISIONs 91, 94, 95) | o360: "I want to merge the 2.1 into 2.0 ... (owner ~01:35, o355)" |
| r2 | 2026-11-19 | Fast merge queue <br> Pull requests merge one at a time per repo, across machines. [REL-13] <br> A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together. [REL-13] <br> When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next. [REL-13] <br> (v2.1 planned) merge-queue: a merge queue (named only). | consolidation (TOP-DECISION 89) | o289: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Fast merge queue <br> Pull requests merge one at a time per repo, across machines. <br> A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together. <br> When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-14

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Every release is noted <br> Every release has a release note that says what changed and lists the issues it fixed; the test that proves each fix is Regression's (REG-6). | consolidation (TOP-DECISION 89): absorbed into DEL-1 | o226: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Every release is noted <br> Every release has a release note that says what changed and lists the issues it fixed; the test that proves each fix is Regression's (REG-6). | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-15

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-20 | A ready pull request is on main within 5 minutes <br> From the moment a pull request is ready (reviewed, its own checks green on its head) to its commit on main takes 5 minutes or less, and a merge of one pull request never makes another ready one re-run its lane or CI. [REL-15] <br> The affected run on the pull request's head counts for the rest of the checks: the merge_group run is a fixed small tier that finishes within 5 minutes, and a pushed pull-request branch starts one CI run, not two. The wiki publish after the merge is outside the 5 minutes. [REL-15] <br> With the merge_queue setting on, merge.py leaves a moved base to GitHub's merge queue, and prints MERGED only after gh reports the pull request merged; with it off the moved-base refusal is unchanged. [REL-15] <br> (v2.0 planned) Health prints the median and slowest of the last 20 merges and fails one over 5 minutes. [REL-15] | readme-six: absorbed into DEL-17 (o514) | o641: "yes build it" |
| r1 | 2026-11-20 | A ready pull request is on main within 5 minutes <br> From the moment a pull request is ready (reviewed, its own checks green on its head) to its commit on main takes 5 minutes or less, and a merge of one pull request never makes another ready one re-run its lane or CI. [REL-15] <br> The affected run on the pull request's head counts for the rest of the checks: the merge_group run is a fixed small tier that finishes within 5 minutes, and a pushed pull-request branch starts one CI run, not two. The wiki publish after the merge is outside the 5 minutes. [REL-15] <br> With the merge_queue setting on, merge.py leaves a moved base to GitHub's merge queue, and prints MERGED only after gh reports the pull request merged; with it off the moved-base refusal is unchanged. [REL-15] <br> (v2.0 planned) Health prints the median and slowest of the last 20 merges and fails one over 5 minutes. [REL-15] | merging must not take 45 minutes; the target is under 5 | o486: "approved by operation-top under owner delegation (DOC-2, o486), goal rel-15-queue" |

## Tests


