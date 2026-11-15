# Three defects of the release and lane tooling are fixed or closed with proof: merge.py never tells the owner to gh pr merge a release PR blocked by failing checks; one stale page on main no longer fails every goal's pr lane; goal.py new --here refuses in the main checkout

- Slug: defects-b
- Touches: docs

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py with a release PR blocked by failing required checks never prints a gh pr merge instruction (it names the failing checks and stops), proven by a toy seen red, or issue 3870 is closed with proof that release-head-status already fixed it
2. The pr-lane rows review-findings-skill-lines and settings-render-fresh judge the goal's own diff, not pages stale on main: a stale page on main with a goal that does not touch it passes, proven by a row seen red, or issue 3876 is closed with proof
3. goal.py new --here run in the main checkout (the checkout the installed skills point to) refuses, naming a worktree as the fix; run in a goal worktree it still works, proven by a toy seen red

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
