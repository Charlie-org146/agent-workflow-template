# private-lines-v1051: main holds no line the Mac private scan refuses (owner o19)

- Slug: private-lines-v1051
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. docs/wiki/Monitoring.md, skills/workflow-monitoring/scripts/auto.py and the docs/ROADMAP.md line behind wiki:Roadmap:369 hold no flagged word; each line keeps its meaning and nothing else changes beyond generated stamps.
2. auto.py classifies private-data questions exactly as before, shown by a test, and a commit staging all three files passes the pre-commit private scan.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-private-class.py`.
   Expect: every line starts with PASS and the exit status is 0.
2. Stage docs/wiki/Monitoring.md, docs/ROADMAP.md and skills/workflow-monitoring/scripts/auto.py and commit.
   Expect: the pre-commit private scan passes.
