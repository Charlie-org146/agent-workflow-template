# Migrate every live template requirement into the feature format in place (goal G1 of the v1.1.0 brief, owner o700 typed 23:18; Operation TD658, TD659): each keeps its ID, page and every word, no page is rebuilt, nothing is lost, every old Reviewed mark is cleared and listed, missing metrics, tests and references are marked, features over five requirements are listed to split, with a report and a safe re-run

- Slug: migrate-features
- Touches: docs/wiki, README.md, docs
- ETA: 365 active minutes (estimate 290m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every live requirement (27 on main), then it becomes a feature on the page where it already is, keeping its ID, its page and every word, proven by a hash of each requirement's text before and after listed in the report
2. Given every page outside those 27 entries, then it is byte-identical before and after; no page is rebuilt and the How-to-use pages and figures stay
3. Given the counts of test links, revision rows and references, then they are the same before and after, each requirement shows its metric from its page's Success metrics or 'metric missing' and its test or 'test missing', and each feature shows its references or 'reference missing'
4. Given the old Reviewed marks, then every one is cleared and listed in the report with its date and record, and features with more than five requirements are listed 'to split'
5. Given a second run of the migration, then it leaves an empty diff, and the goal stops at the PR

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 docs/migrations/features-v1-check.py check` on the committed branch.
   Expect: every line starts with PASS and the last line reads `CHECK OK`.
2. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: it prints `DOCS OK`.
3. Open `docs/wiki/Documentation.md`.
   Expect: each requirement reads `**Unreviewed**`, with no `<!-- reviewed ... -->` comment, and a blank line then a `Feature markers v1` list follows its own lines.
4. Run `python3 docs/migrations/features-v1.py run`.
   Expect: it prints `wrote 0 files`, and `git status` stays clean.
5. Read `docs/migrations/features-v1-report.md`.
   Expect: 27 features with equal hashes before and after, 29 cleared marks (26 requirement, 3 page-level), the features over five lines under `To split`, and DOC-27 and DOC-28 named as skipped.

## PR notes

What changed: the 27 live requirements on the 11 feature pages become features in place, each keeping its ID, page and every word (text hash before and after listed in `docs/migrations/features-v1-report.md`). Each entry's Reviewed mark is cleared and each gets a block of `  - ` bullets after its own lines: its reference (the Follows cell, as link text), and one line per requirement line with its metric and test result. Two scripts and the report are new, all under `docs/migrations`: `features-v1.py run` and, as its own file so the proof shares no code with it, `features-v1-check.py check`. No other file changes.

Owner decisions: the plan gate was answered `rec` by the owner (record o706, and the owner also typed `rec` directly in the operation session), which is: the marker blocks are written into the 27 pages (UC1a); all 29 Reviewed marks are cleared (UC2a, the owner's o700 order); the test count shows on every line of an ID (D2a); the blocks are write-once snapshots until the checker goal recomputes them (D6a); and health's new FAIL rows and the release-gate effect are reported, not fixed (D7a). Re-run `features-v1.py run` to refresh a block.

release gate (review.py check_reviews) now lists every Unreviewed requirement, the 27 migrated and DOC-27 and DOC-28, as not Reviewed

Health: after this merge `health.py check` shows six new FAIL rows from the `principle-map` rule (`principle N has no Reviewed requirement`), compared as sets with the unmigrated tree; they clear as the owner reviews one feature per principle. Reported, not fixed: the rule file is outside this goal's touches. Operation is told before merge.

Why 29 marks are cleared: the owner ordered it (o700), and the new standard lets a feature be Reviewed only by the owner's own typed words naming that ID; the old marks came from relayed answers. The text hash of every requirement is unchanged, so the old marks are kept in the report with their date, seal and the review-log row (context, not proof). The 29 are 26 requirement marks (SET-10 was already Unreviewed) and 3 page-level `Review:` lines (Automation, Regression, Setup) whose lock covers the requirement lines.

Found while building: the page check rejects external links on a page, so the reference bullet shows each source's link text without its URL; the URLs stay in the Principles table.

For the checker goal: the marker bullets are indented `  - ` bullets after a blank line, so a checker that counts bullets without stopping at a blank line would count them as requirement lines. A request for Operation: hold wiki-page edits from other goals until this merges, because the counts 27, 26, 3 and 29 are asserted against the base.

Deferred: a committed toy test and regression row for the scripts need `dev/toy`, outside this goal's touches. The accepted record for Operation to file or not: one test that runs `check` on a fixture, plus the negative controls listed below.

Shape spec: DOC-27 as pinned in `.claude/worktrees/consolidate-documentation-9216aa/operation-top/readme-drafts/frozen-source-v1.1.0-2349.html`, sha256 beginning 396af06cf2c369d3; used as a spec only, nothing from it is added. DOC-27 itself is merged by the earlier goal and is the durable copy.

Internal cleanup of this repo; adopting repos migrate in a later goal.

Order and safety: the branch is merged up to main only after the earlier goal (doc27-28-text-2) merges; the pull request is opened as a draft and stays one until the owner says; auto-merge is never armed and `merge.py` is never run.
