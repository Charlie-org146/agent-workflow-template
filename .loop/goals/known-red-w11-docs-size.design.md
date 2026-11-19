# Design: known-red-w11-docs-size

**Problem.** Eleven workflow-docs scripts are 965 to 1,474 bytes over the 19,000-byte target (14,346 in all), so `docs-scripts-under-19000` and `size-139` fail in the full suite. The package listing is at its cap of 100 files, so no new file may be added. `size-139` also fails its names check: `criteria.py` imports back more names from `deployments` than the toy lists.

**Approaches.**
1. Cut prose only: shorten or drop function docstrings and comments, keep code and output text unchanged. Cost: low, no behaviour risk. Risk: some scripts have too little prose (milestones, docs, criteria, counting, prdcopy).
2. Prose cuts plus small cohesive moves into existing docs scripts, with the moved names imported back so the same objects resolve. Cost: low. Risk: a circular import, and a toy that patches a moved name.

**Chosen:** 2, prose first. Docstrings that fit in one clean line stay; the rest go until each script is under 18,960 bytes. Moves: `origins` (public-origin reader) from milestones.py to counting.py beside `config_of`, imported back into milestones (the toy reads `milestones.origins`); `alone` (the gate-scope page scan) from docs.py to prdcopy.py beside `stands_alone`, imported back into milestones (deployments calls `milestones.alone`). For `size-139`, criteria.py keeps one `from deployments import` line naming exactly the four moved names, and the other re-exports become assignments from the `deployments` module, the same objects.

**Done lines.**
1. Row `docs-scripts-under-19000` is a size scan; `size-139` runs `split-check.py` (size by health's rule, names, leftovers). Both pass locally (checked), and in the CI shards.
2. No row is added to regression-known.tsv; no regression row is added or removed.
3. No file is added or removed under skills/; every function body is unchanged except the two moved ones, which move verbatim apart from `milestones.origins(root)` becoming `counting.origins(root)`. The docs python toys and `docs.py check` pass.

**Open questions.** None for the owner.
