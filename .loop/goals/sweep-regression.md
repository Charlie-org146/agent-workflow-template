# Every open Regression: <row> issue is rerun on current main, passing rows closed with proof and failing rows grouped by cause

- Slug: sweep-regression
- Touches: docs

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each open 'Regression: <row>' issue is rerun with regression.py's own run command on current main, a passing row's issue is closed with the pass line as proof, and the rows that still fail are grouped by cause (real defect with the file, known Windows-only, needs Linux or Mac, flaky) in one summary comment on a new tracking issue; the counts of closed, still failing by group and skipped are reported and nothing else is fixed

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
