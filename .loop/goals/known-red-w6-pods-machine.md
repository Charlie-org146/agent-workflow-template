# The pods, mon15 and machine regression rows that are red on main in the full run 44463859531 pass again: pods-independent pods-lock pods-owner mon15-merge-lock mon15-pod-owner machine-apply-installs machine-done-7 machine-windows plan-cache-key. Each is fixed, or removed with evidence that the behaviour it tests is gone; none is moved to the known list (owner: "No waivers u can do it").

- Slug: known-red-w6-pods-machine
- Touches: not declared
- ETA: 290 active minutes (estimate 230m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: pods-independent pods-lock pods-owner mon15-merge-lock mon15-pod-owner machine-apply-installs machine-done-7 machine-windows plan-cache-key
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `bash dev/toy/test-pods.sh layers twopods; bash dev/toy/test-pods.sh lock; bash dev/toy/test-pods.sh owner`.
   Expect: each run ends with `ALL PASS`.
2. Run `unset PYTHONDONTWRITEBYTECODE; bash dev/toy/test-machine.sh machine-apply-installs; bash dev/toy/test-machine.sh machine-windows`.
   Expect: each prints a `PASS:` line.
3. Run `bash dev/toy/test-plan-cache.sh key | tail -1`.
   Expect: `ALL PASS`.
