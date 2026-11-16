# Regression rows and full-suite time are capped; going over a cap blocks delivery (#4511, owner o51)

- Slug: test-caps
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. max_regression_rows and max_suite_seconds are settings in .loop/config.json with defaults, shown in Home's settings table.
2. A goal whose rows take the repo over either cap is refused at qa with the numbers, unless it removes or merges at least as many rows as it adds or the owner raises the cap in their own words; a goal that only consolidates is always allowed.
3. Health shows rows and suite time against both caps, warning at 90% and failing over the cap, each with a negative control, and the Guardrails page states this as a requirement under owner record o51.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
