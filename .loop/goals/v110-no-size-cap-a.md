# No size limits, part A: the limits end (owner o984, done lines o988; frozen copy no-size-cap-done-lines-APPROVED-o988-2026-11-25.md, which gives the new DOC-26, GRD-20 and REG-4 text)

- Slug: v110-no-size-cap-a
- Touches: skills, dev, docs/wiki, .loop
- ETA: 385 active minutes (estimate 305m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a script of any size, a SKILL.md of any length, a page with any number of Problem lines, metrics or requirements, a principle with any number of requirements, any number of regression rows, and a plan of any number of files, when the package, health, docs, sizing and plan checks run, then none of them warns or refuses on that size.
2. Given the marketplace's package rules (200 files, 5,000,000 bytes, 20 KB per packaged script), when the package check runs, then each still refuses past its limit, and its negative control still fails.
3. Given the Principles, Guardrails, Home, README, Setup and START pages, the settings table and the requirements whose text set our limits (DOC-26, GRD-20, REG-4), when they are read, then none states a size limit of ours, principle 5 reads "Nothing in our rules caps the size of a script, page or test table; the marketplace's own package rules still apply, and a change is never hidden by reformatting.", and the old frozen size clauses, including v110-ontime's 20-file line, are noted as met.
4. Given the rows that check only one of our size limits, when the goal merges, then each is removed together with its checker, and no row is loosened in place, skipped, or added to a known list.
5. Given the package, when the goal's checks run, then no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
