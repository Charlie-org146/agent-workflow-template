#!/bin/bash
# reads: docs/wiki/Documentation.md docs/wiki/Health.md docs/wiki/Automation.md docs/wiki/Setup.md
# reads: .loop/regression.tsv
# Test the milestone-freeform wording and rows: DOC-4, DOC-10, HLT-2, HLT-4, AUT-2, AUT-3 and SET-1 say a milestone is
# optional (Unreviewed after the owner's un-review, or later re-reviewed with the same text), none says an issue or a pull
# request must have one (DOC-10 keeps a standing "Backlog: <Feature>" milestone per feature and HLT-4 puts a defect on no
# milestone), and every other milestone-freeform row has a seen-failing date. usage: test-milestone-wording.sh
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
cd "$here" || exit 1
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }

echo "== the seven requirement lines and the four pages"
out=$(python3 - <<'PY'
import re
pages = {"Documentation": ["DOC-4", "DOC-10"], "Health": ["HLT-2", "HLT-4"], "Automation": ["AUT-2", "AUT-3"], "Setup": ["SET-1"]}
bad = []
for page, ids in pages.items():
    text = open("docs/wiki/%s.md" % page).read()
    head = re.search(r"^Review: (.*)$", text, re.M).group(1)
    if not (head.startswith("**Unreviewed**") or head.startswith("**Reviewed ")):
        bad.append("%s has no Review line" % page)
    for key in ids:
        m = re.search(r"^- %s: (\*\*[^*]+\*\*) (.*?)\n((?:  .*\n)*)" % key, text, re.M)
        if not m:
            bad.append("%s is missing" % key)
            continue
        block = (m.group(2) + "\n" + m.group(3)).lower()
        for phrase in ("every open issue is on", "issue to milestone to feature", "every open issue on a milestone"):
            if phrase in block:
                bad.append("%s says %r" % (key, phrase))
        if key == "DOC-10" and "optional" not in block and "only when i put it there" not in block:
            bad.append("%s does not say a milestone is optional" % key)
        if key == "HLT-4" and "on no milestone" not in block:
            bad.append("%s does not say a defect is on no milestone" % key)
print("; ".join(bad) or "CLEAN")
PY
)
[ "$out" = CLEAN ] && ok "the seven lines say a milestone is optional or not at all, and none says an issue or a pull request must have one" || bad "wording: $out"
[ "$fails" = 0 ] && echo "PASS milestone-freeform:milestone-wording-unreviewed"

echo "== every other milestone-freeform row was seen failing"
f0=$fails
out=$(python3 - <<'PY'
rows = [l.rstrip("\n").split("\t") for l in open(".loop/regression.tsv") if not l.startswith("#")]
want = ["no-milestone-issue-ok", "no-milestone-page-ok", "home-milestone-optional", "pr-no-milestone", "health-file-no-milestone",
        "regression-issue-no-milestone", "digest-no-milestone", "setup-no-milestone-step",
        "milestone-v1-free-form", "milestone-wording-unreviewed"]
have = {r[0]: r for r in rows}
gone = [w for w in want if w not in have]
unseen = [w for w in want if w in have and not have[w][4].strip()]
msg = (["missing " + ", ".join(gone)] if gone else []) + (["no seen_red for " + ", ".join(unseen)] if unseen else [])
print("; ".join(msg) or "CLEAN")
PY
)
[ "$out" = CLEAN ] && ok "the ten other rows exist and each has a seen-failing date" || bad "rows: $out"
[ "$fails" = "$f0" ] && echo "PASS milestone-freeform:milestone-rows-seen-red"
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
