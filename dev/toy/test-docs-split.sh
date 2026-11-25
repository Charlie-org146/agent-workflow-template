#!/bin/bash
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
# windows: ok
# reads: skills/workflow-docs/scripts/render.py skills/workflow-docs/scripts/counting.py
# Issue 1402: render.py sat at 97% of the script cap, so the Automation block code (BUILT_IN, config_of, entries,
# automation_block) moved to counting.py unchanged. The block a toy config renders is the text it rendered before
# (dev/toy/docs-split-golden.txt, made from the code before the move). Python only, so it runs the same on Linux,
# macOS and Windows. (Principle 5 retired our own size cap, o988; the package rule is dev/package.py's.)
# Value: protects=render.py stays readable with the Automation block unchanged (issue 1402); fails_when=the block
# output changes or the moved name is no longer the same object; why_new=no other row pins the Automation block
# text; seam=none; no_claim=the Settings block
set -u
d=$(mktemp -d); toy_on_exit 'rm -rf "$d"'
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
S="$here/skills/workflow-docs/scripts"
mkdir -p "$d/.loop" "$d/.github/workflows"
cat > "$d/.loop/config.json" <<'EOF'
{"base": "main", "regression_cron": "off", "digest_mail": "off", "automation": [{"name": "backup", "does": "Copies things.", "cadence": "15 3 * * *", "runs": "mac:com.toy.backup"}, {"name": "report", "does": "Weekly.", "cadence": 7, "runs": "claude:weekly"}]}
EOF
: > "$d/.github/workflows/health.yml"
out=$(python3 - "$S" "$d" "$here/dev/toy/docs-split-golden.txt" <<'PY' 2>&1
import sys
sys.path.insert(0, sys.argv[1])
import counting, render
want = open(sys.argv[3], encoding="utf-8", newline=None).read()
got = counting.automation_block(sys.argv[2])
print("block", got == want)
print("alias", render.config_of is counting.config_of)
PY
)
echo "$out" | grep -qx "block True" && ok "the Automation block a toy config renders is the text it rendered before the move" || bad "block: $out"
echo "$out" | grep -qx "alias True" && ok "render.config_of is counting.config_of" || bad "alias: $out"
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "FAILED $fails"; exit 1; }
