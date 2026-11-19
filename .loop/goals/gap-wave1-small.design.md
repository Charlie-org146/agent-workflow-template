# Design: gap-wave1-small

## Problem

Three small gaps between the README and the code (readme-conformance G01, G02, G03). The memory floor defaults to 4 GB (replan.py, lanes_cli.py, file.py, settings.py) and 3.5 GB (board_status.py) in code, while the README says 3 GB. `milestones_source` is read by milestones.py but is not in the settings table, so an adopter's migration check flags it as unknown (#5079); and an adopter's own GitHub image URLs (blob or raw) count as outside the repo for DOC-19 (#5078). A GH_TOKEN or GITHUB_TOKEN in the environment turns writes on in the Automation digest, `regression.py red`, `regression.py run` (not-runnable to-do) and `runs.py owed_record`, though GRD-5.1 says only `--live` writes.

## Approaches

1. One shared constant for the floor, imported by every script. Cost: a cross-skill import (the skills load each other by path), a new helper, and growth in scripts that are within 1,000 bytes of the cap. Risk: high for a one-number fix.
2. Change each literal to 3 (the settings table's default stays the single documented source). Cost: eight one-character edits and one prose line. Risk: low; the repo's own config sets the key, and a machine-local setting still overrides because every reader keeps `cfg.get("min_free_memory_gb", 3)`.

Chosen: approach 2. For G02, add `milestones_source` to the settings table (default empty, opt-in, trimmed help text elsewhere in settings.py to pay for it), validate `url:` or `mcp:<server>:<id>` (`mcp:notion:` needs 32 hex) in `fill_repo`, and keep it out of the migration check's "missing" list like `regression_runs`. In prdcopy.py allow the repo's own image blob/raw URLs (png, jpg, jpeg, gif, svg, webp) in NEAR; source files, issues and other repos' images still fail. For G03, the four sites take only `--live`; the Mac tick already passes `digest --live`.

## What each done line needs

1. 3 GB everywhere: replan.py, lanes_cli.py, file.py (two places), board_status.py (two places), settings.py, plus the Regression how-to line. A row runs the readers with no key (3) and with a key set (the override).
2. `milestones_source` in the table, validated; an own-repo image URL passes DOC-19 and another repo's does not; a bad value is refused.
3. A token with no `--live` writes nothing; `--live` writes. One row with a negative control; the older token rows keep their meaning.
4. No requirement text changes, no new shipped file; every touched script stays under 19,000 LF bytes or does not grow; rows merged so the net is 0 or fewer.

## Open questions

None for the owner. The README's "image" scope for #5078 is read as images only, matching the issue.
