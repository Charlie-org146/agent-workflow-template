# Full-auto approval never answers an owner-words PENDING line, and min_free_memory_gb is registered once

- Slug: guard-fixes
- Touches: skills/workflow-delivery/scripts/auto.py, skills/workflow-setup/scripts/settings.py, .loop/config.json, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. auto.py full_auto skips any PENDING line that asks for owner words (a reviewed page or requirement change, or a criteria_max raise) and leaves it waiting for an owner-words record, with a toy case proven red (#4287)
2. min_free_memory_gb is in the settings registry and this repo's .loop/config.json holds the key exactly once, at 3.5 (#4048, first half; the registry already lists it with shipped default 4, which this goal leaves as is)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
