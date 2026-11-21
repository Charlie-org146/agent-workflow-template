# Migrate every live template requirement into the feature format in place (goal G1 of the v1.1.0 brief, owner o700 typed 23:18; Operation TD658, TD659): each keeps its ID, page and every word, no page is rebuilt, nothing is lost, every old Reviewed mark is cleared and listed, missing metrics, tests and references are marked, features over five requirements are listed to split, with a report and a safe re-run. Re-frozen as migrate-features-2 (owner o711) to add ls-narrow-triggers to the known-to-fail list, citing #4061

- Slug: migrate-features-2
- Touches: docs/wiki, README.md, docs, .loop/regression-known.tsv
- ETA: 325 active minutes (estimate 259m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every live requirement (27 on main), then it becomes a feature on the page where it already is, keeping its ID, its page and every word, proven by a hash of each requirement's text before and after listed in the report
2. Given every page outside those 27 entries, then it is byte-identical before and after; no page is rebuilt and the How-to-use pages and figures stay
3. Given the counts of test links, revision rows and references, then they are the same before and after, each requirement shows its metric from its page's Success metrics or 'metric missing' and its test or 'test missing', and each feature shows its references or 'reference missing'
4. Given the old Reviewed marks, then every one is cleared and listed in the report with its date and record, and features with more than five requirements are listed 'to split'
5. Given a second run of the migration, then it leaves an empty diff, and the goal stops at the PR
6. Given .loop/regression-known.tsv, then it gains one row for ls-narrow-triggers citing #4061 (macOS-only, red on main; owner o711), no other row changes, and the qa lane at the final head shows no FAIL

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
6. Run `git diff origin/main -- .loop/regression-known.tsv`.
   Expect: exactly one added line, for `ls-narrow-triggers`, citing #4061, and no removed line.
7. Read the Result section of the pull request.
   Expect: the regression lane ran at the final head in a fresh clean clone and shows no FAIL.

## PR notes

This goal (migrate-features-2) is migrate-features re-frozen by the owner's typed words (record o711) with one added done line: `.loop/regression-known.tsv` gains one row for `ls-narrow-triggers` (red on main 48ac06e7d, macOS only because `test-local-schedule.sh` skips non-Darwin hosts), citing #4061. No other row of that file changes. The migration, its report and its pages are exactly as built and checked in migrate-features (head 6eaeecb7a); the check script's allowed-file list grows by the known list and this goal's own records, and it proves the known-list diff is one added line. The notes below are carried over from migrate-features.

What changed: the 27 live requirements on the 11 feature pages become features in place, each keeping its ID, page and every word (text hash before and after listed in `docs/migrations/features-v1-report.md`). Each entry's Reviewed mark is cleared and each gets a block of `  - ` bullets after its own lines: its reference (the Follows cell, as link text), and one line per requirement line with its metric and test result. Two scripts and the report are new, all under `docs/migrations`: `features-v1.py run` and, as its own file so the proof shares no code with it, `features-v1-check.py check`. No other file changes except, in this goal, the known list row and the check's allowlist and proof 6.

Owner decisions: the plan gate was answered `rec` by the owner (record o706, and the owner also typed `rec` directly in the operation session); the owner then ordered, in record o708, that this goal merges when green after the earlier goal, which is: the marker blocks are written into the 27 pages (UC1a); all 29 Reviewed marks are cleared (UC2a, the owner's o700 order); the test count shows on every line of an ID (D2a); the blocks are write-once snapshots until the checker goal recomputes them (D6a); and health's new FAIL rows and the release-gate effect are reported, not fixed (D7a). Re-run `features-v1.py run --refresh` to refresh a block (the flag is needed once the base already carries blocks, so a later run cannot overwrite them by accident).

release gate (review.py check_reviews) now lists every Unreviewed requirement, the 27 migrated (and DOC-27 and DOC-28 once they land), as not Reviewed

Health: after this merge `health.py check` shows six new FAIL rows from the `principle-map` rule (`principle N has no Reviewed requirement`), compared as sets with the unmigrated tree; they clear as the owner reviews one feature per principle. Reported, not fixed: the rule file is outside this goal's touches. Operation is told before merge.

Why 29 marks are cleared: the owner ordered it (o700), and the new standard lets a feature be Reviewed only by the owner's own typed words naming that ID; the old marks came from relayed answers. The text hash of every requirement is unchanged, so the old marks are kept in the report with their date, seal and the review-log row (context, not proof). The 29 are 26 requirement marks (SET-10 was already Unreviewed) and 3 page-level `Review:` lines (Automation, Regression, Setup) whose lock covers the requirement lines.

Found while building: the page check rejects external links on a page, so the reference bullet shows each source's link text without its URL; the URLs stay in the Principles table.

For the checker goal: the marker bullets are indented `  - ` bullets after a blank line, so a checker that counts bullets without stopping at a blank line would count them as requirement lines. A request for Operation: hold wiki-page edits from other goals until this merges, because the counts 27, 26, 3 and 29 are asserted against the base.

Deferred: a committed toy test and regression row for the scripts need `dev/toy`, outside this goal's touches. The accepted record for Operation to file or not: one test that runs `check` on a fixture, plus the negative controls listed below.

Shape spec: DOC-27 as pinned in the frozen source draft, sha256 beginning 781aaacb72806fcd; used as a spec only, nothing from it is added. DOC-27 itself is merged by the earlier goal and is the durable copy.

Internal cleanup of this repo; adopting repos migrate in a later goal.

Check change (named, as Operation asked): `features-v1-check.py` is loosened in exactly one way, its changed-file allowlist now also admits `.loop/regression-known.tsv`, `.loop/kept/migrate-features-2.tsv` and this goal's own records (`.loop/goals/migrate-features-2.*`); and one proof is added, number 6: the known-list diff against the base is exactly one added line, for `ls-narrow-triggers` citing #4061, with no removed line. Nothing else in the check changes. Negative control: a second added row prints `FAIL 6 ... added 2, removed 0` and the check exits non-zero.

Order and safety: this goal merges first, before the goal that adds DOC-27 and DOC-28 (Operation TD668 and TD678), so the branch holds main as it is (48ac06e7d) and nothing newer; the pull request is opened as a draft and stays one until the owner says; auto-merge is never armed and `merge.py` is never run.

Manual negative controls (each run in a throwaway clone; all behave as stated, and the review added controls 13 to 15 and re-ran all of them on the final code):
1. A forced hash mismatch (unit changed on the second call): `REFUSED: the text of CHK-1 changed`, no file written.
2. A Reviewed mark not on the base: `REFUSED: DOC-26 holds a Reviewed mark that is not on 48ac06e7d`, exit non-zero.
3. One broken proof (a stray line added to a page): `check` exits non-zero with `FAIL 2 each page ... equals BASE byte for byte: Machines`.
4. A CRLF page: every one of its 296 lines is CRLF after the run, marker lines included.
5. A last entry with no final newline: the block is added once and the page still ends without a newline.
6. A real sub-bullet that starts with `Line` (`Line 9: metric reasons ...`) survives a re-run, and the block is regenerated.
7. An ID-token collision: a Success metrics bullet naming `DOC-27` and `DOC-2-x` leaves DOC-2 at `metric missing`.
8. A hostile Follows cell (`<!--`, `-->` and a URL): the Reference bullet reads `evil x t tail`.
9. An absent reviews log: the report reads `record not available` and the run exits 0.
10. Hostile review-log text (`<!-- a | b -->`): the report cell reads `evil a / b c`, with the table still seven columns.
11. A run interrupted between renames (failure injected at the 4th rename): it prints `REFUSED`, the three files it touched and `git checkout --` for those paths; running that command leaves a clean tree and no temporary folder.
12. A write target with uncommitted changes: `REFUSED: these paths have uncommitted changes`.
13. A later owner review (INT-1 marked Reviewed after the migration), re-run with the base at main: `REFUSED: INT-1 holds a Reviewed mark that is not in the report`, and the report still lists its 26 entry marks.
14. The same dirty target when the script is run from `docs/migrations` instead of the repo root: still refused (the guard runs from the repo root).
15. A base that already holds marker blocks: `REFUSED ... pass --refresh to rewrite them`; with `--refresh` the run writes 0 files and the tree stays clean.

`check` on the final head (base 48ac06e7d): every proof passes and it ends `CHECK OK` with exit 0. DOC-27 and DOC-28 are a note, not a proof (see the order change below): none present, none required.
What `check` proves, and what it does not: it proves every page equals the base byte for byte once the marker blocks are stripped and the marks restored, that each block is well formed (a Reference and one numbered Line per requirement line), that the test rows and the Principles table are untouched, and done lines 1 to 5 (done line 6 is proof 6). It does not re-derive the values inside a block (reference text, metric hit, linked-row count); `run` writes those from the repo's own parsers, and they are snapshots until the checker goal recomputes them.

Order change (Operation TD668): this goal merges before the goal that adds DOC-27 and DOC-28, so the check's proof `skipped IDs present on HEAD` became a note: those two IDs are skipped if present and nothing is required if they are absent, the report says the goal that adds them lands later, and the sentence above reads `(and DOC-27 and DOC-28 once they land)`. No other proof changed.

Scoped review of the order-change diff (everything since 30ee5e1ff), one reviewer, verdict recorded: no other proof weakened, no assertion removed beyond the one named, no defect in the changed lines; `VERDICT: SAFE`. Its one cosmetic point (a stale paragraph about the old failing proof) is fixed above.

Regression lane (qa, Operation TD676 and TD680): run only in a fresh clean clone at the final head, with the session variables cleared, and its result is the Result section of this pull request. The earlier lane run in the working tree was void. `ls-narrow-triggers` fails on main itself (macOS only, #4061) and is on the known list in this change (owner o711, done line 6).
