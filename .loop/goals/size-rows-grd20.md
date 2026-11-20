# Every regression row that fails a script at a fixed byte count other than 20,480 is brought to the approved GRD-20's two lines: WARN at 19,000 bytes or more, FAIL above 20,480 (TD482, as TD412 and TD480). Today's third case: trim-setup-under-19000 fails setup.py at 20,032 bytes, which GRD-20 makes a warning. Only rows stricter than the approved text change; ls-size-budget is already aligned in regrd20-trims

- Slug: size-rows-grd20
- Touches: .loop, dev/toy
- ETA: 465 active minutes (estimate 370m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression.tsv on this branch, then no row fails a script under 20,481 bytes, and every changed row warns from 19,000; the PR lists each changed row as 'TD482: aligned to approved GRD-20'
2. Given each changed row, then a negative control fails it at 20,481 bytes and only warns at 19,500, shown by a toy, and trim-setup-under-19000 passes with a warning on today's setup.py
3. Given this goal's diff, then docs.py check and criteria.py render --check pass, and each changed row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
