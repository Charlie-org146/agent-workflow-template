# Repair the test rows' reads declarations so lanes_cli.py check is clean, carrying v110-fast-reads-static's built work (owner record o858, top's o873: lines 2 and 5 of the path C split; line 1 moved to split-import-component)

- Slug: v110-fast-reads-decl
- Touches: dev/toy, .loop/regression.tsv, skills/workflow-regression, docs/wiki
- ETA: 310 active minutes (estimate 247m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main, then lanes_cli.py check reports zero declaration problems.
2. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
