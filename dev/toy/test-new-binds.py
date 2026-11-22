#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/fit.py skills/workflow-monitoring/scripts/sessions.py
"""new-binds (#4257): goal.py new, run inside a Claude app worker session (CLAUDE_CODE_HOST_SESSION_ID set), binds the new goal
to that session like `sessions.py bind SLUG self` and says BOUND; outside an app session it changes nothing.
usage: test-new-binds.py [in|out]"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
goal = os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py")
only = sys.argv[1] if len(sys.argv) > 1 else ""
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def fresh():
    repo = tempfile.mkdtemp(prefix="new-binds-")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["init", "-q", "-b", "main", repo], check=True)
    os.makedirs(os.path.join(repo, ".loop"))
    with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
        json.dump({"base": "main", "workers": "app"}, handle)
    with open(os.path.join(repo, "flow.json"), "w") as handle:
        json.dump({"steps": dict.fromkeys(("idea", "plan", "build", "review", "qa", "ship"), "built-in")}, handle)
    subprocess.run(git + ["add", "-A"], cwd=repo, check=True)
    subprocess.run(git + ["commit", "-q", "-m", "base"], cwd=repo, check=True)
    trust(repo)
    return repo


def trust(home, shape="trusting"):
    """The trust file under HOME: a readable one that trusts HOME (the fixture default), or one of the shapes untrusted() refuses."""
    path = os.path.join(home, ".claude.json")
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)
    if shape == "trusting":
        json.dump({"projects": {home: {"hasTrustDialogAccepted": True}}}, open(path, "w"))
    elif shape == "empty":
        open(path, "w").close()
    elif shape == "garbage":
        open(path, "w").write("{not json")
    elif shape == "directory":
        os.makedirs(path)
    elif shape == "no projects":
        json.dump({"numStartups": 1}, open(path, "w"))
    return path


def freeze(repo, session):
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CONFIG_DIR")}
    env.update(HOME=repo, USERPROFILE=repo, LOOP_FLOW=os.path.join(repo, "flow.json"), LOOP_ROLE="worker", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if session:
        env["CLAUDE_CODE_HOST_SESSION_ID"] = session
    done = subprocess.run([sys.executable, goal, "new", "g", "--here", "--goal", "x", "--done", "one"], cwd=repo, capture_output=True, text=True, env=env)
    path = os.path.join(repo, ".git", "loop", "runs", "g.json")
    state = json.load(open(path)) if os.path.exists(path) else {}
    return done.stdout + done.stderr, state


if only in ("", "in"):
    said, state = freeze(fresh(), "local_toy-session")
    print(said)
    check("inside an app session the new goal is bound to it and says BOUND", (state.get("session") or {}).get("id") == "local_toy-session" and state.get("worker") == "session" and "BOUND g" in said)
if only in ("", "out"):
    said, state = freeze(fresh(), "")
    check("outside an app session nothing is bound and nothing is said about it", state.get("slug") == "g" and not state.get("session") and "BOUND" not in said)
if only in ("", "operation"):  # #5616: the governing session is never a worker, whatever id it goes by, and the pool never counts it as free
    repo, scripts = fresh(), os.path.join(root, "skills", "workflow-monitoring", "scripts")
    loop = os.path.join(repo, ".git", "loop")
    os.makedirs(loop, exist_ok=True)
    json.dump({"local_app-toy": {"state": "free", "name": "operation"}, "w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "LOOP_POD", "LOOP_ROLE"))}
    env.update(HOME=repo, USERPROFILE=repo)

    def tool(*args, **more):
        done = subprocess.run([sys.executable] + list(args), cwd=repo, capture_output=True, text=True, env=dict(env, **more))
        return done.returncode, done.stdout + done.stderr

    check("negative control: before it claims, the pool counts both sessions free", "2 free" in tool(os.path.join(scripts, "pool.py"), "status", LOOP_ROLE="worker")[1])
    open(os.path.join(loop, "operation.id"), "w").write("other-op\n")  # another live operation session's id
    code, said = tool(os.path.join(scripts, "operate.py"), "claim", CLAUDE_CODE_SESSION_ID="cli-toy", CLAUDE_CODE_HOST_SESSION_ID="local_app-toy")
    tool(os.path.join(scripts, "operate.py"), "claim", CLAUDE_CODE_SESSION_ID="cli-toy", CLAUDE_CODE_HOST_SESSION_ID="local_app-toy")
    ids = open(os.path.join(loop, "operation.id")).read().split()
    check("claim appends: another operation session's id stays, and a second claim adds no duplicate", ids[0] == "other-op" and len(ids) == len(set(ids)) == 3)
    check("operate.py claim registers both ids of the operation session, its CLI id and its app id (they differ)", code == 0 and {"cli-toy", "local_app-toy"} <= set(ids))
    check("the app id is not counted as free", "1 free" in tool(os.path.join(scripts, "pool.py"), "status", LOOP_ROLE="worker")[1])
    code, said = tool(os.path.join(scripts, "sessions.py"), "bind", "g", "local_app-toy", LOOP_ROLE="worker")
    check("bind refuses the operation session's app id", code != 0 and "never a worker" in said and "local_app-toy" in said)
    code, said = tool(os.path.join(scripts, "sessions.py"), "bind", "g", "w1", LOOP_ROLE="worker")
    check("and still binds an ordinary session", code == 0 and "w1" in said)
sep_name = lambda path: path.replace("\\", "/")
if only in ("", "trust"):  # TD509: a folder with no trust entry in ~/.claude.json is refused, and the file is never written
    repo, scripts = fresh(), os.path.join(root, "skills", "workflow-monitoring", "scripts")
    loop, tree = os.path.join(repo, ".git", "loop"), os.path.join(repo, "tree")
    os.makedirs(os.path.join(loop, "runs"), exist_ok=True)
    os.makedirs(tree)
    json.dump({"slug": "g", "status": "queued", "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
    json.dump({"w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
    claude = os.path.join(repo, ".claude.json")
    env = {k: v for k, v in dict(os.environ, LOOP_ROLE="worker", HOME=repo, USERPROFILE=repo).items() if k != "CLAUDE_CONFIG_DIR"}

    def bind():
        done = subprocess.run([sys.executable, os.path.join(scripts, "sessions.py"), "bind", "g", "w1"], cwd=tree, capture_output=True, text=True, env=env)
        return done.returncode, done.stdout + done.stderr

    code, said = bind()
    check("negative control: with a readable file that trusts the folder, bind goes through", code == 0 and "w1" in said)
    for shape in ("missing", "empty", "garbage", "directory", "no projects"):  # TD509 / #5741: an unreadable trust file trusts nothing
        claude = trust(repo, shape)
        before = open(claude).read() if os.path.isfile(claude) else None
        json.dump({"slug": "g", "status": "queued", "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
        json.dump({"w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
        code, said = bind()
        want = "REFUSED: ask the owner to trust %s (FOLDER_TRUST): open it once in Claude Code; %s must be readable." % (tree, claude)
        sep = lambda t: t.replace("/", os.sep)  # Windows separator effect: expanduser keeps "/" in "~/.claude.json" where os.path.join gives "\"; nothing else is normalised
        check("a %s trust file trusts nothing: bind is refused with the whole plain reason" % shape, code != 0 and sep(want) in sep(said))
        check("and the %s trust file is never written" % shape, (open(claude).read() if os.path.isfile(claude) else None) == before and (shape == "missing") != os.path.exists(claude))
    claude = os.path.join(repo, ".claude.json")
    json.dump({"projects": {os.path.join(repo, "elsewhere"): {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    before = open(claude).read()
    json.dump({"slug": "g", "status": "queued", "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
    json.dump({"w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
    code, said = bind()
    check("a worktree with no trust entry is refused: ask the owner to trust it", code != 0 and "ask the owner to trust" in said and tree in said)
    check("and ~/.claude.json is read only: it is byte for byte as it was", open(claude).read() == before)
    done = subprocess.run([sys.executable, os.path.join(scripts, "sessions.py"), "assign", "g", "--text", "go"], cwd=tree, capture_output=True, text=True, env=env)
    check("assign refuses the same untrusted worktree", done.returncode != 0 and "ask the owner to trust" in done.stdout + done.stderr)
    json.dump({"projects": {repo: {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    code, said = bind()
    check("a trusted parent folder lets it through", code == 0 and "w1" in said)
    for kind in ("new repo, no trust file yet", "upgraded repo, trust file knows only other projects"):  # TD862: the one-time step is named, never taken for the owner
        claude = os.path.join(repo, ".claude.json")
        if kind.startswith("new"):
            os.remove(claude)
        else:
            json.dump({"numStartups": 7, "projects": {os.path.join(repo, "older-repo"): {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
        json.dump({"slug": "g", "status": "queued", "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
        json.dump({"w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
        code, said = bind()
        check("%s: the refusal names the step (open the folder once in Claude Code) and the trust file" % kind, code != 0 and tree in said and "open it once in Claude Code" in said and sep_name(claude) in said.replace("\\", "/"))
        projects = {os.path.join(repo, "older-repo"): {"hasTrustDialogAccepted": True}, tree: {"hasTrustDialogAccepted": True}} if not kind.startswith("new") else {tree: {"hasTrustDialogAccepted": True}}
        json.dump({"numStartups": 8, "projects": projects}, open(claude, "w"))  # what opening the folder once in the app writes
        code, said = bind()
        check("%s: after that one step, bind goes through" % kind, code == 0 and "w1" in said)
    cfg = os.path.join(repo, "cfgdir")  # TD884: CLAUDE_CONFIG_DIR set means Claude keeps its trust file at $CLAUDE_CONFIG_DIR/.claude.json
    os.makedirs(cfg, exist_ok=True)
    env["CLAUDE_CONFIG_DIR"] = cfg
    os.remove(os.path.join(repo, ".claude.json"))
    json.dump({"slug": "g", "status": "queued", "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
    json.dump({"w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
    code, said = bind()
    check("CLAUDE_CONFIG_DIR set with no file there: bind is refused, naming that path", code != 0 and tree in said and sep_name(os.path.join(cfg, ".claude.json")) in said.replace("\\", "/"))
    json.dump({"projects": {tree: {"hasTrustDialogAccepted": True}}}, open(os.path.join(cfg, ".claude.json"), "w"))
    code, said = bind()
    check("CLAUDE_CONFIG_DIR set with a trusting file there and none in HOME: bind goes through", code == 0 and "w1" in said)
    del env["CLAUDE_CONFIG_DIR"]
if only in ("", "restart"):  # TD509: selfcheck names untrusted worktrees of bound sessions and worktree entries whose folder is gone
    repo, scripts = fresh(), os.path.join(root, "skills", "workflow-monitoring", "scripts")
    loop, tree = os.path.join(repo, ".git", "loop"), os.path.join(repo, "tree")
    os.makedirs(os.path.join(loop, "runs"), exist_ok=True)
    os.makedirs(tree)
    json.dump({"slug": "g", "status": "running", "session": {"id": "w1"}, "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
    claude = os.path.join(repo, ".claude.json")
    env = {k: v for k, v in dict(os.environ, LOOP_ROLE="worker", HOME=repo, USERPROFILE=repo).items() if k != "CLAUDE_CONFIG_DIR"}

    def selfcheck():
        done = subprocess.run([sys.executable, os.path.join(scripts, "unattended.py"), "selfcheck"], cwd=repo, capture_output=True, text=True, env=env)
        return done.stdout

    check("negative control: with a readable file that trusts the folder, no folder is called untrusted", "folder trust" not in selfcheck())
    os.remove(claude)
    check("with no ~/.claude.json the bound session's worktree is MISSING folder trust, with its slug", "MISSING folder trust: g" in selfcheck())
    json.dump({"projects": {os.path.join(repo, "elsewhere"): {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    check("a bound session whose worktree has no trust entry is MISSING folder trust, with its slug", "MISSING folder trust: g" in selfcheck())
    json.dump({"projects": {repo: {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    check("a trusted parent clears it", "folder trust" not in selfcheck())
    check("negative control: with every folder present no worktree is called gone", "MISSING worktrees" not in selfcheck())
    gone = os.path.join(repo, "gone")
    subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "--detach", gone], check=True)
    shutil.rmtree(gone)
    check("a worktree entry whose folder is gone is MISSING worktrees, with the fix", "MISSING worktrees: 1 entries whose folder is gone. Fix: git worktree prune" in selfcheck())
if only in ("", "scratch"):  # TD509: scratch lives under ~/.workflow-loop/scratch, and no loop script hard-codes /tmp
    home = tempfile.mkdtemp(prefix="scratch-home-")
    done = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-monitoring", "scripts", "operate.py"), "scratch", "../my goal"], capture_output=True, text=True,
                          env=dict(os.environ, HOME=home, USERPROFILE=home, LOOP_ROLE="worker"))
    path = done.stdout.strip()
    check("operate.py scratch GOAL makes and prints a folder under ~/.workflow-loop/scratch, whatever the goal text", os.path.isdir(path) and os.path.realpath(path).startswith(os.path.realpath(os.path.join(home, ".workflow-loop", "scratch")) + os.sep))
    hard = re.compile(r"""["'](?:/private)?/tmp[/"']""")
    found = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(root, "skills")) for f in fs if f.endswith((".py", ".sh")) and hard.search(open(os.path.join(d, f), errors="replace").read())]
    check("no loop script hard-codes /tmp (%s)" % ", ".join(found), not found)
    check("negative control: a script that does is found", bool(hard.search('open("/tmp/x.log")')))
if only in ("", "wintrust"):  # #5722: the trust test on Windows-style paths, run in a child process with a path shim; the real HOME is never opened
    OLD = '''def untrusted(folder):
    try:
        with open(os.path.join(os.path.expanduser("~"), ".claude.json")) as handle:
            known = json.load(handle)["projects"]
        path = os.path.realpath(folder) + "/"
        return "" if any(v.get("hasTrustDialogAccepted") and path.startswith(os.path.realpath(k).rstrip("/") + "/") for k, v in known.items()) else "REFUSED: ask the owner to trust %s (FOLDER_TRUST)." % folder
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return ""
'''
    CHILD = '''import builtins, importlib.util, json, ntpath, os, sys, types
scripts, old, plan = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
opened, real_open = [], builtins.open
def spy(path, *args, **more):
    opened.append(os.path.abspath(str(path)))
    return real_open(path, *args, **more)
sys.path.insert(0, scripts)
spec = importlib.util.spec_from_file_location("operate", os.path.join(scripts, "operate.py"))
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)
real = os
shim = types.SimpleNamespace(**{k: getattr(real, k) for k in dir(real) if not k.startswith("__")})
shim.sep = chr(92)
shim.path = types.SimpleNamespace(join=real.path.join, expanduser=real.path.expanduser, realpath=ntpath.normpath, normcase=ntpath.normcase)
builtins.open = spy
out = []
for item in plan:
    del opened[:]
    os.environ["HOME"] = os.environ["USERPROFILE"] = item["home"]
    op.os = shim if item["win"] else real
    ns = dict(vars(op))
    ns["os"] = op.os
    exec(old, ns)
    row = {"home": real.path.expanduser("~"), "env": [os.environ["HOME"], os.environ["USERPROFILE"]]}
    for key, fn in (("new", op.untrusted), ("old", ns["untrusted"])):
        try:
            row[key] = fn(item["folder"])
        except Exception as err:
            row[key] = "EXC " + type(err).__name__
    row["opened"] = list(opened)
    out.append(row)
print(json.dumps(out))
'''
    scripts = os.path.join(root, "skills", "workflow-monitoring", "scripts")
    real_file = os.path.abspath(os.path.join(os.path.expanduser("~"), ".claude.json"))
    homes = []

    def home(entries, raw=None):  # a temporary home whose trust file holds ENTRIES (key -> value), or the text RAW
        folder = tempfile.mkdtemp(prefix="wintrust-")
        homes.append(folder)
        with open(os.path.join(folder, ".claude.json"), "w") as handle:
            handle.write(raw if raw is not None else json.dumps({"projects": entries}))
        return folder

    trust = lambda *keys: {k: {"hasTrustDialogAccepted": True} for k in keys}
    root_w = "C:" + chr(92) + "Users" + chr(92) + "x" + chr(92) + "repo"
    bs = chr(92)
    plan = [  # (home, folder, windows paths?)
        (home(trust(root_w)), root_w + bs + ".git" + bs + "loop" + bs + "g", True),
        (home(trust(root_w)), "c:" + bs + "users" + bs + "X" + bs + "REPO" + bs + "wt", True),
        (home(trust(root_w.lower())), root_w + bs + "wt", True),
        (home(trust(root_w)), root_w, True),
        (home(trust(root_w)), "D:" + bs + "other", True),
        (home(trust(root_w)), root_w + "2" + bs + "wt", True),
        (home(trust("C:" + bs)), "C:" + bs + "Users" + bs + "x", True),
        (home({root_w: "yes"}), root_w + bs + "wt", True),
        (home({}, raw="{not json"), root_w + bs + "wt", True),
    ]
    posix_root = tempfile.mkdtemp(prefix="wintrust-posix-")
    homes.append(posix_root)
    for folder in (os.path.join(posix_root, "wt"), posix_root + "2", posix_root + bs, os.path.dirname(posix_root)):
        plan.append((home(trust(posix_root)), folder, False))
    done = subprocess.run([sys.executable, "-I", "-c", CHILD, scripts, OLD, json.dumps([{"home": h, "folder": f, "win": w} for h, f, w in plan])], capture_output=True, text=True, env={k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"})
    try:
        got = json.loads(done.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        got = []
        print("child output: " + (done.stdout + done.stderr)[-400:])
    refused = lambda text: text.startswith("REFUSED: ask the owner to trust")
    ok = len(got) == len(plan)
    new = [r["new"] for r in got] if ok else [""] * len(plan)
    old = [r["old"] for r in got] if ok else [""] * len(plan)
    check("wintrust windows worktree under a trusted root is trusted", ok and new[0] == "")
    check("wintrust drive letter case differs on either side", ok and new[1] == "" and new[2] == "")
    check("wintrust the root itself is trusted", ok and new[3] == "")
    check("wintrust an outside folder is refused", ok and refused(new[4]))
    check("wintrust a prefix only sibling is refused", ok and refused(new[5]))
    check("wintrust a drive root entry trusts a path under it", ok and new[6] == "")
    check("wintrust a non dict entry and a malformed file are refused without raising", ok and refused(new[7]) and refused(new[8]))
    if os.sep == "/":
        check("wintrust posix paths give the same answers as before, including that a sibling named with a trailing backslash stays refused", ok and new[9] == "" and refused(new[10]) and refused(new[11]) and refused(new[12]))
    else:
        check("wintrust posix paths give the same answers as before, including that a sibling named with a trailing backslash stays refused (skipped on a backslash host)", True)
    check("wintrust negative control the old text refuses the windows worktree under its root", ok and refused(old[0]) and old[3] == "")
    home_ok = lambda told, temp, real_home: told == temp and told != real_home
    check("wintrust the child ran on a temporary HOME and USERPROFILE and never the real ones", ok and all(home_ok(r["home"], h, os.path.expanduser("~")) and r["env"] == [h, h] for r, (h, _, _) in zip(got, plan)) and all(real_file not in r["opened"] and os.path.join(h, ".claude.json") in r["opened"] for r, (h, _, _) in zip(got, plan)))
    check("wintrust negative control the home check refuses a child whose HOME is the real home", not home_ok("/the/real/home", "/tmp/a-temporary-home", "/the/real/home"))
    for folder in homes:
        shutil.rmtree(folder, ignore_errors=True)
print("PASS: goal.py new binds an app session's goal" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
