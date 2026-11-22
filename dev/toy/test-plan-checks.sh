#!/bin/bash
# reads: dev/toy/test-plan-levels.sh dev/toy/test-plan-parallel.sh dev/toy/test-plan-board.sh
# DEL-22.1, 22.2, 22.3, 22.5 and done line 7 in one script (one regression row, REG-4): it runs the levels, parallel and board toys, each in its own
# temp HOME and TMPDIR (removed at the end), and passes only if every one of them EXITS 0 and its last stdout line is ALL PASS (stderr is kept apart,
# so a stray line there cannot turn a pass red). Their PASS lines (rules, controls, sizes) are repeated here so the row's check can name them.
# usage: test-plan-checks.sh
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
fails=0
for t in levels parallel board; do
  out=$(bash "$here/dev/toy/test-plan-$t.sh" 2>/dev/null); rc=$?
  printf '%s\n' "$out" | grep -E '^(PASS|FAIL|NOTE)'
  if [ "$rc" = 0 ] && printf '%s\n' "$out" | tail -1 | grep -qx "ALL PASS"; then echo "PASS: test-plan-$t.sh exited 0 and printed ALL PASS"; else echo "FAIL: test-plan-$t.sh exit $rc, last line: $(printf '%s\n' "$out" | tail -1)"; fails=$((fails + 1)); fi
done
[ "$fails" = 0 ] && echo "ALL PASS" || echo "$fails FAILED"
[ "$fails" = 0 ]
