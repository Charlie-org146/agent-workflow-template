# The regression row landed-left-alone (dev/toy/test-monitoring.sh: a landed goal with an empty pr field, and a mender running after its goal lands, are left alone) passes on main again, so pull-request CI stops failing on it for every PR (red on main since at least nightly 44440316472; owner o355 gap scope; TOP-DECISION 142).

- Slug: landed-left-alone-fix
- Touches: not declared
- ETA: 270 active minutes (estimate 215m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. landed-left-alone passes on the merged result, locally and in a targeted regression.yml run on the branch, with the cause named: either the code under test is fixed or the toy's stale expectation is corrected to match the requirement it proves, never loosened
2. The row was seen failing on main before the fix and passing after (seen-red recorded), no other monitoring row turns red, net regression rows 0 or fewer, no new file, every script under its size cap

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
