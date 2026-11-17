#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/narrow.py
"""affected-deleted (#4554, REG-4): a deleted file that isn't NO_EFFECT is a real change, so the root runners still run;
a change only to NO_EFFECT files (a deleted or edited VERSION) still reaches none.

The toy repo has three rows: ta reads src/a.txt, tb reads src/b.txt, and tc is a root runner (`cd "$here"`). Each run of
`lanes_cli.py affected` is checked for the rows it picks."""
import os
import re
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CLI = os.path.join(root, "skills", "workflow-regression", "scripts", "lanes_cli.py")
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def write(base, rel, text):
    os.makedirs(os.path.dirname(os.path.join(base, rel)) or base, exist_ok=True)
    with open(os.path.join(base, rel), "w", newline="\n") as handle:
        handle.write(text)


def affected(repo, *paths):
    """The ids `affected` picks for paths, as a sorted list, and its output."""
    done = subprocess.run([sys.executable, "-B", CLI, "affected"] + list(paths), cwd=repo, capture_output=True, text=True)
    found = re.search(r"^AFFECTED \d+ of \d+ rows \(([^)]*)\)", done.stdout, re.M)
    return sorted(x for x in (found.group(1) if found else "?").split(", ") if x), done.stdout + done.stderr


with tempfile.TemporaryDirectory() as repo:
    git = lambda *a: subprocess.run(["git", "-c", "user.name=Toy", "-c", "user.email=t@example.test", "-c", "core.autocrlf=false"]
                                    + list(a), cwd=repo, capture_output=True, text=True)
    git("init", "-q", "-b", "main")
    write(repo, "src/a.txt", "a\n")
    write(repo, "src/b.txt", "b\n")
    write(repo, "VERSION", "1.0.0\n")
    write(repo, "dev/ta.sh", "#!/bin/bash\n# reads: src/a.txt\ncat src/a.txt\n")
    write(repo, "dev/tb.sh", "#!/bin/bash\n# reads: src/b.txt\ncat src/b.txt\n")
    write(repo, "dev/tc.sh", '#!/bin/bash\n# reads: src/a.txt\ncd "$here" && cat src/a.txt\n')
    write(repo, ".loop/regression.tsv", "# id\tlevel\tcommand\nta\tland\tbash dev/ta.sh\ntb\tland\tbash dev/tb.sh\ntc\tland\tbash dev/tc.sh\n")
    git("add", "-A")
    git("commit", "-qm", "rows")
    ids, said = affected(repo, "src/b.txt")
    check(ids == ["tb", "tc"], "an edited real file reaches its row and the root runner (%s)" % ids)
    ids, said = affected(repo, "VERSION")
    check(ids == [], "negative control: an edited VERSION (NO_EFFECT) reaches no row (%s)" % ids)
    os.remove(os.path.join(repo, "src", "b.txt"))
    ids, said = affected(repo, "src/b.txt")
    check(ids == ["tb", "tc"] and "DELETED" in said, "a deleted real file reaches the rows that name it and the root runner (%s)" % ids)
    os.remove(os.path.join(repo, "VERSION"))
    ids, said = affected(repo, "VERSION")
    check(ids == [], "negative control: a deleted VERSION (NO_EFFECT) still reaches no row (%s)" % ids)
    write(repo, ".loop/goals/g.md", "goal\n")
    git("add", "-A")
    git("commit", "-qm", "goal file")
    ids, said = affected(repo, ".loop/goals/g.md")
    check(ids == [], "negative control: an edited goal file under .loop/goals/ (NO_EFFECT, in a folder) reaches no row (%s)" % ids)
    os.remove(os.path.join(repo, ".loop", "goals", "g.md"))
    ids, said = affected(repo, ".loop/goals/g.md")
    check(ids == [] and "DELETED" not in said, "negative control: a deleted goal file under .loop/goals/ still reaches no row (%s)" % ids)
sys.exit(1 if failed else 0)
