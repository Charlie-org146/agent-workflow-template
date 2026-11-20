# The regression row settings-render-tables passes again (issue 5469; TD439: first in the red-row queue because it blocks #5518 and so the release). The row's toy copies the repo and expects a stale automation row on Home.md to prove that rendering the Tests tables leaves README.md and Home.md unchanged; since the approved README moved Home's Settings and Automation blocks (docs-format-v2 #5462 and readme-six #5499), Home has no automation row, so the toy prints 'Home.md has no automation row to make stale'. The fix aims the toy at where the generated block lives now, with the same check: a stale generated block on the front pages, and a Tests-tables render that leaves README and Home unchanged. Same strength, no check loosened, no page text changed

- Slug: settings-render-tables-fix
- Touches: dev/toy, .loop/regression.tsv
- ETA: 390 active minutes (estimate 309m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the toy on this branch, when it makes a generated block stale on the page where that block lives now and renders the Tests tables, then README.md and Home.md are byte for byte unchanged and the row passes; and a negative control where the render does rewrite README or Home makes the toy fail
2. Given this goal's diff, then only the row's toy (and the row's command or description if its file moved) and the goal's record files change, no wiki or README text changes, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
