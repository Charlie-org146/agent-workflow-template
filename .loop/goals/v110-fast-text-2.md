# Write the principle 3 split and the Fast features' text (v1.1.0 task 5, part 1b)

- Slug: v110-fast-text-2
- Touches: docs/wiki, docs, README.md, dev/toy, .loop/regression.tsv
- ETA: 245 active minutes (estimate 196m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the docs, then the principles are renumbered 1 to 8 with 3 Fast, 4 Cheap and 5 Small and their sentences as in frozen-source-final-1742; the pages carry DEL-19 (revised), DEL-17, DEL-25, DEL-26, DEL-27 and DEL-22's title "Fast plans" as pinned, with Reviewed marks from o738-o742; every reference to an old principle number is updated; and docs.py check passes.
2. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
