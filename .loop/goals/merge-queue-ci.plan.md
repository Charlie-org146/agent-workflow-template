# merge-queue-ci plan

Checked against code: NARROW (lanes_cli.py) is the template `regression.py workflow` writes to regression-pr.yml; `ls-narrow-triggers` (.loop/regression.tsv) runs `test-local-schedule.sh triggers`, whose check builds the file in a toy and greps it.

Steps:
1. lanes_cli.py NARROW: add `merge_group:` with `types: [checks_requested]` under `pull_request:`; shorten the MATRIX_JOB comment so the file ends smaller than main (18,662 vs 18,674 LF bytes).
2. Regenerate .github/workflows/regression-pr.yml with `regression.py workflow`; keep only that file's change (regression.yml untouched).
3. test-local-schedule.sh `triggers` check: assert merge_group and its types, no `ref:` override on checkout (github.sha is used), and a negative control: a copy with merge_group stripped fails the assertion.

Done-line tests: all three live in the existing ls-narrow-triggers row (net rows 0). Before the change the merge_group greps fail; after, they pass.

Could break: pull_request behaviour (unchanged, template lines only added); concurrency group uses github.ref, unique per merge-group ref. Out of scope: merge.py and the queue itself (goal merge-queue), rulesets, requirement text.
