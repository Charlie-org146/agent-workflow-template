#!/bin/bash
# reads: dev/toy/test-operate.sh
# The operate loop under load (issue 5478 follow-up, TD442): starts one busy loop per CPU, each of which dies with this script even on
# SIGKILL (it checks its parent), then runs dev/toy/test-operate.sh with TOY_GROUP=loop (the polling sections and the operate-loop
# section: the loop starts a batch line by itself, prints the live board on its cadence, wakes on a report, prints a change, starts
# the goal that waited, and ends when nothing is left) 2 times, one after the other, and requires ALL PASS from each, with no retry.
# Negative control: an agent that reports after 20 s with a patience of 2 s must fail the group, so a slowed loop is seen.
# usage: test-operate-loop-load.sh [RUNS]
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
runs=${1:-2}
cpus=$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 2)
me=$$
out=$(mktemp -d)
for _ in $(seq "$cpus"); do (while kill -0 "$me" 2>/dev/null; do :; done) & done
toy_on_exit 'kill $(jobs -p) 2>/dev/null; rm -rf "$out"'
passed=0
for i in $(seq "$runs"); do
  last=$(TOY_GROUP=loop bash "$here/dev/toy/test-operate.sh" "$out/run$i" 2>&1 | tail -1)
  [ "$last" = "ALL PASS" ] && passed=$((passed + 1)) || echo "run $i FAILED: $last"
done
echo "operate loop under load ($cpus busy loops): $passed of $runs passed"
last=$(FAKE_AGENT_DELAY=20 TOY_PATIENCE=2 TOY_GROUP=loop bash "$here/dev/toy/test-operate.sh" "$out/slow" 2>&1 | tail -1)
[ "$last" != "ALL PASS" ] && echo "negative control: an agent slower than the patience fails the operate loop ($last)" || { echo "FAIL: negative control: the loop passed though the agent was slower than the patience"; exit 1; }
[ "$passed" = "$runs" ] && echo "ALL PASS" || exit 1
