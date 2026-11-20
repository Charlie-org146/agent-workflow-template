# The pull request check runs package.py's static release rules (file count, script sizes, disclosure) so main never holds what the release would refuse (TD479; HLT-2's new wording, o667). Main's release push was red four times, 11:03 to 11:29, on 'Size: 105 files' while no PR saw it. Only the static rules run, not package.py's --help pass, and only while every merge stays within the 3-minute target (TD468): measure the added seconds

- Slug: fast-release-rules
- Touches: .github, skills, dev/toy
- ETA: 440 active minutes (estimate 349m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a PR that brings the package to 101 files, then its PR check fails on the file count, shown by a toy, and the 105-file state replayed fails too
2. Given the PR check with the static rules added, then the PR body shows the measured added seconds per run, and the merge stays within 3 minutes on a free runner
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
