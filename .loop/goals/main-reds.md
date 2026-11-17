# main-reds: the unclaimed v2.0 issues that keep template main red are fixed in one goal (#4901 #4896 #4865 #4858 #4683 #4660 #4695 #4772 #4758; owner o22)

- Slug: main-reds
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The rows named in #4901 (DEL-10, routing.py starting processes without the guard), #4896 (judge-key-old and the other two) and #4865 (consistency) pass on a clean checkout because their cause is fixed in code, and any of them listed in .loop/regression-known.tsv are removed from it.
2. #4858, #4683 and #4772: the leak guard no longer flags routine logs written outside the test, the Home guard covers lanes/ and schedule/, and a signal during a commit hook rolls back while git still holds the index; each has a regression row that fails before the fix and passes after.
3. #4660, #4695 and #4758: audit.py reads CHANGELOG headings with or without a leading v, docs.py sync files issues under the right milestone, and the toy SMTP credential no longer trips GitGuardian; each has a row.

## Verify by hand

1. Run `python3 skills/workflow-health/scripts/health.py check --group consistency`.
   Expect: the group is green and reports no duplicate requirement IDs.
2. Run `python3 dev/toy/test-home-guard.py guard`.
   Expect: routine logs and concurrent lane tickets are allowed; changes to settings and schedule entries are caught; strict mode catches routine logs too.
3. Inspect `dev/toy/test-machine.sh` and run `bash dev/toy/test-machine.sh machine-mailer`.
   Expect: the toy SMTP value is assembled at runtime and the mailer reports no secret in its output.

## Issues

Fixes #4901, fixes #4896, fixes #4865, fixes #4858, fixes #4683, fixes #4660, fixes #4695, fixes #4772, fixes #4758.
