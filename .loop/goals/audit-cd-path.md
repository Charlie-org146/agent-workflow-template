# docs audit resolves a row's test path against the folder its command cd's into (#4502)

- Slug: audit-cd-path
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. A regression row whose command is 'cd sub && bash test.sh' gets no 'test no longer matches' from the docs audit when sub/test.sh exists, and still gets it when sub/test.sh is missing.
2. A toy runs both cases, plus a row with no cd as the control, and has a regression row.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
