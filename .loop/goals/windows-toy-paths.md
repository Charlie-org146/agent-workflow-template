# Make three toys pass on Windows by fixing only their fixtures and setup: the link-page fixtures and the home-guard registry fixture

- Slug: windows-toy-paths
- Touches: dev/toy/test-link-form-note.sh, dev/toy/test-docs-link.sh, dev/toy/test-home-guard.py
- ETA: 235 active minutes (estimate 185m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the Windows temp path, when test-link-form-note.sh and test-docs-link.sh run, then the fixture PRD link raises no DOC-19 finding and the toys print "PASS: new code: the wiki step merge.py runs finds nothing and passes" and no FAIL.
2. Given a repos.json entry written with a Windows path, when the guard runs, then the leak line names "schedule/repos.json#fixture".
3. Given a fixture path with "/Users/" in a link, when docs.py check runs, then DOC-19 still flags it (the control).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
