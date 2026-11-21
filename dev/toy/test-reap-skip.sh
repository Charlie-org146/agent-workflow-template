#!/bin/bash
# reads: dev/toy/reap.py dev/toy/reap.sh
# TD520: the REAP step where ps is not permitted. usage: test-reap-skip.sh
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }

echo "== the REAP step where ps is not permitted (TD520)"
# A sandbox can forbid ps. reap.py then exits 77 with a named SKIP line and reap.sh ends the test as SKIPPED (77), never as a quiet pass; a ps that
# fails for another reason is still a failure; a reap that finds nothing is a pass.
d=$(mktemp -d); toy_on_exit 'rm -rf "$d"'
mkdir "$d/bin"; printf '#!/bin/sh\necho "ps: Operation not permitted" >&2\nexit 1\n' > "$d/bin/ps"; chmod +x "$d/bin/ps"
out=$(cd "$here/dev/toy" && PATH="$d/bin:$PATH" python3 -c 'import reap; reap.LINUX = False; reap.table()' 2>&1); rc=$?
[ "$rc" = 77 ] && grep -q "^SKIP: REAP: cannot list processes (.*not permitted" <<<"$out" && ok "reap.py: a ps that is not permitted exits 77 with a named SKIP line" || bad "reap.py ps denied: rc=$rc $out"
printf '#!/bin/sh\necho "ps: unknown failure" >&2\nexit 1\n' > "$d/bin/ps"
out=$(cd "$here/dev/toy" && PATH="$d/bin:$PATH" python3 -c 'import reap; reap.LINUX = False; reap.table()' 2>&1); rc=$?
[ "$rc" = 1 ] && grep -q "^REAP: cannot list processes" <<<"$out" && ! grep -q SKIP <<<"$out" && ok "negative control: a ps that fails for another reason is still a failure, not a skip" || bad "reap.py ps broken: rc=$rc $out"
for stub in 77 1 0; do
  printf 'import sys\nsys.exit(%s)\n' "$stub" > "$d/stub$stub.py"
  out=$(TOY_SKIP_FILE="$d/skip$stub" bash -c '. "$1/dev/toy/reap.sh"; _toy_reap_py="$2"; exit 0' x "$here" "$d/stub$stub.py" 2>&1); rc=$?
  case $stub in
    77) [ "$rc" = 77 ] && [ -s "$d/skip77" ] && ok "reap.sh: a test that would pass ends as SKIPPED (77) and writes the skip file when ps is not permitted" || bad "reap.sh stub 77: rc=$rc";;
    1) [ "$rc" = 1 ] && [ ! -e "$d/skip1" ] && ok "negative control: a reap that fails (1) still fails the test, with no skip" || bad "reap.sh stub 1: rc=$rc";;
    0) [ "$rc" = 0 ] && [ ! -e "$d/skip0" ] && ok "negative control: a reap that finds nothing leaves the test a pass" || bad "reap.sh stub 0: rc=$rc";;
  esac
done

[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
