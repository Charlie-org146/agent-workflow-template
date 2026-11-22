# Temporarily raise the package file cap to 200 (owner o718, GRD-21): the package is published by website upload, and a later minor revises GRD-21

- Slug: grd21-cap-lift-2
- Touches: dev/package.py, dev/toy, docs/wiki, docs, .loop/regression.tsv, README.md
- ETA: 360 active minutes (estimate 288m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given dev/package.py, then MAX_FILES is 200, a package of 200 files passes its file check and a 201st file fails it
2. Given docs/wiki/How-to-use-Guardrails.md's package-limits table, then the agent-upload row says it no longer applies because the package is published by website upload, our figure is 200 against the buyer's agent's 200 and the website's 1,000, none of ours is looser than the limit that applies, and the change is marked temporary until a later minor revises GRD-21 (o718)
3. Given dev/toy/test-package-caps.py, dev/toy/test-package-headroom.py and the row package-caps-held, then each checks against 200 and keeps its negative control: a 201st file fails
4. Given GRD-20 and GRD-21's requirement text and review marks, then neither changes
5. Given the whole change, then the docs check, package check and private-name scan pass and no other regression row changes result

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
