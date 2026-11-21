# Plan: template-only (attempt 2)

## Implementation plan

Goal: the loop ships only as the GitHub template (SET-10); the requirement text of the owner's item 5 (SET-10, GRD-20, SET-1) is in as drafted; the release makes a tag and its generated notes only, no asset; the package-only and script-byte-only gates and rows are retired. The branch (loop/template-only, PR #5687 at 14b01eb9) already holds the work; this plan states what it does and what remains to verify.

### Steps
1. Requirement text (done): SET-10, GRD-20, SET-1 revised on owner records o677/o678; GRD-20 and SET-1 reviewed on o679; principle 5 prose in README and Home; README, Home and Principles cells follow.
2. Release (done): release.yml makes `gh release create vX --generate-notes` with no VERSION stamp, no zip; regression-pr.yml and its generator drop the package step; dev/package.sh and dev/test-package.sh removed.
3. Gates and rows (done): 39 package-only and byte-only rows cut; health's script-byte rule, its control and health_script_bytes removed; size-check.py becomes unread-check.py (byte part gone).
4. Mixed toys (done): byte and package asserts removed from the mixed toys (under dev/toy: 36 files modified, 12 removed, 1 renamed to unread-check.py, 1 added: health-standin.py); test-plan-cache keeps its states check as its own case.
5. Kept on purpose: dev/package.py (file cap, script size and listing checks removed) and listing.json, because the update/adopt/sync toys build update.py's fixtures with them; named follow-up update-package-path.
6. Stacked change dropped (uc1b, owner record o691): codex-git-root is its own goal and PR again; this branch no longer carries it (commit d5fc8291f restored its files to main's versions).
7. To do, from the CEO review (details in the accepted obligations): CEO-1 the no-package assert in test-release-ci.py; CEO-6 the skills-static-rules row; CEO-7 the asset-less update case in test-update-asset.py; the two generated Tests rows that still say size-check.py; the PR-body tables and statements.
8. Still to verify in this attempt: review (read the diff against main, and audit all 39 cut rows and every cut case for "tests only a removed limit"), qa (docs.py check, render --check, the changed toys against a clean main), a CI run on the final head after the last merge (green or fully classified), ship (private scan, push gate, goal.py pr onto #5687).

### Risks
Many toys touched at once (checked against a clean origin/main baseline); the Reviewed marks depend on o679; main moves often (merge, regenerate the generated tables, restamp).

### CEO decisions
CEO-1 accepted, CEO-2 and CEO-3 deferred, CEO-4 skipped, CEO-5 (the stacked codex-git-root change) first accepted on Operation's order, then dropped by the owner (uc1b, o691); the accepted obligations are in the accepted block that follows the review record.

### Final decisions (owner record o691, gate reply "rec except uc1b")
uc1b: drop the stacked codex-git-root commits from this branch; codex-git-root is its own goal and PR (rebased), not done here. uc2a: ENG-1 stands (the release job tags a release commit whose tree has VERSION set; main untouched; no zip; update.py unchanged); add a toy proving a no-zip adopter sees the true latest version, and it must fail with ENG-1 reverted. d1a: dev/skills-scan.py runs in the affected and merge-group jobs, with its row; net rows must stay at or below zero, folding new checks only into existing defect-category rows. d2a: the post-release view step is warn-only with a concurrency group. d3a: no per-toy surviving-assert count and no static-rules alias. p1a: the plan is approved as written, with ENG-1 superseding DX-1.

## Review record

### CEO review (SELECTIVE EXPANSION)

**0A Premise challenge.** Real problem: the loop shipped two ways (template repo and an Agensi skills package) and the owner decided on one; text, release, gates and rows still described both. The plan solves that directly (not a proxy). Do nothing: CI keeps building and gating a zip nobody consumes, rows keep failing on a limit that no longer exists, and requirement text contradicts the owner's decision.

**0B Existing code leverage.** criteria.py revise/review (owner records), regression.py workflow (regenerates CI files), settings.py reference, render and restamp-own: all reused. Rebuild: none; dev/package.py is kept as the fixture builder instead of rewritten.

**Reality rows**
REALITY: premise-table pass 10 claims, unverified=0: 694 rows on main vs 669 here (.loop/regression.tsv); known list 32 vs 26 (.loop/regression-known.tsv); release is `gh release create ... --generate-notes` (.github/workflows/release.yml:66); dev/package.py and listing.json kept (ls); 90 files changed, +426/-1505 (git diff origin/main --shortstat) [measured]
REALITY: already-done pass origin/main is still 48ac06e7d, merged into the branch; the only main commits naming SET-10 are the restored README sentence (7718fd05a, 2e87406fd), which the item 5 text builds on, not duplicates
REALITY: surface-check pass goal.py pr, criteria.py render|review|revise, regression.py add|red|sync|workflow all exist skills/workflow-delivery/scripts/goal.py:1
REALITY: binding-decisions pass the decision search returned no branch decisions; the owner records o677/o678/o679 and Operation's TD554 to TD604 messages bind: item 5 text verbatim, no review without an owner record, no push without Operation's word docs/wiki/Setup.md:18
REALITY: numbers pass every number above re-derived by command [measured]; the 12 red rows and 7 failing CI jobs are [re-measure before gate] .loop/regression.tsv:1
REALITY: deferred-asks pass TD591's requests all have a step; the update-package-path retirement is deferred with its reason (CEO-2) .loop/regression.tsv:277
REALITY: pr-count pass one PR (#5687); a split would cost a second queue run for no gain; the stacked codex-git-root change splits back out if template-only goes red .loop/config.json:1

**0C Dream state.**
CURRENT: two distribution paths, gates for both  ->  THIS PLAN: one path (template + tag), package gates and rows retired, package.py kept only as a fixture builder  ->  12-MONTH IDEAL: template releases reach adopters as an automatic pull request (SET-1), update.py has no package path, package.py and listing.json are gone.

**0D Alternatives.** A minimal (text + release only, High risk), B recommended and built (gates and rows cut, package.py kept as a fixture builder, L, Medium risk), C ideal (also remove update.py's package path now, XL, High risk). B is the highest completeness that stays in one reviewable change (P1, P3); C is deferred as CEO-2. No new approach question: B was approved in the design and the owner's yes covered the text.

**0F/0G Scope candidates** (S/M/L/XL):
| # | Proposal | Effort | Decision | Reasoning |
|---|----------|--------|----------|-----------|
| CEO-1 | Assert in test-release-ci.py that release.yml builds no zip and uploads no asset | S | ACCEPTED | in the blast radius, one file, stops the package step returning silently (P2) |
| CEO-2 | Retire update.py's package path, dev/package.py, listing.json and their fixtures | XL | DEFERRED | outside the blast radius, rewrites SET-3/4/5 rows; follow-up goal update-package-path (P3) |
| CEO-3 | Make test-platform-limits.py and test-machine-log.py hermetic | M | DEFERRED | owned by Operation (TD604, goal toy-hermetic); qa waits on it |
| CEO-4 | Turn health-standin.py into a real WARN size rule | M | SKIPPED | no production need; a rule only for a toy is the pathology (P5) |
Complexity check (HOLD): 90 files is over 8, but 70 are single-assert toy edits and generated pages; fewer moving parts cannot meet the done lines. Invariants kept: SET-10, GRD-20, SET-1 text as the owner approved it; no check loosened.

**0I Temporal.** Hour 1: the implementer must know the owner's text is frozen (records o677 to o679). Hours 2-3: toys that grep specific PASS lines hide failures a whole-toy run does not show (hit: 12 rows). Hours 4-5: the shards run toys in a different environment than this Mac (known-no-block passes alone and red on shards). 6+: regenerated tables and restamps conflict on every main merge. Effort: human ~2 days / CC ~2 hours for what remains.

**Dual voices.** Native CEO reviewer (completed, INPUT ceo b0d7f84f...): 9 findings (1 critical, 3 high, 5 medium). outside voice (completed): 5 findings (4 high, 1 medium), VERDICT FINDINGS.
CEO DUAL VOICES - CONSENSUS TABLE:
  Dimension                              Native   Outside   Consensus
  1. Premises valid?                     no       no       CONFIRMED: the template-only premise is stated, not tested against who consumes the zip or the listing
  2. Right problem to solve?             yes      yes(?)   CONFIRMED with a caveat: deleting the package surface is right; both ask for a customer thesis (taste, PR-body line)
  3. Scope calibration correct?          no       no       CONFIRMED: the stacked codex-git-root change is the wrong coupling (USER CHALLENGE, below)
  4. Alternatives sufficiently explored? no       no       CONFIRMED: package.py kept as a fixture builder and the update path unproven; both ask for an asset-less update toy (CEO-7)
  5. Competitive/market risks covered?   no       no       CONFIRMED: the dropped store channel has no adoption signal (PR-body line)
  6. 6-month trajectory sound?           no       no       CONFIRMED: the update/version path can strand or half-update installs
Findings and dispositions (ledger rows CEO-1 to CEO-7; every disposition is an auto-decision on the six principles, not an owner answer):
- Upgrade path unproven and unowned after merge (native 1, outside voice 2 and 4): CEO-7 accepted (update toy against an asset-less release, shows the sync.py skip); update.py stays unsupported until update-package-path; stays an accepted risk flagged to Operation.
- Retained behavior hidden inside the package gate (outside voice 3, verified: dev/package.py --static still runs frontmatter, inventory, script and safety scans and passes on this tree): CEO-6 accepted as a TASTE decision (a lane row keeps the scan); this reverses my cut of release-static-rules.
- Stacked codex-git-root (native 5, outside voice 5): both voices agree the structure should change. USER CHALLENGE, never auto-decided: original direction = stack it at Operation's order (TD569) so both land in one test-table cycle; proposed change = land codex-git-root on its own and rebase, or keep per-commit boundaries; reasoning = attribution of CI failures, a whole-change rollback that also reverts the permission fix, and one reviewer reading two features; blind spots = the one-cycle constraint and whether main can take the permission fix alone; cost of being wrong = a second queue cycle against an unreviewable PR. The stack stands until Operation decides.
- toy-hermetic gate has no deadline (native 6, outside voice 5): Operation's order; the deadline and the main-red fallback are theirs to set; noted in the PR body.
- "No loosened check" relies on later judgment (native 4, outside voice 3): the PR-body table covers all 39 cut rows with the removed limit; a surviving-assert count per toy is skipped as YAGNI (taste).
- Line-scan of YAML fragile (native 7): CEO-1 gains block-scalar negative controls; the `gh release create` argument check stays primary.
- Deferred work without owner (native 8): the PR body names them; listing.json and package.py marked fixture-only; no TODOS.md exists, so no TODO is written.
- Dropped channel, SET-10 unreviewed, no consumer check (native 2, 3, 9; outside voice 1): PR-body lines (trade, signal, SET-10's reviewer); the owner decided the one-channel direction, so the plan records the trade and does not reopen it.

**Section 1 Architecture** (2 findings: the stack coupling; the release/update contract):
```
  push to main -> release.yml: hold if main-red open -> version step (newest v tag + PR label)
        -> gh release create vX --target SHA --generate-notes   (tag + notes, no asset)
  adopter: update.py -> gh release download *.zip   (none)
                     -> gh release download --archive zip (source archive) -> VERSION from archive
                     -> sync.py: skip repo step when template_version >= target
  PR lane: regression-pr.yml shards (no package step) ; land lane rows ; skills-static-rules (CEO-6)
```
Single points of failure: the version step (newest tag); update.py reads VERSION from the source archive. Rollback: revert the whole change (also reverts the stacked permission fix; see the challenge).
**Section 2 Error and Rescue map** (capabilities):
  release job | hold (main-red open) | rescued: skips, no release | user sees: the job note
  version step | no previous v tag / label read fails | `|| true` on labels, patch default; first tag gap: GAP-1 none known, verified by the first-release watch
  gh release create | tag exists at SHA | rescued by the version step's skip=1
  update.py | no zip asset | rescued: source archive | version may lag: ACCEPTED RISK (tested by CEO-7)
  update.py | no release or timeout | UPDATE_GH refusal with the tail of gh's error | rescued
  sync.py | same version, changed files | repo step skipped: partial update, shown by CEO-7, not fixed here (GAP-2, owned by update-package-path)
  CEO-1 scan | YAML style not parsed | the argument check is primary; block-scalar controls
  rows | a cut row that tested more than the removed limit | review audits all 39; GAP-3 closed only when the audit is done
**Section 3 Security**: the removed package safety scan is the one real exposure (Medium likelihood, Medium impact: a secret, obfuscated text or an agent-aimed instruction in skills/ reaches adopters unscanned); mitigated by CEO-6. release.yml permissions unchanged; no new secret; the private-name scan runs at ship and on the final head; owner text only through owner records.
**Section 4 Data flow and edge cases**: release flow shadow paths: nil (no labels: patch), empty (no previous tag: first tag), error (gh api fails: `|| true`), conflict (tag already at SHA: skip), stale (main moved: the version step reads the newest tag at run time). update.py: no zip, no archive (refusal), older archive (nothing to do), equal version with changed files (applies files, sync skips repo: GAP-2). No user-visible interaction is added.
**Section 5 Code quality** (1 issue): dev/toy/health-standin.py is a test-only rule stand-in; it is small and named for its purpose; no duplicated behavior; no method branches more than five times. Over-engineering: none; under-engineering: the line-scan of YAML (CEO-1 controls).
**Section 6 Test review**:
```
  new thing                         test                                   gap
  no-package assert (CEO-1)         test-release-ci.py + negative controls  to build
  static scan row (CEO-6)           row skills-static-rules + control       to build
  asset-less update (CEO-7)         test-update-asset.py case               to build
  13 repaired rows                  each row alone                          done (0290de098)
  cut rows (39)                     audit table in the PR body              to build
  release job live                  first-release watch (4 checks)          after merge
```
Hostile QA: an unlisted upload tool in release.yml (argument check primary); chaos: main moves during the wait for toy-hermetic (final-head CI run). Flakiness: known-no-block red only on the shards (not reproduced).
**Section 7 Performance**: the per-PR package step and 39 rows go; the lane gets shorter; the added rows are cheap (one static scan, one toy case). No new background job.
**Section 8 Observability**: the release is the tag and its notes; health still reports Size, Hygiene and Adoption; the first-release watch is the day-one check; red proofs record each new row.
**Section 9 Rollout**: order = merge, release.yml runs on the next push to main, operator watches the first release; old and new code never run together (a single workflow file); rollback = revert the whole change (also the stacked fix) and re-run the release; no migration, no flag.
**Section 10 Trajectory**: debt = dev/package.py, listing.json, health-standin.py, update.py's package path (all named; update-package-path retires the first three); reversibility 4/5 for the code, 3/5 for published asset-less releases; the 1-year question: a new engineer sees a repo that ships by tag only, with a fixture-only package.py: the docstring note (accepted) makes that obvious.
**Section 11 Design**: SKIPPED (no UI scope).

**NOT in scope** (deferred): CEO-2 update-package-path (update.py's package path, dev/package.py, listing.json and their fixtures); CEO-3 toy-hermetic (Operation). (rejected): CEO-4 health-standin as a real rule; a surviving-assert count per toy.
**What already exists**: owner records and criteria.py revise/review; regression.py workflow and red proofs; release.yml's version step; update.py's source-archive fallback; dev/toy/fakegh; the private-name scan.
**Dream state delta**: moves from two distribution paths to one; the last mile (adopter pull requests, no update.py package path) is SET-1's future work.
**Error and Rescue Registry**: 8 rows above, 2 gaps (GAP-2 owned by update-package-path, GAP-3 closed by the review audit).
**Failure Modes Registry**:
  CODEPATH | FAILURE MODE | RESCUED? | TEST? | USER SEES? | LOGGED?
  version step | no v tag yet | Y (patch from 0.0.0 shape) | N (first-release watch) | a wrong first tag | Y (job log)
  update.py via source archive | VERSION lags the tag | N | CEO-7 | a stale version | Y
  sync.py | equal version, changed files | N | CEO-7 | partial update | Y
  CEO-1 scan | unlisted upload tool | partial (argument check) | controls | silent | N
  rows | cut row tested more than a limit | N until audit | audit table | silent | N
Critical gaps (RESCUED=N, TEST=N, silent): 0 after CEO-7 and the audit.
**Diagrams**: system architecture, data flow with shadow paths, error flow, deployment sequence and rollback flowchart are the ones above (release, update, lane); no state machine is added; stale diagram audit: docs/wiki pages that draw the release or package flow were regenerated or reworded by this change (Setup, Guardrails, Release): none stale found by grep for "package".
**Implementation tasks** (see JSONL): T1 CEO-1 assert and controls (P1); T2 CEO-6 row (P2); T3 CEO-7 toy case (P1); T4 stale-name fix (P2); T5 PR-body tables and statements (P1); T6 the 7-job CI diagnosis (P1).

### DX review (DX POLISH, product type: agent skill / CLI / template)

**Persona card.** Who: a solo developer or an AI coding agent adopting the template into a repo and keeping it current. Context: runs `/workflow-setup` once, then `update --check` when a release lands. Tolerance: about 10 minutes for the first adoption, one command for an update. Expects: a release that carries what update needs.
**Developer empathy narrative.** I make a repo from the template, run the setup command, merge its branch, and it works. Weeks later a release lands. I run `update --check`; it says what is new, I apply it, and my own settings stay. Today, if the release has no zip, I get the source archive, its VERSION file says an older number than the tag, and `--check` may tell me I am up to date while skill files changed. I would not know. If an archive is bad, the error tells me to use a package built by a dev script I do not have. [observed from update.py lines 172 to 175, 241 to 244, 308 and sync.py 206 to 208; not run live]
**Competitive benchmark** (reference benchmarks; research through the web was not run, so these are estimated, not measured): GitHub template repos (create from template, one step, no updates), cookiecutter/copier (copier update re-applies a template with a recorded answers file, one command), pre-commit autoupdate (one command, rewrites pins). This product: adopt = make repo + install skills + setup + merge, about 8 minutes [estimated]; update = one command, now through the source archive. Target tier: Competitive (2 to 5 minutes) is not claimed; the plan keeps the current trajectory and does not change adoption.
**Magical moment.** `update --check` shows what the newest release brings and which skill files you changed; delivered by the existing update.py preview, no new vehicle (DX POLISH).
**Developer journey map**
STAGE | DEVELOPER DOES | FRICTION | STATUS
1 Discover | finds the template on GitHub | store listing channel dropped (trade recorded, CEO) | deferred
2 Install | make repo from template, install skills | six steps before first goal, unmeasured (outside voice 2) | deferred (clean-machine walkthrough is a follow-up)
3 Hello world | `/workflow-setup`, merge the setup branch | unchanged | ok
4 Real usage | runs goals | unchanged | ok
5 Debug | reads update.py errors | UPDATE_BAD_ARCHIVE names dev/package.py (CAP6 fix wrong) | deferred to update-package-path
6 Upgrade | `update --check`, `update` | asset-less fallback: VERSION may lag the tag; no warning (CAP4) | DX-1 accepted (taste)
**First-time developer confusion report.** T+0:00 makes the repo, reads README: finds the Agensi/package mentions only in Roadmap items and a skill reference. T+2:00 runs setup: fine. T+5:00 runs `update --check` against a release with no zip: reads "UP TO DATE" while the template moved (predicted from code, not run). T+6:00 hits UPDATE_BAD_ARCHIVE on a bad download and is told to use `dev/package.py`, which an adopter does not have. Addressed by DX-1 and DX-2; the rest deferred.
**Dual voices.** Native DX reviewer (completed): 1 Critical (CAP4 update.py asset-less fallback can report success), 6 High, 7 Medium, 2 Low. outside voice (completed): 5 findings (1 High, 4 Medium), VERDICT FINDINGS.
DX DUAL VOICES - CONSENSUS TABLE:
  Dimension                           Native  Outside  Consensus
  1. Getting started < 5 min?          6/10    open   CONFIRMED: unmeasured; the plan never writes the new path (follow-up walkthrough)
  2. API/CLI naming guessable?         6/10    ok     DISAGREE (taste): native wants a static-rules alias, the outside voice does not raise it; deferred to CEO-2
  3. Error messages actionable?        4/10    gap    CONFIRMED: update.py's bad-archive fix names dev/package.py; asset-less success signal
  4. Docs findable & complete?         6/10    gap    CONFIRMED: stale package and store wording in a few places (DX-2)
  5. Upgrade path safe?                3/10    gap    CONFIRMED: both rate it the weakest; a USER CHALLENGE below
  6. Dev environment friction-free?    7/10    ok     CONFIRMED
USER CHALLENGE 2 (not decided here): both voices (and both CEO voices) say the asset-less release is safe only after the update path is fixed: the outside voice recommends completing update-package-path before removing release assets; native recommends at least a tag-versus-VERSION warning. Original direction (the owner's SET-10): no package asset from the next release. Proposed change: keep the zip until update-package-path lands, or ship the DX-1 warning with this change. Reasoning: existing adopters can be told "up to date" while behind. Blind spots: nobody has measured how many adopters use the update path; the stale-version case needs VERSION to lag the tag. Cost of being wrong: a silent stale install for every adopter on the next release, against a one-release delay of the owner's decision. The decision stands as the owner made it, with DX-1 as the minimum mitigation, until the owner or Operation decides.
**Pass 1 Getting started 6/10** (target 8): the adopt path is unchanged and the new path is not written; no instrumented time; fix in scope = none beyond the walkthrough follow-up. **Pass 2 API/CLI 6/10**: `update.py --from PACKAGE` help still advertises the package; a CLI help rewording belongs to update-package-path; names otherwise unchanged. **Pass 3 Errors 4/10 (CAP4) to 6/10 after DX-1**: ERROR PATH MATRIX (agent-ready-v1)
  Path                         | Class   | what | fix  | recovery | code | context | trace | redaction | channel | Cap
  update asset-less fallback   | success | fail | fail | fail     | fail | fail    | N/A   | pass      | fail    | CAP4:channel (success while behind)
  UPDATE_BAD_ARCHIVE           | runtime | pass | fail | pass     | pass | pass    | N/A   | pass      | pass    | CAP6:fix (names dev/package.py)
  CEO-1 scan failure           | usage   | spec | spec | N/A      | spec | N/A     | N/A   | pass      | spec    | CAP6:code (message contract unspecified until DX-6)
  release job after create     | runtime | pass | spec | spec     | N/A  | pass    | N/A   | pass      | pass    | CAP6:recovery (rerun semantics unstated)
  unexpected failure           | crash   | the plan names none; recorded as the trace gap
**Pass 4 Docs 6/10 to 7/10**: stale package and store wording in four places (DX-2). **Pass 5 Upgrade 3/10 to 5/10**: the weakest; the warning (DX-1), notes surfacing in the PR title (DX-3) and the "keep it current" note (DX-4) are the in-scope parts; the update-preview-with-release-notes and the old-install migration test are update-package-path. **Pass 6 Dev environment 7/10**: no issue; works in CI non-interactively; no new tooling. **Pass 7 Community 5/10**: unchanged; the dropped store channel is a recorded trade. **Pass 8 Measurement 5/10**: the first-release watch (4 checks) is the measurement; automated release assertion DX-5; no telemetry added (a policy, not asked).
**DX Scorecard**
+====================================================================+
| Dimension            | Score  | Prior  | Trend  |
| Getting Started      | 6/10   | n/a    | -      |
| API/CLI/SDK          | 6/10   | n/a    | -      |
| Error Messages       | 4/10 (CAP4) to 6/10 after DX-1 | n/a | - |
| Documentation        | 6/10 to 7/10 after DX-2 and DX-4 | n/a | - |
| Upgrade Path         | 3/10 to 5/10 after DX-1, DX-3, DX-4 | n/a | - |
| Dev Environment      | 7/10   | n/a    | -      |
| Community            | 5/10   | n/a    | -      |
| DX Measurement       | 5/10 to 6/10 after DX-5 | n/a | -   |
| TTHW                 | ~8 min [estimated] | not measured | -  |
| Competitive Rank     | Needs Work (5-10 min, estimated)             |
| Magical Moment       | designed via the existing update --check preview |
| Product Type         | agent skill / CLI / template           |
| Mode                 | POLISH                                       |
| Overall DX           | initial 5/10, after the accepted fixes 6/10  |
+====================================================================+
| DX PRINCIPLE COVERAGE: Zero Friction gap (unmeasured) | Learn by Doing covered (update --check) | Fight Uncertainty gap (CAP4) | Opinionated + Escape Hatches covered (--from, --tag) | Code in Context covered | Magical Moments covered | Agents Are Users gap (success while behind) |
+====================================================================+
**DX Implementation Checklist**
[ ] Time to hello world measured on a clean machine (follow-up; not in this change)
[ ] Installation is one command: gap, five steps today
[ ] Magical moment delivered via the existing update --check preview
[ ] Every new error meets the agent-ready contract: DX-1, DX-6
[ ] Docs copy-paste examples work: DX-4
[ ] Upgrade path documented with a note: DX-4
[ ] Changelog or release notes surface the change: DX-3
**NOT in scope (DX)**: clean-machine TTHW walkthrough per agent (follow-up); update preview showing release notes, old-install migration test, bad-archive fix wording, `--from PACKAGE` help (update-package-path); error codes for the stacked the outside voice refusal (codex-git-root owner); rename stubs for size-check.py and dev/package.sh (rejected: dev tools, no adopter caller); a static-rules alias for package.py (CEO-2); an opt-out comment for the asset ban (rejected: the ban encodes SET-10); a single verify command (rejected: the PR-body table is the entry point); GitHub issues for the follow-ups (outward action; left to Operation).
**What already exists (DX)**: update.py's `--check`, `--tag`, `--from` and its stable error codes; `gh release create --generate-notes`; How-to-use-Setup's "Keep it current" step; the fake gh for toys.
**Implementation tasks (DX)**: T1 DX-1 warning in update.py (P1); T2 DX-2 stale wording in 3 places (P2); T3 DX-3 PR title (P2); T4 DX-4 setup page note (P2, doc text written with the file tool under owner record o685 only if the push hook matches only prose, named in the PR body); T5 DX-5 release.yml assertion (P2); T6 DX-6 scan failure message contract (P1).

### Eng review (scope accepted as-is)

**Step 0 Scope challenge.** Plan files counted by the plan itself: 90 changed files under the diff, plus 7 to 8 more for the accepted additions (test-release-ci.py, test-update-asset.py, release.yml, regression-pr.yml and its generator, a thin dev/skills-scan.py, the regression table, three docs); well over 8 files and 1 new script, so the structure question was auto-decided (question_id plan-eng-review-structure): original arrangement kept; a smaller arrangement does not exist because 70 of the 90 files are single-assert toy edits and generated pages; no feature was cut (scope never reduces, P2). Result: scope accepted as-is. Complexity check: one new script (dev/skills-scan.py), no new service or class. Search check: none new (GitHub release API and git plumbing are built-ins; [Layer 1]). TODOS cross-reference: the repo has no TODOS.md; the follow-ups live in the PR body.
**Reality rows**
REALITY: premise-table pass 9 claims, unverified=0: VERSION in the repo is 1.0.112 while the newest tag is v1.0.157 (VERSION:1, git tag) [measured]; update.py takes the version from the archive's VERSION (skills/workflow-setup/scripts/update.py:172-175) and returns "nothing to do" when it is older than the installed one (skills/workflow-setup/scripts/update.py:399-401); regression-pr.yml skips rows for Markdown-only changes (.github/workflows/regression-pr.yml:35) and the removed step ran in the affected and merge-group jobs (commit 48ac06e7d .github/workflows/regression-pr.yml:56 and 88); the source archive is 11.1 MiB uncompressed against update.py's 20 MiB cap (skills/workflow-setup/scripts/update.py:49) [measured, git archive]; the fallback to the source archive exists since v0.23.0 (git log -S);  dev/toy/test-update-asset.py:36-41 already tests that a release without an asset falls back to the source archive (selection only, with empty placeholder zips)
REALITY: already-done pass origin/main is still 48ac06e7d (git fetch); nothing in main duplicates the release-commit fix .github/workflows/release.yml:57-66
REALITY: surface-check pass `gh release view --json assets,tagName` and `gh release delete` exist (gh help); `git commit-tree`, `git tag`, `gh release create --verify-tag` are standard git and gh; package.py --static exists dev/package.py:442
REALITY: binding-decisions pass no branch decisions in the decision search; the owner records, Operation's orders (qa gate, ban on two toys, TD601 plan route, o685 doc text) bind docs/wiki/Setup.md:18
REALITY: numbers pass 11.1 MiB, 1.0.112, v1.0.157, 90 files, 694 to 669 rows: all re-derived by command [measured], the first-release timings are [re-measure before gate] VERSION:1
REALITY: deferred-asks pass the CI diagnosis, the 13 rows, the cut-case list, the two Tests rows: each has a step .loop/regression.tsv:277
REALITY: pr-count pass one PR; splitting the stacked change is the user challenge, its queue cost is one more cycle .loop/config.json:1
FINDING from the reality rows (corrects the CEO record): the plan said the fallback was "not proven by a toy"; selection is proven (dev/toy/test-update-asset.py:36-41), version identity and loading are not.

**Dual voices.** Native ENG reviewer (completed, INPUT eng c08ce025...): 11 findings (2 high, 8 medium, 1 low) plus edge cases. outside voice (completed): 5 findings (3 high, 2 medium), VERDICT FINDINGS.
ENG DUAL VOICES - CONSENSUS TABLE:
  Dimension                           Native  Outside  Consensus
  1. Architecture sound?               no      no     CONFIRMED: version identity is broken for asset-less releases; verified (VERSION 1.0.112 vs tag v1.0.157)
  2. Test coverage sufficient?         no      no     CONFIRMED: fixtures prove selection not loading; surviving-row audit is manual; full-archive size untested
  3. Perf risks + budget/bench named?  ok      gap    DISAGREE (taste): outside voice 5 (11.1 of 20 MiB cap), native none; measured and recorded as an accepted risk
  4. Security threats covered?         gap     gap    CONFIRMED: the static scan lost its per-PR and merge-group enforcement; notes and PR text are unscanned
  5. Error paths handled?              gap     gap    CONFIRMED: post-publication check, rerun and retry semantics
  6. Deployment risk manageable?       no      no     CONFIRMED: the first release is public and irreversible; existing adopters' installed updaters cannot be patched
Single-voice critical flagged: none single; the version-identity finding is critical and verified.
**The critical finding, verified.** After this change every release's source archive carries VERSION 1.0.112, the value written by the last release commit, while tags are at v1.0.157. An adopter whose installed template version came from a zip (for example 1.0.157) runs update and reads "AVAILABLE v1.0.112 is older than INSTALLED v1.0.157: nothing to do" (skills/workflow-setup/scripts/update.py:399-401) for every future release: the update path is silently dead for every existing adopter, and their installed update.py cannot be patched through the path it breaks. The DX-1 warning cannot reach them either. Fix (ENG-1): the release job tags a release commit whose tree is the merge commit's tree with VERSION set to the new version, so the source archive's VERSION equals the tag; no zip, no change to main, no change to update.py. This replaces DX-1.
USER CHALLENGE 3 (not decided here): the Eng voices make User Challenge 2 concrete. Original direction: no zip from the next release. Proposed change: ship ENG-1 (VERSION correct inside the tag) with this change, or keep a stamped zip for one more release. Reasoning: verified stranding of every existing adopter. Blind spots: nobody has counted adopters on the zip path; a tag on a commit that is not on main is unusual (tag history shows a detached release commit). Cost of being wrong: every adopter silently stops updating. ENG-1 is accepted as the minimum safe form of the owner's decision, so the owner's direction (no asset) is kept; only whether to ship without ENG-1 is the owner's call.

**Section 1 Architecture** (4 issues). Dependency graph (new and changed):
```
  merge to main -> release.yml: hold? -> version step (newest v tag + PR label)
        -> release commit = merge tree + VERSION=X  (ENG-1; parent = merge SHA; main untouched)
        -> git tag vX (annotated, message names the merge SHA)  -> git push origin vX
        -> gh release create vX --verify-tag --generate-notes -> gh release view assertion (warn-only, ENG-3)
  adopter: update.py -> *.zip? none -> source archive of vX -> VERSION == X -> sync.py repo step
  PR lane: regression-pr.yml (affected + merge group) -> dev/skills-scan.py (ENG-2) ; shards run rows
```
Coupling: release.yml now owns a git object (the release commit); the update path depends on VERSION inside the tag. SPOF: the version step (newest tag). Security: the release job keeps `contents: write` only for tags; `pull-requests: read` and `issues: read` stay for the label and hold reads. Production failure: the tag push succeeds and release creation fails: the rerun finds the tag (idempotence keyed on the parent SHA, ENG-1) and creates the release only. Design-twice: second shape = write VERSION on main through a release PR; rejected (protected base, one more merge, ships a commit per release). Red flags: hand-synced list (the cut-row list is checked by the mechanical audit, ENG-5); two ways to do one task (package.py --static and dev/skills-scan.py: the scan entry point delegates, one owner).
**Section 2 Code quality** (2 issues): dev/skills-scan.py must be a pass-through only (calls package.py's static rules, no copy), documented as the entry point CEO-2 will move; health-standin.py already carries its own docstring and reads header. Cyclomatic: no new function branches more than five times. Diagram accuracy: the Setup page's release flow wording is updated by DX-4.
**Section 3 Test review.** Coverage diagram:
```
CODE PATHS                                             USER FLOWS
[+] .github/workflows/release.yml                      [+] adopter updates from an asset-less release
  |- version step                                        |- [GAP] [->E2E] installed 1.0.157, archive VERSION 1.0.158: updates (CEO-7 + ENG-1)
  |- release commit + tag (ENG-1)                        |- [GAP] archive VERSION == tag: no stale claim
  |   |- [GAP] VERSION at tag == version, tree otherwise equal   [+] maintainer reruns a failed release job
  |   |- [GAP] rerun: tag exists, release missing         |- [GAP] rerun creates the release only
  |   '- [GAP] main ref unchanged
  '- final view step (warn-only)  [GAP] message names tag
[+] dev/toy/test-release-ci.py (CEO-1, DX-6, ENG-4)    [+] a skills change that only edits Markdown
  |- [GAP] shlex allowlist, continuation, variable      |- [GAP] [->E2E] CI runs dev/skills-scan.py for it (ENG-2)
  |- [GAP] failure messages and codes (REL-CI-001..3)
  '- [GAP] negative controls on temp copies
[+] update.py fallback (existing code, read-only)       [+] 39 cut rows
  |- [* TESTED] selection to source archive (test-update-asset.py:36)   |- [GAP] mechanical audit table (ENG-5)
  |- [GAP] archive without VERSION / unparsable / no archive
  '- [GAP] loading: version reported, sync skip
COVERAGE: 4 of 19 paths tested (21%); 15 gaps, all carried by accepted obligations or the audit
```
Test requirements: each GAP has an owner row in the accepted obligations (CEO-1, CEO-7, DX-6, ENG-1 to ENG-5). Value cards (protects/fails_when/why_new/seam/no_claim) are in the test plan artifact. LLM/eval scope: no prompt or skill-text change that needs an eval; the safety scan itself is the nearest check. Tests made obsolete: the 39 cut rows and the cases cut from three rows (listed in the PR body). Regression rule: the release job's existing behavior (hold, version, skip when tagged) is at risk; the exact contract is carried by test-release-ci.py and the idempotence case in ENG-1.
**Section 4 Performance** (1 issue): the lane gets shorter (no per-PR static run, 39 rows fewer); the restored static scan costs one pass over 100 files (seconds); the source archive is 11.1 MiB uncompressed against the 20 MiB cap in skills/workflow-setup/scripts/update.py:49 [measured]; growth of docs or fixtures can break updates without changing installed content: accepted risk owned by update-package-path, numbers in the PR body.
**Outside voice dispositions.** outside voice 1 = native E1/E2: ENG-1 (accepted); old installed updaters are not retrofittable, ENG-1 fixes them from the release side. outside voice 2: ENG-2 (accepted, security). outside voice 3: factually corrected: the surviving row skill-size-116 chained size-139 and size-141 at the pushed head 14b01eb9; local commit 0290de098 already fixed it, so no change; the symbol-move checks of those two cases were part of the removed split-check.py (a budget helper), audited again in ENG-5. outside voice 4 = native E4: ENG-3. outside voice 5: accepted risk. Native E3: a dry run on a scratch repository creates a public release (outward action): not done here; the first-release watch plus the temp-clone toy stand in; flagged. Native E6: ENG-6. E7: ENG-5. E8: ENG-7. E9: ENG-8. E10: ENG-9. E11: CEO-6 stays but its negative control is required (it is).
**Test plan artifact**: written under the project state folder (see the path in the PR record). **TODOS.md**: not written; the repo has no TODOS.md and its tracker is the roadmap (owner text) and issues; the deferred items are update-package-path, toy-hermetic, a clean-machine adoption walkthrough, the update preview showing release notes, error codes for the stacked the outside voice refusal, and a static-rules alias; they go in the PR body.
**NOT in scope (eng)**: a scratch-repository dry run of the release (public release; outward), a surviving-assert count per toy beyond the mechanical audit, retiring update.py's package path (CEO-2), a merge-queue slot for the final step (Operation's process).
**What already exists (eng)**: git plumbing in the release job's runner; the version step; update.py's source-archive fallback and its toy; package.py's static rules; regression.py workflow generator; fake gh.
**Failure modes registry**
  CODEPATH | FAILURE MODE | RESCUED? | TEST? | USER SEES? | LOGGED?
  release commit + tag | tag push fails | Y (job red, nothing published) | ENG-1 toy | red job | Y
  release create | fails after the tag exists | Y (rerun creates the release only) | ENG-1 toy | red then green | Y
  final view step | assets non-empty or release missing | warn only, not fatal | ENG-3 | warning | Y
  update.py via archive | VERSION != tag | prevented by ENG-1 | ENG-1 + CEO-7 | correct version | Y
  update.py | archive without VERSION | Y (refuses UPDATE_BAD_ARCHIVE) | CEO-7 case | refusal with code | Y
  static scan | Markdown-only change skips it | Y after ENG-2 | ENG-2 control | CI red | Y
  notes | private name in a PR title | Y after ENG-8 | ship scan | red scan | Y
  cut rows | a cut row tested more than a limit | Y after ENG-5 | audit table | PR-body table | N
Critical gaps (RESCUED=N, TEST=N, silent): 0 after the accepted obligations (1 before: version identity).
**Worktree parallelization**: Lane A: release.yml + test-release-ci.py (ENG-1, ENG-3, CEO-1, DX-6) ; Lane B: dev/skills-scan.py + generator + CEO-6 row (ENG-2) ; Lane C: test-update-asset.py (CEO-7) ; Lane D: docs and rows (DX-2, DX-4, Tests rows). A and B touch .github/workflows and the generator (shared module: sequence B after A for lanes_cli.py); C and D are independent. Launch A, C, D; then B; then the audit (ENG-5). Sequential in practice: one worker session (3 lanes parallel, 1 sequential).
**Completion summary**: Scope accepted as-is; reality rows 7/7, unverified 0; Architecture 4 issues; Code quality 2; Test gaps 15; Performance 1; NOT in scope written; What already exists written; TODOS.md not written (reason above); failure modes 8 rows, 0 critical gaps after obligations; unresolved decisions 3 (User Challenges 1 to 3) plus Taste decisions CEO-6, DX-5 (revised), ENG-1 shape; outside voice codex completed; lake score 0/0 (N/A: no scored question asked; auto-decided).

### Accepted obligations (CEO)

- CEO-1 (accepted, S, one test file): test-release-ci.py scans line by line with the standard library, treating the indented lines of a `run: |` block as run lines and ignoring comment lines. Every `.github/workflows/*.yml` has no step that runs `dev/package`, `package.py` or a step named package. release.yml has none of `zip`, `tar`, `gzip`, `7z`, `zipfile`, `--attach`, `gh release upload`, `uploads.github.com`, `actions/upload-artifact`, `actions/create-release`, `softprops/action-gh-release`, `ncipollo/release-action` (whole words) and passes no file argument to `gh release create` (only the tag, `--target`, `--title`, `--generate-notes`). regression-pr.yml keeps its legitimate `actions/upload-artifact` for shard logs. The scan is a function of a file path; the negative control runs it on a temp copy of release.yml with a zip step added and on a temp copy of regression-pr.yml with a package step added, and sees both fail. The generated regression-pr.yml is what the generator in lanes_cli.py emits (regression.py workflow regenerates it), so scanning it covers the generator. The row that runs test-release-ci.py is rel-ci-release (land lane); verify by running test-release-ci.py alone and that row alone.
- No check is loosened. "Loosened" means a check removed on a surface that still exists; a check removed because its surface is removed on purpose (the Agensi package and its store listing, the file cap, the script byte limit) is a cut. package.py's edits are in scope for that reason: its listing and disclosure checks guarded the store submission, and listing.json stays only as inert fixture input for the update, adopt and sync toys; package.py stays as a fixture builder and retiring it is CEO-2. The PR body lists every cut row and cut case with its case name and the removed limit (skill-size-116: size-139 and size-141, script byte warn at 19,000 and fail at 20,480; machine-task-layout: machine-caps, machine.py byte cap; same-lines: "over 20 KB is a FAIL with a fix", the 20 KB script FAIL), and review audits all 39 cut rows and every cut case against the toy source and confirms each tests only a removed limit.
- The 13 repaired rows (the 12 red on the shards plus machine-task-layout, which chained the same removed case; all in commit 0290de098) pass alone on the branch; verify by running each row command alone. test-platform-limits.py and test-machine-log.py are not among them and are not claimed.
- Review fix: two generated Tests rows (unread-asserts-control and unread-asserts-count) still say size-check.py in their descriptions; fix the descriptions in .loop/regression.tsv to unread-check.py, regenerate the Tests tables, and grep for any other old name; verify with grep and docs.py check.
- The adopted repo's name stays out of template text (README, wiki pages, workflows); verify with the private scan at ship (the private-name scan that goal.py ship runs, with the list from LOOP_PRIVATE_NAMES).
- SET-10 stays Unreviewed: the owner's records reviewed GRD-20 and SET-1 on o679 (o677 and o678 were the revision records) and a review needs an owner record, so this goal does not review SET-10; verify that the Setup page shows SET-10 Unreviewed and that the PR body says so.
- The release version is computed by the version step of release.yml from the newest v tag and the release:minor or release:major PR label; that step is unchanged. The steps that stamped VERSION into a package and built the zip are removed; the repo's VERSION is written by release commits as before. The first release after merge is watched by Operation, who checks three things: the tag v<next> exists at the merge commit, the release notes were generated, and the release holds zero assets. Rollback is a revert of the whole change, not of release.yml alone, because the change also removes dev/package.sh and dev/test-package.sh.
- update.py's package path is unchanged. It downloads the release's `*.zip` and, when there is none, the release's source archive (update.py lines 242 to 244), and takes the version from the VERSION file in that archive (update.py lines 172 to 175). The fallback is therefore read from the code, not proven by a toy against an asset-less release, and the version it sees is whatever VERSION the last release commit wrote, which may lag the newest tag. This is an accepted risk, flagged to Operation and owned by update-package-path; the path is unsupported until then. Adopter pull requests (SET-1) are future work; only the SET-1 text is in this change.
- The CI run 44861339984 at 14b01eb9 (7 of 11 jobs red: affected and shards 1 and 3 to 7) is diagnosed job by job as Operation asked: each FAIL line run alone on origin/main 48ac06e7d and on the branch, classified main-red, caused by this change, or caused by the stacked codex-git-root change, with an "affected rows only" rule when a job lists many rows; verify with the table in the PR body. Both SHAs go stale, so ship needs a CI run on the final head after the last merge, green or fully classified, before the PR is called ready.
- The PR body names the follow-ups update-package-path and toy-hermetic (Operation, TD604); the repo has no TODOS.md, so the body is their record.
- qa and ship are gated outside this plan: qa does not run until toy-hermetic is on main (Operation's order, TD604), the unblock trigger is Operation's word that it is merged, and ship does not start before qa is recorded. Review, the CI diagnosis and the row repairs proceed meanwhile. If the trigger never comes the goal waits and Operation decides (for example recording the two leaking toys as main-red). A late merge of toy-hermetic restarts only qa and the final-head CI run.
- CEO-6 (taste, accepted S): a land-lane row `skills-static-rules` keeps running `python3 dev/package.py --static` and expects "static rules hold", because that scan (frontmatter, inventory, scripts, and the safety scan for secrets, obfuscation, agent-aimed instructions, dangerous commands and private prefixes in the shipped skills files) guards the template's content whatever its distribution; it replaces the cut row release-static-rules, with the reason that package.py stays until CEO-2 moves the scan; the per-PR CI step stays removed because the land lane runs rows. Verify by running the row alone, and with a negative control that puts an obfuscation pattern in a temp copy of a skills file and sees the scan fail. Surfaced as a taste decision at the final gate.
- CEO-7 (accepted, S to M, both voices): test-update-asset.py gains a case that serves update.py an asset-less release (the fake gh offers only the source archive) and asserts the source archive is used, which version is reported, and that sync.py skips the repo step when the installed template version already equals it (sync.py lines 206 to 208), so the partial-update shape is visible; verify by running the toy alone and the row that runs it.
- CEO-1 also covers block scalars in the line scan: negative controls for `run: >` and `run: |-` forms, and the argument check on `gh release create` stays the primary guard with the token list secondary.
- The PR body records the intentional trade (the reach of the dropped Agensi channel for one distribution path), the signal the owner will watch (template uses, forks, adopter pull requests), who reviews SET-10 and when (the owner, by their own record), and that listing.json and dev/package.py are fixture-only until CEO-2; dev/package.py's docstring says so.
- The first-release watch has a fourth check: update.py run against the real published release.
- The grep for old names covers wiki pages and generated Tests tables as well as the tsv; the private scan runs again on the final head after the last merge.
- User Challenge (not decided here): both voices recommend landing codex-git-root on its own instead of stacking it; the stack stands, as Operation ordered, until they decide.

### Accepted obligations (DX)

- DX-1 (taste, accepted S): when update.py takes the source archive because the release has no zip, it prints one stderr line when the archive's VERSION differs from the release tag, naming both (`update: release v1.2.3 has no package asset; used the source archive whose VERSION says 1.2.2`), with the stable code UPDATE_NOASSET, and keeps its exit status; CEO-7's toy case asserts the line. This is the minimum mitigation for the CAP4 success-while-behind path; the rest of the update path stays with update-package-path. Surfaced at the final gate with the User Challenge below.
- DX-2 (accepted, routine docs): remove the stale package and store wording in skills/workflow-docs/references/commands.md line 20 (the Agensi sentence), in the description of row review-help-runs-alone ("so the package gate accepts"), and in settings.py's template_repo description ("if the package names none"); regenerate the settings reference and the Tests tables; the Roadmap items package-under-cap and agensi-ready are owner text and are not edited (flagged to Operation). Verify with grep for agensi, package gate and package names none.
- DX-3 (accepted, S): the PR title says "no zip asset; template-only" so the generated release notes of the first release carry it; verify in the PR title and the first release's notes.
- DX-4 (accepted, S, doc text): How-to-use-Setup's "Keep it current" step says that update works from the release's source archive until update-package-path and that it is unsupported until then; any doc text written with the file tool is named in the record and the PR body (owner record o685, only where the push hook matches only prose); verify by reading the page and docs.py check.
- DX-5 (taste, accepted S): release.yml ends with a step that runs `gh release view v<next> --json assets,tagName` and fails with a message naming the tag and `gh release delete` when the release holds an asset or is missing; CEO-1's scan keeps the file free of upload tokens; verify by reading release.yml and by the first-release watch.
- DX-6 (accepted, S): every failure of the CEO-1 scan prints the file and line, the matched token or argument, the rule (no-package-step, banned-token, file-argument), a fix line, a stable code REL-CI-001 to REL-CI-003 and exits non-zero on stderr; a missing or unreadable path is a usage error with what, fix and code; the negative controls assert that text, and add a backslash-continued line and an expanded variable argument; verify by running test-release-ci.py alone.
- User Challenge 2 (not decided here): both DX voices, with both CEO voices, say asset-less releases are safe only once update-package-path lands; the owner's SET-10 stands, with DX-1 as the minimum mitigation, until the owner or Operation decides.

### Accepted obligations (Eng)

- ENG-1 (accepted, S to M; supersedes DX-1, so update.py stays unchanged): the release job creates a release commit whose tree is the merge commit's tree with VERSION set to the new version and the merge commit as its parent, tags that commit (annotated, the message names the merge SHA), pushes only the tag, and runs `gh release create vX --verify-tag --generate-notes`; main is not touched, no zip is built. The existing skip rule (a v tag already points at this SHA) is replaced by one keyed on the parent: if a tag whose commit has this merge SHA as parent exists, only the missing release is created. Verify with a toy that runs the same git steps in a temp clone: VERSION at the tag equals the version, `git diff` between the tag and the merge commit shows only VERSION, main's ref is unchanged, and a second run creates no second tag; and by update.py run against the first real release (fourth watch check). CEO-7's case then asserts that an archive whose VERSION equals the tag is updated from, and that an older installed version proceeds (the verified stranding case: archive VERSION 1.0.112 against installed 1.0.157 prints "nothing to do").
- ENG-2 (accepted, S, security): the static scan keeps its per-PR and merge-group enforcement under a name that does not say package: a thin dev/skills-scan.py that calls package.py's static rules with no copy of them, run as a step in the generated regression-pr.yml in the affected job and in the merge-group job (the generator in lanes_cli.py emits both), and by the skills-static-rules row; CEO-1's package-step rule allows this one entry point and nothing else named package; negative controls: a temp copy of a skills Markdown file with an obfuscation pattern fails the entry point, and a temp copy of the generated workflow without the step fails the workflow assert; CEO-6 is therefore settled as required, not taste.
- ENG-3 (accepted, S): DX-5's final `gh release view` step is warn-only (continue-on-error) because it runs after publication; release.yml gains a `concurrency` group so two merges cannot compute the same next version; the release job's permissions stay contents: write, pull-requests: read, issues: read; verify by reading release.yml and by the CEO-1 scan.
- ENG-4 (accepted, S): CEO-1 tokenizes the `gh release create` command with shlex and allows only the tag, `--target X`, `--title X`, `--verify-tag` and `--generate-notes`; any other token, including a variable or a continuation, fails; any reference to a local script or local action from release.yml fails unless that file is scanned too; the token list stays secondary.
- ENG-5 (accepted, S to M): the cut audit is mechanical: a script lists, for each cut row and cut case, the removed lines from `git diff origin/main`, the removed limit, and the verdict; it confirms each touched toy's remaining assertion names, that no surviving row names a removed case, shard assignment and timing for the red shards, the health "twelve groups, every rule has a control" wording, and greps package.sh, test-package, size-check, health_script_bytes in docs, hooks, skills and config; the table goes in the PR body; the symbol-move checks of size-139 and size-141 (part of the removed split-check) are looked at again and kept if they test something other than a limit. Corrects outside voice 3's claim for the pushed head: 0290de098 already removed the chained cases from the row.
- ENG-6 (accepted, text): the stacked codex-git-root commits stay a separate range (merge, not squash); the PR body says a rollback of the whole change also takes TD569 and gives the split steps.
- ENG-7 (accepted, process): once qa starts, no more merges of main into the branch except one final merge followed by the final-head CI run; the deadline for toy-hermetic is Operation's.
- ENG-8 (accepted, S): the private scan at ship also covers the PR title and body, the branch name and commit messages, and the first-release watch reads the generated notes for private names; a fifth watch check.
- ENG-9 (accepted, S): at ship, after the last merge, GRD-20 and SET-1 still show Reviewed with their current text hash and SET-10 shows Unreviewed.
- ENG-10 (accepted, S): CEO-7's toy also covers an archive without a VERSION file, an unparsable VERSION and no archive (each refuses with its code, nothing written); the source archive size is recorded (11.1 MiB against the 20 MiB cap, update.py line 49) in the PR body as an accepted risk owned by update-package-path.
- User Challenge 3 (not decided here): whether to ship without ENG-1, or keep a stamped zip for one more release; ENG-1 is accepted as the minimum safe form of the owner's direction.

