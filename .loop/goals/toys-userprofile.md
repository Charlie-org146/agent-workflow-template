# Toys that set HOME also set USERPROFILE (#4514)

- Slug: toys-userprofile
- Touches: dev/toy, .loop/regression.tsv

## Done lines

Frozen. A wrong done line needs a new goal.

1. dev/toy/test-prd-copy.sh sets USERPROFILE alongside HOME, and the toys-set-userprofile row passes on this PC and on CI.
2. A check finds every toy that sets HOME without USERPROFILE and fails on one, with a negative control.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
