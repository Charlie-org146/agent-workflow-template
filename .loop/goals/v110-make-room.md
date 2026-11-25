# One-time make room (part A, owner o954; owner o1009, ledger o957; split by owner o1016, ledger o962): split the core scripts that sit at the size line (goal, flow and lane in workflow-delivery; merge in workflow-release; fit, role and routing are part B, the goal v110-make-room-b) into sibling modules by pure moves, with no behaviour change, so later goals have room without asking for new files

- Slug: v110-make-room
- Touches: skills/workflow-delivery/scripts, skills/workflow-release/scripts/merge.py, dev/toy, .loop/regression.tsv
- ETA: 425 active minutes (estimate 339m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the seven split scripts and their new modules, when size-check runs, then each ends with at least 6,000 bytes of room to the 19,000-byte line.
2. Given the regression rows that pass on the merge base, when they run on the head, then every one passes, no row is added to a known or skip list, and the move check shows every moved line byte-identical but for imports and module prefixes.
3. Given the package, when pods-size and the package rows run, then they pass with the new modules listed.
4. Given every command, flag, setting name and output line of the seven scripts, when they are compared before and after, then none changes.
5. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
