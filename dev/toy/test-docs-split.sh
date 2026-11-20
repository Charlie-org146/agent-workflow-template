#!/bin/bash
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
# windows: ok
# reads: skills/workflow-docs/scripts/render.py skills/workflow-docs/scripts/counting.py
# Issue 1402: render.py sat at 97% of the script cap, so the Automation block code (BUILT_IN, config_of, entries,
# automation_block) moved to counting.py unchanged. The block a toy config renders is the text it rendered before
# (dev/toy/docs-split-golden.txt, made from the code before the move), and render.py and counting.py stay under 90%
# of the cap. Python only, so it runs the same on Linux, macOS and Windows.
# Value: protects=render.py stays readable and under health's size warning with the Automation block unchanged
# (issue 1402); fails_when=render.py or counting.py is over 20,480 bytes or the block output changes;
# why_new=no other row pins the Automation block text or these two sizes; seam=none; no_claim=the Settings block
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
import os, sys
sys.path.insert(0, sys.argv[1])
import counting, render
want = open(sys.argv[3], encoding="utf-8", newline=None).read()
got = counting.automation_block(sys.argv[2])
print("block", got == want)
print("alias", render.config_of is counting.config_of)
for name in ("render.py", "counting.py"):
    size = len(open(os.path.join(sys.argv[1], name), "rb").read().replace(b"\r\n", b"\n"))
    print(name, size <= 20480, size)  # GRD-20 (TD482): over 19,000 warns, only over 20,480 fails
PY
)
echo "$out" | grep -qx "block True" && ok "the Automation block a toy config renders is the text it rendered before the move" || bad "block: $out"
echo "$out" | grep -qx "alias True" && ok "render.config_of is counting.config_of" || bad "alias: $out"
echo "$out" | grep -q "^render.py True " && echo "$out" | grep -q "^counting.py True " \
  && ok "render.py and counting.py are each within the 20,480-byte cap (GRD-20)" || bad "sizes: $out"
python3 "$here/dev/toy/size-check.py" --control "$here/skills/workflow-docs/scripts/render.py" "$here/skills/workflow-docs/scripts/counting.py" >/dev/null \
  && ok "negative control: size-check warns over 19,000, fails at 20,481 and warns at 19,500" || bad "size-check control"
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "FAILED $fails"; exit 1; }
