# SET-1: The setup, hooks and agent-permission rows (SET-*, grd*, adopt fixture) pass on Linux CI (#4553)

- Slug: ci-setup-rows
- Touches: not declared
- ETA: 205 active minutes (estimate 162m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the 14 rows in #4553, when the full suite runs on CI, then each passes or is fixed with its real cause written on #4553
2. The same rows still pass on the PC

## Verify by hand

1. Open the regression run of this branch linked on issue #4553 and find the 14 rows it names.
   Expect: each shows PASS except lanes-trace, whose remaining cause (the suite-wide trace exceeds the 900 s CI row limit, #4153) is written on #4553.
2. On a Mac or Linux shell in this repo, run `bash dev/toy/test-setup-adopt.sh setup-refusal-writes-120`.
   Expect: it ends with PASS lines and no "something stayed written"; no `.git/index.lock` is left in its temp repos.
