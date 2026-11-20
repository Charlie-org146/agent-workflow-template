#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/pageformat.py
"""#5605: a kept marker re-stamps a guide page (one with the guide marker and no Review line, such as Principles) the way it
re-stamps a How-to-use page, so a goal that changes the code the page maps to passes docs.py check without editing the page.

Without the marker the page still prints STALE; a page whose text changed, or one that is not a guide page, is not re-stamped."""
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-docs", "scripts"))
import audit  # noqa: E402
import docs  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


GUIDE = "<!-- workflow-docs guide -->" + chr(10) + "# Principles" + chr(10) + chr(10) + "Each principle names the requirements that follow it, and the code under it is read from the source tree." + chr(10)
PLAIN = "<!-- workflow-docs -->" + chr(10) + "# Notes" + chr(10) + chr(10) + "A plain page with no Review line and no guide marker, written with enough words to count as written." + chr(10)
with tempfile.TemporaryDirectory() as tmp:
    root = os.path.join(tmp, "repo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    os.makedirs(os.path.join(root, ".loop"))
    os.makedirs(os.path.join(root, "docs", "wiki"))
    os.makedirs(os.path.join(root, "src"))
    os.environ.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")  # CI has no git identity: the re-stamp commit brings its own
    subprocess.run(["git", "config", "user.useConfigOnly", "true"], cwd=root, check=True)
    run = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(a), cwd=root, check=True, capture_output=True)
    for name, text in ((".loop/config.json", "{}"), (".loop/docs.tsv", "Principles" + chr(9) + "src" + chr(10) + "Notes" + chr(9) + "src" + chr(10)),
                       ("docs/wiki/Principles.md", GUIDE), ("docs/wiki/Notes.md", PLAIN), ("src/a.py", "x = 1" + chr(10))):
        with open(os.path.join(root, name), "w") as handle:
            handle.write(text)
    run("add", "-A")
    run("commit", "-q", "-m", "pages")
    with open(os.path.join(root, "src", "a.py"), "w") as handle:
        handle.write("x = 2" + chr(10))
    run("commit", "-q", "-am", "code change")
    here = os.getcwd()
    os.chdir(root)
    stale = lambda page: any(k == "STALE" and p == page for k, p, _ in docs.problems(root, None))
    check(stale("Principles"), "a code change after the page makes the guide page STALE")
    check(stale("Principles"), "negative control: with no kept marker the guide page still prints STALE")
    check(audit.relock(root, "slug", ["Notes"]) == [], "negative control: a page with no Review line that is not a guide page is not re-stamped")
    with open(os.path.join(root, "docs", "wiki", "Principles.md"), "a") as handle:
        handle.write(chr(10) + "A changed line." + chr(10))
    check(audit.relock(root, "slug", ["Principles"]) == [], "negative control: a guide page whose text changed since its commit stays refused")
    run("checkout", "--", "docs/wiki/Principles.md")
    before = open(os.path.join(root, "docs", "wiki", "Principles.md")).read()
    check(audit.relock(root, "slug", ["Principles"]) == ["Principles"], "a stale guide page whose text is as committed is re-stamped by a kept marker")
    check(not stale("Principles"), "after the kept marker the guide page no longer prints STALE")
    check(open(os.path.join(root, "docs", "wiki", "Principles.md")).read() == before, "the guide page itself was not edited")
    check(stale("Notes"), "the other stale page, which has no marker, still prints STALE")
    os.chdir(here)
    for key in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM"):
        os.environ.pop(key)
if failed:
    sys.exit(1)
print("PASS: #5605: a kept marker re-stamps a guide page, and without it the page is still STALE")
