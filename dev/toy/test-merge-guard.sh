#!/bin/bash
# reads: skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/autorelease.py
# reads: skills/workflow-release/scripts/release.py skills/workflow-release/scripts/wiki.py
# reads: skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/lanes.py
# reads: skills/workflow-regression/scripts/narrow.py skills/workflow-delivery/scripts/lanekit.py skills/workflow-regression/scripts/lanes_cli.py dev/toy/fakegh/gh
# reads: skills/workflow-monitoring/scripts/machines.py dev/toy/test-merge-batch.sh
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
# REG-4 (Amendment A1c, V2, E-8): before merging, merge.py refuses when the pull request head moved since the pr lane
# (HEAD_MOVED, exit 4) or the base moved in paths this goal's rows reach (BASE_MOVED, exit 2); a base move elsewhere
# only notes it; a base it can't fetch refuses (BASE_FETCH, exit 3).
# Value: protects=a merge never lands on a base or head its affected rows didn't run on; fails_when=merge.py merges
# without checking pr_head/pr_base or refuses every base move; why_new=merge.py checked only the PR state; seam=none;
# no_claim=GitHub's own merge (fakegh) and the race after the check (documented)
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION
export HOME=$(mktemp -d) PATH="$here/dev/toy/fakegh:$PATH"
export USERPROFILE="$HOME"
# the empty HOME hides any git identity, and a CI runner can't guess one: without these every commit here fails (#4554)
export GIT_AUTHOR_NAME=Toy GIT_AUTHOR_EMAIL=t@example.test GIT_COMMITTER_NAME=Toy GIT_COMMITTER_EMAIL=t@example.test
d=$(mktemp -d); toy_on_exit 'rm -rf "$d" "$HOME"'
export FAKE_GH_DIR="$d/gh"; mkdir -p "$FAKE_GH_DIR"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
git init -q --bare -b main "$d/origin.git"
n="$d/repo"; git clone -q "$d/origin.git" "$n" 2>/dev/null; cd "$n"
mkdir -p src dev .loop
printf 'a\n' > src/a.txt; printf 'b\n' > src/b.txt
printf '#!/bin/bash\n# reads: src/a.txt\ncat src/a.txt\n' > dev/ta.sh  # lanes: no read (toy repo file)
printf '#!/bin/bash\n# reads: src/b.txt\ncat src/b.txt\n' > dev/tb.sh  # lanes: no read (toy repo file)
printf '# id\tlevel\tcommand\nta\tland\tbash dev/ta.sh\ntb\tland\tbash dev/tb.sh\n' > .loop/regression.tsv
git add -A; git commit -qm base; git push -q origin main
base=$(git rev-parse HEAD)
git switch -qc loop/g; echo a2 >> src/a.txt; git commit -qam "goal changes a"; head=$(git rev-parse HEAD)
M="$here/skills/workflow-release/scripts"
moved() {  # STATE-JSON: print "<code>|<line>" from base_moved, or "none"
  python3 - "$M" "$1" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1]); import merge, os
merge.REACH = os.environ.get("REACH_OVERRIDE") or merge.REACH
got = merge.base_moved(json.loads(sys.argv[2]), {"base": "main"}, ".")
print("none" if got is None else "%d|%s" % got)
PY
}
st="{\"slug\": \"g\", \"pr_base\": \"$base\", \"pr_head\": \"$head\"}"
check() { if eval "$2"; then ok "$1"; else bad "$1"; echo "    out: $out"; fi; }
out=$(moved "{\"slug\": \"g\", \"pr_base\": \"\", \"pr_head\": \"$head\"}"); check "a recorded head with no recorded base refuses BASE_MOVED, never merges unchecked (exit 2)" 'grep -q "^2|REFUSED (BASE_MOVED): the base the pr lane ran on was not recorded" <<<"$out"'
out=$(moved "{\"slug\": \"g\"}"); check "a goal from before the base was recorded still merges (nothing to compare)" '[ "$out" = none ]'
out=$(moved "$st"); check "an unmoved base merges" '[ "$out" = none ]'
git switch -q main; echo b2 >> src/b.txt; git commit -qam "base changes b"; git push -q origin main; git switch -q loop/g
out=$(moved "$st"); check "a base move in paths the goal's rows don't reach notes it and merges" 'grep -q "^NOTE: main moved in paths this goal.s rows don.t reach; merging" <<<"$out" && tail -1 <<<"$out" | grep -qx none'
printf 'import sys\nsys.exit("planner crashed")\n' > "$d/crash.py"
out=$(REACH_OVERRIDE="$d/crash.py" moved "$st"); check "a planner that fails can't clear a base move: BASE_MOVED, never merged unchecked (exit 2)" 'grep -q "^2|REFUSED (BASE_MOVED)" <<<"$out"'
out=$(moved "{\"slug\": \"g\", \"pr_base\": \"$(printf 'd%.0s' {1..40})\", \"pr_head\": \"$head\"}"); check "a recorded base git can't diff (missing here) refuses BASE_MOVED (exit 2)" 'grep -q "^2|REFUSED (BASE_MOVED)" <<<"$out"'
git switch -q main; echo a3 >> src/a.txt; git commit -qam "base changes a"; git push -q origin main; git switch -q loop/g
out=$(moved "$st"); check "a base move in a path the goal's rows reach refuses BASE_MOVED with its fix (exit 2)" 'grep -q "^2|REFUSED (BASE_MOVED): main moved in paths this goal.s rows reach (lane on .*, base now .*). Fix: goal.py pr g, then merge.py g" <<<"$out"'
git remote set-url origin "$d/nowhere.git"
out=$(moved "$st"); check "a base that can't be fetched refuses BASE_FETCH and merges nothing (exit 3)" 'grep -q "^3|REFUSED (BASE_FETCH): cannot fetch origin/main: .*nothing merged" <<<"$out"'
git remote set-url origin "$d/origin.git"
# the head check, through merge.py itself
common=$(git rev-parse --git-common-dir); mkdir -p "$common/loop/runs"
printf '{"auto_merge": true, "base": "main"}\n' > .loop/config.json
echo "{\"slug\": \"g\", \"status\": \"done\", \"pr\": \"https://example.test/pull/1\", \"pr_base\": \"$base\", \"pr_head\": \"$head\"}" > "$common/loop/runs/g.json"
out=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=0000000000000000000000000000000000000000 python3 "$M/merge.py" g 2>&1); rc=$?
check "a pull request head that moved since the pr lane refuses HEAD_MOVED with its fix (exit 4), nothing merged" '[ $rc = 4 ] && grep -q "^REFUSED (HEAD_MOVED): the pull request head moved since the pr lane passed (lane on .*, PR head 000000000000). Fix: goal.py pr g, then merge.py g" <<<"$out" && [ ! -e "$FAKE_GH_DIR/merged" ]'
mkdir -p docs/wiki; echo page > docs/wiki/Page.md; git add docs/wiki/Page.md; git commit -qm "wiki page"; wiki=$(git rev-parse HEAD)
out=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$wiki python3 "$M/merge.py" g 2>&1); rc=$?
check "a head moved only by a wiki page commit (wiki.py prepare) is not HEAD_MOVED: it notes it and goes on to the base check" '[ $rc = 2 ] && grep -q "^REFUSED (BASE_MOVED)" <<<"$out" && grep -q "^NOTE: the pull request head moved only by wiki page commits (wiki.py prepare); merging ${wiki:0:12}" <<<"$out"'
git mv src/b.txt docs/wiki/b.md; git commit -qm "move code into the wiki"; moved=$(git rev-parse HEAD)
out=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$moved python3 "$M/merge.py" g 2>&1); rc=$?
check "a file moved into the wiki folder is no wiki-only move: HEAD_MOVED (exit 4)" '[ $rc = 4 ] && grep -q "^REFUSED (HEAD_MOVED)" <<<"$out"'
git reset -q --hard "$wiki"; printf 'x\n' > docs/wiki/SKILL.md; git add docs/wiki/SKILL.md; git commit -qm "skill page"; skill=$(git rev-parse HEAD)
out=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$skill python3 "$M/merge.py" g 2>&1); rc=$?
check "a SKILL.md, even in the wiki folder, is no wiki-only move: HEAD_MOVED (exit 4)" '[ $rc = 4 ]'
git reset -q --hard "$wiki"
ln -s ../../src/a.txt docs/wiki/link.md; git add docs/wiki/link.md; git commit -qm "symlink page"; link=$(git rev-parse HEAD)
out=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$link python3 "$M/merge.py" g 2>&1); rc=$?
check "a symlink named like a wiki page is no wiki-only move: HEAD_MOVED (exit 4)" '[ $rc = 4 ]'
git reset -q --hard "$wiki"
echo x > src/c.txt; git add src/c.txt; git commit -qm code; code=$(git rev-parse HEAD)
out=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$code python3 "$M/merge.py" g 2>&1); rc=$?
check "a head moved by any other commit still refuses HEAD_MOVED (exit 4)" '[ $rc = 4 ] && grep -q "^REFUSED (HEAD_MOVED)" <<<"$out"'
# #5171: --go-head binds a GO to one head and to CI on exactly that head (the PR's rollup is that head's, so a green parent never counts)
echo "{\"slug\": \"g\", \"status\": \"done\", \"pr\": \"https://example.test/pull/1\", \"pr_base\": \"$base\", \"pr_head\": \"$head\"}" > "$common/loop/runs/g.json"
go() { echo "{\"slug\": \"g\", \"status\": \"done\", \"pr\": \"https://example.test/pull/1\", \"pr_base\": \"$base\", \"pr_head\": \"$head\"}" > "$common/loop/runs/g.json"  # a refusal that reopens the goal must not mask the next check
  FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$head FAKE_GH_ROLLUP="$1" python3 "$M/merge.py" g --go-head "${2:-$head}" 2>&1; }
ok1='[{"name":"suite","status":"COMPLETED","conclusion":"SUCCESS"}]'
out=$(go "$ok1" deadbeefdeadbeef); rc=$?
check "a GO for another head refuses GO_HEAD (exit 4), nothing merged" '[ $rc = 4 ] && grep -q "^REFUSED (GO_HEAD): the GO was for deadbeefdead, the PR head is ${head:0:12}" <<<"$out"'
out=$(go "$ok1" abc); rc=$?
check "a GO that names no more than a few characters refuses GO_HEAD (exit 4)" '[ $rc = 4 ] && grep -q "^REFUSED (GO_HEAD)" <<<"$out"'
out=$(go '[{"name":"suite","status":"IN_PROGRESS","conclusion":""}]'); rc=$?
check "a check still running on the head refuses CI_PENDING, naming it (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_PENDING): suite on head ${head:0:12}" <<<"$out"'
out=$(go '[{"name":"suite","status":"COMPLETED","conclusion":"FAILURE"}]'); rc=$?
check "a check red on the head refuses CI_RED, naming it (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_RED): suite on head" <<<"$out"'
out=$(go '[]'); rc=$?
check "a head with no check reported (green only on its parent) refuses CI_MISSING (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_MISSING): no check reported on head" <<<"$out"'
printf '{"required_status_checks": {"checks": [{"context": "suite", "app_id": null}]}}\n' > "$FAKE_GH_DIR/protection.json"
out=$(go '[{"name":"other","status":"COMPLETED","conclusion":"SUCCESS"}]'); rc=$?
check "a required check never reported on the head refuses CI_MISSING, naming it (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_MISSING): suite on head" <<<"$out"'
out=$(go '[{"name":"suite","status":"COMPLETED","conclusion":"SUCCESS"},{"name":"known","status":"COMPLETED","conclusion":"FAILURE"}]')
check "a red check no rule requires does not stop a GO whose required checks are green" '! grep -q "CI_\|GO_HEAD" <<<"$out" && grep -q "BASE_MOVED" <<<"$out"'
rm -f "$FAKE_GH_DIR/protection.json"
out=$(go "$ok1" "${head:0:9}")
check "with every check green on the head, a GO that names it (even shortened) passes the gate" '! grep -q "CI_\|GO_HEAD" <<<"$out" && grep -q "BASE_MOVED" <<<"$out"'
# --go-head discounts rows that are red on main (the known file, or FAIL in main's latest full run), so the gate stays on for every other row
git worktree add -q "$d/mainwt" main; mkdir -p "$d/mainwt/.loop"; printf '# id\treason\nknown-row\tred on main\n' > "$d/mainwt/.loop/regression-known.tsv"
printf '# id\tstatus\tdate\trun\tflaky\nmain-red-run\tFAIL\t2026-11-18\t\t\nfine-row\tPASS\t2026-11-18\t\t\n' > "$d/mainwt/.loop/regression-runs.tsv"
(cd "$d/mainwt" && git add .loop && git commit -qm "main reds" && git push -q origin main); git worktree remove --force "$d/mainwt"; git fetch -q origin
aff='[{"name":"affected","status":"COMPLETED","conclusion":"FAILURE","detailsUrl":"https://example.test/o/r/actions/runs/9/job/777"}]'
log() { printf '%s\n' "$@" | sed 's/^/2026-11-19T01:02:03.4Z /' > "$d/job.log"; export FAKE_GH_JOBLOG="$d/job.log"; }
log "FAIL known-row" "FAIL main-red-run" "PASS fine-row"; out=$(go "$aff")
check "a red check whose only failing rows are known main reds passes the gate, naming the rows and the job log" '! grep -q "REFUSED (CI_\|GO_HEAD)" <<<"$out" && grep -q "^GO_HEAD ok: affected red only on known main reds (known-row, main-red-run); logs: https://example.test/o/r/actions/runs/9/job/777$" <<<"$out"'
log "FAIL known-row" "FAIL brand-new-row"; out=$(go "$aff"); rc=$?
check "negative control: one failing row that is not a main red refuses CI_RED (exit 5), nothing discounted" '[ $rc = 5 ] && grep -q "^REFUSED (CI_RED): affected on head" <<<"$out" && ! grep -q "GO_HEAD ok" <<<"$out"'
log "FAIL known-row"; out=$(go "$aff" deadbeefdeadbeef); rc=$?
check "negative control: a main-red-only run still refuses a GO for another head (GO_HEAD, exit 4)" '[ $rc = 4 ] && grep -q "^REFUSED (GO_HEAD)" <<<"$out"'
out=$(go '[{"name":"affected","status":"COMPLETED","conclusion":"FAILURE","detailsUrl":"https://example.test/o/r/actions/runs/9/job/777"},{"name":"suite","status":"IN_PROGRESS","conclusion":""}]'); rc=$?
check "negative control: a discounted red next to a check still running refuses CI_PENDING (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_PENDING): suite on head" <<<"$out"'
printf '{"required_status_checks": {"checks": [{"context": "affected", "app_id": null}, {"context": "suite", "app_id": null}]}}\n' > "$FAKE_GH_DIR/protection.json"
out=$(go "$aff"); rc=$?
check "negative control: a discounted red with a required check never reported refuses CI_MISSING (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_MISSING): suite on head" <<<"$out"'
rm -f "$FAKE_GH_DIR/protection.json"
unset FAKE_GH_JOBLOG; out=$(go "$aff"); rc=$?
check "negative control: a job log that cannot be read keeps CI_RED (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_RED): affected on head" <<<"$out"'
log "no rows here"; out=$(go '[{"name":"lint","status":"COMPLETED","conclusion":"FAILURE","detailsUrl":"https://example.test/o/r/actions/runs/9/job/778"}]'); rc=$?
check "negative control: a red check whose log names no failing regression row keeps CI_RED (exit 5)" '[ $rc = 5 ] && grep -q "^REFUSED (CI_RED): lint on head" <<<"$out"'
unset FAKE_GH_JOBLOG
printf '#!/bin/bash\n# reads: src/a.txt\ncd "$here" && cat src/a.txt\n' > dev/tc.sh  # lanes: no read (toy repo file)
printf 'tc\tland\tbash dev/tc.sh\n' >> .loop/regression.tsv; touch VERSION; git add -A; git commit -qm "root runner"
out=$(python3 -B "$here/skills/workflow-regression/scripts/lanes_cli.py" affected VERSION; python3 -B "$here/skills/workflow-regression/scripts/lanes_cli.py" affected src/b.txt)
check "a change only to NO_EFFECT files (a release's VERSION) reaches no root runner; a real change still does" 'grep -qx "AFFECTED 0 of 3 rows ()" <<<"$out" && grep -q "^AFFECTED 2 of 3 rows (tb, tc)" <<<"$out"'
# merge batching (merge-queue C): its own toy, folded in here so it adds no regression row
out=$(bash "$here/dev/toy/test-merge-batch.sh" 2>&1 | tail -4); check "merge.py --batch: off by default, one release per batch, a red, conflicting, safety, major or stale-GO case never merges (dev/toy/test-merge-batch.sh)" 'grep -qx "ALL PASS" <<<"$out"'
# #5306: private.py finds lane with no PYTHONPATH, loaded by path as merge.py does, from a checkout and an installed skills copy
cp -r "$here/skills" "$d/inst"
lane_import() { (cd "$d" && env -u PYTHONPATH python3 -B -c 'import importlib.util as u,sys;s=u.spec_from_file_location("private",sys.argv[1]);m=u.module_from_spec(s);s.loader.exec_module(m);import importlib;importlib.import_module("lane");print("LANE OK")' "$1/workflow-delivery/scripts/private.py" 2>&1); }
out=$(lane_import "$here/skills")$(lane_import "$d/inst")
check "private.py pr_result imports lane without PYTHONPATH from a checkout and an installed skills folder (no ModuleNotFoundError)" '[ "$(grep -c "^LANE OK" <<<"$out")" = 2 ] && ! grep -q ModuleNotFoundError <<<"$out"'
# merge queue (REL-13): with a ruleset that requires a queue, merge.py enqueues at the GO'd head with `--auto` and waits; a gh stand-in
# answers the queue calls and passes everything else to the toy's fake gh
Q="$d/q"; mkdir -p "$Q/bin"
cat > "$Q/bin/gh" <<SHIM
#!/bin/bash
echo "\$*" >> "$Q/calls"; st="$Q/state"; s=\$(cat "\$st" 2>/dev/null || echo open)
case "\$1 \$2" in
  "api repos/"*"/rules/branches/main") case "\${QUEUE:-on}" in err) echo boom >&2; exit 1;; on) echo '[{"type": "merge_queue"}]';; *) echo '[]';; esac; exit 0;;
  "pr view") oid="\${HEADNOW:-$head}"; case \$s in merged) echo '{"state": "MERGED", "isInMergeQueue": false, "headRefOid": "'\$oid'"}';;
      queued) echo '{"state": "OPEN", "isInMergeQueue": true, "headRefOid": "'\$oid'"}'; echo merged > "\$st";;
      *) echo '{"state": "OPEN", "isInMergeQueue": false, "headRefOid": "'\$oid'"}';; esac; exit 0;;
  "pr merge") if [[ "\$*" == *--auto* ]]; then [ -n "\${QDROP:-}" ] || echo queued > "\$st"
      else [ "\${QUEUE:-on}" = on ] && { echo "the base branch requires a merge queue" >&2; exit 1; }; echo merged > "\$st"; fi; exit 0;;
esac
exec "$here/dev/toy/fakegh/gh" "\$@"
SHIM
chmod +x "$Q/bin/gh"
land() { rm -f "$Q/calls" "$Q/state"; (export PATH="$Q/bin:$PATH" LOOP_QUEUE_POLL=0.01 LOOP_QUEUE_GRACE=0; python3 - "$M" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1]); import merge
print(merge.land(".", "main", "https://example.test/pull/1", sys.argv[2] or None) or "LANDED")
PY
); }
out=$(QUEUE=on land "$head")
check "a ruleset that requires a queue: one 'pr merge --merge --auto --match-head-commit <head>', never a plain merge, and it waits until the PR is merged" '[ "$out" = LANDED ] && [ "$(grep -c "^pr merge" "$Q/calls")" = 1 ] && grep -qx "pr merge https://example.test/pull/1 --merge --auto --match-head-commit $head" "$Q/calls"'
out=$(QUEUE=on HEADNOW=deadbeefdeadbeefdeadbeef land "$head")
check "a queued PR whose head moved refuses naming both heads" 'grep -q "left the queue: OPEN at deadbeefdead, not ${head:0:12}" <<<"$out"'
out=$(QUEUE=on QDROP=1 land "$head")
check "a queue entry that was dropped (still open, not queued) refuses QUEUE_DEQUEUED instead of waiting forever" 'grep -q "QUEUE_DEQUEUED" <<<"$out"'
out=$(QUEUE=err land "$head")
check "unreadable rules refuse QUEUE_UNREADABLE and merge nothing" 'grep -q "QUEUE_UNREADABLE" <<<"$out" && ! grep -q "^pr merge" "$Q/calls"'
out=$(QUEUE=off land "$head")
check "no queue required: merges directly with --match-head-commit as before, no --auto" '[ "$out" = LANDED ] && grep -qx "pr merge https://example.test/pull/1 --merge --match-head-commit $head" "$Q/calls" && ! grep -q -- "--auto" "$Q/calls"'
rm -f "$Q/calls"; (export PATH="$Q/bin:$PATH" QUEUE=on; gh pr merge https://example.test/pull/1 --merge --match-head-commit "$head" 2>"$Q/err"); rc=$?
check "negative control: the old direct merge fails under a queue ruleset (the case the enqueue path exists for)" '[ $rc = 1 ] && grep -q "requires a merge queue" "$Q/err"'
prot() { (export PATH="$Q/bin:$PATH" QUEUE=$1; python3 - "$M" <<'PY'
import sys
sys.path.insert(0, sys.argv[1]); import autorelease
print(autorelease.protected(".", "main"))
PY
); }
check "a ruleset with only a merge_queue rule is protected, so the release goes through a release pull request, never a direct push" '[ "$(prot on)" = True ] && [ "$(prot off)" = False ]'
printf '{"auto_merge": true, "merge_batch": true, "base": "main"}\n' > .loop/config.json
out=$(export PATH="$Q/bin:$PATH" QUEUE=on; python3 "$M/merge.py" g h --batch 2>&1); rc=$?
check "merge.py --batch under a queue refuses in one line pointing to the queue and merges nothing" '[ $rc != 0 ] && grep -q "^REFUSED: main has a merge queue" <<<"$out" && [ "$(grep -c . <<<"$out")" = 1 ]'
out=$(export PATH="$Q/bin:$PATH" QUEUE=off; python3 "$M/merge.py" g h --batch 2>&1)
check "negative control: a repo with no queue still batches (no queue refusal)" '! grep -q "merge queue" <<<"$out"'
printf '{"auto_merge": true, "base": "main"}\n' > .loop/config.json
# MERGE-TIME (health): the median from a PR's last check to its merge, over the last 20 merges
H="$here/skills/workflow-health/scripts"; mt() { LOOP_HEALTH_MERGES="$1" python3 - "$H" <<'PY'
import sys
sys.path.insert(0, sys.argv[1]); import rules
for r in rules.merge_time("."):
    print(r["state"], r["detail"])
PY
}
mk() { printf '[{"headRefName": "loop/a", "mergedAt": "2026-11-19T10:00:00Z", "statusCheckRollup": [{"completedAt": "2026-11-19T09:50:00Z"}]}, {"headRefName": "loop/b", "mergedAt": "2026-11-19T11:00:00Z", "statusCheckRollup": [{"completedAt": "2026-11-19T10:35:00Z"}]}]' > "$1"; }
mk "$d/m.json"; out=$(mt "$d/m.json")
check "merged PRs whose checks finished 10 and 25 minutes before main: WARN, MERGE-TIME median 18 min (target 15)" '[ "$out" = "WARN MERGE-TIME median 18 min (target 15)" ]'
sed -i 's/10:35:00Z/10:50:00Z/' "$d/m.json"; out=$(mt "$d/m.json")
check "negative control: both merges 10 minutes after the last check stay under the target (INFO, not WARN)" '[ "$out" = "INFO MERGE-TIME median 10 min (target 15)" ]'
out=$(mt "$d/missing.json"); check "data that cannot be read gives UNREAD, never green" '[ "${out%% *}" = UNREAD ]'
mk "$d/m.json"; sed -i 's/^\[/[{"headRefName": "release\/v1.0.1-a", "mergedAt": "2026-11-19T10:08:00Z", "statusCheckRollup": []}, /' "$d/m.json"; out=$(mt "$d/m.json")
check "MERGE-TIME runs to the release: a PR merged at 10:00 and released at 10:08 counts 18 minutes, the release PR itself is not counted (median of 18 and 25 is 22)" '[ "$out" = "WARN MERGE-TIME median 22 min (target 15)" ]'
# DEL-20: the release commit (VERSION and CHANGELOG.md on its parent) is tree-equal modulo stamps, so its pass carries and its queue run is the short path
git switch -q main 2>/dev/null; git checkout -q -b rel "$base" 2>/dev/null || git checkout -q -b rel; printf '1.0.1
' > VERSION; printf '# Changelog
' > CHANGELOG.md; git add VERSION CHANGELOG.md; git commit -qm "Release v1.0.1"
tems() { python3 - "$M" "$1" "$2" <<'PY'
import sys
sys.path.insert(0, sys.argv[1]); import autorelease
print(autorelease.tems(".", sys.argv[2], sys.argv[3]))
PY
}
check "a release commit (VERSION and CHANGELOG.md on its parent) qualifies as a record-only commit: tree equal modulo stamps" '[ "$(tems HEAD~1 HEAD)" = True ]'
echo more >> src/a.txt; git commit -qam "code with the release"
check "negative control: a release commit that also changes code does not qualify" '[ "$(tems HEAD~2 HEAD)" = False ]'
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
