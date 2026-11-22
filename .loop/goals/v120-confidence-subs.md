# Feature confidence counts sub-requirement rows, names untested sub-requirements and never shows 100% while one is untested (release v1.2.0; patch for #5790, second half)

- Slug: v120-confidence-subs
- Touches: skills/workflow-docs, dev/toy, .loop/regression.tsv, docs, README.md
- ETA: 300 active minutes (estimate 240m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a feature page whose Requirements section lists sub-requirements as indented " - ... [ID.n]" lines, then a regression row keyed to ID.n links to that requirement in the docs check and on the Tests page, and counts toward the feature's confidence
2. Given a feature with one declared sub-requirement that has no passing row, then its confidence is capped at 99% and the render names the untested sub-requirement
3. Given a sub-requirement that appears only under Retired, Non-goals, Success metrics or in a code block, then it is not declared and not counted
4. Given a feature with no declared sub-requirements, then its confidence is computed and shown as before
5. Given the whole change, then the docs check, package check and private-name scan pass, every new behaviour has a regression row with a negative control (one row running every case), no existing row changes result, no file newly crosses 19,000 bytes or the 20,480 cap, and the pull request lists every feature score the change moves

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
