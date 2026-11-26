#!/bin/bash
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
# windows: ok
# reads: dev/package.py
# Issue 3125: a Windows CRLF checkout gets the same package verdict as Linux. A script under the marketplace's
# per-script rule in LF bytes, and over it with CRLF on disk, is judged by its LF bytes in package.py's Scripts rule.
# (Principle 5 retired health's own size and skill-lines rules, o988.)
# Value: protects=the package check agrees between Windows and Linux (issue 3125); fails_when=the package rule
# reads the CRLF working tree; why_new=no row wrote CRLF files before judging them; seam=none;
# no_claim=a real Windows checkout
set -u
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
out=$(python3 - "$here" <<'PY' 2>&1
import os, sys, tempfile
here = sys.argv[1]
sys.path.insert(0, here + "/dev"); import package
root = tempfile.mkdtemp()
def put(rel, text):
    path = os.path.join(root, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as h: h.write(text.replace("\n", "\r\n").encode())
put("skills/x/scripts/a.py", "x = 1\n" * 3350)             # 20,100 LF bytes, 23,450 with CRLF
package.failures.clear(); package.fail = lambda rule, text: package.failures.append((rule, text))
package.check_scripts(root, ["skills/x/scripts/a.py"])
print("package", [f for f in package.failures if "bytes" in f[1]] == [])
PY
)
echo "$out" | grep -qx "package True" && ok "package.py's Scripts rule reads LF bytes of a CRLF file" || bad "package: $(echo "$out" | tail -3)"
[ "$fails" = 0 ] && echo "ALL PASS"
exit $((fails != 0))
