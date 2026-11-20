# The release package builds again: skills/workflow-docs/scripts/deployments.py no longer imports auto across skills (#5579 broke it; package.py refuses a cross-skill import). It reads auto.CLASSES in place, loaded by path, and still fails closed when unreadable

- Slug: fix-release-import
- Touches: skills
- ETA: 60 active minutes (estimate 48m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given this branch, then `python3 dev/package.py` passes (no `imports auto` failure), and rows package-gate-head and package-passes-3800 pass
2. Given deployments.py, then it reads auto.CLASSES from workflow-monitoring in place (never a copy, DEL-9) with no import statement of another skill, and answers "unreadable" when it cannot load it
3. Given the delegated records toy, then it still passes, and package-gate-head and package-passes-3800 each have a fresh red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/package.py --out /tmp/pkg-check.zip | tail -1`.
   Expect: a line starting `PASS:` and no `imports auto` line.
2. Run `python3 dev/toy/test-delegated-records.py | tail -3`.
   Expect: only PASS lines (15).
3. Add `import auto` under `import importlib.util` in `skills/workflow-docs/scripts/deployments.py` and run step 1 again (then undo it).
   Expect: `FAIL Scripts: skills/workflow-docs/scripts/deployments.py imports auto, which is not in the standard library`.
