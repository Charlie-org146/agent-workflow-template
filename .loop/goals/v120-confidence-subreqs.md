# Feature confidence counts sub-requirement rows and KNOWN rows as not passing, and names untested sub-requirements (release v1.2.0; patch for #5790)

- Slug: v120-confidence-subreqs
- Touches: skills/workflow-docs, dev/toy, .loop/regression.tsv, docs, README.md
- ETA: 315 active minutes (estimate 251m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a feature whose requirement has sub-requirements (its ID followed by .n), then rows keyed to a sub-requirement count toward that feature's confidence, and a row in state KNOWN counts as not passing
2. Given a feature with one sub-requirement that has no passing row, then its confidence never shows 100% and the untested sub-requirement is named in the render
3. Given a feature with no sub-requirements and no row in state KNOWN, then its confidence is computed and shown as before
4. Given the whole change, then the docs check, package check and private-name scan pass, every new behaviour has a regression row with a negative control, no existing row changes result, no file newly crosses 19,000 bytes or the 20,480 cap, and the pull request lists every feature score the change moves

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
