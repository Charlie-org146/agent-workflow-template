# Plan: adoption-count-fix

## Implementation plan

Checked against the code: `follows()` (sections.py:99) and `adoption()` (sections.py:121) exist; `adoption()` has one caller, the row loop at sections.py:165, and reads `follows()`. The toy is `dev/toy/test-follows-adoption.py`; the render is `skills/workflow-docs/scripts/criteria.py render`.

Build steps, in order:

1. `follows()` splits a bullet at `; ` only outside brackets and parentheses, and only when the text before the split is itself a complete `source: tag` pair with a known tag; a bullet that does not split completely stays one source. Already built in commit dce2f7ea; build confirms it, it does not rewrite it.
2. `adoption()` counts adopted sources over all sources; adapted, planned and own count 0; no sources is not measured. Docstring wording only.
3. The toy gains the cases below.
4. `criteria.py render` rewrites the Adoption cells and headlines in README, Home and Principles after main is merged.
5. `docs.py check --own` and `criteria.py render --check` pass; stale own pages are re-stamped.

Test for each done line (a negative control is seen failing before the change, on main's counter):

- Done line 1: a two-source bullet (adapted; adopted) returns 50 (checked: main returns 100, one source whose text holds the whole bullet); single-source bullets (adopted, adapted, planned, own, and a four-bullet cell) return main's values; a semicolon inside `[A; B](u)`, `[A: adopted; B](u)`, a link target, or a bare `A; B` does not split; an unknown tag does not split.
- Done line 2: after render, only the HLT-2 and MCH-1 cells and the two headlines that average them change (33 to 25 percent, 25 to 20 percent); `render --check` prints TABLES OK and `docs.py check` passes.
- Done line 3: `git diff origin/main...HEAD --stat` lists only sections.py (12,196 bytes, under 19,000), the three front pages, the toy, this goal's records and wiki re-stamps; no requirement text, tag or Follows line differs; the private-names scan is clean.

What could break:

- A Follows line whose source text holds `; ` followed by something shaped like `x: adopted` inside prose, which would split wrongly. The bracket and parenthesis depth rule and the all-parts-must-be-tagged rule make it fall back to one source.
- A page re-render reordering unrelated cells. Checked by diffing the render: only the two rows and their headlines move.
- sections.py growing past the size cap. It is 12,196 bytes.

Out of scope: any requirement text, tag or Follows line; MCH-1 stays at 20 percent (Operation's ruling); the Adoption definition itself; other generated pages.

PENDING: none for the owner.

## Review record

Filled by the plan review.
