#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/counting.py skills/workflow-docs/scripts/prd.py
# reads: skills/workflow-monitoring/scripts/replan.py skills/workflow-monitoring/scripts/graph.py skills/workflow-monitoring/scripts/govern_hook.py
"""merge-unblock A (#3867, #3122): a comments-only change to mapped code stales no page; a code change stales it and the
merge re-stamps it (reviewed text unchanged, slug logged); a changed wording stays LOCKED.
usage: test-merge-unblock.py [comments|restamp|locked|merge|ff|slot|hook]"""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-docs", "scripts"))
os.environ["LOOP_ROLE"] = "worker"
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
sys.path.insert(0, os.path.join(root, "skills", "workflow-monitoring", "scripts"))
import criteria  # noqa: E402
import audit  # noqa: E402
import docs  # noqa: E402
import prd  # noqa: E402
import operate  # noqa: E402
import wiki  # noqa: E402

fails = 0
only = sys.argv[1] if len(sys.argv) > 1 else ""


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def git(*args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=repo, capture_output=True, text=True)


def write(path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", newline="\n") as handle:
        handle.write(text)


def commit(message):
    git("add", "-A")
    git("commit", "-q", "-m", message)


def stale():
    return [p for k, p, _ in docs.problems(repo, "") if k == "STALE"]


def page(problem):
    body = ("<!-- workflow-docs -->\n# A\nReview: **Unreviewed**\n\n## Problem\n%s\n\n## Requirements\n- A-1: Be useful\n\n"
            "## Non-goals\nNothing else here.\n\n## Success metrics\nIt stays fresh.\n\n## Tests\nNone yet.\n") % problem
    now = prd.prints(criteria.sections(body), criteria.rules())
    return prd.set_review(body, "Review: **Reviewed 2026-01-01** <!-- prd %s -->" % " ".join("%s=%s" % (k, now[k]) for k in prd.KEYS))


def build():
    global repo
    repo = tempfile.mkdtemp(prefix="merge-unblock-")
    git("init", "-q", "-b", "main")
    write(".loop/config.json", "{}\n")
    write(".loop/docs.tsv", "A\ta.py\n")
    write("a.py", '"""Docs."""\n\n\ndef run():\n    return 1\n')
    write("docs/wiki/A.md", page("Readers need a page that says what a.py does today."))
    commit("a page and its code")
    os.chdir(repo)


repo = ""
if only in ("", "comments"):
    build()
    write("a.py", '"""More docs."""\n\n\ndef run():\n    # a note\n    return 1\n')
    commit("comments and docstring only")
    check("a comments-only change to mapped code leaves the page fresh (stale: %s)" % stale(), not stale())
    write("a.py", '"""More docs."""\n\n\ndef run():\n    return 2\n')
    commit("a real change")
    check("a real code change still stales it", stale() == ["A"])
if only in ("", "restamp"):
    build()
    write("a.py", "def run():\n    return 2\n")
    commit("a real change")
    check("the page is stale before the merge", stale() == ["A"])
    done = audit.relock(repo, "my-goal", ["A"])
    commit("Wiki: re-stamp pages for my-goal")
    check("restamp marks the page kept by the goal (%s)" % done, done == ["A"] and "kept my-goal" in open(os.path.join(repo, "docs/wiki/A.md")).read())
    check("and the page is no longer stale (%s)" % stale(), not stale())
    log = open(os.path.join(repo, ".git", "loop", "reviews.tsv")).read()
    check("and the reviews log names the goal's slug", "restamp\tA\tmy-goal" in log)
    check("and the page's review line still parses", prd.review_of(open(os.path.join(repo, "docs/wiki/A.md")).read(), criteria.rules())[1] is None)
if only in ("", "locked"):
    build()
    write("a.py", "def run():\n    return 2\n")
    write("docs/wiki/A.md", open(os.path.join(repo, "docs/wiki/A.md")).read().replace("what a.py does", "what a.py is for"))
    commit("code and wording both change")
    check("a changed wording is not re-stamped, so it stays LOCKED", audit.relock(repo, "my-goal", ["A"]) == [])
if only in ("", "merge"):
    build()
    bare = tempfile.mkdtemp(prefix="merge-unblock-origin-")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], capture_output=True)
    git("remote", "add", "origin", bare)
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "goal")
    write("a.py", "def run():\n    return 2\n")
    commit("the goal changes mapped code only")
    git("push", "-q", "origin", "goal")
    git("checkout", "-q", "main")
    git("fetch", "-q", "origin")
    before = [l for l in wiki.pending(repo, {}, head="origin/goal") if ": STALE " in l]
    check("merge.py would refuse the page before the re-stamp (%s)" % before, bool(before))
    subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-monitoring", "scripts", "operate.py"), "apply", "my-goal", "goal"], cwd=repo)
    git("fetch", "-q", "origin")
    after = [l for l in wiki.pending(repo, {}, head="origin/goal") if ": STALE " in l]
    check("after the merge step's re-stamp nothing is stale (%s)" % after, not after)
    check("and the goal's branch got a re-stamp commit", "re-stamp pages for my-goal" in git("log", "-1", "--format=%s", "origin/goal").stdout)
if only in ("", "ff", "ffconflict"):
    tmp = tempfile.mkdtemp(prefix="merge-unblock-ff-")
    origin, repo, other = (os.path.join(tmp, n) for n in ("origin.git", "repo", "other"))
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], capture_output=True)
    subprocess.run(["git", "clone", "-q", origin, repo], capture_output=True)
    write(".loop/regression-runs.tsv", "a\tpass\nm\tpass\nz\tpass\n")
    write("a.txt", "a\n")
    commit("base")
    git("push", "-q", "origin", "main")
    subprocess.run(["git", "clone", "-q", origin, other], capture_output=True)
    with open(os.path.join(other, "b.txt"), "w") as handle:
        handle.write("b\n")
    with open(os.path.join(other, ".loop", "regression-runs.tsv"), "w", newline="\n") as handle:
        handle.write("a\tpass\nm\tpass\nz\tfail\n")
    for step in (["add", "-A"], ["commit", "-q", "-m", "origin moves"], ["push", "-q", "origin", "main"]):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t"] + step, cwd=other, capture_output=True)
    git("fetch", "-q", "origin")
    if only == "ffconflict":
        write(".loop/regression-runs.tsv", "a\tpass\nm\tpass\nz\tskip\n")  # the line origin changed too: the stash apply conflicts
        code, said = operate.fast_forward(repo, "main")
        left = open(os.path.join(repo, ".loop", "regression-runs.tsv")).read().replace("\r", "")
        check("a conflicting lane record never leaves the file unmerged (%s)" % git("status", "--porcelain").stdout.strip(), code == 0 and not git("ls-files", "-u").stdout.strip() and "<<<<" not in left)
        check("the file is origin's, and the dirty results stay in the named stash the step prints", left == "a\tpass\nm\tpass\nz\tfail\n" and "operate-forward-" in said and "operate-forward-" in git("stash", "list").stdout)
        sys.exit(1 if fails else 0)
    write(".loop/regression-runs.tsv", "a\tfail\nm\tpass\nz\tpass\n")
    check("a plain fast-forward refuses while the lane record is dirty", git("merge", "--ff-only", "-q", "origin/main").returncode != 0)
    check("a dirty lane record alone is stashed, the checkout moves", operate.fast_forward(repo, "main")[0] == 0 and git("rev-parse", "HEAD").stdout == git("rev-parse", "origin/main").stdout)
    check("and the record is put back, with no stash left", open(os.path.join(repo, ".loop", "regression-runs.tsv")).read().replace("\r", "") == "a\tfail\nm\tpass\nz\tfail\n" and not git("stash", "list").stdout.strip())
if only in ("", "slot"):
    import contextlib
    import io
    import threading
    import time
    sys.path.insert(0, os.path.join(root, "skills", "workflow-monitoring", "scripts"))
    import graph  # noqa: E402
    common = tempfile.mkdtemp(prefix="merge-unblock-slot-")
    runs = os.path.join(common, "loop", "runs")
    os.makedirs(runs)
    graph.pr_queue("hold", runs, "first")
    time.sleep(0.05)
    graph.pr_queue("hold", runs, "second")
    check("a goal waits for the one whose pr lane started before its own", graph.pr_queue("before", runs, "second") == "first")
    check("and the first goal waits for nobody", graph.pr_queue("before", runs, "first") == "")
    check("a goal that never started a lane waits for none", graph.pr_queue("before", runs, "third") == "")
    os.environ["LOOP_SLOT_POLL"] = "0.05"
    threading.Timer(0.3, lambda: graph.pr_queue("free", runs, "first")).start()
    out = io.StringIO()
    began = time.time()
    with contextlib.redirect_stdout(out):
        graph.pr_queue("wait", runs, "second")
    check("merge.py waits for the earlier lane's goal, then goes on (%s)" % out.getvalue().strip(), time.time() - began >= 0.25 and "first" in out.getvalue())
if only in ("", "hook"):
    import json
    sys.path.insert(0, os.path.join(root, "skills", "workflow-monitoring", "scripts"))
    import govern_hook  # noqa: E402
    build()
    os.makedirs(os.path.join(repo, ".git", "loop"), exist_ok=True)
    with open(os.path.join(repo, ".git", "loop", "session-pool.json"), "w") as handle:
        json.dump({"local_worker": {"name": "worker", "state": "busy"}}, handle)
    git("worktree", "add", "-q", "-b", "g", os.path.join(repo, ".git", "loop", "worktrees", "g"))
    tree = os.path.join(repo, ".git", "loop", "worktrees", "g")

    def call(command, cwd, session="local_worker"):
        return govern_hook.decide({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd, "session_id": session})

    said = call("git commit -m stray", repo)
    check("a worker's commit in the main checkout is refused (%s)" % said[:60], "main checkout" in said and "GRD-4" in said)
    check("a worker's commit in its own worktree passes", call("git commit -m ok", tree) == "")
    check("a commit aimed at a worktree with -C or cd passes", call("git -C %s commit -m ok" % tree, repo) == "" and call("cd %s && git commit -m ok" % tree, repo) == "")
    check("another session's commit in the main checkout is not this hook's business", call("git commit -m mine", repo, "local_other") == "")
    check("a worker's other commands in the main checkout pass", call("git status", repo) == "" and call("python3 x.py", repo) == "")
print("PASS: merge-unblock A" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
