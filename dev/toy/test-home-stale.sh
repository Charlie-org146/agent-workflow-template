#!/bin/bash
# windows: ok
# reads: skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/render.py skills/workflow-docs/scripts/counting.py
# reads: skills/workflow-docs/scripts/pageformat.py skills/workflow-setup/scripts/setup.py
# A generated Home that docs.tsv maps to code (issue 4608): a change to a mapped path leaves it STALE only when its fresh render
# differs, DOC-4 still passes it, and a config value kept on one machine (skip-worktree) never reaches a rendered page.
# usage: test-home-stale.sh [clears|control|kept]   no ID runs every part. No model is called.
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID
here=$(cd "$(dirname "$0")/../.." && pwd); only=${1:-}
. "$here/dev/toy/reap.sh"
d=${TOY_KEEP:-$(mktemp -d)}; [ -n "${TOY_KEEP:-}" ] || toy_on_exit 'rm -rf "$d"'
export HOME="$d/home" PYTHONDONTWRITEBYTECODE=1; mkdir -p "$HOME"
export USERPROFILE="$HOME"
want() { [ -z "$only" ] || [ "$only" = "$1" ]; }
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
docs="python3 $here/skills/workflow-docs/scripts/docs.py"
render="python3 $here/skills/workflow-docs/scripts/criteria.py render"
"$here/dev/toy/make.sh" "$d/toy" >/dev/null || exit 1
cd "$d/toy/repo" || exit 1
git config user.email t@example.test; git config user.name t
mkdir engine; printf 'def run():\n    return 1\n' > engine/core.py; git add -A; git commit -qm "A code folder"
python3 "$here/skills/workflow-setup/scripts/setup.py" >/dev/null 2>&1
git switch -q main && git merge -q --no-edit workflow-setup || { echo "FAIL: setup did not merge"; exit 1; }
H=docs/wiki/Home.md
# Home maps README.md and .loop/config.json; its one feature row is written (no placeholder text), so only staleness is in play
sed -i '/^Home\t/d' .loop/docs.tsv; printf 'Home\tREADME.md,.loop/config.json\n' >> .loop/docs.tsv
sed -i 's/Write this page from what is really in the repo\./The calculator engine./' $H
git commit -qam "Home written and mapped to README and config"
home_lines() { grep -E "^(STALE|UNWRITTEN|MISSING) Home|^FORMAT Home" <<<"$1"; }
[ -z "$(home_lines "$($docs check 2>&1)")" ] && ok "a fresh fixture passes check on Home" || { bad "the fixture's Home is not clean: $(home_lines "$($docs check 2>&1)")"; exit 1; }

# clears: a goal changes README.md, then config.json; Home's render is unchanged, so check says nothing about Home (DOC-4 passes)
if want clears; then
  sed -i 's/A tiny calculator\./A tiny calculator that adds./' README.md; git commit -qam "README text"
  out=$($docs check 2>&1); [ -z "$(home_lines "$out")" ] && ok "a README change with Home's render unchanged leaves Home clear" || bad "Home: $(home_lines "$out")"
  sed -i 's/"criteria": true,/"criteria": true,\n  "max_tries": 3,/' .loop/config.json; git commit -qam "A config key at its default"
  out=$($docs check 2>&1); [ -z "$(home_lines "$out")" ] && ok "a config.json change with Home's render unchanged leaves Home clear" || bad "Home: $(home_lines "$out")"
  grep -q "FORMAT Home" <<<"$out" && bad "DOC-4 fails the generated Home" || ok "DOC-4 still passes the generated Home"
fi

# control: a Home that differs from its fresh render still fails once a mapped path changes
if want control; then
  sed -i 's/"health_cron": "47 \*\/4 \* \* \*"/"health_cron": "off"/' .loop/config.json; git commit -qam "health_cron off, Home not re-rendered"
  out=$($docs check 2>&1)
  grep -q "^STALE Home" <<<"$out" && ok "a Home unlike its fresh render is STALE" || bad "a Home unlike its fresh render passes: $out"
  $render >/dev/null 2>&1; git commit -qm "Home re-rendered" -- $H
  [ -z "$(home_lines "$($docs check 2>&1)")" ] && ok "re-rendering Home clears it" || bad "Home after render: $(home_lines "$($docs check 2>&1)")"
fi

# kept: a value kept with skip-worktree never reaches Home or README (the committed config renders them)
if want kept; then
  git update-index --skip-worktree .loop/config.json
  sed -i 's/"digest_owner": ""/"digest_owner": "KEPTLOCALLY"/' .loop/config.json
  $render >/dev/null 2>&1
  grep -rq KEPTLOCALLY README.md docs/wiki && bad "a kept config value reached a committed page" || ok "a kept (skip-worktree) value never reaches a rendered page"
  git update-index --no-skip-worktree .loop/config.json
  $render >/dev/null 2>&1
  grep -rq KEPTLOCALLY README.md docs/wiki && ok "control: an ordinary config value does reach the page" || bad "control: the value never rendered, so the check above proves nothing"
fi
[ "$fails" = 0 ]
