# rel-15-release: plan

Idea and plan only; no build, no lane. Build waits for rel-15-queue merging and operation's BUILD.
Read: autorelease.py (push_release_commit, create_release, finish 355-383), merge.py (advance 190-215, line 168, the
`gh pr merge --merge` call near 340), release.py (bump, changelog_text, cmd_cut), .github/workflows/regression.yml
(`push: tags: v*`) and regression-pr.yml, health rules.py `template_version` (VERSION vs newest CHANGELOG heading),
setup update.py (reads VERSION from a source tree or archive).

## Today and what REL-15 needs

finish() on an unprotected base calls `push_release_commit` (VERSION + CHANGELOG commit pushed to main, with a fetch/bump
retry loop); on a protected base `merge.advance` opens a release PR, waits for its checks and merges it. Either way a
second commit or PR follows every goal. Then `create_release` runs `gh release create vX --target <that commit>`.

## Tool chosen: `gh release create` in a workflow (https://cli.github.com/manual/gh_release_create)

Not release-please (https://github.com/googleapis/release-please): it works by keeping a standing release pull request and
a commit that bumps VERSION/CHANGELOG, which is exactly the second pass REL-15 removes. `gh release create --generate-notes`
makes the tag and release from one step and pushes no commit. (Principle 7: adopt, don't rebuild; the tool is the gh
the repo already uses.)

## Design

- New `.github/workflows/release.yml`: `on: push: branches: [main]`, `permissions: contents: write`, one short job, no lane.
  It reads the release part from the merge commit (`Release-Part: patch|minor|major` trailer, written by merge.py in the
  `gh pr merge --merge --body` text), takes the highest existing `v*` tag, bumps it, and runs
  `gh release create vX.Y.Z --target $GITHUB_SHA --title vX.Y.Z --generate-notes`. A merge without a trailer (a docs or
  test change, today's `stage_part` "patch" case) releases a patch, so every merge is released as today.
- Idempotent: if the tag exists at that sha the job exits 0 (rerun safe).
- VERSION and CHANGELOG.md: no release commit, so main's copies stop moving on their own. Decision for the Release page:
  CHANGELOG.md is replaced by the GitHub release notes (the page says so and the file keeps its history); VERSION on main
  is the last bumped value and the workflow stamps the true version into the release asset instead. This leaves
  adopters (setup update reads VERSION from the package/archive) needing the release asset, not main's file.
  See Question 1: it is the one design call I can't make alone.
- `regression.yml` has `push: tags: ["v*"]`; the tag the workflow creates would start a full CI run, the very pass REL-15
  forbids. Remove that trigger (the 4-hourly schedule and workflow_dispatch stay).
- autorelease.py: finish() calls a new small `release_from_ci(state)` instead of push_release_commit/advance when
  `release_ci` is on: it records the part, waits (capped) for the tag, `gh release view` to read the URL, and prints
  RELEASED. The old path stays when the setting is off. autorelease.py is 18,945 bytes and merge.py 18,994 (cap 20,480):
  move the old release-commit path into `autorelease_old.py`? No: keep it, add the new function in a new file
  `release_ci.py` imported by finish() so neither script grows past 19,000.
- Health: `template_version` compares VERSION with the newest CHANGELOG heading; with both frozen it stays true, so no rule
  change if the page keeps both files as last-written. If the owner picks "stop writing both", the rule gets an INFO
  case "released from CI" (rules.py has ~5 bytes free, so the rule moves into controls/rules split; costs +30 min).

## Done lines

1. Workflow + finish(): toy `dev/toy/test-release-ci.py` runs finish() against a fake origin and fake gh, asserts no
   push to the base and no `gh pr create`, tag/release made once, rerun safe; workflow YAML parsed: trigger is push to
   main, no lane step, `regression.yml` has no tag trigger. Seen red first. 150 min.
2. Release page: names `gh release create` and its link, says who writes VERSION/CHANGELOG.md and in which PR (answer to
   Question 1), says the wiki publish after the merge is outside the 5 minutes; docs check, wiki.py prepare. 45 min.
3. Health and existing release checks pass (`health.py check`, the release toys test-autorelease/test-release/test-merge-*),
   no new regression row red on current main. 55 min.

Own estimate 250 min active, inside the frozen 275m.

## Cannot prove without a live release

- That GitHub fires `release.yml` on the merge push and that GITHUB_TOKEN may create the tag and release (repo
  Actions permissions: read/write; tag-protection rules would refuse it).
- That `--generate-notes` output reads acceptably and that the tag push really starts no other workflow.
- That the time from merge to a visible release is under the 5 minutes on GitHub's runners.
- Behaviour under a merge queue (needs the repo in an organization; rel-15-queue's limit too).
Locally these are proved by toys with a fake gh and parsed YAML only.

## Questions for operation before BUILD

1. VERSION/CHANGELOG.md: (a) freeze both and release from the tag, notes in the GitHub release (my pick, zero commits);
   or (b) keep writing them, in the goal's own PR before its lane (then every PR conflicts on them). Which?
2. Carry the part in a `Release-Part:` trailer on the merge commit. OK, or a PR label?
3. Remove `push: tags: v*` from regression.yml. OK (it is outside Touches; it is `.github/workflows`, which is in Touches).

VERDICT: self: plan covers D1-D3; open items are the three questions.
DEPTH: condensed
