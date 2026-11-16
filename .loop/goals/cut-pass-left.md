# release.py cut trusts a row's PASS only on the current commit and lists the rows it left unrun (#4508)

- Slug: cut-pass-left
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. The cut reruns a row whose only PASS in regression-runs.tsv is on an older commit, and does not rerun a row with a PASS on the current commit; a toy checks both.
2. Rows not run before the cut's 900-second stop are printed by the cut and written into the release notes as LEFT with their count; a toy forces the stop, and a negative control finishes with nothing LEFT.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
