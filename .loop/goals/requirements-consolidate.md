# Make the README's condensed structure real on the feature pages: the 161 requirements consolidate into the 43 of condensed.json, each surviving ID reworded to carry everything it absorbs, the absorbed IDs retired as moved, and the README principles work (readme-principles-table4) carried in the same PR; the last content merge before the v2.0 gate (owner 01:32, 01:36, 01:40; TOP-DECISIONs 89-90).

- Slug: requirements-consolidate
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. For each of the 43 consolidated requirements in condensed.json (copy at the git common dir's loop/condensed.json), the surviving ID gets a new revision whose text is the consolidated text, carrying every absorbed guarantee, number, limit and refusal, with v2.0 and v2.1 items as marked sub-bullets and the why 'consolidation (TOP-DECISION 89)'; one that spans features lives on its primary feature's page with a one-line pointer on the others; SET-1 states that files the template owns install exactly and the repo's own files are adapted, never overwritten, with the SET-1 vs SET-7 conflict marked resolved citing the owner's 01:40 words; reworded requirements land Unreviewed and only a surviving requirement whose text is unchanged keeps its Reviewed mark
2. Each absorbed ID is retired with 'moved to <ID>' and its Revisions history kept, GRD-2 and OPS-13 are retired with their reasons, nothing is deleted and no ID is reused; every regression row, test, doc and README reference that names an absorbed ID points to the surviving ID, no test is dropped, and net regression rows are 0 or fewer
3. It carries readme-principles-table4 as one PR: the README and Principles.md cite the 43 surviving IDs under the six principles, health's principle list and judge mapping are six, the DOC-23 r4 and HLT-2 revisions land Unreviewed, the README check in pageformat.py follows the shape with negative controls; docs, entry, wiki and criteria checks pass; the 43 final texts plus HLT-2 and DOC-23 go to the operation for the owner's one-pass review; it re-merges once onto the final main as the last v2.0 content merge

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: it prints DOCS OK.
2. Run `python3 skills/workflow-docs/scripts/criteria.py guard origin/main requirements-consolidate`.
   Expect: it prints GUARD OK.
3. Open docs/wiki/Home.md and README.md.
   Expect: each lists the 43 requirements under the six principles, and none of the retired IDs (for example GRD-3, DEL-12, OPS-15) appears as live.
4. Open docs/wiki/Regression.md and look up REG-2.
   Expect: it reads "moved to REG-4" and its Revisions history is still there.

