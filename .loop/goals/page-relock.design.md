# page-relock design

Problem: a reviewed page's lock R hashes its whole Requirements section, so another goal's reviewed edit to a different line moves R on every other branch and the owner must re-review the page (#3915).

Approaches:
1. Make the check ignore R movement caused by owner-reviewed lines, and re-stamp with a `relock` command that logs why. Cost: one small module (prd.py and criteria.py have no room under 19,000 bytes). Risk: forged line seals; mitigated by requiring each line to be main's own line or an ID in the reviews log.
2. Hash each line separately in the page lock. Cost: changes every stamp on every page; owner re-reviews all.

Chosen: 1. Page stays LOCKED when any line is unreviewed, its seal is broken, a line is neither on main nor in the reviews log, or a line main has was dropped, or Problem, Non-goals or Success metrics moved.

Done line: toy `dev/toy/test-page-relock.py`, seen red, covers the two-branch merge and the unreviewed-line case.
