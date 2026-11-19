# Health is green on main for the v2.0.0 gate: every requirement reference resolves, the known traceability gaps are closed, the SKILL.md files fit, and the caps are set for v2.0 (TOP-DECISION 37)

- Slug: v2-health-green
- Touches: docs/wiki/Roadmap.md, docs/wiki/Delivery.md, docs/wiki/Documentation.md, docs/wiki/Guardrails.md, docs/wiki/Health.md, docs/wiki/Home.md, docs/wiki/Check-in-and-board.md, docs/wiki/How-to-use-Documentation.md, docs/wiki/Integrations.md, docs/wiki/Monitoring.md, docs/wiki/Regression.md, docs/wiki/Automation.md, docs/wiki/Tests.md, skills/workflow-monitoring/SKILL.md, skills/workflow-release/SKILL.md, skills/workflow-monitoring/references, skills/workflow-release/references, .loop/regression.tsv, .loop/config.json, skills/workflow-health/scripts/defects.py
- ETA: 225 active minutes (estimate 178m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Every requirement reference on the wiki and PRD pages names a requirement some page defines. The 32 health consistency fails on main 43c410ef (16 IDs: GRD-14 x6; DOC-7, DOC-17 x3; GRD-11, DOC-9, DOC-5, DEL-8, DEL-6, DEL-11, DEL-10 x2; GRD-13, DOC-8, DEL-5, DEL-15, DEL-13, AUT-8 x1) are each repointed to the requirement's current home or removed; only the reference changes, recorded as revisions under o194 where a requirement's text holds it; no other wording change.
2. #4557 has its defect test (regression.py add --category defect --link #4557, seen red first), and row quiet-plain-import-4892 points at the requirement it really guards, or is removed if it guards nothing.
3. skills/workflow-monitoring/SKILL.md (151) and skills/workflow-release/SKILL.md (150) are under 150 lines, with detail moved to references/.
4. .loop/config.json has max_suite_seconds 2800 and criteria_max 23 (TOP-DECISION 37), and health.py check prints 'HEALTH: green' on the branch. Two v2.1 issues are filed: the suite back under 1900 seconds, and requirements merged back to 19 per page.
5. Nothing else; net test rows at most +1.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
