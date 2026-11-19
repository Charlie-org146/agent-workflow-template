# Plan: requirements-consolidate

Status: the build is done on this branch; what remains is proof.

1. Revisions and retirements: 43 revisions, 8 second revisions, carries (DEL-3, OPS-16, CHK-1), stamps (REL-13, DEL-1), DOC-1 r6, 117 plus 4 retires, all through criteria.py with the named owner records. Done.
2. Repoint rows, tests, How-to items, runbooks and README references to survivors. Done; toys fixed (adoption-golden, automation-budgets, defect, deployments, machine).
3. Merge main (v1.0.87) and table4 (1154ab26). Done; guard OK.
4. Proof: docs.py check, entry.py check, wiki.py prepare, the toy comparison against the base, then the qa lane over the affected regression rows (ask operation-mac first).
5. Hold four Reviewed marks (HLT-2, OPS-1, DOC-2, HLT-4) for operation-top's read; do not mark them on our own.
6. Re-merge the final main after the train; then the pr lane, on operation-mac's go.

Condensed review (owner override): one spec-review round, one plan pass. Findings: no gap against the three done lines; risk is only main moving, handled by re-merge.
