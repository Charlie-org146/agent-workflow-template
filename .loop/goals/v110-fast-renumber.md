# Renumber the principles 1 to 8 with the principle 3 split, names and numbers only (v1.1.0 task 5, part 1a)

- Slug: v110-fast-renumber
- Touches: docs/wiki, docs, README.md, dev/toy, .loop/regression.tsv, skills/workflow-delivery/references/commands.md
- ETA: 275 active minutes (estimate 219m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the docs, then the "principles renumber 1 to 8" with principle 3 Fast, 4 Cheap and 5 Small as in frozen-source-final-1742 ("Today's 4 Private, 5 Reproducible and 6 Autonomous become 6, 7 and 8"; "GRD-20 moves here", to 5 Small); every other feature sits under the principle the page names, except OPS-16, which stays where it is until the owner's answer; no principle sentence is changed; every reference to an old principle number is updated; and docs.py check passes.
2. Given the health check, then it is not red after the renumbering.
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
