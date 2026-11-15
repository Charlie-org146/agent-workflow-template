# Decide whether v1.0.0 goes: the short checks pass on a clean origin/main, and v1.0.0 is prepared as a draft release.

- Slug: v1-go-no-go
- Touches: CHANGELOG.md, VERSION

## Done lines

Frozen. A wrong done line needs a new goal.

1. On a clean origin/main health.py check, dev/package.py, docs.py check and entry.py lag run and their results are reported; every failure is fixed here if small or listed by name with its cause.
2. v1.0.0 is prepared through workflow-release as a draft (changelog, version) and the draft link and results go to operation; v1.0.0 is not published.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
