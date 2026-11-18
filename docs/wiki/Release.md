<!-- workflow-docs -->
# Release

Review: **Unreviewed** <!-- kept extra-cols-links@3606a12a -->

How to use: [How-to-use-Release](How-to-use-Release)

## Problem

- Goals keep landing fixes while a release is being deployed, so quality drifts and I can't say what a version really holds.
- Nothing stops a milestone shipping with open issues, a red test, a failing health check, requirements I never reviewed or stale docs.
- When a release goes wrong I have no snapshot to go back to, so a bad release is repaired forward.

## Requirements

### Functional

- REL-1: **Unreviewed** A version number says what changed, and a major ships only through the gate
  - A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone.
  - A goal's release never bumps a major: `release.py` refuses it, naming `review.py promote`, so a major version exists only after the gate passed.
- REL-2: **Unreviewed** Every issue on the milestone is closed, or the owner moved it by name
  - `review.py gate vX` lists the open issues of milestone `vX.0` and refuses each one, naming its number.
  - An issue passes only with a release waiver of kind `moved` whose owner-words record names the issue; a record that does not name it, or does not exist, waives nothing.
- REL-3: **Unreviewed** The full regression suite passes on the release candidate, and each known-red row is fixed or waived with an issue
  - The gate runs the whole nightly suite on a checkout of the candidate, not the goal lane.
  - A row that fails, could not run or is on the known-red list refuses, naming the row, unless a `red` waiver gives its issue and its owner record names the row; a suite that did not run refuses.
  - A suite that runs past `max_suite_seconds` is not itself a refusal (health reports that cap); the gate waits up to four hours (`LOOP_GATE_SECONDS`), and a run a time budget stopped with rows left refuses, since rows that did not run prove nothing.
- REL-4: **Unreviewed** Health passes, every requirement is Reviewed by the owner, and no wiki page is stale
  - The gate runs the health check on the candidate and refuses unless it prints `HEALTH: green`.
  - It refuses each requirement on a feature page that is still Unreviewed, naming the requirement and its page, and each page the docs audit calls stale.
- REL-5: **Unreviewed** Once the release candidate is cut, only fixes for gate failures enter staging
  - From a major's `vX.0.0-rc.N` tag until the `vX.0.0` tag exists, `merge.py` refuses a goal with `frozen for vX.0.0`.
  - A goal passes only when its goal file names a subject of the last gate run's refusals: an issue, a row, a requirement, a page or `health`; before any gate run, none passes.
- REL-6: **Unreviewed** Promoting a major tags it, keeps a snapshot branch and sends a state report
  - `review.py promote vX --owner-record ID` runs only in the operation session, only when that owner-words record names `vX.0.0`, and only when every gate check passes; a refusal makes no tag, branch or release.
  - It moves main to the candidate by fast-forward, tags `vX.0.0`, keeps branch `release/vX`, and moves waived issues to the milestone the waiver names.
  - The state report (review state of each page, test results, health, closed issues, changes since the last major) is the release's notes and is mailed; a machine with no mail secrets prints `EMAIL not sent` and the report path, and the tag stays.
- REL-7: **Unreviewed** `revert vX` puts main back on the snapshot through a pull request
  - It pushes a branch whose tree is `release/vX`'s on top of the base, and opens a pull request to the base; it never pushes the base itself.
  - It refuses when `release/vX` does not exist, and a worker cannot run it.
- REL-8: **Unreviewed** Promotion and every waiver are the owner's words, never a worker's or a peer session's
  - Only the operation session runs `promote` or `revert`; a worker is refused with `REVIEW_ROLE`.
  - A waiver counts only when its owner-words record exists and names its subject, and the record id is kept beside the waiver in the git folder, outside the repo.
- REL-9: **Unreviewed** The merge's wiki check refuses only for what the goal changed
  - `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it, and a page only merge.py's own re-render of the Tests tables changed counts as left alone.
  - Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so.
  - On the base branch itself every finding counts.

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
| r1 | 2026-11-18 | A version number says what changed, and a major ships only through the gate <br> A patch is a fix, a minor is a goal shipped inside a milestone, and a major is a milestone. <br> A goal's release never bumps a major: `release.py` refuses it, naming `review.py promote`, so a major version exists only after the gate passed. | migration r1; date from the run day | o51: "Yes to both" |

### REL-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Every issue on the milestone is closed, or the owner moved it by name <br> `review.py gate vX` lists the open issues of milestone `vX.0` and refuses each one, naming its number. <br> An issue passes only with a release waiver of kind `moved` whose owner-words record names the issue; a record that does not name it, or does not exist, waives nothing. | migration r1; date from the run day | o51: "Yes to both" |

### REL-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | The full regression suite passes on the release candidate, and each known-red row is fixed or waived with an issue <br> The gate runs the whole nightly suite on a checkout of the candidate, not the goal lane. <br> A row that fails, could not run or is on the known-red list refuses, naming the row, unless a `red` waiver gives its issue and its owner record names the row; a suite that did not run refuses. <br> A suite that runs past `max_suite_seconds` is not itself a refusal (health reports that cap); the gate waits up to four hours (`LOOP_GATE_SECONDS`), and a run a time budget stopped with rows left refuses, since rows that did not run prove nothing. | migration r1; date from the run day | o51: "Yes to both" |

### REL-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Health passes, every requirement is Reviewed by the owner, and no wiki page is stale <br> The gate runs the health check on the candidate and refuses unless it prints `HEALTH: green`. <br> It refuses each requirement on a feature page that is still Unreviewed, naming the requirement and its page, and each page the docs audit calls stale. | migration r1; date from the run day | o51: "Yes to both" |

### REL-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Once the release candidate is cut, only fixes for gate failures enter staging <br> From a major's `vX.0.0-rc.N` tag until the `vX.0.0` tag exists, `merge.py` refuses a goal with `frozen for vX.0.0`. <br> A goal passes only when its goal file names a subject of the last gate run's refusals: an issue, a row, a requirement, a page or `health`; before any gate run, none passes. | migration r1; date from the run day | o51: "Yes to both" |

### REL-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Promoting a major tags it, keeps a snapshot branch and sends a state report <br> `review.py promote vX --owner-record ID` runs only in the operation session, only when that owner-words record names `vX.0.0`, and only when every gate check passes; a refusal makes no tag, branch or release. <br> It moves main to the candidate by fast-forward, tags `vX.0.0`, keeps branch `release/vX`, and moves waived issues to the milestone the waiver names. <br> The state report (review state of each page, test results, health, closed issues, changes since the last major) is the release's notes and is mailed; a machine with no mail secrets prints `EMAIL not sent` and the report path, and the tag stays. | migration r1; date from the run day | o51: "Yes to both" |

### REL-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | `revert vX` puts main back on the snapshot through a pull request <br> It pushes a branch whose tree is `release/vX`'s on top of the base, and opens a pull request to the base; it never pushes the base itself. <br> It refuses when `release/vX` does not exist, and a worker cannot run it. | migration r1; date from the run day | o51: "Yes to both" |

### REL-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Promotion and every waiver are the owner's words, never a worker's or a peer session's <br> Only the operation session runs `promote` or `revert`; a worker is refused with `REVIEW_ROLE`. <br> A waiver counts only when its owner-words record exists and names its subject, and the record id is kept beside the waiver in the git folder, outside the repo. | migration r1; date from the run day | o51: "Yes to both" |

### REL-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | The merge's wiki check refuses only for what the goal changed <br> `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it, and a page only merge.py's own re-render of the Tests tables changed counts as left alone. <br> Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so. <br> On the base branch itself every finding counts. | merge.py re-renders other pages Tests tables on the goal branch; those pages are not the goal pages | o56: "Yes, start it" |
| r1 | 2026-11-18 | The merge's wiki check refuses only for what the goal changed <br> `merge.py` refuses a DOC-19 or DOC-4 finding on a page the goal's diff changes (a How-to-use page counts as changed when its feature page is), a page the diff made stale, and a stale generated block or table (the Tests tables, START.md); the same findings on a page the goal leaves alone never refuse it. <br> Each such untouched page gets one issue on its feature's "Backlog: <Feature>" milestone (Home and skill docs on "Backlog: Documentation"), made when missing and not again while one is open; the prepare step lists them as left for health and files nothing, and a gh that cannot file leaves the merge going and says so. <br> On the base branch itself every finding counts. | migration r1; date from the run day | o51: "Yes to both" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [rel-major-refused](Tests#t-rel-major-refused) | requirement | REL-1 | Given a goal whose release would bump a major, when release.py bumps the version, then it refuses naming review.py promote; a minor and a patch still bump. | not run |
| - | requirement | REL-1 | no passing test | not enforced |
| [rel-open-issue-refused](Tests#t-rel-open-issue-refused) | requirement | REL-2 | Given a milestone with an open issue the owner has not moved by name, when review.py gate runs, then it refuses naming the issue; an issue with a waiver whose owner record names it does not refuse. | not run |
| - | requirement | REL-2 | no passing test | not enforced |
| [rel-red-row-refused](Tests#t-rel-red-row-refused) | requirement | REL-3 | Given a known-red or failing full-suite row with no waiver naming an issue and an owner record, or a suite that did not run, when the gate runs, then it refuses naming the row. | not run |
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
