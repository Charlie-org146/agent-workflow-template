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
