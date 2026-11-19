# The 11 workflow-docs scripts go under the 19,000-byte target by trims and cohesive splits only, behaviour unchanged, no scattering, net files 0 or fewer in the package listing (package cap 100 holds), so the v2.0 gate's full suite has no size FAIL (TOP-DECISION 55 and 57, o195 no waivers)

- Slug: known-red-w11-docs-size
- Touches: not declared
- ETA: 225 active minutes (estimate 177m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards: docs-scripts-under-19000 size-139
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main
3. The package listing has no more files than on main, and no behaviour changes: every row that passes on main still passes on the PR head

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
