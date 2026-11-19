# Every requirement bullet in the consolidated README (requirements-consolidate) is audited against the code, tests, docs and adopter migration, and a gap table records each as done, partial or missing with evidence and the goal that closes it; the 38 issues moved to v2.0 are each mapped to a README bullet as a gap, closed by a named goal, or proposed for close; the v2.0 gate waits on zero gaps (owner o236; TOP-DECISION 95, 97, 121)

- Slug: readme-conformance
- Touches: not declared
- ETA: 220 active minutes (estimate 175m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A gap table in .loop/ lists every README requirement bullet with status done, partial or missing, the evidence (file and line, test row or doc page) and the closing goal for each gap, built first from requirements-consolidate's pushed tip and re-run as a delta after it merges
2. Each of the 38 issues moved to v2.0 is mapped to a README bullet and marked a gap, closed by a named goal, or proposed for close with a reason; the close list goes to operation-top in one message for the owner's words
3. It changes no requirement text, adds no shipped file, and net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
