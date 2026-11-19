# Design: pr-regen-start

Problem: goal.py pr pushes a head whose START.md or stamped wiki pages are stale, so merge.py refuses after the MERGE-GO (#5317; seen on #5307 and #5318).

Approaches: (A) a new check in merge.py (refuses, does not fix); (B) goal.py pr runs the existing entry.py write and wiki.py prepare --commit before the lane. Chose B: the head the lane passes on is the head merge.py accepts. Size: goal.py and fit.py are at the cap, so fit.py gains regen() by reusing one path helper and dropping three docstrings; goal.py drops a dead return and a longer expression.

Done lines: 1 regen commits START.md and pages before the push; 2 nothing stale adds no commit (toy case with a stale-before control); 3 sizes not above main.

Open questions: none.
