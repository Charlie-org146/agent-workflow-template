# goal.py, role.py, lane.py and setup.py are under 19,000 bytes and the package is back to 98 files (#138, #352, #3852, #2158, #4497)

- Slug: trim-scripts-98
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. On main, workflow-delivery's goal.py, role.py and lane.py and workflow-setup's setup.py are each under 19,000 bytes, and the size rows for them pass.
2. The package holds 98 files after folding one module into another, the package-headroom row passes, and every regression row that touched the folded module still passes.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
