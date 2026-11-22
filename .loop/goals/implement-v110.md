# Implement DOC-27, DEL-19's goal format, the revised DOC-28 and DEL-23 (v1.1.0 task 4), and pass every one of their test cases

- Slug: implement-v110
- Touches: skills/workflow-docs, skills/workflow-release, skills/workflow-delivery, skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs/wiki, docs, README.md
- ETA: 1185 active minutes (estimate 948m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every DOC-27, DEL-19, DEL-23 and DOC-28 test case on its page, then each runs as a real test linked to its requirement and passes, and each fails on a fixture that breaks only that rule.
2. Given features in the new format, when docs.py check runs, then it enforces DOC-27: the sections and their order, at most five requirements, one metric and at least one test case each, the Reference section and its tags, the milestone, and a Reviewed mark only from the owner's typed record naming that ID; it reads the Success metrics table as the index of the inline metrics and matches "Success metric N.N." and "Test cases" exactly.
3. Given a goal, then DEL-19's format is enforced: title, the task it serves, Given/when/then done lines, touches and release; freezing with no task named, or editing a frozen done line, is refused; a goal that skipped its review can't open its PR; a PR whose head moved after its checks can't merge; the drawn steps page is generated from the code, and a step added without regenerating fails docs.py check.
4. Given tasks, then DEL-23 is enforced: starting a task with no frozen brief is refused and one changed word in a frozen brief fails the check; an added task shows on the one task list by name, with its state, goals and ETA, within a minute; a task naming another doesn't start before that one is done, and two independent tasks can both run; a task with an unmerged goal or unmet done-when line can't be marked done.
5. Given a release, when the release tool runs, then it enforces the revised DOC-28: three kinds; a major or minor without a frozen brief is refused, and the brief lists tasks in order; a feature task not named in a frozen brief builds green but can't merge, and merges once named; a bug-fix task merges any time as a patch; a cut with a named task not done is refused, and the tag notes list every task; the brief records each task's result; a major with a non-empty known-red list is refused, with no waiver (o714's narrow reading).
6. Given the template's own pages, when docs.py check runs, then it passes, and missing metrics, tests and references, features "to split", and the page-rebuild items are reported, not failed.
7. Given the package, then DOC-28's brief logic and DEL-23's task logic live in skills/workflow-release/scripts/brief.py (one new file, o718/o719), the rest in existing scripts; every script stays under 20,480 bytes (19,000 warns); the package stays within MAX_FILES; and test-release-gate.py's "no file is added to the shipped package" becomes "the shipped package stays within MAX_FILES", keeping a control where one file over fails (o719).
8. Given the regression list, then net rows rise by at most 4, one per feature (DOC-27, DEL-19, DEL-23, DOC-28), new cases fold into existing scripts, and no existing test turns red.

## Notes

- o710 items 1 to 3: allow iso.org, basecamp.com, peps.python.org and scrumguides.org as link origins; change "the two tests" to "both tests"; the milestone is "v1.1.0 dry run", which DOC-27 and DOC-28 carry.
- Plan by hand only if autoplan refuses (o713, o716, o721), with all three reviews in full and DEPTH: full. Autoplan did not refuse for this goal.
- o714 (the narrow reading): a major with a non-empty known-red list is refused, with no waiver.
- o718: MAX_FILES is 200 (the grd21-cap-lift goal); this goal merges after it, because brief.py is file 101.
- o719: the release-gate check "no file is added to the shipped package" becomes "the shipped package stays within MAX_FILES", keeping a control where one file over fails.
- o736: the implementation may add up to 4 regression rows, one per feature.
- TD702 Q2: report-only, as done line 6 states.
- Byte room and trims are measured in `.loop/goals/implement-v110.bytes.md`.

## PR notes

Owner words: o737 accepted the red team's six principle breaks as stated; the Reviewed-file protection is filed as #5760.
Cost and bytes: `.loop/goals/implement-v110.bytes.md` (every touched script, base and now, room left; no script reaches
20,480 and none newly crosses 19,000). Exactly one new file, `skills/workflow-release/scripts/brief.py` (o718, o719).

Behavior changes (file, old, new):
- `goal.py new` / `fit.goal_format`: old, a goal needed only a done line; new, it needs `--task` and Given/when/then done lines, and
  the goal file carries Task and Release lines (`goal.py adopt` is exempt). Every toy caller was updated in the same commit.
- `role.requirement_gate`: a goal whose review step was skipped can no longer open its pull request (DEL-19.2).
- `sections.features` and `docs.py check [--strict]`: DOC-27's sections, five requirements, metric and test case each, the metrics
  table as the index, tagged references with a specific source, the milestone, one principle, and the Reviewed mark. A missing
  metric, test or reference on an Unreviewed feature is a NOTE (reported, not failed); `--strict` fails every NOTE.
- `criteria.py review` -> `sections.reviewed`: a new-form Reviewed mark needs an owner record naming exactly that ID and adds its
  ID, record id and date to `.loop/reviews.tsv` (the file's protection is #5760); with no line the check reports a NOTE for a mark
  dated before 2026-11-22 and fails one dated after.
- The steps block in `docs/wiki/Delivery.md` is generated from `flow.py`'s STEPS; a stale one fails `docs.py check`.
- `brief.py` and its hooks: `merge.py` refuses a feature task no frozen release brief names; `release.py cut` and `autorelease.py`
  refuse a minor without a frozen brief or with a named task not done, and a patch that would ship a feature task; the tag notes and
  `## Results` list every task; `review.py gate` refuses every known-red row with no waiver (o714); `live_board.py` shows the task
  list; `fit.goal_format` refuses a task with no frozen brief when the repo keeps `.loop/tasks/`.
- `dev/toy/test-release-gate.py`: "no file is added" became "the shipped package stays within MAX_FILES" with a control one over (o719).
- Four rows (o736), each seen red: feature-standard-doc27, goal-format-del19, tasks-del23, release-briefs-doc28.

Preconditions still open when this was written: MAX_FILES 200 (grd21-cap-lift) is not on the merge base, so the MAX_FILES check and
`test-pods.sh size` count 101 files against 100; DEL-23's text is not on the pages, so `docs.py check` prints `LINK regression: rows
link to DEL-23`. Both clear when those goals merge and this branch merges main.

Test evidence (toys run one at a time with the lane env form, an empty private-name list and a git identity): test-goal, test-new-here,
test-docs, test-criteria, test-goal-adopt, test-autorelease, test-delivery-release pass; test-docs-sections, test-guards, test-defect,
test-release, test-release-gate, test-milestones, test-migration, test-delivery-prd, test-codex and test-lanes show the same failures on
an unmodified copy of the base (DOC-25 migrate and template render, resume from another checkout, size-140, "four numbers", the Release
page's live requirements, milestone setup text, migration trace, private-name cases, codex), except `categories` in test-defect, which fails
only because this worktree's local config holds a 2.5 GB memory floor that changes a generated settings block.

Added after the first report (operation-mac: all of (a) to (f) in scope, (g) my decision):
- (a) End-to-end cases through the real scripts: `test-delivery-release.sh briefs` (merge.py refuses an unnamed feature task, holds a named one for its minor cut, the automatic release refuses a minor with no frozen brief or with a named task not done and releases once done, with the changelog and the brief's `## Results` naming the task), `test-release.sh` 3e (`release.py cut --bump minor`, same), `test-release-gate.py` (`review.py gate` lists every known-red row). A feature task's goal is now released with its minor cut: `autorelease.finish` prints `HELD ... for its minor cut` and records no release of its own.
- (b) The DEL-19 row also requires the existing merge-guard case "a pull request head that moved since the pr lane refuses HEAD_MOVED" and the push-guard case "a worker's push to main is refused" to pass (merge-guard-base-head and the other cases of that script are on the known-red list; only those named lines are required).
- (c) A whole page in the new form (it has a Reference section) must have exactly Problem, Requirements, Non-goals, Success metrics, Reference, Revisions, Tests; the old section checks (`sections.KINDS`, `criteria.contract`) accept the Reference section. The old content rules (DOC-7 to DOC-9, DOC-18 How-to page, DOC-19 links) still apply to such a page; the template's feature migration owns those.
- (d) A page or a feature whose text changed with no new revision row fails (`milestones.new_form`, against origin/<base>).
- (e) `goal.py new` refuses a task whose feature is Unreviewed unless the task is `Kind: fix`; it needs the task's brief (`.loop/tasks/`), so a repo with no tasks is untouched.
- (f) `goal.py pr` refuses a goal file in the new format that lacks a part (title, slug, touches, ETA, task, release, done lines); `goal.py adopt` reads the task from the goal file (a file with a Release line and no task is refused; an older file adopts as before). A touches line of "not declared" and a release of "none" are explicit values and accepted.
- (g) My choice: typed scores. `docs.py check --strict` compares every typed Confidence score (N% (a of b)) in the README, Home and Principles tables with health's latest full run (`sections.latest_full`, no new format) and says "no health run to compare" and fails when there is none; the default check does not, because it would call `gh run download` on every run.
- Cases of DOC-27 that remain page-rebuild items and are NOT built here: 27.4's structure cases (the nine-column principle table with a Review column, no How-to-use pages, exactly the listed figures, "N of M reviewed" on the front pages) and 27.5's "N of M reviewed rises by one". They conflict between done line 1 (every test case) and done line 6 (page-rebuild items are reported, not failed): reported to the operation session as a decision for the owner.
- Steps page: the generated line in `Delivery.md` meets line 3 only as the operation session ruled (v110-fast-steps-2 lands the generated page first or after; the later merges up).
- Not done: `watch.py go --task`; scheduling.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
