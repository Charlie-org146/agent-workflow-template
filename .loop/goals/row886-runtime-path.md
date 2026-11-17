# row886-runtime-path: the perms-private-refused row builds its private path at runtime, so commits that stage .loop/regression.tsv pass the private scan (owner o7, o11)

- Slug: row886-runtime-path
- Touches: not declared
- ETA: 270 active minutes (estimate 216m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Row perms-private-refused in .loop/regression.tsv no longer contains a literal home path; it builds the path at runtime and still fails when the private-row refusal is removed (negative control).
2. A commit that stages .loop/regression.tsv passes the pre-commit private scan, and no other row or file changes beyond what that needs.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
