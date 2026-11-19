# Three README gaps close: the memory floor defaults to the README's 3 GB in code (a machine may still set its own locally, GRD-12); adopted repos get the milestones_source setting and their own-repo links (#5079, #5078); and a token in the environment never enables writes, only --live does (GRD-5.1) (TOP-DECISION 135, readme-conformance G01, G02, G03)

- Slug: gap-wave1-small
- Touches: not declared
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The code's memory-floor default is 3 GB everywhere (no 4 or 3.5 left as a default), a machine-local setting still overrides it, and a row proves both
2. An adopted repo has a milestones_source setting and its wiki and README links point at its own repo, not the template, each with a negative control (#5079, #5078)
3. A GH_TOKEN or similar token in the environment never turns on writes; only --live does, proven by a row with a negative control (GRD-5.1)
4. No requirement text changes, no new shipped file, every touched script stays under 19,000 bytes or does not grow, net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
