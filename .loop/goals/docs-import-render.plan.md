# Plan: docs-import-render

Checked against the code: `skills/workflow-docs/scripts/docs.py:190` holds `__import__("render")`; lines 207, 257 and 327 import render inside functions; `render.py` imports only counting, criteria, pageformat and deployments, so a module-level import cannot cycle.

Steps:
1. Add `import render` after `import entry` in the import block; change line 190 to `render.home_fresh(...)`; delete the three function-local `import render` lines. docs.py ends smaller than on main (19,181).
2. Row `docs-no-plain-dunder-import` (source docs-import-render:1, criterion): `docs.py` holds no `__import__`. Seen red on main's docs.py, green after. The existing `package-passes` and `prd-no-dunder-import-3800` rows are the full proof and are run too.
3. Row `docs-import-rows-run` (source docs-import-render:2): runs entry-adopt, sync-default-source, sync-propose and sync-template-redirect; any that still fails has its real cause written on #4652.
4. `docs.py check --own` and `regression.py sync`.

What could break: any caller that relied on render loading late. Render imports nothing from docs, so none. Out of scope: other scripts over the cap (#4653), the six unread rows (#4556).
