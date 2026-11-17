<!-- workflow-docs -->
# Release

Review: **Unreviewed**

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

### Non-functional

None

## Non-goals

- Staging, release-candidate tags and the promotion of a minor or a patch belong to release-channels (Delivery); this page covers only a major.
- The gate never fixes a failure and never moves an issue itself except one the owner waived by name.

## Success metrics

- No major ships with an open milestone issue, a red unwaived row, a failing health check, an Unreviewed requirement or a stale page.
- Every major leaves a `vX.0.0` tag, a `release/vX` branch and a state report, and `revert vX` can put main back.

## Tests

