# The folder-trust check fails closed when the trust file can't be read (security patch for GRD-4; fixes #5741; owner o723)

- Slug: trust-fail-closed
- Touches: skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a trust file that is missing, unreadable or unparseable, then untrusted() treats every worktree as untrusted and bind refuses with a plain reason
2. Given a readable trust file that trusts the root, then binds work as after pc-path-trust (negative control)
3. Given the change, then checks green (docs, package, private-name), no existing row turns red, no test loosened, no new file under skills/

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
