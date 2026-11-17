# howto-kinds plan

Checked against the code: milestones.py, deployments.howto, pageformat.frontdoor and home, agents.py and seed.py exist.

Build steps
1. milestones.kinds and unlisted; deployments.howto calls them; pageformat.frontdoor and home accept the links-only form; agents.py and seed.py write links.
2. The nine How-to-use pages get the What's delivered table and Kind blocks; README and Home link the pages.
3. DOC-4 and DOC-5 reworded (o87), the Kind rules under DOC-19, all Unreviewed; dev/toy/test-how-to-kinds.py and four doc19 rows.

Tests per done line: 1 doc19-kind-row, doc19-kind-fields, doc19-readme-links; 2 doc19-command-listed; 3 docs check on this repo and the rows.

What could break: repos whose README still holds How-to-use tables fail DOC-5 until converted; the bash toys that exercise setup are not runnable on this PC, so the Mac lane covers them.

Out of scope: marking anything Reviewed; rewording DOC-18.

PENDING: none
