# Design: docs-import-render

Problem: `docs.py` line 190 calls `__import__("render")`, added by #4608. The package safety scan refuses `__import__` as obfuscation, so `package-passes` and `prd-no-dunder-import-3800` fail on main, and rows that build or refuse a package (entry-adopt, sync-*) probably fail with them (#4652).

Approaches:
1. Local `import render` at line 190. Cost: +9 bytes in a file already at 19,181, over the cap that the goal must not grow.
2. A module-level `import render` beside the other imports, and drop the three function-local `import render` lines. Render imports only counting, criteria, pageformat and deployments, never docs, so there is no cycle. Cost: a few lines touched; docs.py gets smaller.

Chosen: 2. It meets done line 1 and keeps docs.py under its size on main.

Done line 1: the module import plus removing `__import__`; `package-passes` and `prd-no-dunder-import-3800` run green.
Done line 2: run each of entry-adopt, sync-default-source, sync-propose, sync-template-redirect; on a failure write the real cause on #4652.

Open questions: none.
