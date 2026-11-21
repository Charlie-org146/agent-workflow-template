#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/fit.py skills/workflow-release/scripts/autorelease.py skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/review.py skills/workflow-monitoring/scripts/machines.py skills/workflow-monitoring/scripts/operate.py
"""Proves #5674: each push or GitHub-write site that once sent text without the private-name scan (fit.pr_open,
autorelease.label_part, merge.merge_pr, review.promote and revert, machines.batch_assemble and batch, operate.apply)
refuses a planted fixture name BEFORE it writes, and a clean payload still goes through (the negative control).
Fixture repos, a made-up name in a fixture list under a temp dir, a fake gh on PATH, a local bare origin. No network."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import types

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for part in ("workflow-delivery", "workflow-release", "workflow-monitoring"):
    sys.path.insert(0, os.path.join(here, "skills", part, "scripts"))

T = tempfile.mkdtemp(prefix="scan-push-sites-")
NAME = "zzplanted"
LISTS = {}
for key, lines in (("name", NAME + "\n"), ("label", NAME + "\nrelease:major\n")):
    LISTS[key] = os.path.join(T, "names-" + key)
    open(LISTS[key], "w").write(lines)
LISTS["broken"] = os.path.join(T, "names-broken")
open(LISTS["broken"], "w").write("(\n")
LISTS["missing"] = os.path.join(T, "names-missing")
os.environ.update(LOOP_PRIVATE_NAMES=LISTS["name"], GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.test",
                  GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.test", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)

GH_LOG = os.path.join(T, "gh.log")
BIN = os.path.join(T, "bin")
os.makedirs(BIN)
with open(os.path.join(BIN, "gh"), "w") as handle:
    handle.write('#!/bin/sh\necho "$*" >> "$GH_LOG"\n'
                 'case "$1 $2" in\n"pr view") echo "${FAKE_VIEW:-{\\"title\\":\\"t\\",\\"headRefName\\":\\"b\\"}}"; exit "${FAKE_VIEW_RC:-0}";;\n'
                 '"pr create") echo https://example.test/pull/1;;\nesac\nexit 0\n')
os.chmod(os.path.join(BIN, "gh"), 0o755)
os.environ.update(PATH=BIN + os.pathsep + os.environ["PATH"], GH_LOG=GH_LOG)

import autorelease  # noqa: E402
import fit  # noqa: E402
import machines  # noqa: E402
import merge  # noqa: E402
import operate  # noqa: E402
import release  # noqa: E402
import review  # noqa: E402

fails = []
CP = subprocess.CompletedProcess


def check(ok, text):
    print(("PASS " if ok else "FAIL ") + text)
    if not ok:
        fails.append(text)


def git(cwd, *args):
    done = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)
    if done.returncode:
        raise SystemExit("toy setup: git %s failed: %s" % (" ".join(args), done.stderr))
    return done.stdout.strip()


def repo(name):
    """A work clone on branch `work` (base branch `trunk`), with a local bare origin."""
    top, origin = os.path.join(T, name), os.path.join(T, name + ".git")
    os.makedirs(os.path.join(top, ".loop"))
    git(top, "init", "-q", "-b", "trunk")
    open(os.path.join(top, ".loop", "config.json"), "w").write(json.dumps({"base": "trunk"}))
    open(os.path.join(top, "a.txt"), "w").write("clean\n")
    git(top, "add", "-A")
    git(top, "commit", "-q", "-m", "start")
    subprocess.run(["git", "clone", "-q", "--bare", top, origin], check=True)
    git(top, "remote", "add", "origin", origin)
    git(top, "fetch", "-q", "origin")
    git(top, "checkout", "-q", "-b", "work")
    return top, origin


def log():
    return open(GH_LOG).read() if os.path.exists(GH_LOG) else ""


def reset():
    open(GH_LOG, "w").close()


def refused(call):
    """(True, message) when CALL exits with a refusal."""
    try:
        call()
    except SystemExit as stop:
        return True, str(stop.code)
    return False, ""


# 1. fit.pr_open
top, origin = repo("fit")
calls = []


class G:
    def root(self):
        return top

    def run(self, args, check=False):
        calls.append(args)
        return CP(args, 0, "https://example.test/pull/1\n", "")

    def no(self, text):
        sys.exit("REFUSED: " + text)

    def state_path(self, slug):
        return os.path.join(T, slug)

    def write(self, path, text):
        open(path, "w").write(text)


state = {"branch": "work", "goal": "a clean goal", "slug": "fit"}
bad, why = refused(lambda: fit.pr_open(G(), state, "trunk", {}, "text with %s inside" % NAME))
check(bad and "private name" in why and not calls, "fit.pr_open refuses a planted name in the PR body before git push or gh pr create")
bad, why = refused(lambda: fit.pr_open(G(), dict(state, goal="goal " + NAME), "trunk", {}, "clean body"))
check(bad and not calls, "fit.pr_open refuses a planted name in the PR title before it pushes")
done = fit.pr_open(G(), state, "trunk", {}, "a clean body")
check(done.endswith("/pull/1") and any(c[:2] == ["git", "push"] for c in calls) and any(c[:3] == ["gh", "pr", "create"] for c in calls),
      "fit.pr_open still pushes and opens a clean PR (negative control)")

# 2. autorelease.label_part
release.save = lambda *a, **k: None
top, origin = repo("label")
cfg, state = {"merge_queue": True}, {"release_part": "major", "pr": "7", "slug": "label"}
os.environ["LOOP_PRIVATE_NAMES"] = LISTS["label"]
reset()
bad, why = refused(lambda: autorelease.label_part(top, cfg, state))
check(bad and "gh" not in log(), "autorelease.label_part refuses a label the list names before gh label create or pr edit")
os.environ["LOOP_PRIVATE_NAMES"] = LISTS["name"]
reset()
autorelease.label_part(top, cfg, state)
check("pr edit 7 --add-label release:major" in log(), "autorelease.label_part still labels the PR with a clean name (negative control)")

# 3. merge.merge_pr
reset()
os.environ["FAKE_VIEW"] = json.dumps({"title": "Add " + NAME, "headRefName": "b"})
done = merge.merge_pr(top, "7", "abc")
check(done.returncode and "REFUSED" in done.stderr and "pr merge" not in log(), "merge.merge_pr refuses a planted name in the PR title before gh pr merge")
os.environ["FAKE_VIEW"] = json.dumps({"title": "t", "headRefName": "loop/" + NAME})
done = merge.merge_pr(top, "7", "abc")
check(done.returncode and "pr merge" not in log(), "merge.merge_pr refuses a planted name in the head branch before gh pr merge")
os.environ["FAKE_VIEW"] = '{"title":"t","headRefName":"b"}'
os.environ["FAKE_VIEW_RC"] = "1"
done = merge.merge_pr(top, "7", "abc")
check(done.returncode and "pr merge" not in log(), "merge.merge_pr refuses when it cannot read the PR text (fails closed)")
os.environ.pop("FAKE_VIEW_RC")
done = merge.merge_pr(top, "7", "abc")
check(not done.returncode and "pr merge 7 --merge --match-head-commit abc" in log(), "merge.merge_pr still merges a clean PR (negative control)")
os.environ.pop("FAKE_VIEW")

# 4 and 5. review.promote and review.revert, with git, gh and the gate faked
calls = []


def fake_git(*args, cwd=None, check=True):
    calls.append(["git"] + list(args))
    if args[0] == "rev-parse":
        return git(cwd, *args)
    return "abc123" if args[0] == "commit-tree" else ""


def fake_run(args, cwd=None, **kw):
    calls.append(list(args))
    return CP(args, 0, "https://example.test/pull/2\n", "")


gate = os.path.join(T, "gate-common")
os.makedirs(os.path.join(gate, "gate"))
real_git, real_release_run = release.git, release.run
release.git, release.run = fake_git, fake_run
review.table = lambda top, name: [["rec", "", "", "", "v1.0.0"]]
review.gate_refusals = lambda *a: ([], {})
review.common_of = lambda top: gate
review.waivers = lambda *a: {}
review.email = lambda *a: ""
review.OK = lambda args, cwd: not args[0].startswith("refs/tags/")
pushed = lambda: [c for c in calls if c[:2] == ["git", "push"] or c[:3] in (["gh", "pr", "create"], ["gh", "release", "create"]) or c[:2] == ["git", "tag"]]
for text, label, planted in (("- #9 closed issue titled %s\n" % NAME, "the closed-issue titles in the release notes", True), ("- #9 a clean title\n", "", False)):
    review.state_report = lambda *a, text=text: text
    calls.clear()
    if planted:
        bad, why = refused(lambda: review.promote(top, {"base": "trunk"}, 1, "rec", "HEAD"))
        check(bad and "private name" in why and not pushed() and not os.path.exists(os.path.join(gate, "gate", "v1.0.0.md")),
              "review.promote refuses a planted name in %s before the tag, push or gh release create" % label)
    else:
        code = review.promote(top, {"base": "trunk"}, 1, "rec", "HEAD")
        check(code == 0 and any(c[:2] == ["git", "push"] for c in calls) and any(c[:3] == ["gh", "release", "create"] for c in calls),
              "review.promote still tags, pushes and releases clean notes (negative control)")
pro, _ = repo("pro-bad")
open(os.path.join(pro, "later.txt"), "w").write("has %s inside\n" % NAME)
git(pro, "add", "-A")
git(pro, "commit", "-q", "-m", "work after the base")
review.state_report = lambda *a: "- #9 a clean title\n"
calls.clear()
bad, why = refused(lambda: review.promote(pro, {"base": "trunk"}, 1, "rec", "HEAD"))
check(bad and "private name" in why and not pushed(), "review.promote refuses a planted name in a commit it would push to the base, the tag and release/vX")
calls.clear()
bad, why = refused(lambda: review.revert(top, {"base": NAME + "-trunk"}, 1))
check(bad and "private name" in why and not pushed(), "review.revert refuses a planted name before git push or gh pr create")
calls.clear()
code = review.revert(top, {"base": "trunk"}, 1)
check(code == 0 and any(c[:2] == ["git", "push"] for c in calls) and any(c[:3] == ["gh", "pr", "create"] for c in calls),
      "review.revert still pushes and opens a clean revert PR (negative control)")
release.git, release.run = real_git, real_release_run

# 6. machines.batch_assemble: a planted name in a member's commit never reaches origin's batch/<id>
M = types.SimpleNamespace(run=lambda args, cwd=None: subprocess.run(args, cwd=cwd, capture_output=True, text=True), ar=autorelease)


def members(top, body):
    out = []
    for slug in ("one", "two"):
        git(top, "checkout", "-q", "-b", "m-" + slug, "trunk")
        open(os.path.join(top, slug + ".txt"), "w").write(body if slug == "two" else "clean\n")
        git(top, "add", "-A")
        git(top, "commit", "-q", "-m", "member " + slug)
        git(top, "push", "-q", "origin", "m-" + slug)
        out.append((slug, {"branch": "m-" + slug}, {"headRefOid": git(top, "rev-parse", "HEAD")}))
    git(top, "checkout", "-q", "work")
    return out


for name, body, planted in (("assemble-bad", "has %s inside\n" % NAME, True), ("assemble-ok", "all clean\n", False)):
    top, origin = repo(name)
    kept, alone, head = machines.batch_assemble(M, top, "trunk", "bid1", members(top, body))
    there = bool(git(top, "ls-remote", "origin", "refs/heads/batch/bid1"))
    if planted:
        check(not kept and not head and not there, "machines.batch_assemble refuses a planted name in a member's change before it pushes batch/<id>")
    else:
        check(kept == ["one", "two"] and head and there, "machines.batch_assemble still assembles and pushes a clean batch (negative control)")

# 7. machines.batch: the draft PR's title and body
runs = []
M2 = types.SimpleNamespace(load=lambda path: {"slug": os.path.basename(path)[:-5], "branch": "x"}, ar=autorelease,
                           run=lambda args, cwd=None: (runs.append(list(args)), CP(args, 0, "https://example.test/pull/3\n", ""))[1])
real_assemble = machines.batch_assemble
machines.batch_ready = lambda M, top, base, state: ({"headRefOid": "abc"}, "")
machines.batch_assemble = lambda M, top, base, bid, members: ([m[0] for m in members], [], "headsha0000000000")
for slugs, planted in (([NAME + "-a", "b"], True), (["a", "b"], False)):
    runs.clear()
    common = tempfile.mkdtemp(dir=T)
    code = machines.batch(top, common, {"base": "trunk"}, slugs, "", M2)
    made = [r for r in runs if r[:3] == ["gh", "pr", "create"]]
    if planted:
        check(code == 1 and not made, "machines.batch refuses a planted name in the draft PR text before gh pr create")
    else:
        check(code == 0 and made, "machines.batch still opens the draft PR for a clean batch (negative control)")

# 8. operate.apply: the re-stamp commit pushed to the goal's branch
real_run = operate.run
page = {"text": ""}


def apply_run(args, cwd=None):
    if any("audit.py" in str(a) for a in args) and "rerender" in args:
        os.makedirs(os.path.join(cwd, "docs", "wiki"), exist_ok=True)
        open(os.path.join(cwd, "docs", "wiki", "Page.md"), "w").write(page["text"])
        return CP(args, 0, "re-rendered Page\n", "")
    if any("docs.py" in str(a) for a in args):
        return CP(args, 0, "", "")
    return real_run(args, cwd)


operate.run = apply_run
for name, text, planted in (("apply-bad", "# Page\n%s\n" % NAME, True), ("apply-ok", "# Page\nclean\n", False)):
    top, origin = repo(name)
    git(top, "push", "-q", "origin", "work")
    before = git(top, "ls-remote", "origin", "refs/heads/work")
    page["text"] = text
    os.chdir(top)
    seen = io.StringIO()
    with contextlib.redirect_stdout(seen):
        code = operate.apply("slug", "work")
    after = git(top, "ls-remote", "origin", "refs/heads/work")
    if planted:
        check(before == after and code == 1 and seen.getvalue().startswith("REFUSED: a private name would be pushed") and "(PRIVATE_NAME)" in seen.getvalue(),
              "operate.apply refuses a planted name in the re-stamped pages before it pushes, prints the whole refusal and exits 1")
    else:
        check(before != after and code == 0, "operate.apply still pushes a clean re-stamp and exits 0 (negative control)")
os.chdir(T)

# 9. a MISSING or BROKEN list: every newly scanned site refuses (PRIVATE_LIST) and writes nothing
REAL_HOME = os.environ.get("HOME")
EMPTY_HOME = os.path.join(T, "home-without-a-list")
os.makedirs(EMPTY_HOME)
for mode in ("nolist", "missing", "broken"):
    if mode == "nolist":  # the real no-list state: LOOP_PRIVATE_NAMES unset, a home that holds no list
        os.environ.pop("LOOP_PRIVATE_NAMES")
        os.environ["HOME"] = EMPTY_HOME
    else:
        os.environ["LOOP_PRIVATE_NAMES"] = LISTS[mode]
        os.environ["HOME"] = REAL_HOME
    top, origin = repo("closed-" + mode)
    word = {"nolist": "no list at all", "missing": "a list file that does not exist", "broken": "a broken list"}[mode]
    calls.clear()
    bad, why = refused(lambda: fit.pr_open(G(), {"branch": "work", "goal": "g", "slug": "x"}, "trunk", {}, "a clean body"))
    check(bad and "PRIVATE_LIST" in why and not calls, "fit.pr_open refuses with %s before it writes" % word)
    reset()
    bad, why = refused(lambda: autorelease.label_part(top, cfg, {"release_part": "major", "pr": "7", "slug": "x"}))
    check(bad and "PRIVATE_LIST" in why and not log(), "autorelease.label_part refuses with %s before it writes" % word)
    reset()
    os.environ["FAKE_VIEW"] = '{"title":"t","headRefName":"b"}'
    done = merge.merge_pr(top, "7", "abc")
    check(done.returncode and "PRIVATE_LIST" in done.stderr and "pr merge" not in log(), "merge.merge_pr refuses with %s before gh pr merge" % word)
    os.environ.pop("FAKE_VIEW")
    release.git, release.run = fake_git, fake_run
    review.state_report = lambda *a: "- #9 a clean title\n"
    calls.clear()
    bad, why = refused(lambda: review.promote(top, {"base": "trunk"}, 1, "rec", "HEAD"))
    check(bad and "PRIVATE_LIST" in why and not pushed(), "review.promote refuses with %s before it tags or pushes" % word)
    calls.clear()
    bad, why = refused(lambda: review.revert(top, {"base": "trunk"}, 1))
    check(bad and "PRIVATE_LIST" in why and not pushed(), "review.revert refuses with %s before it pushes" % word)
    release.git, release.run = real_git, real_release_run
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        kept, alone, head = real_assemble(M, top, "trunk", "bid2", members(top, "all clean\n"))
    check(not kept and "PRIVATE_LIST" in err.getvalue() and not git(top, "ls-remote", "origin", "refs/heads/batch/bid2"), "machines.batch_assemble refuses with %s before it pushes batch/<id>" % word)
    runs.clear()
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        code = machines.batch(top, tempfile.mkdtemp(dir=T), {"base": "trunk"}, ["a", "b"], "", M2)
    check(code == 1 and "PRIVATE_LIST" in err.getvalue() and not [r for r in runs if r[:3] == ["gh", "pr", "create"]], "machines.batch refuses with %s before gh pr create" % word)
    page["text"] = "# Page\nclean\n"
    git(top, "push", "-q", "origin", "work")
    before = git(top, "ls-remote", "origin", "refs/heads/work")
    os.chdir(top)
    seen = io.StringIO()
    with contextlib.redirect_stdout(seen):
        code = operate.apply("slug", "work")
    check(code == 1 and "(PRIVATE_LIST)" in seen.getvalue() and before == git(top, "ls-remote", "origin", "refs/heads/work"), "operate.apply refuses with %s before it pushes" % word)
    os.chdir(T)
os.environ["HOME"] = REAL_HOME
os.environ["LOOP_PRIVATE_NAMES"] = LISTS["name"]

# 10. merge.py stops when operate.py apply refuses (rc 1) and writes nothing to GitHub
top, origin = repo("stopapply")
cfgpath = os.path.join(top, ".loop", "config.json")
open(cfgpath, "w").write(json.dumps({"base": "trunk", "auto_merge": True}))
runs_dir = os.path.join(top, ".git", "loop", "runs")
os.makedirs(runs_dir)
open(os.path.join(runs_dir, "s.json"), "w").write(json.dumps({"slug": "s", "pr": "7", "status": "done", "branch": "work"}))
fake_apply = os.path.join(T, "fake-operate.py")
merge.wiki.where, merge.wiki.top_of, merge.pods = (lambda *a: None), (lambda *a: True), None
real_operate = merge.OPERATE
os.chdir(top)
sys.argv = ["merge.py", "s"]
for text, rc in (("REFUSED: a private name would be pushed (PRIVATE_NAME)", 1), ("clean", 0)):
    open(fake_apply, "w").write("import sys\nprint(%r)\nsys.exit(%d)\n" % (text, rc))
    merge.OPERATE = fake_apply
    reset()
    try:
        merge.main()
        stop = ""
    except SystemExit as stopped:
        stop = str(stopped.code)
    except Exception as crash:  # noqa: BLE001 - the clean case runs on into code this toy does not set up
        stop = ""
    if rc:
        check("operate.py apply refused" in stop and "PRIVATE_NAME" in stop and not log(), "merge.py stops on a refused apply, says why, and calls gh not at all")
    else:
        check("operate.py apply refused" not in stop and "pr view" in log(), "merge.py goes on to gh pr view after a clean apply (negative control)")
merge.OPERATE = real_operate
os.chdir(T)

print("ALL PASS" if not fails else "FAILED: %d" % len(fails))
sys.exit(1 if fails else 0)
