# A feature whose PRD lives in Notion (or another source) stays in step with its repo page: docs.py sync reports drift and fixes only the repo side

- Slug: external-sync
- Touches: skills/workflow-docs, dev/toy, docs, .loop/regression.tsv

## Done lines

Frozen. A wrong done line needs a new goal.

1. With a feature's PRD source set to an external page, docs.py sync prints DRIFT for a changed requirement, rewrites the repo page to match, and prints not connected with no connector

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. In a scratch git repo, save a PRD file with two lines `- TH-1: **Unreviewed** Reads the sensor` and `- TH-2: **Unreviewed** Alerts above 80`, add `Sensor<TAB>src<TAB>url:/path/to/that/file` to `.loop/docs.tsv`, then run `python3 skills/workflow-docs/scripts/docs.py sync`.
   Expect: `DRIFT Sensor: TH-1 added`, `DRIFT Sensor: TH-2 added`, `SYNCED Sensor`, and `.loop/prd/Sensor.md` lists both.
2. Edit TH-2's text in the PRD file and run `docs.py sync --dry-run`.
   Expect: `DRIFT Sensor: TH-2 changed (...)`, exit 1, and `.loop/prd/Sensor.md` unchanged; run it without `--dry-run` and the copy follows.
3. Change the docs.tsv source to `mcp:notion:abc` and run `docs.py sync` with LOOP_PRD_READER unset.
   Expect: `not connected: Sensor (mcp:notion:abc): ...`, exit 0, nothing rewritten.
