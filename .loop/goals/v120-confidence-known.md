# Feature confidence counts a row whose real latest state is KNOWN as not passing (release v1.2.0; patch for #5790, first half)

- Slug: v120-confidence-known
- Touches: skills/workflow-docs, dev/toy, .loop/regression.tsv, docs, README.md
- ETA: 260 active minutes (estimate 205m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a feature with a regression row whose real latest state is KNOWN, then that row counts as not passing in the feature's confidence (it is in the total, not in the passing count), and a row that passes or never ran is not turned into KNOWN
2. Given a feature with no row in state KNOWN, then its confidence is computed and shown as before
3. Given the whole change, then the docs check, package check and private-name scan pass, the one new behaviour has a regression row with a negative control, no existing row changes result, no file newly crosses 19,000 bytes or the 20,480 cap, and the pull request lists every feature score the change moves

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
