# One slots command counts pull requests in checks (TD474, TD477, TD534): slots prints SLOTS used/cap, where used is the open PRs of the repo with any check not yet completed and cap is a config key (default 2), and exits 1 when used is at or over cap; the watcher, the operation session and Codex briefs use it before a push. It lives in an existing script with room; built by the Codex fallback

- Slug: slot-counter
- Touches: skills, dev/toy
- ETA: 295 active minutes (estimate 235m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a fake gh with 2 PRs with pending checks and cap 2, then slots exits 1 printing SLOTS 2/2; with 1 pending it exits 0 printing SLOTS 1/2; a PR whose checks all completed is not counted (toy, negative control)
2. Given the pull request, then its row is SEEN RED with the command removed, the cap key is in the settings table with its default, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then the package stays at 100 files, no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
