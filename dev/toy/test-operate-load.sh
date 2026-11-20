#!/bin/bash
# reads: dev/toy/test-operate.sh
# Issue 99: the operate-all toy suite's polling sections pass 10 of 10 under load. Starts one busy loop per CPU, each of which dies
# with this script even on SIGKILL (it checks its parent), then runs dev/toy/test-operate.sh with TOY_GROUP=timing (the sections that
# poll: waits, status, reports, follow-up, worker guard; what a busy machine slows) 10 times, in two streams of five (each run in its
# own directory; about 10 s a run even under load), and requires ALL PASS from every run, with no retry. The whole suite is checked unloaded by the operate-all row; ten whole runs one after
# the other took about 25 minutes under load, past the row limit (issue 5478). Negative control: with an agent that reports after 20 s and
# a patience of 2 s the waits give up and the group must not pass. usage: test-operate-load.sh [RUNS]
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
runs=${1:-10}
cpus=$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 2)
me=$$
out=$(mktemp -d)
for _ in $(seq "$cpus"); do (while kill -0 "$me" 2>/dev/null; do :; done) & done
toy_on_exit 'kill $(jobs -p) 2>/dev/null; rm -rf "$out"'
stream() { for i in $(seq "$1" 2 "$runs"); do TOY_GROUP=timing bash "$here/dev/toy/test-operate.sh" "$out/run$i" 2>&1 | tail -1 > "$out/last$i"; done; }
stream 1 & first=$!
stream 2 & second=$!
wait "$first" "$second"  # the two streams only: the busy loops end with this script
passed=0
for i in $(seq "$runs"); do
  if grep -qx "ALL PASS" "$out/last$i"; then passed=$((passed + 1)); else echo "run $i FAILED: $(cat "$out/last$i")"; fi
done
echo "operate-all under load ($cpus busy loops): $passed of $runs passed"
last=$(FAKE_AGENT_DELAY=20 TOY_PATIENCE=2 TOY_GROUP=timing bash "$here/dev/toy/test-operate.sh" "$out/impatient" 2>&1 | tail -1)
[ "$last" != "ALL PASS" ] && echo "negative control: an agent slower than the patience fails the polling sections ($last)" || { echo "FAIL: negative control: the group passed though the agent was slower than the patience"; exit 1; }
[ "$passed" = "$runs" ] && echo "ALL PASS" || exit 1
