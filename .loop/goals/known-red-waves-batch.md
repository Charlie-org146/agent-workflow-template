# One PR carries the ready file-disjoint known-red waves w1-migration (#5132), w3-deploy-links (#5133) and w6-pods-machine (#5134), plus three newly visible main reds, so they cost one CI and one merge (TOP-DECISION 71; owner: "No waivers u can do it").

- Slug: known-red-waves-batch
- Touches: not declared
- ETA: 270 active minutes (estimate 215m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards: migration-blocks-inserted migration-clean migration-flags migration-gaps-pr migration-gaps-state migration-major-refused migration-robustness migration-v1 migration-writes-nothing deploy-doc14-reviewed deploy-not-locked deploy-section-optional deploy-table-refused deployments-counts-pages home-topic-column link-page-passes link-unread-never-pass del-16-on-page pods-independent pods-lock pods-owner mon15-merge-lock mon15-pod-owner machine-apply-installs machine-done-7 machine-windows plan-cache-key home-guard-catches-leak home-howto-linksonly plan-identity
2. doc19-readme-links stays removed from .loop/regression.tsv with its evidence (DOC-5 retired into DOC-18; frontdoor() now DOC-23; format-frontdoor keeps coverage)
3. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main; scripts stay under their size caps (narrow.py and merge.py under 19,000)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `bash dev/toy/test-migration.sh clean | tail -1; bash dev/toy/test-deployments.sh | tail -1; bash dev/toy/test-docs-link.sh | tail -1`.
   Expect: each last line is `ALL PASS`.
2. Run `bash dev/toy/test-pods.sh layers twopods | tail -1; bash dev/toy/test-pods.sh lock | tail -1; bash dev/toy/test-pods.sh owner | tail -1`.
   Expect: each last line is `ALL PASS`.
3. Run `bash dev/toy/test-docs-format.sh | tail -1; bash dev/toy/test-plan-cache.sh identity | tail -1; bash dev/toy/test-plan-cache.sh key | tail -1`.
   Expect: each last line is `ALL PASS`.
4. Run `python3 skills/workflow-docs/scripts/docs.py check | tail -1; wc -c skills/workflow-regression/scripts/narrow.py skills/workflow-release/scripts/merge.py`.
   Expect: `DOCS OK: 16 pages`, and both files under 19,000 bytes.
