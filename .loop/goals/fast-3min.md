# Merges take 3 minutes or less from push to main (DEL-17; owner, TD468 top priority). First measure a baseline: the last 5 merged PRs, each push-to-main time split into PR checks, wait before enqueue, and queue time. Then cut it: enqueue the moment a PR's checks pass on its exact head (no idle wait), and run docs.py check once instead of in both affected and the merge queue. Report the measured after-times; nothing that guards safety (GitGuardian, the private-name scan, DEL-9) is skipped or weakened

- Slug: fast-3min
- Touches: .github, skills, dev/toy
- ETA: 430 active minutes (estimate 342m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the pull request, then it shows the baseline for the last 5 merges (push to main, split into checks, wait and queue) and the same split measured after the change
2. Given the change, then docs.py check runs once per merge, enqueueing happens as soon as checks pass on the exact head, and GitGuardian, the private-name scan and every required check still run
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
