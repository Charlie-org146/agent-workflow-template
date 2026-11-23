# Implement DEL-26 and DEL-27: tests on GitHub in parallel, affected-only, and the full set once in the merge queue (v1.1.0 task 5, part 5b)

- Slug: v110-fast-ci-2
- Touches: .github/workflows, skills/workflow-regression, skills/workflow-delivery, dev/toy, .loop/regression.tsv, docs
- ETA: 225 active minutes (estimate 179m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every DEL-26 and DEL-27 test case on its page, then each runs as a real test linked to its requirement and passes, and each fails on a fixture that breaks only that rule.
2. Given a PR, then its tests run on GitHub as parallel jobs within their limits, only the tests the change reaches and never fewer, with unchanged results reused from the cache; a test cut for time or not run fails the checks, naming the test and its time; and nothing private goes to CI (DEL-26, which absorbs #5757 and lanes-on-github-2's design).
3. Given a green PR, then it opens within 1 minute and enters the merge queue at once; the queue runs the full set once on the merged result; green to main takes at most 10 minutes; and a merge never makes another ready PR re-test (DEL-27).
4. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
