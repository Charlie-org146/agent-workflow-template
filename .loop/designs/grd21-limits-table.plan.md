# Plan: grd21-limits-table (condensed)
1. Read the Agensi packaging page; record every limit it states.
2. Add one "Package limits" table to How-to-use-Guardrails (limit, Agensi's figure, ours, date read 2026-11-18).
3. Extend dev/toy/test-package-caps.py with the table check and a negative control; repoint row package-caps-held to GRD-21 with an updated scenario (net rows zero).
4. Re-render with the floor dropped, commit; docs.py check, guard, wiki.py prepare.
5. Draft GRD-21 r2 (location clause only) and send r1 and r2 to the operation; GRD-21 stays as is.
