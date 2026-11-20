# merge.py --go-head keeps the CI gate on when a PR's only red rows are known main reds, so a GO stays bound to the exact head (issue #5289; TOP-DECISION 154; owner o355 gap scope).

- Slug: go-head-main-reds
- Touches: not declared
- ETA: 260 active minutes (estimate 208m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py --go-head SHA refuses GO_HEAD unless the pull request head is SHA, refuses CI_RED when a required check fails on any row that is not a known main red, and merges when the only failing rows are known main reds (listed in .loop/regression-known.tsv or red on main's latest full regression run), naming each discounted row in its output
2. Negative controls, each seen red: a new red row still refuses CI_RED; a head that is not SHA still refuses GO_HEAD; a pending or missing check still refuses CI_PENDING or CI_MISSING; main-red rows alone pass and are named
3. merge.py ends at or under 19,000 bytes (new code goes to a script with room, never into an over-cap script), no new shipped file, net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
