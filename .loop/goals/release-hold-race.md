# The release hold has no race (TD517): release.yml's hold step does not hold for an open main-red issue that the pushed commit's merged PR lists in closingIssuesReferences, because GitHub closes a Fixes issue seconds after the push and the hold read it as still open (run 44838027926 held #5628's release for #5627). An unrelated open main-red issue still holds

- Slug: release-hold-race
- Touches: .github, dev/toy
- ETA: 335 active minutes (estimate 265m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a pushed commit whose merged PR closes the only open main-red issue, then release.yml releases at once; given another open main-red issue the PR does not close, it still holds (toy with a fake gh, negative control)
2. Given the pull request, then its toy row is SEEN RED with the change reverted, the hold still makes at most two gh calls, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
