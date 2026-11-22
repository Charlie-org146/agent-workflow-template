# Implement DEL-25: quick checks before every push, no local test lane (v1.1.0 task 5, part 4)

- Slug: v110-fast-checks
- Touches: .pre-commit-config.yaml, skills/workflow-setup, skills/workflow-delivery, dev/toy, .loop/regression.tsv, docs
- ETA: 210 active minutes (estimate 167m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every DEL-25 test case on its page, then each runs as a real test linked to its requirement and passes, and each fails on a fixture that breaks only that rule.
2. Given a push, then the quick checks (lint, the docs check, the private-name scan, the size limits) run through the pre-commit framework within their limit, default 1 minute. No full test lane runs on the machine unless GitHub is unavailable, and generated files are made the same way every time and never rewritten at PR time (DEL-25).
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
