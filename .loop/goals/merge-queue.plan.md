# merge-queue: plan

Checked against the code on origin/main b47ac4813. Every name below exists unless marked NEW.

## Findings from checking the design against the code
1. `autorelease.protected()` (autorelease.py:71) tests only for a `pull_request` rule. A ruleset with a `merge_queue` rule
   and no `pull_request` rule makes it False, so `finish()` (autorelease.py:366) would try the direct push and be refused
   (GH013). Fix: `protected()` also returns True for a `merge_queue` rule type. This is the "release commit" answer:
   the release PR path (`merge.advance`, `merge.start`) is already built; only its trigger and its merge call change.
2. `merge.py main()` holds `pods.merge_lock` for the whole process (merge.py:290; graph.py:391 is a pid lock released at
   exit). Holding it while waiting for the queue would serialize enqueues and defeat build concurrency 3. Fix: release the
   lock after the enqueue call, retake it before `ar.finish` (the version bump and the release PR need the one-at-a-time
   lock so three merged entries never compute the same version). NEW: `pods.unlock` if graph.py has none (check; else
   remove `merge.lock` by pid check).
3. `advance()` merges the release PR with a plain `gh pr merge url --merge` (merge.py:199) and line 342 merges the goal PR
   the same way. Both go through one NEW helper `land(top, url, head)` that enqueues with `--auto --match-head-commit`
   when `queue_on()` else merges as today, then returns when MERGED.
4. `.github/workflows/regression-pr.yml` triggers on `pull_request` and `push` only; `merge_group` is missing.
   That file is merge-queue-ci's (pc-w9). This goal does not edit it; it lists which contexts report on merge_group
   (done line 5) after merge-queue-ci lands, and the toy proves the listing function.
5. `private.required_checks()` already reads the ruleset's required contexts and `ar.go_gate()` checks them on the PR
   head; for a queue, the PR-head gate stays as is, and the merge-group commit is GitHub's to gate.

## Build steps (ordered)
1. criteria.py revise REL-13 with the approved text, `--user --owner-record o283`; commit the page. Build starts after.
2. merge.py: add `queue_on(top, base)` (reads `rules/branches/<base>`; a failed read refuses QUEUE_UNREADABLE, never a
   silent direct merge) and `land()`; replace the two plain merge calls; unlock/relock around the wait; `--batch` refusal
   when `queue_on`. Pay in bytes: cut the module docstring to a short usage, drop the `_pods` comment, fold `leave_queue`
   and `load` pieces; target at or under 18,994 LF bytes (measure with `tr -d '\r' | wc -c`).
3. autorelease.py: `protected()` true on `merge_queue`.
4. rules.py: NEW rule `merge_time(root)`: from `gh pr list --state merged --limit 20 --json mergedAt,statusCheckRollup`,
   minutes from the last check's completedAt to mergedAt; median; row text `MERGE-TIME median N min (target 15)`; WARN above
   15, UNREAD (never green) when gh or data fails. Register beside `check_time`. rules.py stays under 19,000 (now 18,575:
   pay with trimmed docstrings if the rule is over 400 bytes).
5. dev/toy/test-merge-guard.sh: cases on the fake gh (`dev/toy/fakegh/gh`): queue on and green PR -> exactly one
   `--merge --auto --match-head-commit <head>`, no plain merge; head moved -> refusal naming both heads; queue off -> direct
   merge; negative control: the pre-change direct-merge-only path fails the queue case; `--batch` under a queue -> one-line
   refusal and a no-queue repo still batches; `protected()` true for a merge_queue-only ruleset; the release PR is enqueued
   through `land`; merge_group contexts list. Health toy: PRs 10 and 25 minutes -> median and WARN, unreadable -> UNREAD.
6. Fold these into existing rows (net rows 0): extend `merge-guard-base-head`-family rows' toy and the health row that runs
   rules; no new tsv row; the tsv edit is a changed command or text only if a row's Given text must mention the case.
7. docs: Release.md gets only the REL-13 revision; How-to-use-Release.md lists the ruleset values and the recipe (merge
   commit, concurrency 3, group size 1 to 3, all entries must pass, required checks, who flips it and when).
8. Fill `## Verify by hand` in the goal file; PR body (written by goal.py pr from the goal and steps) must carry the ruleset
   values, the new-ruleset recipe, the merge_group check list and the GitGuardian note: add them to the How-to page and the
   goal's verify section so the body quotes them.

## Test for each done line (a row seen failing first, then passing)
1: the criteria text compare (existing docs audit/criteria checks); 2: toy queue case + negative control; 3: toy health
case; 4: grep of the How-to page and the verify section for each ruleset value; 5: toy merge_group listing; 6: toy release
via queue; 7: recipe grep; 8: toy batch cases; 9: size check row (existing script-size row) plus `git diff --stat`.

## What could break
Hold-the-lock timing (item 2); a fake gh that differs from real gh on `--auto` (the first real merge proves it);
`protected()` now true more often (a repo with a queue rule but no PR rule takes the release PR path, which is right);
merge.py over 19,000 bytes; the criteria `revise` flow needing the owner-record file entry (o283) present.

## Out of scope
Creating or changing the ruleset (the owner flips it after this is on main); `regression-pr.yml` (merge-queue-ci);
tag-only releases; any bypass actor (listed as an owner option only).

## Red team (fresh reviewer, code-only brief): approve with changes. Folded in
Settled answers to the three questions the done lines name:
- Release commit under a queue: a release PR through the queue (no bypass, no tag-only). `protected()` counts a
  `merge_queue` rule (autorelease.py, declared in touches by TD219). `advance` merges the release PR through `land()`.
  The one-at-a-time lock is taken only after the goal PR is MERGED and held through `ar.finish` until the release PR is
  MERGED, so the version (computed from origin/base in `push_release_commit`) cannot collide; the goal PRs themselves queue
  concurrently. This replaces build step 2's "unlock/relock": `pods.unlock` does not exist and graph.py is 13 bytes under
  the cap, so graph.py is NOT edited; in queue mode `main()` skips `merge_lock` before the enqueue and calls it before
  `ar.finish`. A bypass is listed with the ruleset values as an owner option only.
- Required checks on merge_group: a ruleset's required-status list is one list for the PR and the merge-group commit, so
  "GitGuardian required on pull_request only" cannot be set in a ruleset. The recipe lists only contexts that report on
  merge_group; the affected job (needs `merge_group` in regression-pr.yml, merge-queue-ci) is in; GitGuardian is out of
  the required list if it does not report there (advisory on PRs), and the PR body says that plainly, including that the
  GO gate (`private.required_checks`) reads the same list. To verify after merge-queue-ci lands, list the contexts on a real
  merge-group run.
- GRD-6: owner-set platform rules (Guardrails.md says the base refuses direct and force pushes, owner-set, health reads
  that they are set); nothing in the repo enforces or reads them today, rules.py has no rules/branches read. Until the
  owner creates the ruleset, local hooks are all that apply. Recorded for the owner; no requirement text changes.

Plan changes from the review:
1. `land()` polls `gh pr view --json state,isInMergeQueue,headRefOid`; MERGED returns; CLOSED, a changed head, or OPEN and
   not in the queue past a grace of 120 s (a dequeued entry) refuses; an overall deadline from LOOP_MERGE_LOCK_SECONDS
   (default 1800); a re-run finds `isInMergeQueue` and only waits (no second `--auto`). `queue_on` may use
   `isMergeQueueEnabled`; a failed read refuses, never a direct merge.
2. The toy supplies its own `gh` shim ahead of dev/toy/fakegh/gh on PATH (rules, `isInMergeQueue`, `--auto`, `pr view`),
   because dev/toy/fakegh/gh is outside touches.
3. Byte budget: merge.py has no waiting loop to trim (the design said so wrongly). The pay is the module docstring (about
   900 bytes), the `_pods` comment, and folding `load`/`leave_queue` into one-liners; measure with `tr -d '' | wc -c`
   after each edit. autorelease.py (18,945) trims blank lines and docstrings to pay for the `protected()` change.
4. MERGE-TIME uses the max `completedAt` among a PR's checks to `mergedAt`; missing values give UNREAD. rules.py is
   18,206 LF bytes (not 18,575, which counts CRLF); about 790 bytes of room.
5. `--batch` under a queue refuses before `merge_lock` is taken (merge.py:274), using `queue_on` from `top` and `base`.
6. Hand-off for merge-queue-ci (pc-w9), outside this goal: regression-pr.yml needs `merge_group: types: [checks_requested]`
   and `${{ github.event_name }}` in its concurrency group (or `gh-readonly-queue/**` in branches-ignore on push),
   or the push run and the merge_group run share `github.ref` and cancel each other, and a cancelled required check
   dequeues the entry. Also `regression.py run --reuse` must compute its affected set on a merge-group ref.
7. Out of scope, noted: `release_statuses` posts commit statuses to the release PR head; a required context satisfied only by
   such a status never reports on the merge-group commit. The recipe says every required context must be an Actions check
   that runs on merge_group.
