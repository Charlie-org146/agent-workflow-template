# Known-red-zero group B (TD493): the 18 known rows whose command passes on a scratch copy of main on the Mac (draft section B) are each proved on GitHub with a single-row run before they leave .loop/regression-known.tsv; a Mac pass is not proof, and removal only makes the gate stricter. pods-size is in this group. Rows that fail on GitHub stay, with the reason updated

- Slug: known-red-b
- Touches: .loop
- ETA: 410 active minutes (estimate 325m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of the group's rows, then a GitHub run link shows it PASS, or it stays on the known list with the GitHub failure quoted
2. Given .loop/regression-known.tsv on this branch, then only the GitHub-proved rows are removed and nothing is added
3. Given this goal's diff, then only .loop/regression-known.tsv and the goal record change, and docs.py check and render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
