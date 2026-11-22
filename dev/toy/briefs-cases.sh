# Sourced by test-delivery-release.sh (case: briefs). DOC-28 and DEL-23 through merge.py and the automatic release.
frz() { python3 - "$1" <<'PY'
import hashlib, sys
text = open(sys.argv[1]).read()
open(sys.argv[1], "a").write("Frozen: %s r1 2026-11-22\n" % hashlib.sha256(text.encode()).hexdigest())
PY
}
BRIEF="python3 $here/skills/workflow-release/scripts/brief.py"

if want briefs; then
  echo "== DOC-28: tasks and release briefs through merge.py and the automatic release"
  git switch -q main; git pull -q origin main; mkdir -p .loop/tasks docs
  printf '# feat\n\nFeature: ZZ-1\nPurpose: p\nKind: feature\n## Done when\n\n1. it works\n' > .loop/tasks/feat.md; frz .loop/tasks/feat.md
  printf '# fixt\n\nFeature: ZZ-1\nPurpose: p\nKind: fix\n## Done when\n\n1. it works\n' > .loop/tasks/fixt.md; frz .loop/tasks/fixt.md
  sed 's/fixt/t/' .loop/tasks/fixt.md | sed '$d' > .loop/tasks/t.md; frz .loop/tasks/t.md
  git add -A; git commit -qm "tasks feat and fixt"; git push -q origin main
  TASK=feat finish ft1; v=$(remote_file VERSION)
  out=$(merge ft1); echo "$out" | tail -2
  grep -q "REFUSED BRF-6" <<<"$out" && [ "$(remote_file VERSION)" = "$v" ] && [ "$(state ft1 release)" != cut ] \
    && ok "DOC-28: merge.py refuses a feature task that no frozen release brief names, and nothing is released" || bad "DOC-28: unnamed feature task"
  git switch -q main; git pull -q origin main
  printf '# v9.9.0\n\n## Tasks\n\n1. feat\n' > docs/release-brief-9.9.0.md; frz docs/release-brief-9.9.0.md
  git add -A; git commit -qm "release brief 9.9.0"; git push -q origin main
  git switch -q loop/ft1; $goal pr ft1 >/dev/null
  out=$(merge ft1); echo "$out" | tail -2
  grep -q "HELD ft1 for its minor cut 9.9.0" <<<"$out" && [ "$(remote_file VERSION)" = "$v" ] && [ "$(state ft1 release)" = merged ] \
    && ok "DOC-28: once a frozen brief names it the feature task merges, held for its minor cut with no release of its own" || bad "DOC-28: named feature task"
  TASK=fixt finish cut1; python3 - "$R/cut1.extra.json" <<'PY'
import json, os, sys
data = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
data.setdefault("set", {})["bump"] = "minor"
json.dump(data, open(sys.argv[1], "w"))
PY
  next=$(bumped "$v" minor)
  out=$(merge cut1); echo "$out" | tail -2
  grep -q "BRF-3" <<<"$out" && [ "$(remote_file VERSION)" = "$v" ] \
    && ok "DOC-28: a minor cut with no frozen release brief is refused" || bad "DOC-28: cut with no brief"
  git switch -q main; git pull -q origin main
  printf '# v%s\n\n## Tasks\n\n1. feat\n' "$next" > docs/release-brief-$next.md; frz docs/release-brief-$next.md
  git add -A; git commit -qm "release brief $next"; git push -q origin main
  git switch -q loop/cut1; $goal pr cut1 >/dev/null
  out=$(merge cut1); echo "$out" | tail -2
  grep -q "BRF-5" <<<"$out" && grep -q "tasks not done: feat" <<<"$out" && [ "$(remote_file VERSION)" = "$v" ] \
    && ok "DOC-28: a minor cut with a named task not done is refused" || bad "DOC-28: cut with open task"
  $BRIEF finish feat --met 1 >/dev/null
  out=$(merge cut1); echo "$out" | tail -2
  [ "$(remote_file VERSION)" = "$next" ] && remote_file CHANGELOG.md | grep -q "task feat" && remote_file docs/release-brief-$next.md | grep -q "^- feat: ft1" \
    && ok "DOC-28: the minor cut releases once every named task is done; the changelog names the task and the brief records its goals" || bad "DOC-28: the cut"
  git switch -q main; git pull -q origin main; git add -A; git commit -qm "tasks done"; git push -q origin main
fi
