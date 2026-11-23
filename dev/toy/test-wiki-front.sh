#!/bin/bash
# reads: skills/workflow-release/scripts/wiki.py skills/workflow-docs/scripts/sections.py skills/workflow-docs/scripts/render.py
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/prdcopy.py skills/workflow-docs/scripts/criteria.py
# reads: skills/workflow-monitoring/scripts/operate.py skills/workflow-setup/scripts/setup.py skills/workflow-docs/scripts/docs.py
# The wiki step's one commit (wiki-commit-front-files): wiki.py prepare --commit commits the README together with the wiki folder when
# the README equals a clean render of the committed tree, leaves it dirty and named when it does not, never reads GitHub in the audit's
# render, and never leaves its throwaway tree behind. Real chain, toy repo and toy origin only; temporary HOME; no network.
# usage: test-wiki-front.sh [CASE[,CASE...]]   CASE: commit nothing foreign retry staged tree term private env stable note order (default: all)
#        TOY_SKILLS=DIR runs the scripts of another checkout (the base export for a red run, or a mutated copy for a negative control).
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH TOY_PROTECT TOY_PR_MODE GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
set -u
here=$(cd "$(dirname "$0")/../.." && pwd); only=${1:-all}
. "$here/dev/toy/reap.sh"
export LOOP_ROLE=worker LOOP_PRIVATE_NAMES=/dev/null
SK=${TOY_SKILLS:-$here/skills}
export HOME=$(mktemp -d); export USERPROFILE="$HOME"
mkdir -p "$HOME/.workflow-loop"; : > "$HOME/.workflow-loop/private-names"
d=$(mktemp -d); export TMPDIR="$d/tmp"; mkdir -p "$TMPDIR"
toy_on_exit 'rm -rf "$d" "$HOME"'
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
want() { if eval "$2" >/dev/null 2>&1; then ok "$1"; else bad "$1"; fi; }
wiki="python3 $SK/workflow-release/scripts/wiki.py"
"$here/dev/toy/make.sh" "$d/base" >/dev/null 2>&1 || { echo "FAIL: toy repo"; exit 1; }
cd "$d/base/repo" || exit 1
python3 "$SK/workflow-setup/scripts/setup.py" --bare >/dev/null 2>&1
git switch -q main; git merge -q --no-edit workflow-setup >/dev/null 2>&1
git remote set-url origin https://github.com/toy-owner/toy-repo.git  # an identity the render can read; nothing here pushes
python3 - <<'PY'
import json
c = json.load(open(".loop/config.json")); c["criteria"] = True
json.dump(c, open(".loop/config.json", "w"), indent=2)
PY
python3 "$SK/workflow-docs/scripts/docs.py" add Toy-notes --paths README.md >/dev/null 2>&1
printf '<!-- workflow-docs -->\n# Toy notes\n\nThe toy is a tiny calculator.\n' > docs/wiki/Toy-notes.md
printf '# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\nta\tland\ttrue\tCAL-1\t2026-01-01\tGiven a, when it runs, then it passes.\tcriterion\t\ntb\tland\ttrue\tCAL-1\t2026-01-01\tGiven b, when it runs, then it passes.\tcriterion\t\n' > .loop/regression.tsv
cat > README.md <<'EOF'
# toy

A tiny calculator.

## 1. Docs

The sentence.

| Requirement | Summary | Follows | Feature | Adoption | Confidence |
|---|---|---|---|---|---|
| [CAL-1 Adds](u) | s | a: adopted | Calc | 100% | 50% (1 of 2) |

<!-- settings:begin -->
OLD SETTINGS
<!-- settings:end -->
EOF
git add -A; git commit -qm "stale README" >/dev/null 2>&1
# a fake gh that answers from $TOY_GH_ANSWER (a TSV of test id and result): the latest full run on main
mkdir -p "$d/shim"
cat > "$d/shim/gh" <<'SH'
#!/bin/bash
if [ "$1 $2" = "run list" ]; then echo '[{"databaseId": 7, "conclusion": "success"}]'; exit 0; fi
if [ "$1 $2" = "run download" ]; then
  while [ $# -gt 0 ]; do [ "$1" = "-D" ] && dest=$2; shift; done
  mkdir -p "$dest/results-x"; cp "${TOY_GH_ANSWER:-/dev/null}" "$dest/results-x/r.tsv" 2>/dev/null; exit 0
fi
exit 1
SH
chmod +x "$d/shim/gh"; export PATH="$d/shim:$PATH"
printf 'ta\tPASS\ntb\tFAIL\n' > "$d/ans1.tsv"; printf 'ta\tPASS\ntb\tPASS\n' > "$d/ans2.tsv"
export TOY_GH_ANSWER="$d/ans1.tsv"
n=0
fresh() { n=$((n + 1)); r="$d/c$n"; mkdir -p "$r"; cp -R "$d/base/repo" "$r/repo"; cd "$r/repo" || exit 1; export TOY_ROOT="$r/repo"; }
tmps() { ls "$TMPDIR" 2>/dev/null | grep -c '^wikifront-'; }
section() { [ "$only" = all ] || case ",$only," in *",$1,"*) true ;; *) false ;; esac; }
prep() { $wiki prepare toy --commit 2>&1; }
commit_only() { python3 -c "import sys;sys.path.insert(0,sys.argv[1]);import sections;sys.exit(sections.commit_wiki(*sys.argv[2:]))" "$SK/workflow-docs/scripts" "$PWD" docs/wiki toy README.md 2>&1; }

if section commit; then fresh
  # Value: protects=a stale README is committed with the wiki pages by the real chain (done line 1); fails_when=the wiki commit takes the folder only; why_new=no toy ran prepare --commit with a stale README; seam=none; no_claim=a real GitHub wiki (toy origin)
  out=$(prep); echo "$out" | grep -q "COMMITTED the wiki pages" ; head=$(git rev-parse HEAD)
  want "the README the audit rewrote is committed and the tree is clean" '[ -z "$(git status --porcelain)" ] && git show --name-only --format=%s HEAD | grep -qx README.md && [ "$(git log -1 --format=%s)" = "Wiki: update pages for toy" ]'
  want "the success line names the README and says it equals a clean render" 'echo "$out" | grep -q "COMMITTED the wiki pages for toy and README.md (equal to a clean render"'
  want "no throwaway tree is left in the temp folder" '[ "$(tmps)" = 0 ]'
fi
if section nothing; then fresh
  prep >/dev/null; head=$(git rev-parse HEAD); out=$(prep)
  want "a second run with nothing stale commits nothing and leaves the tree clean" '[ "$(git rev-parse HEAD)" = "$head" ] && [ -z "$(git status --porcelain)" ] && ! echo "$out" | grep -q "^COMMITTED"'
fi
if section foreign; then fresh
  printf '\nMy own paragraph, written by hand.\n' >> README.md
  out=$(prep); head=$(git rev-parse HEAD)
  # Value: protects=a hand edit is never swept into the generated commit and never lost; fails_when=the commit takes the whole file, or the file is rewritten over the edit; why_new=nothing tested a foreign README edit; seam=none; no_claim=none beyond protects
  want "a README with an edit the render would not make stays dirty, keeps the edit and is named on stdout" 'echo "$out" | grep -q "^WIKI_FRONT_DIRTY: README.md differs from a render of the committed tree, so the wiki commit left it. Fix:" && git status --porcelain | grep -q "^ M README.md" && grep -q "My own paragraph" README.md && [ "$head" = "$(git rev-parse HEAD)" ]'
  commit_only >/dev/null; rc=$?
  want "the commit step exits 1 for it" '[ "$rc" = 1 ]'
fi
if section retry; then fresh
  printf '\nMy own paragraph, written by hand.\n' >> README.md
  prep >/dev/null; python3 - <<'PY'
t = open("README.md").read().replace("\nMy own paragraph, written by hand.\n", "")
open("README.md", "w").write(t)
PY
  out=$(prep)
  want "after the extra edit is removed the next run commits the README (the decision comes from the file, not from the last run)" 'echo "$out" | grep -q "and README.md" && [ -z "$(git status --porcelain)" ]'
fi
if section staged; then fresh
  prep >/dev/null; git reset -q --hard HEAD~1; echo stranger > stranger.txt; git add stranger.txt
  python3 - <<'PY'
t = open("README.md").read().replace("OLD SETTINGS", "OLDER SETTINGS")
open("README.md", "w").write(t)
PY
  git add README.md; python3 - <<'PY'
t = open("README.md").read().replace("OLDER SETTINGS", "OLDEST SETTINGS")
open("README.md", "w").write(t)
PY
  out=$(prep)
  want "a README with staged changes is left dirty and named, and an unrelated staged file stays staged and uncommitted" 'echo "$out" | grep -q "^WIKI_FRONT_DIRTY: README.md has staged changes" && git diff --cached --name-only | grep -qx stranger.txt && ! git show --name-only --format= HEAD | grep -q stranger.txt'
fi
if section tree; then fresh
  prep >/dev/null
  want "the throwaway tree is gone after a normal run and nothing was registered in the shared git folder" '[ "$(tmps)" = 0 ] && [ -z "$(git worktree list | sed 1d)" ] && [ ! -d "$(git rev-parse --git-common-dir)/worktrees" ]'
fi
if section term; then fresh
  mkdir -p skills/workflow-docs/scripts
  printf 'import time\ntime.sleep(60)\n' > skills/workflow-docs/scripts/render.py; git add -A; git commit -qm "slow render" >/dev/null 2>&1
  printf '\nedit\n' >> README.md
  python3 -c "import sys;sys.path.insert(0,sys.argv[1]);import sections;sys.exit(sections.commit_wiki(*sys.argv[2:]))" "$SK/workflow-docs/scripts" "$PWD" docs/wiki toy README.md >/dev/null 2>&1 &
  echo $! > "$d/pid"; for _ in $(seq 100); do [ "$(tmps)" != 0 ] && break; sleep 0.1; done
  seen=$(tmps); kill -TERM "$(cat "$d/pid")"; wait "$(cat "$d/pid")" 2>/dev/null; rc=$?
  # Value: protects=the throwaway tree is removed on a TERM and the repository is untouched; fails_when=cleanup is missing on the signal path; why_new=new temp state; seam=none; no_claim=a hard kill (SIGKILL cannot be caught; the next run sweeps trees older than an hour)
  want "a TERM during the tree render ends with exit 143, removes the tree and leaves the repository as it was" '[ "$seen" = 1 ] && [ "$rc" = 143 ] && [ "$(tmps)" = 0 ] && [ -z "$(git diff --cached --name-only)" ]'
fi
if section private; then fresh
  mkdir -p skills/workflow-docs/scripts
  cat > skills/workflow-docs/scripts/render.py <<'PY'
import os, sys
rep = os.environ["TOY_REPORT"]
with open(rep, "w") as fh:
    for dp, dn, fn in os.walk("."):
        for f in fn:
            fh.write(os.path.join(dp, f) + "\n")
    fh.write(open(os.path.join(".git", "config")).read())
def render(args):
    return 0
PY
  git add -A; git commit -qm "report render" >/dev/null 2>&1; printf '\nedit\n' >> README.md
  export TOY_REPORT="$d/report$n.txt"; commit_only >/dev/null 2>&1
  # Value: protects=the throwaway tree holds no private-name list, mail address or local path; fails_when=the tree copies the checkout's git config or home files; why_new=new temp state; seam=none; no_claim=a scan of every byte of a real repository's history
  want "the tree holds no mail address, no home path, no checkout path and no private-name list" '! grep -q "t@example.test" "$TOY_REPORT" && ! grep -qF "$HOME" "$TOY_REPORT" && ! grep -qF "$TOY_ROOT" "$TOY_REPORT" && ! grep -q "private-names" "$TOY_REPORT"'
fi
if section env; then fresh
  python3 -c "import sys;sys.path.insert(0,sys.argv[1]);import render,argparse;render.render(argparse.Namespace(check=False,keep=True))" "$SK/workflow-docs/scripts" >/dev/null 2>&1
  export GIT_DIR="$d/nowhere" GIT_INDEX_FILE="$d/nowhere.idx" GIT_WORK_TREE="$d/nowhere2"
  commit_only >/dev/null 2>&1; rc=$?; unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE
  # Value: protects=the commit step ignores inherited GIT_* variables; fails_when=a variable redirects a git command in the tree or the checkout; why_new=a linked or exported tree shares the environment; seam=none; no_claim=a variable set by a git hook of another tool
  want "with GIT_DIR, GIT_INDEX_FILE and GIT_WORK_TREE set to decoys the README is still committed in the real repository" '[ "$rc" = 0 ] && [ "$(git log -1 --format=%s)" = "Wiki: update pages for toy" ] && git show --name-only --format= HEAD | grep -qx README.md'
fi
if section stable; then fresh
  # Value: protects=two audit renders on one commit write the same Confidence figure whatever GitHub answers (done line 2); fails_when=the audit's render reads GitHub; why_new=no toy rendered twice; seam=none; no_claim=the real artifact format (a fake gh stands in)
  head=$(git rev-parse HEAD)
  export TOY_GH_ANSWER="$d/ans1.tsv"; prep >/dev/null; one=$(grep "CAL-1" README.md); git reset -q --hard "$head"
  export TOY_GH_ANSWER="$d/ans2.tsv"; prep >/dev/null; two=$(grep "CAL-1" README.md)
  want "two audit renders on one commit give the same figure when the fake gh answers differently" '[ "$one" = "$two" ] && echo "$one" | grep -q "50% (1 of 2)"'
  git reset -q --hard "$head"
  printf 'ta\tFAIL\t2026-11-23\t\t\n' > .loop/regression-runs.tsv; export TOY_GH_ANSWER="$d/ans2.tsv"; prep >/dev/null; three=$(grep "CAL-1" README.md)
  want "a rewrite of the working run data between renders does not move the figure" '[ "$one" = "$three" ]'
  want "keep mode never fetches a missing PRD copy; the default still does (control)" 'python3 - "$SK/workflow-docs/scripts" "$PWD" <<PY
import sys
sys.path.insert(0, sys.argv[1])
import prd, prdcopy
calls = []
prd.read_link = lambda source: calls.append(source) or ("body", None)
off = prdcopy.read(sys.argv[2], "Nope", "url:http://example.invalid/x", True)
assert off == (None, None) and calls == [], (off, calls)
on = prdcopy.read(sys.argv[2], "Nope", "url:http://example.invalid/x")
assert on == ("body", None) and len(calls) == 1, (on, calls)
PY'
  git reset -q --hard "$head"
  python3 -c "import sys;sys.path.insert(0,sys.argv[1]);import render,argparse;render.render(argparse.Namespace(check=False))" "$SK/workflow-docs/scripts" >/dev/null 2>&1
  want "control: the plain docs render still refreshes the figure from GitHub" 'grep "CAL-1" README.md | grep -q "100% (2 of 2)"'
fi
if section note; then fresh
  printf '\nMy own paragraph, written by hand.\n' >> README.md
  out=$(python3 -c "import sys;sys.path.insert(0,sys.argv[1]);import goal;goal.fit.regen(goal.ME,'toy')" "$SK/workflow-delivery/scripts" 2>&1)
  # Value: protects=the pr step shows the dirty-front-file line as its NOTE (the wiki step exits 1, which is what makes fit.regen print its output); fails_when=the line goes to stderr or the step exits 0; why_new=fit.regen prints the wiki output only on a non-zero exit; seam=none; no_claim=the lane refusal that follows in a full goal.py pr (a lane is not run here)
  want "the pr step's regen prints the WIKI_FRONT_DIRTY line in its NOTE" 'echo "$out" | grep -q "^NOTE: stale page: .*" && echo "$out" | grep -q "WIKI_FRONT_DIRTY: README.md differs"'
fi
if section order; then fresh
  # Value: protects=the merge step's head-move test treats a README change inside a generated block as wiki-only and a change outside the blocks as not, so the regen must come before the lane; fails_when=the classifier changes or the README commit lands after the lane; why_new=the order has no test; seam=none; no_claim=a full goal.py pr and merge.py run (their pieces are asserted separately)
  old=$(git rev-parse HEAD)
  python3 - <<'PY'
t = open("README.md").read().replace("OLD SETTINGS", "NEW SETTINGS")
open("README.md", "w").write(t)
PY
  git commit -qam "block only"; mid=$(git rev-parse HEAD)
  sed -i.bak 's/| 100% | 50% (1 of 2) |/| 100% | 100% (2 of 2) |/' README.md; rm -f README.bak; git commit -qam "table cell"; new=$(git rev-parse HEAD)
  op="python3 $SK/workflow-monitoring/scripts/operate.py wiki-only"
  $op "$old" "$mid" >/dev/null 2>&1; a=$?; $op "$old" "$new" >/dev/null 2>&1; b=$?
  want "a README change inside a generated block is wiki-only for the merge step; a change in a table cell is not (HEAD_MOVED), so the front-file commit must precede the lane" '[ "$a" = 0 ] && [ "$b" != 0 ]'
  want "the pr step runs the wiki step (fit.regen) before it starts the pr lane" 'python3 - "$SK" <<PY
import sys
t = open(sys.argv[1] + "/workflow-delivery/scripts/goal.py").read()
body = t.split("def cmd_pr", 1)[1].split("\ndef ", 1)[0]
assert 0 <= body.find("fit.regen(") < body.find("role.lane(state_dir(), slug, \"pr\"")
PY'
fi
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
