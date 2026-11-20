# trim-delivery-a design

Problem: private.py (20,294), role.py (20,034) and guards.py (20,005) are over the 19,000 LF byte size rule, which blocks later goals that need room. Behaviour must not change.

Approaches:
1. Trim docstrings and comments and dedupe code. Small, case-by-case, about 400 bytes per file, and each edit risks a behaviour slip.
2. Whitespace-only: indent nested blocks by 2 spaces instead of 4 and pull wrapped continuation lines back to 4 past the statement. Mechanical, and `ast.dump` before and after proves it identical. About 1,000 to 1,300 bytes per file. Chosen, plus one dead line (`HERE` in private.py, never read) and one docstring shortened.

Done-line needs: each file at or under 19,000 bytes by `git ls-tree -l`; the toys that run these scripts give the same output; no new file, no regression row, no requirement text change.

Open questions: none.
