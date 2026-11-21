# The loop ships only as the GitHub template (TD554, the owner's words in operation-top; the repo's template setting is on): the requirement text from operation-top's readme-drafts/pending-folds.md item 5 goes in as drafted (SET-10 one versioned template, no skills package; GRD-20 keeps the 19,000 warn and 20,480 fail limits and drops the package rules and file cap; SET-1 gains automatic template update PRs); the release stops building or stamping the package and stays a tag release; the package-only gates and rows retire (package-passes, package-passes-3800, package-gate-head, trim-package-98, package-rows-tracked, package-headroom-held, and any row that only enforces the 100-file cap or listing.json), every script-size row stays; listing.json and dev/package.py go only if nothing else reads them

- Slug: template-only
- Touches: README.md, docs, skills, dev, .loop, .github
- ETA: 210 active minutes (estimate 167m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the pull request, then the README and pages carry item 5's text as drafted, the release makes a tag release with no package, and each retired row is gone from regression.tsv and the known list with the reason
2. Given every script-size row, then it still runs and passes, a script at 20,481 still fails (negative control), and nothing that reads listing.json or dev/package.py is left broken (listed with what was kept or removed)
3. Given this goal's diff, then docs.py check and criteria.py render --check pass, no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

Fixes #4653. Owner decisions: the requirement text of item 5 (SET-10, GRD-20, SET-1) went in on owner records o677, o678 and o679; at the final gate of the plan the owner answered `uc1b uc2a` (record o691): the stacked codex-git-root change is dropped from this branch (it is its own goal and PR), and the release tags a release commit with VERSION set (ENG-1).

### What changes
- **Release:** release.yml makes a tag and its generated notes only; no zip, no VERSION stamp into a package. The tag is a release commit (the merge's tree with VERSION set, the merge as its parent), pushed alone: main does not move. Reruns find the tag by its parent and create only a missing release. The version step accepts only v<N>.<N>.<N> tags, starts at 0.0.1 with no tag, and reads zero-padded parts as decimal. The post-release view step only warns; a concurrency group serialises runs. Why: the repo's VERSION is 1.0.112 while tags are at v1.0.157, so without the release commit every no-zip adopter would read `AVAILABLE v1.0.112 is older than INSTALLED v1.0.157: nothing to do` from update.py for every release.
- **Last-release lookups:** because the new tags are not on main, health's `unreleased` rule and the release notes' Fixes range take the newest v tag by version and its parent instead of `git describe` (found by three review sources).
- **Gates:** the package step is gone from the generated workflows; the static safety scan of the shipped skills files (frontmatter, scripts' imports, secrets, encoded text, agent-aimed instructions, dangerous commands, private prefixes) stays, as `dev/skills-scan.py` (a thin entry to dev/package.py's rules) in the affected and merge-group jobs and as the row `skills-static-rules`. Health's script byte rule, its control and `health_script_bytes` are removed, with the retired rule's open issues now closing and an old `off: scripts` entry ignored.
- **Kept on purpose:** `dev/package.py` and `listing.json` are fixture-only (update.py's toys build packages with them) until the follow-up **update-package-path** retires update.py's package path, package.py, listing.json and those fixtures. package.py's dead listing and disclosure code is deleted. update.py is unchanged: with no zip it reads the tag's source archive and its VERSION.
- **Tests:** `test-release-ci.py` scans every workflow (REL-CI-001 to 003, standard library) and runs the release job's own steps in a temp clone with a fake gh: VERSION at the tag is the version, main is untouched, reruns make no second tag, the no-tag and padded-version inputs work, and a **no-zip adopter on 1.0.157 reads the newer version from the tag's source archive; with ENG-1 reverted the adopter reads the stale VERSION and the toy fails** (control).

### Rows: net -30 (main 694, here 664); known list 26 (main 32)
Every cut row and the limit this goal removes (the audit read each row's command and description against its toy; none tests more than the removed limit except where noted):

| Row | Goal | Removed limit |
|---|---|---|
| ls-size-budget | local-schedule:1 | script byte limit (19,000 warn, 20,480 fail) |
| size-budget | lane-control:7 | script byte limit (19,000 warn, 20,480 fail) |
| size-140 | SET-10 | script byte limit (19,000 warn, 20,480 fail) |
| pods-size | pods:6 | Agensi package and script byte limit |
| plan-sizes | lane-plan-cache:5 | Agensi package and script byte limit |
| package-win-parity-1397 | win-package:1 | Agensi package (build, 100-file cap, listing, hang bound) |
| package-win-stdin-1397 | win-package:2 | Agensi package (build, 100-file cap, listing, hang bound) |
| package-hang-stdin | package-hang:1 | Agensi package (build, 100-file cap, listing, hang bound) |
| package-hang-bound | package-hang:2 | Agensi package (build, 100-file cap, listing, hang bound) |
| package-hang-slot | package-hang:3 | Agensi package (build, 100-file cap, listing, hang bound) |
| package-hang-no-skills-file | package-hang:4 | Agensi package (build, 100-file cap, listing, hang bound) |
| package-passes | package-cap-3:1 | Agensi package and script byte limit |
| machine-done-12 | operator-setup:12 | Agensi package and script byte limit |
| size-lf-crlf | - | Agensi package and script byte limit |
| package-gate-controls | DEL-1 | Agensi package and script byte limit |
| package-gate-head | SET-10 | Agensi package and script byte limit |
| repo-rules-threshold | SET-2 | script byte limit (19,000 warn, 20,480 fail) |
| package-caps-held | GRD-20 | Agensi package and script byte limit |
| package-headroom-held | SET-10 | Agensi package and script byte limit |
| package-rows-tracked | SET-10 | Agensi package (build, 100-file cap, listing, hang bound) |
| package-passes-3800 | SET-10 | Agensi package and script byte limit |
| pods-caps-3919 | windows-safe:3 | Agensi package and script byte limit |
| docs-release-scripts-under-19000 | HLT-2 | script byte limit (19,000 warn, 20,480 fail) |
| scripts-c-regression-under-19000 | REG-4 | script byte limit (19,000 warn, 20,480 fail) |
| release-scripts-under-19000 | DEL-1 | script byte limit (19,000 warn, 20,480 fail) |
| docs-scripts-under-19000 | DOC-25 | script byte limit (19,000 warn, 20,480 fail) |
| scripts-a-monitoring-under-19000 | OPS-1 | script byte limit (19,000 warn, 20,480 fail) |
| listing-names-every-command | package-cap-3:1 | Agensi package (build, 100-file cap, listing, hang bound) |
| trim-setup-under-19000 | trim-scripts-98:1 | script byte limit (19,000 warn, 20,480 fail) |
| trim-package-98 | trim-scripts-98:2 | Agensi package and script byte limit |
| size-warn-band | HLT-2 | script byte limit (19,000 warn, 20,480 fail) |
| trim-monitoring-4-size | HLT-2 | script byte limit (19,000 warn, 20,480 fail) |
| full-auto-no-new-file | full-auto-all:4 | Agensi package (build, 100-file cap, listing, hang bound) |
| hands-off-size | hands-off-operation:8 | script byte limit (19,000 warn, 20,480 fail) |
| release-static-rules | fast-release-rules:1 | Agensi package and script byte limit |
| package-static-toy | fast-release-rules:1 | Agensi package (build, 100-file cap, listing, hang bound) |

**Restored narrowed** (they chained a behavior case with a limit case): `ls-scheduled-rule` (from ls-size-budget: the leftover health.yml WARN naming git rm, the missing Actions workflow, the mac exemption) and `plan-cache-states` (from plan-sizes: the Plan cache page names every state). **Cases cut from rows that stay**, each testing only a removed limit: `skill-size-116`: size-139 and size-141 (script byte warn at 19,000 and fail at 20,480, and the symbol-move checks of the split made to fit it); `machine-task-layout`: machine-caps (machine.py and every script under 20,480 bytes; its other half, machine.py not under skills/, stays as `machine-location`); `same-lines`: "over 20 KB is a FAIL with a fix". Kept from the cut asserts: `a FAIL makes the verdict not green` (test-health.sh, now on the docs FAIL). **New rows:** `skills-static-rules` (SET-10), `size-limits-held` (GRD-20, the one criterion row the cuts left uncovered), and `rel-ci-release` now also runs the release and scan checks. **Not mine, fixed on the way:** four rows left twice by an earlier merge are one each; four rows main had folded away that my merge brought back are gone again.

### CI run 44861339984 at 14b01eb9: 7 of 11 jobs red, each FAIL line run alone on main (48ac06e7d) and on this branch
| Job | FAIL lines | Cause |
|---|---|---|
| shard 1 | repeat-no-second | this change: its toy filed the removed `scripts` WARN; now a SKILL.md finding |
| shard 3 | est-backtest-loo | this change: a renamed function (restored) |
| shard 4 | skill-size-116, no-token-would, hlt4-feature-milestones | this change: chained removed cases; toys filed the removed WARN (a test-only stand-in rule, dev/toy/health-standin.py, supplies a WARN; every assertion is unchanged) |
| shard 5 | pr-no-milestone, health-feature-always, health-stale-checkout, known-no-block | this change for the first three (same fix); known-no-block passes alone on main and here and was LEFT over the 200 s row limit on the shard: not this change (inferred: runner load; not reproduced) |
| shard 6 | same-lines, health-findings-table, backlog-milestones-made | this change |
| shard 7 | grd5-health-close | this change (same fixture) |
| affected | the shards' result | consequence of the shard failures |
All 13 rows (these 12 plus machine-task-layout, which chained the same removed case) pass alone on this branch and on main. Still red alone on main and here, not this change: setup-no-milestone-step (known, #5312), test-health-prd parts h1 and h2, and test-health's "a line outside the template" and "check gh calls".

### Review (full pipeline, native and outside voices)
Plan: CEO, DX and Eng phases each with a native reviewer and an outside voice (design skipped, no UI). Code review: six specialists (testing, maintainability, security, performance, simplification, state machines), a red team, a native adversarial pass and two outside passes. One finding was critical and found by three sources (tags off main break `git describe` consumers): fixed with a toy. Also fixed: package.py's dead code, the first-tag and padded-version inputs, a rerun that fails on a transient view error, the masked token header, the scan's controls (one payload per safety class) and the scan as a whole-tree row, two Tests rows that still said size-check.py, stale package and store wording, and the dead helpers in test-release-ci.py. Dropped with evidence: the stand-in rule's "vacuous control" (the small-file and missing-file cases are tested at test-health-prd.sh:94-96 and test-milestones.sh).

### Accepted risks and follow-ups
- **update-package-path** (follow-up goal): retire update.py's package path, package.py, listing.json and the fixtures; until then the path is unsupported. update.py reads the whole-repo source archive: 11.1 MiB uncompressed against its 20 MiB cap [measured], archive hashes are computed from the archive itself, and installs whose update.py predates the archive fallback (v0.23.0) cannot update. The tag's CHANGELOG.md is main's copy.
- **toy-hermetic** (Operation, TD604): qa waits for it on main; the two toys it covers are not run here.
- **First release after merge**, watched by Operation: the tag v<next> exists on a release commit whose parent is the merge; the generated notes exist; the release holds zero assets; update.py run against the real release reads the new version; update.py against the real published release.
- **Rollback** is a revert of this whole change. **The trade:** the dropped store channel's reach for one distribution path; the owner will watch template uses, forks and adopter pull requests. SET-10 stays **Unreviewed** (the owner reviews it by their own record); GRD-20 and SET-1 are Reviewed (o679). The Roadmap's package-under-cap and agensi-ready items are owner text and are untouched.
- **Written with the file tool under o685:** the Keep it current note in How-to-use-Setup.md, one line in DECISIONS.md, and wording fixes in skills/workflow-docs/references/commands.md, settings.py's template_repo description and the review-help-runs-alone row.
