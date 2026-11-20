# Every ETA the loop states is recorded and checked, so the owner can trust it (principle 8 honesty and principle 3's ETA rule, DEL-17, HLT-4; owner words o644: the fast and honest principles are the two most important; TD381). Every ETA a goal, the board or a STATUS message states is recorded with who stated it, when, its basis and the time it names. When that time passes without the event, the ETA is marked missed with its cause, and stays on the board as missed (principle 8). Health prints each layer's hit rate (goal, board, operation STATUS) over the last 20 ETAs and fails when an ETA passed more than 15 minutes ago is neither met nor marked missed. A wrong statement or a missed ETA logged in a run record becomes a finding (HLT-4). Files: the monitoring and health scripts that hold ETAs and findings; the worker lists them, with sizes, before building and sends the list to operation-mac, so nothing collides with module-packing's moves; no script ends over 20,480 bytes

- Slug: eta-honesty
- Touches: skills/workflow-monitoring/scripts, skills/workflow-health/scripts
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal, board or STATUS ETA, when it is stated, then a record holds who, when, basis and the time it names; and given one whose time passed without the event, then it is marked missed with a cause and the board shows it as missed, not hidden (a toy proves both, with a met ETA as the negative control)
2. Given health, then it prints each layer's ETA hit rate over the last 20 and fails when an ETA more than 15 minutes past is neither met nor marked missed, with a negative control where every past ETA is met or marked
3. Given a missed ETA or a statement marked wrong in a run record, then health files it as a finding with the goal and the cause; and given this goal's diff, then only the listed scripts, one toy or row per done line and the record files change, net regression rows are at most plus 2, and each script is under 20,480 bytes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
