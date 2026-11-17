# HLT-3: The health report prints findings as one table with a feature column, and every finding and filed issue is linked to a feature (#4658, owner o73)

- Slug: health-feature-table
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a health run with findings from at least three groups, when the report prints, then findings are one table with feature, group, rule, severity, finding and issue columns, every row naming a feature page or Other, and the digest shows the same table
2. Given findings filed by health.py file, when issues are created or updated, then each carries its feature label whatever feature_labels says, and a finding with no feature is filed under Other
3. The Health page's requirements state the table layout and the always-on feature link (HLT-3 and HLT-4), with a test row for each, and the new wording goes to the owner for review; nothing is marked Reviewed without the owner's words

## Verify by hand

<!-- Numbered steps a person can follow, each with an Expect: line. -->

1. In a clone of this repo, run `python3 skills/workflow-health/scripts/health.py check`.
   Expect: right after the `groups run:` line, a `FINDINGS (N)` line and one table with the columns Feature, Group, Rule, Severity, Finding and Issue; every Feature cell is a wiki page name or Other, sorted by feature with Other last.
2. Run `python3 skills/workflow-health/scripts/health.py preview --group size` with `feature_labels` false in `.loop/config.json`.
   Expect: every WOULD line's tags include `feature:<Page>` or `feature:Other`.
3. After the next scheduled health round, open the pinned Automation digest issue's newest comment.
   Expect: a `### Findings` section with the same table, each issue number a link, and the per-feature sections titled by page or Other (never "No feature").
