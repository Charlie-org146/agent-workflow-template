# A private repo's PR gets a status for every required check, or the goal names the ones it can't post before pr (#4537)

- Slug: private-required-checks
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. On a private repo whose base branch requires a check whose job runs a script other than regression.py, the pr step posts a status for each required check it can run locally, or names each one it cannot and stops before opening the PR, instead of leaving the PR blocked.
2. A toy runs a fixture repo requiring one regression check and one non-regression check, and a negative control requiring only the regression check still passes as before.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
