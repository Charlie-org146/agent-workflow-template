# The full regression run's summary keeps each failing row's last 20 lines of output (#4516)

- Slug: ci-fail-output
- Touches: .github/workflows/regression.yml, skills/workflow-regression/scripts, dev/toy

## Done lines

Frozen. A wrong done line needs a new goal.

1. In the full regression run on CI, the job summary shows each failing row's name with its last 20 lines of output.
2. A toy feeds the summary step one failing and one passing row: the failing row's last lines appear, and the passing row's output does not.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
