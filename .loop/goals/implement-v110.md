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

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
