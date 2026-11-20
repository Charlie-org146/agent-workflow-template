#!/usr/bin/env python3
# reads: dev/package.py
"""dev/package.py --static (the pull request check): the release's static rules without the --help pass or the ZIP.
A 101st shipped file fails it on the file count, and so does the 105-file state main's release push once held; the real tree passes it;
a script that fails its own --help does not fail it (the full run still does)."""
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def package(tree, *flags):
    done = subprocess.run([sys.executable, os.path.join(root, "dev", "package.py"), "--root", tree] + list(flags), capture_output=True, text=True, timeout=120)
    return done.returncode, done.stdout


def copy_of_tree(tmp):
    names = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, check=True).stdout.decode().split("\0")
    for name in filter(os.path.lexists, [os.path.join(root, n) for n in names if n]):
        target = os.path.join(tmp, os.path.relpath(name, root))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(name, target, follow_symlinks=False)
    for step in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "t"]):
        subprocess.run(["git", "-C", tmp] + step, capture_output=True, check=True)


def add_files(tmp, count):
    for n in range(count):
        path = os.path.join(tmp, "skills", "workflow-docs", "references", "extra%d.md" % n)
        with open(path, "w") as handle:
            handle.write("extra\n")
        subprocess.run(["git", "-C", tmp, "add", path], capture_output=True, check=True)


code, out = package(root, "--static")
check("the real tree passes the static rules: %s" % out.strip().splitlines()[-1:], code == 0 and "static rules hold" in out)
with tempfile.TemporaryDirectory() as tmp:
    copy_of_tree(tmp)
    code, out = package(tmp, "--static")
    base = len([l for l in out.splitlines() if l.startswith("PASS")]) and int(out.split("PASS: ")[1].split(" ")[0]) if code == 0 else 0
    check("a copy of the tree passes too (%d files)" % base, code == 0 and base >= 1)
    add_files(tmp, 101 - base)
    code, out = package(tmp, "--static")
    check("a tree of 101 files fails the static rules on the file count", code == 1 and "Size: 101 files, at most 100 allowed" in out)
    add_files_more = 5 - 1
    for n in range(100, 100 + add_files_more):
        path = os.path.join(tmp, "skills", "workflow-docs", "references", "more%d.md" % n)
        open(path, "w").write("extra\n")
        subprocess.run(["git", "-C", tmp, "add", path], capture_output=True, check=True)
    code, out = package(tmp, "--static")
    check("the 105-file state replayed fails it", code == 1 and "Size: 105 files, at most 100 allowed" in out)
with tempfile.TemporaryDirectory() as tmp:
    copy_of_tree(tmp)
    script = os.path.join(tmp, "skills", "workflow-docs", "scripts", "counting.py")
    with open(script, "a") as handle:
        handle.write("\nimport sys\nif '--help' in sys.argv:\n    sys.exit(3)\n")
    subprocess.run(["git", "-C", tmp, "add", "-A"], capture_output=True, check=True)
    code, out = package(tmp, "--static")
    check("a script that fails its own --help does not fail the static rules", code == 0)
    code, out = package(tmp, "--out", os.path.join(tmp, "z.zip"))
    check("negative control: the full run does fail it (--help pass)", code == 1 and "does not run alone" in out)
sys.exit(1 if fails else 0)
