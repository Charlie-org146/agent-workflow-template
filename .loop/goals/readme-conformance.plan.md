# Plan: readme-conformance

Files: `.loop/readme-gap-table.md`, `.loop/readme-issues-map.md`, this plan and the design. Nothing under `skills/`, `docs/`, `dev/` or `.github/` changes; `.loop/regression.tsv` is untouched.

1. Fetch `origin/loop/requirements-consolidate` and read its README (43 requirement rows, 226 distinct bullets, keyed by row and ordinal). Done: tip fc691448.
2. Six read-only passes by feature fill one row per bullet (status, evidence, what is missing, issues, closing idea, size flag). Done: 417 listed statements, 221 distinct on the first tip.
3. Merge the passes by key; re-check by grep every row quoted in the cluster list and decide the rows where passes disagree (stricter reading unless grep says otherwise). Re-audit by hand the rows that changed between README tips (OPS-11, OPS-16.3, CHK-1.2, plan-red-team, ops-findings, DOC-2.6).
4. Group the 88 gaps into 20 clusters, PC-friendly and small first, with scripts at the 19,000-byte line named; mark the four bullets the consolidation PR closes and the clusters that are goals the README already names.
5. Map the 38 issues to a bullet or `none`, with a state and a reason; write the close list.
6. Check: `docs.py check` (DOCS OK), `entry.py check`, `git diff --stat origin/main` limited to `.loop/`, row count of `regression.tsv` unchanged.
7. Review at condensed depth (one spec-review round, one review pass), qa, ship, pr. Send operation-top the table summary and the close list in one message (done) and re-run as a delta when requirements-consolidate merges.

Risks and answers: a wrong `done` row is the main risk, covered by the evidence rule (code plus a passing test or page) and the grep check; a stale table is covered by the delta re-run; the table is long, so the cluster list at the top carries the decisions.
