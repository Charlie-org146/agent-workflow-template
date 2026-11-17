# Design: health-feature-table

## Problem

The health report lists findings group by group, so I can't see at a glance which feature each finding is about or
whether it already has an issue; the digest comment shows issue numbers per feature but not the findings themselves.
Filed health issues carry a feature label only when `feature_labels` is on (off by default), so most findings link to no
feature page at all. The owner works feature first (o73, o74): every finding and issue must name a feature page, or Other.

## Approaches

1. **Replace the per-group lines with the table.** The report becomes header, one findings table, verdict. Cost: about
   fourteen toy tests grep the `FAIL <group> <subject> <rule>:` lines of `health.py check`; all of them would change, and
   HLT-3's "every rule marked pass, warn, fail or unread with its fix" checklist would be lost. Risk: high, late in v1.2.
2. **Add one findings table after the header; keep the group sections as the rule checklist.** The table is where
   findings are read (feature, group, rule, severity, finding, issue); the group sections stay as the per-rule
   pass/warn/fail/unread list with fixes that HLT-3 already promises and the tests read. Cost: one new helper and a few
   lines in check and the digest. Risk: low; the old lines are unchanged.

**Chosen: 2.** It meets done line 1 (findings print as one table, every row a feature or Other, the digest shows the
same table) without breaking the checklist or its tests, and it fits the size caps.

## Shape

- New `skills/workflow-health/scripts/table.py` (every health script is within ~1 KB of the 19,000-byte cap, so the
  logic lives in its own file):
  - `rows_of(rows, root)`: every WARN, FAIL and UNREAD row (Mine's details stay local, as in the report), each with
    Feature (`issues.feature_of`, else `Other`), Group (its title), Rule (`report.rule_of`), Severity (the state),
    Finding (subject and detail, `|` escaped, one line) and Issue (`#N` of the open or closed health issue whose marker
    key matches, from the health issue list check already read; `not filed` when none matches; `not read` when the
    list was not read). Sorted by feature (pages by name, Other last), then group order, then severity.
  - `lines(...)`: `FINDINGS (N)` then a Markdown table, or `FINDINGS: none`.
  - `insert(text, rows, root)`: the report with the table after its header line.
  - `from_report(path)`: the table lines read back from a saved report (the digest's source).
- `health.py check`: inserts the table (when table.py is installed beside it; a lone health.py prints as before).
- `automation.py digest`: a `### Findings` section with the same table from `HEALTH_REPORT`, each `#N` turned into its
  link when the issue is open; the per-feature sections stay. `No feature` shows as `Other` there.
- `file.py plan`: always tags `feature:<Page>`, and `feature:Other` for a finding with no feature, whatever
  `feature_labels` says; the label is created beforehand as now. `feature_labels` keeps its meaning for regression
  issues only, and its setting text says so.
- Pages: HLT-3 and HLT-4 reworded (owner records needed to unreview both; the new wording is left unreviewed for the
  owner); How-to-use-Health mentions the table; Settings text for `feature_labels`.

## Done lines

1. Toy test: a repo with findings in at least three groups; `health.py check` prints one `FINDINGS` table with the six
   columns, every row's Feature a docs.tsv page or Other; `automation.py digest` (dry run, `HEALTH_REPORT` set) prints
   the same rows. New regression row on HLT-3, seen red on the old code.
2. Toy test: `health.py file` with `feature_labels` false (and unset) tags a feature finding `feature:<Page>` and a
   no-feature finding `feature:Other`. New regression row on HLT-4, seen red. The existing tests that assert "no feature
   label when off" for health are updated; regression's own feature_labels tests stay.
3. HLT-3 and HLT-4 text plus the two Tests rows; unreviewed only with the owner records operation-pc gives; never
   marked Reviewed.

## Open questions

- Whether the owner later wants the group sections cut down to pass lines only (approach 1): left for a later goal.

VERDICT: self: approach 2, additive table
