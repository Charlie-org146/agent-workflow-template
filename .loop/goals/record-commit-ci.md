# goal.py pr's record commit no longer forces a second full CI round before merge (o156)

- Slug: record-commit-ci
- Touches: not declared
- ETA: 240 active minutes (estimate 192m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal whose lane passed and whose pr step adds only the record commit (regression-issues.tsv, Tests and Documentation result lines), when CI runs on that head, then it reuses the lane head's result or runs no affected rows, and merge.py accepts it without a fresh full round
2. A head whose record commit touches anything else still gets a full CI round; the Delivery page states the rule with a test row

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
