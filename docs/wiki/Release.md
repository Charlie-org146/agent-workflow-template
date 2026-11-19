<!-- workflow-docs -->
# Release

Review: **Unreviewed** <!-- kept gate-ci-suite@3ac4554f -->

How to use: [How-to-use-Release](How-to-use-Release)

## Problem

- Goals keep landing fixes while a release is being deployed, so quality drifts and I can't say what a version really holds.
- Nothing stops a milestone shipping with open issues, a red test, a failing health check, requirements I never reviewed or stale docs.
- When a release goes wrong I have no snapshot to go back to, so a bad release is repaired forward.

## Requirements

### Functional

- REL-1: **Unreviewed** A version number says what changed
  - A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone.
  - A goal's release never bumps a major; a major exists only after the gate passes.
- REL-2: **Unreviewed** A major's milestone is closed out
  - Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue.
- REL-3: **Unreviewed** The full suite passes on the candidate
  - The gate runs the whole nightly suite on the release candidate.
  - Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses.
  - The suite may instead come from a GitHub Actions run of the regression workflow (review.py gate or promote with --suite-from RUN), but only a run on the candidate's commit that completed with every shard reported, nothing UNRUN and every land or nightly row logged; any other run refuses "suite run does not cover the candidate", and the run id is recorded with the gate result.
- REL-4: **Unreviewed** Health, review and pages pass on the candidate
  - The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails.
- REL-5: **Unreviewed** A candidate admits only gate fixes
  - From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals.
- REL-6: **Unreviewed** Promotion tags, snapshots and reports
  - Promoting a major runs only from the operation session with my record naming that version and every gate check passing.
  - It tags the major, keeps a snapshot branch, and mails a state report as the release notes.
- REL-7: **Unreviewed** A major can be reverted
  - revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it.
- REL-8: **Unreviewed** Promotion and waivers are my words
  - Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject.
- REL-9: **Unreviewed** The merge's wiki check refuses only for what the goal changed
  - `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it, and a page only merge.py's own re-render of the Tests tables changed counts as left alone.
  - Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so.
  - On the base branch itself every finding counts.
- REL-10: **Unreviewed** Every goal ends with a release
  - With auto_merge on, a finished goal is merged and released automatically: version bump, release note, published release and wiki.
  - With auto_merge off it makes a draft release and merges nothing.
  - Any failure shows under Needs you.
- REL-11: **Unreviewed** A merge is never refused late or left half done
  - A merge is refused only for a page the goal's own change made stale, and the pull-request checks catch that before a merge slot is spent.
  - If the merge lands but the release fails, the goal reads "merged, release owed", and a second run finishes it without merging twice.
- REL-12: **Unreviewed** A review hold before auto merge
  - Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows the merge waiting on review.
- REL-13: **Unreviewed** Fast merge queue
  - Pull requests merge one at a time per repo, across machines.
  - A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together.
  - When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next.
- REL-14: **Unreviewed** Every release is noted
  - Every release has a release note that says what changed and lists the issues it fixed; the test that proves each fix is Regression's (REG-6).

### Non-functional

None

## Non-goals

- Staging, release-candidate tags and the promotion of a minor or a patch belong to release-channels (Delivery); this page covers only a major.
- The gate never fixes a failure and never moves an issue itself except one the owner waived by name.

## Success metrics

- No major ships with an open milestone issue, a red unwaived row, a failing health check, an Unreviewed requirement or a stale page.
- Every major leaves a `vX.0.0` tag, a `release/vX` branch and a state report, and `revert vX` can put main back.

## Revisions

### REL-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A version number says what changed <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. <br> A goal's release never bumps a major; a major exists only after the gate passes. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | A version number says what changed, and a major ships only through the gate <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. <br> A goal's release never bumps a major: `release.py` refuses it, naming `review.py promote`, so a major version exists only after the gate passed. | migration r1; date from the run day | o51: "Yes to both" |

### REL-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A major's milestone is closed out <br> Every issue on a major's milestone is closed before the gate passes, or moved by a waiver whose owner record names that issue. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Every issue on the milestone is closed, or the owner moved it by name <br> `review.py gate vX` lists the open issues of milestone `vX.0` and refuses each one, naming its number. <br> An issue passes only with a release waiver of kind `moved` whose owner-words record names the issue; a record that does not name it, or does not exist, waives nothing. | migration r1; date from the run day | o51: "Yes to both" |

### REL-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r3 | 2026-11-19 | The full suite passes on the candidate <br> The gate runs the whole nightly suite on the release candidate. <br> Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. <br> The suite may instead come from a GitHub Actions run of the regression workflow (review.py gate or promote with --suite-from RUN), but only a run on the candidate's commit that completed with every shard reported, nothing UNRUN and every land or nightly row logged; any other run refuses "suite run does not cover the candidate", and the run id is recorded with the gate result. | a CI run of the regression workflow is an accepted suite source for the gate (TOP-DECISION 36) | o191: "TOP-DECISION 36 under the owner's delegation (o168), ~18:12: freeze gate-ci-suite on a" |
| r2 | 2026-11-18 | The full suite passes on the candidate <br> The gate runs the whole nightly suite on the release candidate. <br> Each failing, unrun or known-red row refuses unless an owner-recorded waiver names it with its issue; a suite that did not run refuses. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | The full regression suite passes on the release candidate, and each known-red row is fixed or waived with an issue <br> The gate runs the whole nightly suite on a checkout of the candidate, not the goal lane. <br> A row that fails, could not run or is on the known-red list refuses, naming the row, unless a `red` waiver gives its issue and its owner record names the row; a suite that did not run refuses. <br> A suite that runs past `max_suite_seconds` is not itself a refusal (health reports that cap); the gate waits up to four hours (`LOOP_GATE_SECONDS`), and a run a time budget stopped with rows left refuses, since rows that did not run prove nothing. | migration r1; date from the run day | o51: "Yes to both" |

### REL-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Health, review and pages pass on the candidate <br> The gate refuses unless health is green on the candidate, every requirement is Reviewed by me, and no wiki page is stale, naming each one that fails. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Health passes, every requirement is Reviewed by the owner, and no wiki page is stale <br> The gate runs the health check on the candidate and refuses unless it prints `HEALTH: green`. <br> It refuses each requirement on a feature page that is still Unreviewed, naming the requirement and its page, and each page the docs audit calls stale. | migration r1; date from the run day | o51: "Yes to both" |

### REL-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A candidate admits only gate fixes <br> From a major's release-candidate tag until the major is tagged, the merge refuses any goal that does not fix a subject of the last gate run's refusals. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Once the release candidate is cut, only fixes for gate failures enter staging <br> From a major's `vX.0.0-rc.N` tag until the `vX.0.0` tag exists, `merge.py` refuses a goal with `frozen for vX.0.0`. <br> A goal passes only when its goal file names a subject of the last gate run's refusals: an issue, a row, a requirement, a page or `health`; before any gate run, none passes. | migration r1; date from the run day | o51: "Yes to both" |

### REL-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Promotion tags, snapshots and reports <br> Promoting a major runs only from the operation session with my record naming that version and every gate check passing. <br> It tags the major, keeps a snapshot branch, and mails a state report as the release notes. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Promoting a major tags it, keeps a snapshot branch and sends a state report <br> `review.py promote vX --owner-record ID` runs only in the operation session, only when that owner-words record names `vX.0.0`, and only when every gate check passes; a refusal makes no tag, branch or release. <br> It moves main to the candidate by fast-forward, tags `vX.0.0`, keeps branch `release/vX`, and moves waived issues to the milestone the waiver names. <br> The state report (review state of each page, test results, health, closed issues, changes since the last major) is the release's notes and is mailed; a machine with no mail secrets prints `EMAIL not sent` and the report path, and the tag stays. | migration r1; date from the run day | o51: "Yes to both" |

### REL-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A major can be reverted <br> revert puts main back on a major's snapshot through a pull request, never by pushing the base, and a worker cannot run it. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | `revert vX` puts main back on the snapshot through a pull request <br> It pushes a branch whose tree is `release/vX`'s on top of the base, and opens a pull request to the base; it never pushes the base itself. <br> It refuses when `release/vX` does not exist, and a worker cannot run it. | migration r1; date from the run day | o51: "Yes to both" |

### REL-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Promotion and waivers are my words <br> Only the operation session promotes or reverts, and a waiver counts only when its owner record exists and names its subject. | v2 rewrite: on main since v1.0.61 (release-gate), Unreviewed; text condensed from the page; covers the draft's earlier REL-6 (o44). | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Promotion and every waiver are the owner's words, never a worker's or a peer session's <br> Only the operation session runs `promote` or `revert`; a worker is refused with `REVIEW_ROLE`. <br> A waiver counts only when its owner-words record exists and names its subject, and the record id is kept beside the waiver in the git folder, outside the repo. | migration r1; date from the run day | o51: "Yes to both" |

### REL-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | The merge's wiki check refuses only for what the goal changed <br> `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it, and a page only merge.py's own re-render of the Tests tables changed counts as left alone. <br> Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so. <br> On the base branch itself every finding counts. | merge.py re-renders other pages Tests tables on the goal branch; those pages are not the goal pages | o56: "Yes, start it" |
| r1 | 2026-11-18 | The merge's wiki check refuses only for what the goal changed <br> `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it. <br> Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so. <br> On the base branch itself every finding counts. | migration r1; date from the run day | o51: "Yes to both" |

### REL-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Every goal ends with a release <br> With auto_merge on, a finished goal is merged and released automatically: version bump, release note, published release and wiki. <br> With auto_merge off it makes a draft release and merges nothing. <br> Any failure shows under Needs you. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A merge is never refused late or left half done <br> A merge is refused only for a page the goal's own change made stale, and the pull-request checks catch that before a merge slot is spent. <br> If the merge lands but the release fails, the goal reads "merged, release owed", and a second run finishes it without merging twice. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-12

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A review hold before auto merge <br> Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows the merge waiting on review. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-13

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Fast merge queue <br> Pull requests merge one at a time per repo, across machines. <br> A goal waits only behind goals whose touched files overlap its own, a goal waiting on me yields its place, and several ready goals with separate files are verified and merged together. <br> When main moves, a waiting goal rechecks only the tests the moved files reach, once, when it is next. | migration r1; date from the run day | o47: "Yes, start it end." |

### REL-14

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Every release is noted <br> Every release has a release note that says what changed and lists the issues it fixed; the test that proves each fix is Regression's (REG-6). | migration r1; date from the run day | o47: "Yes, start it end." |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [rel-major-refused](Tests#t-rel-major-refused) | requirement | REL-1 | Given a goal whose release would bump a major, when release.py bumps the version, then it refuses naming review.py promote; a minor and a patch still bump. | not run |
| - | requirement | REL-1 | no passing test | not enforced |
| [rel-open-issue-refused](Tests#t-rel-open-issue-refused) | requirement | REL-2 | Given a milestone with an open issue the owner has not moved by name, when review.py gate runs, then it refuses naming the issue; an issue with a waiver whose owner record names it does not refuse. | not run |
| - | requirement | REL-2 | no passing test | not enforced |
| [rel-red-row-refused](Tests#t-rel-red-row-refused) | requirement | REL-3 | Given a known-red or failing full-suite row with no waiver naming an issue and an owner record, or a suite that did not run, when the gate runs, then it refuses naming the row. | not run |
| [gate-ci-suite](Tests#t-gate-ci-suite) | requirement | REL-3 | Given a GitHub Actions run of the regression workflow, when review.py gate or promote takes it with --suite-from, then it refuses unless the run is on the gate ref, completed, fully reported with nothing UNRUN and logging every land or nightly row, and it refuses exactly the rows that are not PASS without a waiver. | not run |
| - | requirement | REL-3 | no passing test | not enforced |
| [rel-checks-refused](Tests#t-rel-checks-refused) | requirement | REL-4 | Given a failing health check, a requirement that is not Reviewed or a stale wiki page, when the gate runs, then it refuses naming the check, the requirement or the page. | not run |
| - | requirement | REL-4 | no passing test | not enforced |
| [rel-freeze-refuses](Tests#t-rel-freeze-refuses) | requirement | REL-5 | Given a cut release candidate for a major, when a goal that names no recorded gate failure merges, then merge.py refuses with frozen for vX.0.0 and merges nothing; a goal naming one, or a release already tagged, goes on. | not run |
| - | requirement | REL-5 | no passing test | not enforced |
| [rel-promote-snapshot](Tests#t-rel-promote-snapshot) | requirement | REL-6 | Given a release candidate with every gate check green and an owner record naming the version, when promote runs, then it tags vX.0.0, keeps release/vX, moves main, publishes the state report and mails it; a refused gate makes no tag, branch or release. | not run |
| - | requirement | REL-6 | no passing test | not enforced |
| [rel-revert-pr](Tests#t-rel-revert-pr) | requirement | REL-7 | Given release/vX, when revert vX runs, then a branch with the snapshot's tree on top of main is pushed and a pull request to main is opened, and main itself is never pushed. | not run |
| - | requirement | REL-7 | no passing test | not enforced |
| [rel-owner-only](Tests#t-rel-owner-only) | requirement | REL-8 | Given a worker, or an owner record that does not name the version, when promote or revert runs, then it is refused and nothing changes. | not run |
| - | requirement | REL-8 | no passing test | not enforced |
| [gate-untouched-not-refused](Tests#t-gate-untouched-not-refused) | requirement | REL-9 | Given a goal whose diff changes no wiki page while other pages carry DOC-19 or DOC-4 findings, or pages only merge.py's own re-render changed, when merge.py checks the wiki, then it does not refuse on them. | PASS 2026-11-18 |
| [gate-untouched-filed-once](Tests#t-gate-untouched-filed-once) | requirement | REL-9 | Given those findings on untouched pages, when merge.py checks the wiki, then each page is printed as a FINDING and handed to the issue filer once. | not run |
| [gate-one-issue-per-page](Tests#t-gate-one-issue-per-page) | requirement | REL-9 | Given a page with several DOC-19 findings, when they are filed, then one issue carries every line. | not run |
| [gate-generated-still-refused](Tests#t-gate-generated-still-refused) | requirement | REL-9 | Given a stale Tests table, START.md, a stale page and a DOC-18 finding, when merge.py checks the wiki, then each still refuses and none is filed. | not run |
| [gate-changed-page-refused](Tests#t-gate-changed-page-refused) | requirement | REL-9 | Given a DOC-19 finding on a page the goal's diff changes, when merge.py checks the wiki, then it still refuses. | not run |
| [gate-base-branch-counts](Tests#t-gate-base-branch-counts) | requirement | REL-9 | Given the check runs on the base branch itself, when DOC-19 findings exist, then every one counts and none is filed. | not run |
| [gate-issue-not-doubled](Tests#t-gate-issue-not-doubled) | requirement | REL-9 | Given an open issue for a page's findings, when the gate files that page again, then no second issue is opened. | not run |
| [gate-issue-on-feature-backlog](Tests#t-gate-issue-on-feature-backlog) | requirement | REL-9 | Given findings on an untouched How-to-use-X page, Home or a skill doc, when the gate files them, then the issue sits on Backlog: X or Backlog: Documentation, made when missing. | not run |
| [gate-gh-failure-safe](Tests#t-gate-gh-failure-safe) | requirement | REL-9 | Given gh fails or is not installed, when the gate files an issue, then nothing is filed and the merge check does not crash. | not run |
| [gate-pending-scoped](Tests#t-gate-pending-scoped) | requirement | REL-9 | Given findings on untouched pages, when wiki.py prepare or merge.py checks the wiki, then only the goal's own and generated findings remain, and prepare prints the rest as left for health without filing. | not run |
| [gate-nonascii-page-refused](Tests#t-gate-nonascii-page-refused) | requirement | REL-9 | Given a goal that changes a page whose name is not ASCII and a DOC-19 finding on it, when merge.py checks the wiki, then it still refuses. | not run |
| [gate-feature-edit-refuses](Tests#t-gate-feature-edit-refuses) | requirement | REL-9 | Given a goal that changes a feature page and a DOC-19 finding on its How-to-use page, when merge.py checks the wiki, then it still refuses. | not run |
| [gate-list-failure-no-create](Tests#t-gate-list-failure-no-create) | requirement | REL-9 | Given gh issue list fails, when the gate files a page, then no issue is created. | not run |
| [never-merges](Tests#t-never-merges) | requirement | REL-10 | Given auto_merge is off, when goals finish, then nothing is merged. | PASS 2026-11-09 |
| [wiki-release](Tests#t-wiki-release) | requirement | REL-10 | Given a merged goal, when the release runs, then its wiki pages are published, even when python leaves cache files behind. | PASS 2026-11-18 |
| [auto-release](Tests#t-auto-release) | requirement | REL-10 | Given auto-release is on, when a goal merges, then it is released automatically. | PASS 2026-11-12 |
| [wiki-unmapped-stale](Tests#t-wiki-unmapped-stale) | requirement | REL-10 | Given a page no touched path maps to, when the release step runs, then it lists the page as a finding and does not refuse, and merge refuses only for a page its own diff made stale. | PASS 2026-11-18 |
| [del5-patch-default](Tests#t-del5-patch-default) | requirement | REL-10 | Given a goal with a code change and no bump set, when it is released, then the version bump is patch. | PASS 2026-11-12 |
| [del5-bump-set](Tests#t-del5-bump-set) | requirement | REL-10 | Given the operation recorded a minor bump with goal.py set, when the goal is released, then the bump is minor. | PASS 2026-11-12 |
| [del5-release-pr](Tests#t-del5-release-pr) | requirement | REL-10 | Given a protected main that refuses direct pushes, when a goal is released, then the version and changelog land through a release pull request. | PASS 2026-11-12 |
| [autorelease-no-report](Tests#t-autorelease-no-report) | requirement | REL-10 | Given a goal state whose report is null, a string or has a non-string text, when the release fails and merge.py refuses, then it prints REFUSED with its fix on stderr, exits non-zero with no traceback, and records the failure on the goal. | PASS 2026-11-12 |
| [wiki-no-report](Tests#t-wiki-no-report) | requirement | REL-10 | Given a goal state whose report is null or a string, when the wiki publish is refused, then it prints WIKI REFUSED with its fix, exits 1 with no traceback, and records the failure on the goal. | PASS 2026-11-12 |
| [del5-docs-bump-minor](Tests#t-del5-docs-bump-minor) | requirement | REL-10 | Given a goal that changes only docs and the operation recorded a minor bump with goal.py set, when it is released, then the version moves by a minor. | PASS 2026-11-15 |
| [del5-docs-patch-default](Tests#t-del5-docs-patch-default) | requirement | REL-10 | Given a goal that changes only docs and no bump is recorded, when it is released, then the version moves by a patch. | PASS 2026-11-15 |
| [resume-ask-worker-step](Tests#t-resume-ask-worker-step) | requirement | REL-10 | Given a goal set to ask and auto_merge on, when its worker ends with the pull request open, then the release step does not merge it. | not run |
| [resume-unasked-merges](Tests#t-resume-unasked-merges) | requirement | REL-10 | Given a goal with no ask and auto_merge on, when its worker ends with the pull request open, then the release step still merges it. | not run |
| [package-gate-controls](Tests#t-package-gate-controls) | requirement | REL-10 | Given a package with a script over 20,480 bytes, more than 100 files or a script that needs a file outside its folder, when package.py's own checks run, then each fails the package. | not run |
| [skill-refusals-in-references](Tests#t-skill-refusals-in-references) | requirement | REL-10 | Given the release skill's refusals, when SKILL.md and its references folder are read, then every refusal and its fix sit in references/commands.md, SKILL.md points to it, and SKILL.md is under 150 lines. | PASS 2026-11-14 |
| [release-scripts-under-19000](Tests#t-release-scripts-under-19000) | requirement | REL-10 | Given the workflow-release scripts, when their LF sizes are measured, then none is over 19,000 bytes. | not run |
| [scripts-a-delivery-under-19000](Tests#t-scripts-a-delivery-under-19000) | requirement | REL-10 | Given the workflow-delivery scripts, including lane.py and flow.py after merging main, when their sizes are counted in LF bytes, then each is under 19,000 bytes. | PASS 2026-11-16 |
| [del5-merge-forwards-checkout](Tests#t-del5-merge-forwards-checkout) | requirement | REL-10 | Given a main checkout behind origin with a dirty lane record, when merge.py fast-forwards it, then the record is stashed and put back; any other change keeps the checkout as it is. | PASS 2026-11-15 |
| [start-from-head-passes-4340](Tests#t-start-from-head-passes-4340) | requirement | REL-10 | Given a pull request that adds a skill command and carries the START.md its own skills render, when merge.py's wiki.pending audits it, then START.md is not reported. | not run |
| [start-from-head-refuses-4340](Tests#t-start-from-head-refuses-4340) | requirement | REL-10 | Given a pull request whose START.md is stale for its own skills, when merge.py's wiki.pending audits it, then it still reports START.md (#4340). | not run |
| [merge-main-own-finding-4343](Tests#t-merge-main-own-finding-4343) | requirement | REL-10 | Given a goal branch that merged main's stale page, when merge.py's wiki.pending audits it, then main's stale page is printed as a FINDING for health. | not run |
| [audit-head-judges-own-docs](Tests#t-audit-head-judges-own-docs) | requirement | REL-10 | Given a pull request whose head carries its own docs.py, when merge.py's wiki.pending audits it, then the head's own docs.py judges its pages, not the main checkout's. | not run |
| [ff-stash-conflict-never-unmerged](Tests#t-ff-stash-conflict-never-unmerged) | requirement | REL-10 | Given a main checkout whose dirty .loop/regression-runs.tsv conflicts with origin when merge.py fast-forwards it, when the stash apply fails, then the file is restored from HEAD, never left unmerged or with conflict markers, and the dirty results stay in the named stash the step prints. | not run |
| [release-criteria-known-skip](Tests#t-release-criteria-known-skip) | requirement | REL-10 | Given rows that are known, skipped with exit 77 or already recorded PASS, when release.py cut checks its criteria, then none counts as failing and only the rest run. | not run |
| [cut-pass-current-commit](Tests#t-cut-pass-current-commit) | requirement | REL-10 | Given rows whose only PASS is on an older commit and one with a PASS on the current commit, when the cut proves the requirements, then it reruns the older-PASS rows and does not rerun the current-PASS row (#4508). | not run |
| [cut-left-listed](Tests#t-cut-left-listed) | requirement | REL-10 | Given the cut's stop reached before some rows ran, when the cut ends, then it prints those rows as LEFT with their count and writes the same section into the release notes (#4508). | not run |
| [cut-left-none](Tests#t-cut-left-none) | requirement | REL-10 | Given time to run every row, when the cut ends, then nothing is LEFT and the release notes carry no LEFT section (negative control, #4508). | not run |
| - | requirement | REL-11 | no passing test | not enforced |
| [review-hold-blocks](Tests#t-review-hold-blocks) | requirement | REL-12 | Given review_hold is on, when no review of the pull request head is recorded, then merge.py refuses REVIEW_HOLD, merges nothing and the board shows a merge waiting on review. | not run |
| [review-recorded-merges](Tests#t-review-recorded-merges) | requirement | REL-12 | Given review_hold is on, when the operation session records a review of the head, then merge.py merges, and with the setting off merging is unchanged. | not run |
| [review-worker-refused](Tests#t-review-worker-refused) | requirement | REL-12 | Given review_hold is on, when a worker tries to record a review, then it is refused and nothing is recorded. | not run |
| [review-help-runs-alone](Tests#t-review-help-runs-alone) | requirement | REL-12 | Given the review script, when it runs alone with --help, then it prints its usage and exits 0, so the package gate accepts it. | not run |
| - | requirement | REL-12 | no passing test | not enforced |
| [merge-batch-split](Tests#t-merge-batch-split) | requirement | REL-13 | Given 3 ready pull requests with disjoint touches, when wiki.py batch run verifies them on one tree, then they merge together, and a failing batch splits to name the culprit. | not run |
| [pr-joins-queue](Tests#t-pr-joins-queue) | requirement | REL-13 | Given a goal at pr, when goal.py pr joins the pr queue, then it calls pool.pr_join with the goal and its state, with no runs folder, so the queue accepts it instead of crashing. | not run |
| - | requirement | REL-13 | no passing test | not enforced |
| - | requirement | REL-14 | no passing test | not enforced |
| [wiki-release-pycache](Tests#t-wiki-release-pycache) | defect | [#58](https://github.com/jcl2018/agent-workflow-template/issues/58) closed (2026-11-09) | Given python leaves cache files behind, when a goal merges, then its wiki pages are still published. | PASS 2026-11-18 |
| [worker-runs-release](Tests#t-worker-runs-release) | defect | [PR 61](https://github.com/jcl2018/agent-workflow-template/pull/61) merged (2026-11-09) | Given a worker that ends with its pull request waiting, when it finishes, then it runs the release step itself. | PASS 2026-11-18 |
| [issue-129-docs-published](Tests#t-issue-129-docs-published) | defect | [#129](https://github.com/jcl2018/agent-workflow-template/issues/129) closed (2026-11-15) | Given the release skill's docs, when they describe the auto_merge path, then they say merge.py publishes the release with no draft (issue: Release skill says it cuts a draft, but merge.py publishes the release directly). | PASS 2026-11-12 |
| [issue-129-wiki-first-page](Tests#t-issue-129-wiki-first-page) | defect | [#129](https://github.com/jcl2018/agent-workflow-template/issues/129) closed (2026-11-15) | Given a GitHub wiki with no first page, when the release publishes it, then the error names how to create the first page (issue: Release skill says it cuts a draft, but merge.py publishes the release directly). | PASS 2026-11-12 |
| [issue-134-protected-release](Tests#t-issue-134-protected-release) | defect | [#134](https://github.com/jcl2018/agent-workflow-template/issues/134) closed (2026-11-11) | Given a PR-only ruleset on main, when a goal is released, then a release PR lands the version and exactly one GitHub release is made at its merge commit (issue: Autorelease fails on a protected base branch). | PASS 2026-11-12 |
| [issue-154-release-pr-merge](Tests#t-issue-154-release-pr-merge) | defect | [#154](https://github.com/jcl2018/agent-workflow-template/issues/154) closed (2026-11-11) | Given a release PR the loop can't merge because review is required, when merge.py runs, then it records the owner's merge command (issue: merge.py's release push fails on a protected main). | PASS 2026-11-12 |
| [issue-170-patch-on-remove](Tests#t-issue-170-patch-on-remove) | defect | [#170](https://github.com/jcl2018/agent-workflow-template/issues/170) closed (2026-11-11) | Given a goal that removes a file, when it is released, then the bump is patch and the removal is named in the reason (issue: autorelease turns release.py's 'ask' into a silent major bump). | PASS 2026-11-12 |
| [release-head-status](Tests#t-release-head-status) | defect | [#3870](https://github.com/jcl2018/agent-workflow-template/issues/3870) closed (2026-11-14) | Given a release pull request whose head only moves the version and changelog, a lane that could not run, or rows that failed, when merge.py's release step posts statuses, then the goal's pass carries over without a lane, an untested head gets no status, only rows that ran and failed post failure, and the refusal names them instead of asking for a manual merge (#3870). | not run |
| [merge-stale-other-passes](Tests#t-merge-stale-other-passes) | defect | [#3941](https://github.com/jcl2018/agent-workflow-template/issues/3941) closed (2026-11-13) | Given a page stale from a commit the goal never touches, when merge.py checks the wiki, then it prints the page as a FINDING and does not refuse. | not run |
| [merge-stale-own-refuses](Tests#t-merge-stale-own-refuses) | defect | [#3941](https://github.com/jcl2018/agent-workflow-template/issues/3941) closed (2026-11-13) | Given a page the goal's own diff made stale, when merge.py checks the wiki, then it still refuses and names the page. | not run |
| [merge-refused-failed](Tests#t-merge-refused-failed) | defect | [#4004](https://github.com/jcl2018/agent-workflow-template/issues/4004) closed (2026-11-14) | Given a merge.py that gh refuses before the merge, when it ends, then the goal is failed at the same step, never done, so resume works and the board shows it unfinished. | not run |
| [merge-failed-retry](Tests#t-merge-failed-retry) | defect | [#4004](https://github.com/jcl2018/agent-workflow-template/issues/4004) closed (2026-11-14) | Given a goal a refused merge left failed, when merge.py runs again with the fault gone, then it merges the pull request and the goal ends done. | not run |
| [merge-refuses-worktree](Tests#t-merge-refuses-worktree) | defect | [#4020](https://github.com/jcl2018/agent-workflow-template/issues/4020) closed (2026-11-14) | Given merge.py run from a path inside the repo's goal worktrees, when it starts, then it refuses and names the main checkout or the installed skills. | PASS 2026-11-14 |
| [merge-refuses-behind](Tests#t-merge-refuses-behind) | defect | [#4020](https://github.com/jcl2018/agent-workflow-template/issues/4020) closed (2026-11-14) | Given a main checkout behind origin/base, when merge.py starts, then it refuses, says how many commits behind and prints the fast-forward command. | not run |
| [moved-exit-live-at-pr](Tests#t-moved-exit-live-at-pr) | defect | [#4004](https://github.com/jcl2018/agent-workflow-template/issues/4004) closed (2026-11-14) | Given a merge refused because the head or base moved, when it exits, then the goal is running at step pr, not done. | not run |
| [merge-main-own-printed](Tests#t-merge-main-own-printed) | defect | [#4020](https://github.com/jcl2018/agent-workflow-template/issues/4020) closed (2026-11-14) | Given merge.py run from the main checkout with a page stale on main, when it checks the wiki, then it prints the page as a FINDING for health and does not refuse. | not run |
| [release-red-checks-named](Tests#t-release-red-checks-named) | defect | [#3870](https://github.com/jcl2018/agent-workflow-template/issues/3870) closed (2026-11-14) | Given a release PR with a red required check, when merge.py refuses, then it names the check and never advises gh pr merge. | not run |
| [pr-head-audit-passes-4208](Tests#t-pr-head-audit-passes-4208) | defect | [#4208](https://github.com/jcl2018/agent-workflow-template/issues/4208) closed (2026-11-15) | Given a pull request that rewrites a page main left stale, when merge.py's wiki.pending audits it from the main checkout, then it audits the PR head's render and the PR passes (issue 4208). | PASS 2026-11-15 |
| [pr-head-audit-refuses-4208](Tests#t-pr-head-audit-refuses-4208) | defect | [#4208](https://github.com/jcl2018/agent-workflow-template/issues/4208) closed (2026-11-15) | Given a pull request whose diff makes a page stale, when merge.py's wiki.pending audits it from the main checkout, then it is still refused and main's own stale page stays a finding (issue 4208). | PASS 2026-11-15 |
