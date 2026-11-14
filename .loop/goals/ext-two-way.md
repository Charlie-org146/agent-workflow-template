# A feature's PRD can be changed on either side, in the repo by an agent's goal or in the external document by people, and the two always say the same: docs.py sync names each difference as a DELTA, posts it for review as a GitHub issue and a comment on the external page, writes only the accepted text to the other side, and health and the check-in show open deltas as inconsistencies

- Slug: ext-two-way
- Touches: skills/workflow-docs, skills/workflow-health, skills/workflow-monitoring, dev/toy, docs, README.md, .loop/regression.tsv

## Done lines

Frozen. A wrong done line needs a new goal.

1. With a requirement changed on only one side, docs.py sync prints a DELTA naming the page, the ID, which side changed and both texts, and overwrites neither side
2. docs.py sync posts each delta once as a GitHub issue on the feature's milestone and once as a comment on the external page, and prints not connected, never failing, when it has no connector
3. docs.py sync --accept PAGE:ID=repo or =source writes only that side's text to the other side, Notion included, closes the delta and leaves every other requirement as it was
4. Health and the check-in list each open delta as an inconsistency

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. In a scratch git repo make a PRD file with `- TH-1: **Unreviewed** Reads the sensor` and `- TH-2: **Unreviewed** Alerts above 80`, add `Sensor<TAB>src<TAB>url:/path/to/that/file` to `.loop/docs.tsv`, and run `python3 skills/workflow-docs/scripts/docs.py sync`.
   Expect: `SYNCED Sensor` and a copy in `.loop/prd/Sensor.md` beside `Sensor.base`, no DELTA.
2. Edit TH-1 in the copy and TH-2 in the PRD file, then run `docs.py sync --dry-run`.
   Expect: `DELTA Sensor: TH-1 the repo changed (repo: ... | source: ...)`, `DELTA Sensor: TH-2 the source changed (...)`, exit 1, both files unchanged and nothing posted.
3. Run `docs.py sync` with `LOOP_GH` and `LOOP_PRD_WRITER` set to commands that print their arguments, then `docs.py sync --open`.
   Expect: one issue and one comment per delta, the same two DELTA lines from `--open` with their issue links, and a second sync posts nothing more.
4. Run `docs.py sync --accept Sensor:TH-2=source`, then `--accept Sensor:TH-1=repo`.
   Expect: `ACCEPTED Sensor: TH-2` (the copy now has the document's text) and `ACCEPTED Sensor: TH-1` (the writer was asked to `replace TH-1`), each issue closed, and a final sync shows no DELTA.
5. Run `docs.py sync` in a repo whose `.loop/docs.tsv` has no `url:` or `mcp:` source.
   Expect: `NO EXTERNAL PRDS`, exit 0, and no health row or board item about deltas.
