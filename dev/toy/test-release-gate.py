#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/review.py skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/release.py docs/wiki/Release.md
"""release-gate (REL-1 to REL-8, issue 4914): a major ships only through `review.py gate`; `promote` tags vX.0.0, keeps release/vX,
writes the state report and mails it; a cut rc freezes the merge; `revert` opens a pull request back to the snapshot; a goal never
bumps a major; the Release page holds REL-1 to REL-8, Unreviewed; the scripts stay under their size caps.

Builds a throwaway repo with a bare origin; gh, the suite, health, the docs audit and the mail are stood in for inside this
process (no network). usage: test-release-gate.py [issues|rows|checks|owner|promote|revert|freeze|major]  (one leg: only its checks decide the exit)"""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
fails = 0
LEG = sys.argv[1] if len(sys.argv) > 1 else ""


def check(name, ok, extra="", leg="issues"):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok or (LEG and LEG != leg) else 1


def git(*args, cwd=None):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=cwd or repo, capture_output=True, text=True)


tmp = tempfile.mkdtemp(prefix="release-gate-")
origin, repo = os.path.join(tmp, "origin.git"), os.path.join(tmp, "repo")
git("init", "-q", "--bare", "-b", "main", origin, cwd=tmp)
git("clone", "-q", origin, repo, cwd=tmp)
os.makedirs(os.path.join(repo, ".loop", "goals"))
os.makedirs(os.path.join(repo, "docs", "wiki"))
config = os.path.join(repo, ".loop", "config.json")
open(config, "w").write('{"auto_merge": true, "base": "main"}\n')
open(os.path.join(repo, ".loop", "docs.tsv"), "w").write("Page\tfoo.txt\n")
page = os.path.join(repo, "docs", "wiki", "Page.md")
GOOD = "## Requirements\n\n- PG-1: **Reviewed 2026-11-01** one\n  - a\n- PG-2: **Reviewed 2026-11-01** two\n  - b\n"
open(page, "w").write(GOOD)
open(os.path.join(repo, "foo.txt"), "w").write("a\n")
git("add", "-A"); git("commit", "-q", "-m", "base"); git("push", "-q", "origin", "main")
base = git("rev-parse", "HEAD").stdout.strip()
git("switch", "-q", "-c", "staging"); open(os.path.join(repo, "foo.txt"), "a").write("rc\n")
git("commit", "-q", "-am", "the rc build"); git("push", "-q", "origin", "staging")
rc = git("rev-parse", "HEAD").stdout.strip()
git("switch", "-q", "main")
common = os.path.abspath(os.path.join(repo, git("rev-parse", "--git-common-dir").stdout.strip()))
os.makedirs(os.path.join(common, "loop", "runs"), exist_ok=True)
owner_file, waiver_file = (os.path.join(common, "loop", n) for n in ("owner-words.tsv", "release-waivers.tsv"))


def owner(*rows):
    open(owner_file, "w").write("".join("\t".join(r) + "\n" for r in rows))


def waive(*rows):
    open(waiver_file, "w").write("".join("\t".join(r) + "\n" for r in rows))


import merge  # noqa: E402
import release  # noqa: E402
import review  # noqa: E402

merge.pods = None
real_run = subprocess.run
OPEN, CLOSED, calls, tip, merged = [], [{"number": 3, "title": "done thing"}], [], [rc], []
SUITE = ["PASS a", "PASS b"]
HEALTH = ["HEALTH: green"]
DOCS = []
MAIL = [""]
review.run_in = lambda work, script, *args: "\n".join(SUITE if "regression" in script else HEALTH)
release.docs_trouble = lambda *a, **k: list(DOCS)
review.email = lambda top, subject, text: (calls.append(("mail", subject)), MAIL[0])[1]


def fake_run(args, *a, **k):
    if args and args[0] == "gh":
        calls.append(args[1:])
        if args[1:3] == ["issue", "list"]:
            items = OPEN if "open" in args else CLOSED
            return subprocess.CompletedProcess(args, 0, json.dumps(items), "")
        if args[1:3] == ["pr", "view"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"state": "OPEN", "headRefOid": tip[0]}), "")
        if args[1:3] == ["pr", "merge"]:
            merged.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[1:3] == ["release", "view"]:
            return subprocess.CompletedProcess(args, 1, "", "release not found")
        return subprocess.CompletedProcess(args, 0, "https://example.test/x/1\n", "")
    return real_run(args, *a, **k)


def call(fn, *argv, role=""):
    """(exit, output) of fn() inside the throwaway repo with LOOP_ROLE=role and gh stood in."""
    out, old, saved = io.StringIO(), os.getcwd(), os.environ.get("LOOP_ROLE")
    os.chdir(repo)
    os.environ["LOOP_ROLE"] = role
    sys.argv = ["x"] + list(argv)
    subprocess.run = fake_run
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                code = fn()
            except SystemExit as stop:
                code = stop.code
                print(code)
    finally:
        subprocess.run = real_run
        os.chdir(old)
        os.environ["LOOP_ROLE"] = saved or ""
    return code, out.getvalue()


def tags():
    return git("tag", "--list").stdout.split()


def reset():
    OPEN[:] = []
    SUITE[:] = ["PASS a", "PASS b"]
    HEALTH[:] = ["HEALTH: green"]
    DOCS[:] = []
    MAIL[0] = ""
    open(page, "w").write(GOOD)
    git("commit", "-q", "-am", "page", "--allow-empty")
    git("push", "-q", "origin", "main")
    git("branch", "-f", "staging", "origin/staging")


def gate(*more):
    return call(review.main, "gate", "v2", "--ref", rc, *more)


owner(("o1", "t", "operation", "moved #7 to v2.1", "#7"), ("o2", "t", "operation", "waive stale-row, issue 9", "stale-row"))

# 1. issues (REL-2)
OPEN[:] = [{"number": 7, "title": "an open thing"}]
code, said = gate()
check("an open issue on the milestone refuses, naming the issue", code == 1 and "GATE REFUSED v2.0 (issues): #7 an open thing" in said, said)
waive(("moved", "#7", "v2.1", "o1"))
code, said = gate()
check("an issue the owner moved by name (a waiver whose record names it) does not refuse", code == 0 and "GATE PASS v2.0" in said, said)
waive(("moved", "#7", "v2.1", "o2"))
code, said = gate()
check("a waiver whose owner record does not name the issue still refuses", code == 1 and "#7" in said, said)
waive(("moved", "#7", "v2.1", "o404"))
code, said = gate()
check("a waiver with no owner record still refuses", code == 1 and "#7" in said, said)
waive()
OPEN[:] = []

# 2. rows, health, reviews, docs (REL-3, REL-4, REL-1)
reset()
SUITE[:] = ["PASS a", "KNOWN stale-row (red on main)", "FAIL broken-row"]
code, said = gate()
check("a known-red row with no waiver refuses, naming the row", code == 1 and "(suite): row stale-row is KNOWN" in said, said, "rows")
check("a failing row with no waiver refuses, naming the row", "(suite): row broken-row is FAIL" in said, said, "rows")
waive(("red", "stale-row", "#9", "o2"), ("red", "broken-row", "#9", "o404"))
code, said = gate()
check("a row waived with an issue and an owner record does not refuse; one without a record does", "row stale-row" not in said and "row broken-row" in said, said, "rows")
waive()
SUITE[:] = ["PASS a", "BUDGET 15 min: ran 1 of 9 rows; LEFT 8 to the scheduled full suite: x, y"]
code, said = gate()
check("a suite stopped by its time budget with rows left refuses: rows that did not run prove nothing", code == 1 and "(suite): row budget-left is LEFT" in said, said, "rows")
SUITE[:] = []
code, said = gate()
check("a suite that did not run refuses", code == 1 and "(suite): the suite did not run" in said, said, "rows")
reset()
HEALTH[:] = ["HEALTH: not green"]
code, said = gate()
check("a failing health check refuses", code == 1 and "(health): HEALTH: not green" in said, said, "checks")
reset()
open(page, "w").write(GOOD.replace("PG-2: **Reviewed 2026-11-01**", "PG-2: **Unreviewed**"))
git("commit", "-q", "-am", "unreviewed"); git("push", "-q", "origin", "main"); git("branch", "-f", "staging", "main")
code, said = call(review.main, "gate", "v2", "--ref", "main")
check("a requirement that is not Reviewed refuses, naming it", code == 1 and "(reviews): PG-2 (Page) is not Reviewed" in said and "PG-1" not in said, said, "checks")
reset()
DOCS[:] = ["STALE Page: behind foo.txt"]
code, said = gate()
check("a stale wiki page refuses, naming it", code == 1 and "(docs): STALE Page" in said, said, "checks")
reset()
code, said = gate("--no-suite")
check("with every check green and the suite skipped the gate passes", code == 0 and "GATE PASS v2.0" in said, said, "checks")

# 3. promote (REL-6)
reset()
git("switch", "-q", "-c", "staging2", "main"); open(os.path.join(repo, "foo.txt"), "a").write("rc2"+chr(10))
git("commit", "-q", "-am", "the second rc build"); git("push", "-q", "origin", "staging2")
rc2 = git("rev-parse", "HEAD").stdout.strip()
git("switch", "-q", "main")
owner(("o1", "t", "operation", "moved #7 to v2.1", "#7"), ("o9", "t", "operation", "promote v2.0.0", "v2.0.0"))
SUITE[:] = ["PASS a"]
calls.clear()
code, said = call(review.main, "promote", "v2", "--owner-record", "o1", "--ref", rc2)
check("promote refuses when the owner record does not name the version, and changes nothing", code not in (0, None) and "OWNER_RECORD" in said and "v2.0.0" not in tags(), said, "owner")
code, said = call(review.main, "promote", "v2", "--owner-record", "o9", "--ref", rc, role="worker")
check("a worker cannot promote", code not in (0, None) and "REVIEW_ROLE" in said and "v2.0.0" not in tags(), said, "owner")
OPEN[:] = [{"number": 8, "title": "late"}]
calls.clear()
code, said = call(review.main, "promote", "v2", "--owner-record", "o9", "--ref", rc2)
remote = git("ls-remote", "--heads", "--tags", origin).stdout
check("a refused gate makes no tag, no branch and no release", code == 1 and "NOT PROMOTED v2.0.0" in said and "v2.0.0" not in tags()
      and "release/v2" not in remote and "v2.0.0" not in remote and not [c for c in calls if c[:2] == ["release", "create"]], said + remote, "promote")
OPEN[:] = []
code, said = call(review.main, "promote", "v2", "--owner-record", "o9", "--ref", rc)
check("an rc that main has moved past is refused at the push, and the local tag and branch are undone", code not in (0, None) and "PROMOTE_PUSH" in said
      and "v2.0.0" not in tags() and "release/v2" not in git("branch", "--list").stdout, said, "promote")
OPEN[:] = [{"number": 7, "title": "an open thing"}]
waive(("moved", "#7", "v2.1", "o1"))
calls.clear()
code, said = call(review.main, "promote", "v2", "--owner-record", "o9", "--ref", rc2)
remote = git("ls-remote", "--heads", "--tags", origin).stdout
check("promote tags vX.0.0 and keeps release/vX on the rc commit", code == 0 and "v2.0.0" in tags() and git("rev-parse", "v2.0.0^{commit}").stdout.strip() == rc2
      and git("rev-parse", "release/v2").stdout.strip() == rc2 and "refs/heads/release/v2" in remote and "refs/tags/v2.0.0" in remote, said + remote, "promote")
check("promote moves main to the rc commit (fast-forward only)", "%s\trefs/heads/main" % rc2 in remote, remote, "promote")
made = [c for c in calls if c[:2] == ["release", "create"]]
report = open(os.path.join(common, "loop", "gate", "v2.0.0.md")).read() if os.path.exists(os.path.join(common, "loop", "gate", "v2.0.0.md")) else ""
check("promote publishes the state report as the release notes", made and "v2.0.0" in made[0] and "--notes-file" in made[0], str(calls), "promote")
check("the state report names the review state, tests, health, closed issues and changes",
      all(x in report for x in ("## Requirements", "Page: 2 Reviewed, 0 Unreviewed", "## Tests", "1 PASS", "## Health", "HEALTH: green", "#3 done thing", "## Changes since")), report, "promote")
check("promote mails the report", ("mail", "Release v2.0.0") in calls and "EMAILED v2.0.0" in said, said, "promote")
check("a moved waiver moves its issue to the later milestone", ["issue", "edit", "7", "--milestone", "v2.1"] in [c[:5] for c in calls], str(calls), "promote")
waive()
OPEN[:] = []
git("tag", "-d", "v2.0.0"); git("branch", "-D", "release/v2")
git("push", "-q", "origin", ":refs/tags/v2.0.0", ":refs/heads/release/v2")
MAIL[0] = "no mail.env"
code, said = call(review.main, "promote", "v2", "--owner-record", "o9", "--ref", rc2)
check("with no mail secrets the tag stays and the report path is printed", code == 0 and "EMAIL not sent: no mail.env" in said and "v2.0.0" in tags(), said, "promote")

# 4. revert (REL-7)
git("switch", "-q", "main"); git("pull", "-q", "origin", "main")
open(os.path.join(repo, "foo.txt"), "a").write("later\n")
git("commit", "-q", "-am", "work after the release"); git("push", "-q", "origin", "main")
later = git("rev-parse", "HEAD").stdout.strip()
calls.clear()
code, said = call(review.main, "revert", "v2", role="worker")
check("a worker cannot revert", code not in (0, None) and "REVIEW_ROLE" in said, said, "owner")
code, said = call(review.main, "revert", "v2")
branches = git("ls-remote", "--heads", origin, "revert/v2-*").stdout.split()
tree = git("rev-parse", branches[0] + "^{tree}").stdout.strip() if branches else ""
git("fetch", "-q", "origin")
parent = git("rev-parse", (branches[0] if branches else "x") + "^").stdout.strip()
check("revert pushes a branch whose tree is the snapshot's, on top of main", code == 0 and tree == git("rev-parse", "release/v2^{tree}").stdout.strip() and parent == later, said + str(branches), "revert")
prs = [c for c in calls if c[:2] == ["pr", "create"]]
check("revert opens a pull request to main", prs and "--base" in prs[0] and "main" in prs[0], str(calls), "revert")
check("revert never pushes main", git("ls-remote", "--heads", origin, "main").stdout.split()[0] == later, git("ls-remote", origin).stdout, "revert")
code, said = call(review.main, "revert", "v9")
check("revert with no snapshot refuses", code not in (0, None) and "no snapshot branch" in said, said, "revert")

# 5. freeze (REL-5)
tags_now = tags()
git("tag", "-d", "v2.0.0"); git("push", "-q", "origin", ":refs/tags/v2.0.0")
for name in ("g",):
    git("switch", "-q", "-c", "loop/" + name, base)
    open(os.path.join(repo, ".loop", "goals", name + ".md"), "w").write("# fix\n\nfixes #8 in the gate\n")
    git("add", "-A"); git("commit", "-q", "-m", "goal work"); git("push", "-q", "origin", "loop/" + name)
    head = git("rev-parse", "HEAD").stdout.strip()
git("switch", "-q", "main")
tip[0] = head
record = os.path.join(common, "loop", "runs", "g.json")


def write():
    git("fetch", "-q", "origin")
    json.dump({"slug": "g", "branch": "loop/g", "status": "done", "step": "release", "pr": "https://example.test/pull/1",
               "pr_base": git("rev-parse", "origin/main").stdout.strip(), "pr_head": head, "report": {}}, open(record, "w"))


git("push", "-q", "origin", ":refs/tags/v2.0.0-rc.1")
write()
code, said = call(merge.main, "g")
check("with no rc cut, nothing is frozen and the goal merges", "FROZEN" not in said and merged, said[-300:], "freeze")
merged[:] = []
git("tag", "v2.0.0-rc.1", rc)
write()
gate_dir = os.path.join(common, "loop", "gate")
if os.path.exists(os.path.join(gate_dir, "v2.json")):
    os.remove(os.path.join(gate_dir, "v2.json"))
code, said = call(merge.main, "g")
check("a cut rc with no gate run freezes every merge: frozen for v2.0.0, nothing merged", code not in (0, None) and "frozen for v2.0.0" in said and not merged, said[-300:], "freeze")
os.makedirs(gate_dir, exist_ok=True)
json.dump({"ref": "x", "refusals": [["issues", "#7 x", ["#7"]]]}, open(os.path.join(gate_dir, "v2.json"), "w"))
write()
code, said = call(merge.main, "g")
check("a goal that names no recorded gate failure is refused, and the refusal names the subjects", "frozen for v2.0.0" in said and "#7" in said and not merged, said[-300:], "freeze")
json.dump({"ref": "x", "refusals": [["issues", "#8 late", ["#8"]]]}, open(os.path.join(gate_dir, "v2.json"), "w"))
write()
code, said = call(merge.main, "g")
check("a goal that names a recorded gate failure is let through", "FROZEN" not in said and "MERGED" in said and merged, said[-300:], "freeze")
merged[:] = []
git("tag", "v2.0.0", rc)
json.dump({"ref": "x", "refusals": []}, open(os.path.join(gate_dir, "v2.json"), "w"))
write()
code, said = call(merge.main, "g")
check("once vX.0.0 exists the freeze is over", "FROZEN" not in said and merged, said[-300:], "freeze")

# 6. a goal never bumps a major (REL-1)
try:
    release.bump("1.0.54", "major")
    refused = ""
except SystemExit as stop:
    refused = str(stop)
check("release.bump refuses a major: it ships only through review.py promote", "MAJOR_GATE" in refused and "review.py promote" in refused, refused, "major")
check("release.bump still bumps a minor and a patch", release.bump("1.0.54", "minor") == "1.1.0" and release.bump("1.0.54", "patch") == "1.0.55", "", "major")

# 7. the page (REL-1 to REL-8) and the sizes
text = open(os.path.join(root, "docs", "wiki", "Release.md"), encoding="utf-8").read() if os.path.exists(os.path.join(root, "docs", "wiki", "Release.md")) else ""
ids = re.findall(r"^- (REL-\d+): \*\*(Unreviewed|Reviewed[^*]*)\*\*", text, re.M)
check("the Release page holds REL-1 to REL-8, all Unreviewed", [i for i, _ in ids] == ["REL-%d" % n for n in range(1, 9)] and {s for _, s in ids} == {"Unreviewed"}, str(ids), "major")
over = []
for dirpath, _, files in os.walk(os.path.join(root, "skills")):
    for name in files:
        if name.endswith(".py"):
            size = len(open(os.path.join(dirpath, name), "rb").read().replace(b"\r\n", b"\n"))
            cap = 19495 if name == "checkin.py" else 19000
            if size > cap and name in ("review.py", "merge.py", "release.py", "checkin.py"):
                over.append("%s %d" % (name, size))
check("review.py, merge.py and release.py stay under 19,000 bytes, and checkin.py at or under 19,495", not over, ", ".join(over), "major")
added = subprocess.run(["git", "diff", "--name-status", "--diff-filter=A", "origin/main", "--", "skills", "listing.json"], cwd=root, capture_output=True, text=True).stdout
check("no file is added to the shipped package", not added.strip(), added, "major")
sys.exit(1 if fails else 0)
