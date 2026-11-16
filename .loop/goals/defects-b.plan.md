# defects-b plan

1. autorelease.status_held(state, url, number, seen) names red required checks; merge.py passes seen.
2. Toy legs in dev/toy/test-release-head-status.py; rows release-red-checks-named and lane-rows-judge-own-diff, seen red.
3. Regenerate the Tests tables; close 3468 with its row run, 3870 and 3876 with the PR.
