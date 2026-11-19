#!/bin/bash
# windows: ok
# reads: skills/
# reads: skills/workflow-docs/scripts/criteria.py skills/workflow-docs/scripts/docs.py
# reads: skills/workflow-docs/scripts/pageformat.py skills/workflow-docs/scripts/render.py
# reads: skills/workflow-docs/scripts/prd.py skills/workflow-docs/scripts/counting.py skills/workflow-docs/scripts/audit.py
# reads: skills/workflow-docs/references/commands.md skills/workflow-health/scripts/judge.py
# reads: skills/workflow-release/scripts/release.py skills/workflow-release/scripts/wiki.py skills/workflow-release/scripts/merge.py
# reads: skills/workflow-regression/scripts/regression.py
# reads: skills/workflow-setup/scripts/setup.py skills/workflow-setup/scripts/settings.py
# Test the unmigrated-Revisions NOTE (link-form-note, REL-9): with link-form pages plus one migrated local page, the NOTE counts
# only local pages, and the wiki step merge.py runs (wiki.pending) passes; the same fixture on the old code (the two fixes reverted
# in a copy of the scripts) is refused. usage: test-link-form-note.sh [DIR]

set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH  # a toy test never reaches a real session tool
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d)  # setup.py writes the private settings under HOME
export USERPROFILE="$HOME"
export LOOP_OWNER_WORDS='"review it" (the toy owner)'  # review --user with no terminal needs the owner's words
d=${1:-$(mktemp -d)}; rm -rf "$d"; mkdir -p "$d"
"$here/dev/toy/make.sh" "$d" >/dev/null || exit 1
export LOOP_FLOW="$d/flow.json" PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh" PYTHONDONTWRITEBYTECODE=1
unset GH_TOKEN GITHUB_TOKEN
docs="python3 $here/skills/workflow-docs/scripts/docs.py"
cri="python3 $here/skills/workflow-docs/scripts/criteria.py"
prd="python3 $here/skills/workflow-docs/scripts/prd.py"
reg="python3 $here/skills/workflow-regression/scripts/regression.py"
cd "$d/repo" || exit 1
write_howto() { cat > docs/wiki/How-to-use-Delivery.md <<'EOF'
<!-- workflow-docs -->
# How to use Delivery

## What it's for

It prints the median of the numbers given.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| Calculator | Playbook | Median calculation | Ask for a median |

## How to reach or run it

- DEL-1: Ask the agent for the median and read the result.

### Playbook: Calculator

- **Steps:** Give the agent a list and read the median.
- **Templates:** none
- **Stop rules:** Stop on invalid input.

## Links

- PRD page: [Delivery](Delivery)
EOF
}
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
python3 -c "import json; c = json.load(open('.loop/config.json')); c['criteria'] = True; c.pop('criteria_max', None); json.dump(c, open('.loop/config.json', 'w'), indent=2)"
mkdir -p "$FAKE_GH_DIR" docs/wiki skills/toy
printf '## Command map\n\n| Ask | Runs |\n|---|---|\n| `/toy median LIST` | `python3 scripts/calc.py median LIST` |\n' > skills/toy/SKILL.md
printf 'Delivery\tcalc.py\nHome\tREADME.md\n' > .loop/docs.tsv
write_howto
fails=0; day=$(date -u +%F)
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { $docs check 2>&1; }
H=docs/wiki/Home.md; P=docs/wiki/Delivery.md; T=docs/wiki/Tests.md
edit() { python3 - "$1" "$2" "$3" <<'PY'
import sys
p, a, b = sys.argv[1:]
t = open(p).read()
assert a in t, a
open(p, "w").write(t.replace(a, b, 1))
PY
}
cat > $H <<'EOF'
<!-- workflow-docs -->
# Toy

## Features

| Feature | What it does | How to use | Milestone |
|---|---|---|---|
| [Delivery](Delivery) | Prints the median of the numbers given. | [README](https://github.com/toy/repo#how-to-use-delivery) | https://github.com/toy/repo/milestone/1 |
EOF
cat >> README.md <<'EOF'

## How to use

### How to use Delivery

Say these to the agent:

| You say | What happens |
|---|---|
| How do I calculate a median? | [How to use Delivery](https://github.com/toy/repo/wiki/How-to-use-Delivery) |
EOF
cat > $P <<'EOF'
<!-- workflow-docs -->
# Delivery

Review: **Unreviewed**

## Problem

- I want the median of my numbers without working it out by hand.

## Requirements

### Functional

- DEL-1: **Unreviewed** The calculator prints a median.
  - The median of the numbers given is printed.

### Non-functional

- DEL-2: **Unreviewed** It answers quickly.
  - It prints within a second for a short list.

## Non-goals

- No charts.

## Success metrics

- The median is right for every list in the toy run.

## Tests

EOF
$reg add del-1a --level land --command "true" --goal DEL-1 --describe "Given 1 2 3, when the median is asked, then it prints 2." >/dev/null
$reg add del-2a --level land --command "true" --goal DEL-2 --describe "Given a short list, when it runs, then it answers in a second." >/dev/null
$reg run del-1a >/dev/null 2>&1; $reg run del-2a >/dev/null 2>&1
$cri render >/dev/null
git add -A; git commit -qm "Toy pages in the format" >/dev/null
howto() { write_howto
  grep -q '^PRD: ' $P || grep -q '^How to use:' $P || python3 -c "import sys; p = sys.argv[1]; t = open(p).read(); open(p, 'w').write(t.replace('\n## Problem', '\nHow to use: [How-to-use-Delivery](How-to-use-Delivery)\n\n## Problem', 1))" $P; }
reset() { git checkout -q -- .; git clean -qfd docs .loop >/dev/null; howto; }
has() { check | grep -q "$1"; }



echo "== link-form pages plus one migrated local page"
dw=$(cd "$d" && { pwd -W 2>/dev/null || pwd; })
howto
for n in Alpha Beta; do
  low=$(printf %s "$n" | tr A-Z a-z); id=$(printf %s "$n" | cut -c1-3 | tr a-z A-Z)
  printf '# %s PRD\n\n## Requirements\n\n### Functional\n\n- %s-1: **Unreviewed** It does a thing.\n' "$n" "$id" > "$d/$low-prd.md"
  printf '<!-- workflow-docs -->\n# %s\n\nPRD: %s/%s-prd.md\n\nHow to use: [How-to-use-%s](How-to-use-%s)\n\n## Tests\n\n' "$n" "$dw" "$low" "$n" "$n" > docs/wiki/$n.md
  printf '%s\tcalc.py\n' "$n" >> .loop/docs.tsv
  sed -e "s/Delivery/$n/g" -e "s/DEL-1/$id-1/g" docs/wiki/How-to-use-Delivery.md > docs/wiki/How-to-use-$n.md
  printf '| [%s](%s) | It does a thing. | [How to use %s](https://github.com/toy/repo/wiki/How-to-use-%s) | https://github.com/toy/repo/milestone/1 |\n' "$n" "$n" "$n" "$n" >> $H
  $reg add "$low-1a" --level land --command "true" --goal "$id-1" --describe "Given a thing, when it runs, then it is done." >/dev/null
  $reg run "$low-1a" >/dev/null 2>&1
done
python3 - <<'PY'
import glob, re
diagram = ("\n### System diagram\n\n```text\n[Playbook: Calculator | the agent session] --prints--> (the median)\n\n"
           "Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.\n```\n")
for p in glob.glob("docs/wiki/How-to-use-*.md"):
    t = open(p).read()
    if "System diagram" not in t:
        open(p, "w").write(t.replace("\n## How to reach or run it", diagram + "\n## How to reach or run it", 1))
p = "docs/wiki/Home.md"
t = open(p).read()
t = t.replace("\n## Features", "\n<!-- diagram:begin -->\n## System diagram\n\nThe whole toy.\n\n```text\n [Playbook: Calculator | the agent session]\n operation session, worker, step, staging, production, machine, routine, legend, guard\n```\n<!-- diagram:end -->\n\n## Features", 1)
open(p, "w").write(t)
p = "docs/wiki/Delivery.md"
t = open(p).read()
reqs = re.findall(r"^- (DEL-\d+): \*\*Unreviewed\*\* (.*)\n((?:  - .*\n)*)", t, re.M)
rev = "\n## Revisions\n\n" + "".join(
    "### %s\n\n| rev | date | text | why | approved |\n|---|---|---|---|---|\n| r1 | 2026-11-17 | %s | migration r1 | o1: 'reword it' |\n\n"
    % (k, " <br> ".join([txt] + [l.strip()[2:] for l in sub.splitlines()])) for k, txt, sub in reqs)
open(p, "w").write(t.replace("\n## Tests", rev.rstrip("\n") + "\n\n## Tests", 1))
PY
$cri render >/dev/null
git add -A; git commit -qm "Link-form pages and a migrated local page" >/dev/null
$cri review DEL-1 --user >/dev/null
sed -i.bak "s#^del-1a\tland\ttrue#del-1a\tland\tbash gone.sh#" .loop/regression.tsv; rm -f .loop/regression.tsv.bak
$cri render >/dev/null; git add -A; git commit -qm "Reviewed, its test gone" >/dev/null
new="$here/skills"; old=$(mktemp -d)/skills; cp -R "$new" "$old"
python3 - "$old" <<'PY'
import sys
r, c = sys.argv[1] + "/workflow-release/scripts/release.py", sys.argv[1] + "/workflow-docs/scripts/criteria.py"
t = open(r).read(); a = '("UNTESTED", "SKIP", "MILESTONE", "DOCS", "NOTE")'; assert a in t
open(r, "w").write(t.replace(a, '("UNTESTED", "SKIP", "MILESTONE", "DOCS")', 1))
t = open(c).read(); assert "0 < done < local" in t and "(local - done)" in t
open(c, "w").write(t.replace("0 < done < local", "0 < done < len(names)", 1).replace("(local - done)", "(len(names) - done)", 1))
PY
step() { (cd "$d/repo" && python3 -c "
import sys, json
sys.path.insert(0, sys.argv[1] + '/workflow-release/scripts'); sys.path.insert(0, sys.argv[1] + '/workflow-docs/scripts')
import wiki
print('\n'.join(wiki.pending('.', {})))" "$1" 2>&1); }
audit() { (cd "$d/repo" && python3 "$1/workflow-docs/scripts/docs.py" audit --base "" --dry-run 2>&1); }
out=$(audit "$new"); echo "$out"
grep -q "^UNTESTED DEL-1" <<<"$out" && ok "the fixture audit exits non-zero for another reason (an untested Reviewed line)" || bad "fixture has no other trouble: $out"
grep -q "^NOTE Revisions" <<<"$out" && bad "new code: the NOTE still counts link-form pages" || ok "new code: no unmigrated NOTE when every local page is migrated"
grep -q "^NOTE Revisions: 2 page" <<<"$(audit "$old")" && ok "old code counts the 2 link-form pages in the NOTE" || bad "old code gave no NOTE"
got=$(step "$new"); [ -z "$got" ] && ok "new code: the wiki step merge.py runs finds nothing and passes" || bad "new code refused: $got"
got=$(step "$old"); grep -q "^NOTE Revisions: 2 page" <<<"$got" && ok "negative control: the same fixture on the old code is refused by the wiki step" || bad "old code was not refused: $got"
echo
[ "$fails" -eq 0 ] && { echo "ALL PASS"; exit 0; } || { echo "$fails FAILED"; exit 1; }
