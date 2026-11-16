# Plan: test-caps

Built against the design: settings.py (two settings, defaults 1200 rows and 1900 s: the template passes today at 1037 rows), lean.py (rows-cap, suite-cap with the cap helper), controls.py (f_caps, one fixture for both), report.py and health.py (registered under Performance), file.py (suite-cap shown, never filed), role.py (over_caps at qa through need_lane), commands.md, GRD-13 on the Guardrails page (page re-reviewed under o51; GRD-13 itself unreviewed: the record does not cover its ID), toy dev/toy/test-test-caps.py (15 checks), six rows seen red.

## Tests
qa refusal with rows and seconds; consolidation allowed (net 0 or less); own cap can't be raised, base cap read; health pass, warn at 90%, fail over, 0 off; controls fire; settings exist.

## What could break
Scripts near 19,000 bytes (all under); the suite-seconds reading is this machine's recorded full run, so on a machine with none it is not measured (the qa gate then enforces rows only).

## Out of scope
The consolidation pass that brings the template under tighter caps.

PENDING: none
