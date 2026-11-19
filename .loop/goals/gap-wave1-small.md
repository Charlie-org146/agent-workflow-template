# Three README gaps close: the memory floor defaults to the README's 3 GB in code (a machine may still set its own locally, GRD-12); adopted repos get the milestones_source setting and their own-repo links (#5079, #5078); and a token in the environment never enables writes, only --live does (GRD-5.1) (TOP-DECISION 135, readme-conformance G01, G02, G03)

- Slug: gap-wave1-small
- Touches: skills/workflow-monitoring/scripts/replan.py, skills/workflow-monitoring/scripts/board_status.py, skills/workflow-regression/scripts/lanes_cli.py, skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/runs.py, skills/workflow-health/scripts/file.py, skills/workflow-health/scripts/automation.py, skills/workflow-health/scripts/defects.py, skills/workflow-setup/scripts/settings.py, skills/workflow-setup/references/settings.md, skills/workflow-docs/scripts/prdcopy.py, docs/wiki/Home.md, docs/wiki/How-to-use-Regression.md, docs/wiki/Tests.md, .loop/START.md, dev/toy/test-automation.sh, dev/toy/test-automation-email.sh, dev/toy/test-gap-wave1.py, dev/toy/break-gap-wave1.py, .loop/regression.tsv
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The code's memory-floor default is 3 GB everywhere (no 4 or 3.5 left as a default), a machine-local setting still overrides it, and a row proves both
2. An adopted repo has a milestones_source setting and its wiki and README links point at its own repo, not the template, each with a negative control (#5079, #5078)
3. A GH_TOKEN or similar token in the environment never turns on writes; only --live does, proven by a row with a negative control (GRD-5.1)
4. No requirement text changes, no new shipped file, every touched script stays under 19,000 bytes or does not grow, net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. In a repo with no `min_free_memory_gb` in `.loop/config.json`, run `python3 skills/workflow-setup/scripts/settings.py show` and look at the `min_free_memory_gb` row.
   Expect: the value is 3 and the layer is default; setting the key to 5 in the config shows 5 with the layer repo.
2. Put `"milestones_source": "mcp:notion:abc"` in `.loop/config.json` and run `python3 skills/workflow-setup/scripts/settings.py fill-repo`.
   Expect: REFUSED, naming `mcp:notion:<32 hex>`; with 32 hex digits after `mcp:notion:` it fills without complaint, and the health migration check does not list milestones_source as unknown.
3. Add a line to a wiki page with an image from this repo, `https://github.com/<owner>/<repo>/blob/main/docs/a.png?raw=true`, and run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: no LINKS finding for it; the same image path under another repo's name, or a `.py` file link, is still a LINKS finding.
4. With `GH_TOKEN=x` set and no `--live`, run `python3 skills/workflow-health/scripts/automation.py digest`.
   Expect: the comment prints and then `DRY RUN: no --live, so nothing was posted.`, and no gh call writes anything; with `--live` it posts.
5. Run `wc -c` on the ten edited scripts after turning CRLF to LF.
   Expect: each is at or under 19,000 bytes, and `.loop/regression.tsv` holds as many rows as on main.
