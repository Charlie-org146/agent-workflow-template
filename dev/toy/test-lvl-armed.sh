#!/bin/bash
# reads: skills/workflow-regression/scripts/regression.py .loop/regression.tsv .loop/regression-relevel.tsv .loop/regression-risk.tsv docs/wiki/Principles.md
# v110-lvl-relevel: this repository's table, level record and risk data are valid. usage: test-lvl-armed.sh
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
out=$(python3 "$here/skills/workflow-regression/scripts/regression.py" levels --check 2>&1); code=$?
printf '%s\n' "$out"
if [ "$code" = 0 ] && printf '%s\n' "$out" | grep -q '^valid: '; then
  echo "PASS: every row has a valid level and risk entry"
else
  echo "FAIL: the table, the record or the risk data is not valid (exit $code)"
  exit 1
fi
