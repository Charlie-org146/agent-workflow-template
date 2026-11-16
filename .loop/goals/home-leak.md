# Stop toys leaking into the owner's real ~/.workflow-loop on Windows, and fail loudly when one does (issue 4393)

- Slug: home-leak
- Touches: dev/toy, .loop, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. Every toy that touches ~/.workflow-loop isolates it on Windows as well: LOOP_FLOW, LOOP_HEALTH and any similar override point at temp paths, and USERPROFILE is set along with HOME, so no toy reads or writes the owner's real flow.json (dev/toy/test-settings.sh is the known leak)
2. The toy harness hashes the real ~/.workflow-loop before and after each toy and fails loudly when anything changed
3. The other leaking toys are found by grepping dev/toy for expanduser and ~/.workflow-loop and fixed or isolated, and the list of them is in the goal's design
4. Toy cases proven red cover the guard catching a leak and the isolation holding on Windows, and issue 4393 is closed with that proof; every script stays at or under 19,000 bytes and the package at 98 files or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
