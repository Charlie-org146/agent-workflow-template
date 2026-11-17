#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/operate.py skills/workflow-docs/scripts/audit.py skills/workflow-release/scripts/merge.py
# reads: skills/workflow-docs/scripts/render.py skills/workflow-docs/scripts/counting.py skills/workflow-setup/scripts/setup.py
"""DOC-19, issue 4632: operate.py apply (the call merge.py makes before it merges) also re-renders the generated blocks and
tables of a pushed goal branch that differ from a fresh render only because something else moved, in one wiki-only commit that
merge.py accepts; a hand edit inside a generated block is still refused. Builds a throwaway repo with a bare origin: no model,
no network.

1. A branch whose README Settings block is stale because main's was rendered by an older template: apply re-renders it, the
   head moves by wiki-only changes (operate.py wiki-only), and docs.py check --own on the new head reports no STALE line.
2. The same branch with a hand edit inside the Settings block: apply leaves it, and check still says STALE.
3. A branch that added a regression row without re-rendering: apply re-renders the Tests tables."""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SK = os.path.join(root, "skills")
DOCS = os.path.join(SK, "workflow-docs", "scripts", "docs.py")
OPERATE = os.path.join(SK, "workflow-monitoring", "scripts", "operate.py")
REG = os.path.join(SK, "workflow-regression", "scripts", "regression.py")
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


_keep = os.environ.get("TOY_KEEP")
with (tempfile.TemporaryDirectory() if not _keep else __import__("contextlib").nullcontext(_keep)) as tmp:
    home = os.path.join(tmp, "home")
    os.makedirs(home)
    env = dict(os.environ, HOME=home, USERPROFILE=home, PYTHONDONTWRITEBYTECODE="1", GIT_TERMINAL_PROMPT="0")
    for key in ("LOOP_SESSION_TOOL", "LOOP_OPERATION_SESSION", "LOOP_BATCH", "LOOP_ROLE"):
        env.pop(key, None)

    def run(*args, cwd, ok=True):
        done = subprocess.run(list(args), cwd=cwd, env=env, capture_output=True, text=True)
        if ok and done.returncode and args[0] != "git":
            print("  (%s exited %d: %s)" % (os.path.basename(args[1]) if len(args) > 1 else args[0], done.returncode, (done.stdout + done.stderr).strip()[-200:]))
        return done

    def git(*args, cwd):
        return run("git", *args, cwd=cwd).stdout.strip()

    made = run("bash", os.path.join(root, "dev", "toy", "make.sh"), os.path.join(tmp, "toy"), cwd=tmp)
    repo = os.path.join(tmp, "toy", "repo")
    if made.returncode or not os.path.isdir(repo):
        print("FAIL: dev/toy/make.sh did not build the fixture: " + made.stderr[-200:])
        sys.exit(1)
    for pair in (("user.email", "t@example.test"), ("user.name", "t"), ("core.autocrlf", "false")):
        git("config", *pair, cwd=repo)
    os.makedirs(os.path.join(repo, "engine"))
    with open(os.path.join(repo, "engine", "core.py"), "w", newline="\n") as handle:
        handle.write("def run():\n    return 1\n")
    git("add", "-A", cwd=repo)
    git("commit", "-qm", "A code folder", cwd=repo)
    run(sys.executable, os.path.join(SK, "workflow-setup", "scripts", "setup.py"), cwd=repo)
    git("switch", "-q", "main", cwd=repo)
    git("merge", "-q", "--no-edit", "workflow-setup", cwd=repo)
    bare = os.path.join(tmp, "origin.git")
    run("git", "init", "-q", "--bare", bare, cwd=tmp)
    git("remote", "add", "origin", bare, cwd=repo)
    git("push", "-q", "origin", "main", cwd=repo)
    git("remote", "set-head", "origin", "main", cwd=repo)

    def text(path, name):
        with open(os.path.join(path, name), newline="") as handle:
            return handle.read()

    def write(path, name, body):
        with open(os.path.join(path, name), "w", newline="") as handle:
            handle.write(body)

    # main's Settings block was rendered by an older template: one description reads differently
    old = "The branch goals start from and pull requests target."
    readme = text(repo, "README.md")
    check(old in readme, "the fixture's README holds the Settings block")
    write(repo, "README.md", readme.replace(old, "The branch goals start from."))
    git("commit", "-qam", "README rendered by an older template", cwd=repo)
    git("push", "-q", "origin", "main", cwd=repo)

    def branch(name, edit):
        git("switch", "-q", "-c", "loop/" + name, "main", cwd=repo)
        edit()
        git("add", "-A", cwd=repo)
        git("commit", "-qm", "Goal " + name, cwd=repo)
        git("push", "-q", "origin", "loop/" + name, cwd=repo)
        git("switch", "-q", "main", cwd=repo)

    def stale_on(name):
        """The STALE lines docs.py check --own gives the branch's pushed head, in a throwaway checkout."""
        tree = os.path.join(tmp, "tree-" + name)
        git("worktree", "add", "-q", "--detach", tree, "origin/loop/" + name, cwd=repo)
        lines = [l for l in run(sys.executable, DOCS, "check", "--own", "origin/main", cwd=tree).stdout.splitlines() if l.startswith("STALE ")]
        git("worktree", "remove", "--force", tree, cwd=repo)
        return lines

    def applied(name):
        before = git("rev-parse", "origin/loop/" + name, cwd=repo)
        done = run(sys.executable, OPERATE, "apply", name, "loop/" + name, cwd=repo)
        git("fetch", "-q", "origin", cwd=repo)
        return before, git("rev-parse", "origin/loop/" + name, cwd=repo), done.stdout

    # 1. a template reword leaves the branch's Settings block stale; apply re-renders it
    def code():
        with open(os.path.join(repo, "engine", "core.py"), "a", newline="\n") as handle:
            handle.write("# a goal's change\n")


    def real_code():
        with open(os.path.join(repo, "engine", "core.py"), "a", newline="\n") as handle:
            handle.write("\n\ndef extra():\n    return 2\n")  # real code: a comment-only change stales no page

    branch("one", code)
    check(any("Settings" in l for l in stale_on("one")), "the branch is STALE on its Settings block before apply")
    before, after, said = applied("one")
    check(before != after and "RERENDERED README.md" in said, "apply pushes one commit that re-renders README.md (%s)" % said.strip()[:100])
    check(run(sys.executable, OPERATE, "wiki-only", before, after, cwd=repo).returncode == 0, "merge.py accepts the new head: it moved by README blocks and wiki pages only")
    check(not stale_on("one"), "docs.py check --own on the new head reports no STALE line")

    # 2. a hand edit inside the block is refused
    def hand():
        write(repo, "README.md", text(repo, "README.md").replace("| `base` |", "| `base` | HAND EDIT |", 1))

    branch("two", hand)
    before, after, said = applied("two")
    check(before == after, "negative control: apply pushes nothing for a hand edit inside a generated block")
    check(any("Settings" in l for l in stale_on("two")), "negative control: the hand-edited branch is still STALE")

    # 3. a regression row added without a render: the Tests tables are re-rendered
    def row():
        run(sys.executable, REG, "add", "toy-row", "--level", "land", "--command", "true", "--goal", "ENG-1", "--describe", "Given a toy, when it runs, then it passes.", cwd=repo)

    branch("three", row)
    stale = stale_on("three")
    before, after, said = applied("three")
    check(not stale or (before != after and "RERENDERED" in said and "Tests" in said), "a branch with a new regression row and no render gets its Tests tables re-rendered (%s)" % said.strip()[:80])

    # 4. a How-to-use page made stale only by its feature's code is re-stamped by the same apply run
    git("switch", "-q", "main", cwd=repo)
    page = "# How to use Engine\n\n## What it's for\n\nThe calculator engine.\n\n## How to reach or run it\n\nSay what you want to the agent.\n\n## Links\n\n- PRD page: [Engine](Engine)\n"
    write(repo, "docs/wiki/How-to-use-Engine.md", "<!-- workflow-docs -->\n" + page)
    engine = text(repo, "docs/wiki/Engine.md").replace(chr(13) + chr(10), chr(10))
    write(repo, "docs/wiki/Engine.md", engine.replace("# Engine\n", "# Engine\n\nHow to use: [How-to-use-Engine](How-to-use-Engine)\n", 1))
    git("add", "-A", cwd=repo)
    git("commit", "-qm", "A How-to-use page for Engine", cwd=repo)
    git("push", "-q", "origin", "main", cwd=repo)
    branch("four", real_code)
    check(any("How-to-use-Engine" in l for l in stale_on("four")), "the branch is STALE on How-to-use-Engine through the feature's code")
    before, after, said = applied("four")
    check(before != after and "RESTAMPED How-to-use-Engine" in said, "the same apply run re-stamps the How-to-use page (%s)" % said.strip()[:80])
    check(not any("How-to-use-Engine" in l for l in stale_on("four")), "the How-to-use page is no longer STALE on the new head")
    check(run(sys.executable, OPERATE, "wiki-only", before, after, cwd=repo).returncode == 0, "merge.py accepts the head that carries the How-to-use re-stamp")

sys.exit(1 if failed else 0)
