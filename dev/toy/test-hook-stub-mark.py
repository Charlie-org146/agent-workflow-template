#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-setup/scripts/seed.py skills/workflow-setup/scripts/setup.py
"""hook-stub-mark (#4506, SET-1): the hooks `setup --git-hooks` writes are read back as its own; someone else's hook is not.

Setup refuses to write hooks from inside a goal's worktree, so this copies workflow-setup and workflow-delivery to a temp folder
and runs setup from there on temp repos. First repo: write the hooks, then check them: none is foreign. Second repo: a hook
someone else wrote is reported foreign and its text is left byte for byte as it was."""
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.dont_write_bytecode = True
HOOKS = ("pre-commit", "commit-msg", "pre-push")
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def setup(script, repo, *args):
    done = subprocess.run([sys.executable, "-B", script, "--repo", repo, "--git-hooks"] + list(args), capture_output=True, text=True)
    return done.stdout + done.stderr


def states(text):
    return {line.split(":")[0].split()[1]: line.split(": ", 1)[1].strip() for line in text.splitlines() if line.startswith("hook ")}


with tempfile.TemporaryDirectory() as tmp:
    for skill in ("workflow-setup", "workflow-delivery"):
        shutil.copytree(os.path.join(root, "skills", skill), os.path.join(tmp, skill), ignore=shutil.ignore_patterns("__pycache__"))
    script = os.path.join(tmp, "workflow-setup", "scripts", "setup.py")
    mine, other = os.path.join(tmp, "mine"), os.path.join(tmp, "other")
    for repo in (mine, other):
        subprocess.run(["git", "init", "-q", repo], check=True)

    written = setup(script, mine)
    check(all("HOOK %s: written" % name in written for name in HOOKS), "setup --git-hooks writes the three hooks")
    seen = states(setup(script, mine, "--check"))
    check(all(seen.get(name) == "installed" for name in HOOKS), "the hooks just written are read back as installed: %s" % seen)
    check(not any(state == "foreign" for state in seen.values()), "none of the hooks setup wrote is reported foreign")
    again = setup(script, mine)
    check(all("HOOK %s: written" % name in again for name in HOOKS), "a second run recognizes its own hooks and rewrites them")

    theirs = "#!/bin/sh\necho a hook someone else wrote\n"
    path = os.path.join(other, ".git", "hooks", "commit-msg")
    with open(path, "w", newline="\n") as handle:
        handle.write(theirs)
    out = setup(script, other)
    check("HOOK commit-msg: left alone, it is not ours" in out, "setup says the hook someone else wrote is left alone")
    check(states(setup(script, other, "--check")).get("commit-msg") == "foreign", "--check still reports that hook as foreign")
    with open(path, newline="") as handle:
        check(handle.read() == theirs, "the foreign hook's text is unchanged")

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
