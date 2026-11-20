"""Row settings-render-tables: a lane's render rewrites the Tests tables and nothing else (#3777).

Copies the repo to a scratch git repo and makes the generated blocks stale where they live now (the approved format moved them: the
Settings block is in How-to-use-Setup.md, the README holds only its Built-with line, and Home holds no block), the state a lane finds
when the scripts it runs are older than the page. Then it checks that `criteria.py render --tables` leaves README.md, Home.md and the
stale page as they were and that a plain `render` still repairs them; the negative control is that the same check, run after a plain
render (which does rewrite them), reports a change. Same on every platform; exit 0 when all hold."""
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEEP = ("README.md", "docs", ".loop", "skills")


def run(*cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def read(path):
    with open(path, newline="") as handle:
        return handle.read()


def unchanged(pages, before):
    """README.md, Home.md and the stale page are byte for byte what they were."""
    return [read(page) for page in pages] == before


def main():
    scratch = tempfile.mkdtemp(prefix="render-tables-")
    try:
        for name in KEEP:
            src = os.path.join(TOP, name)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(scratch, name), ignore=shutil.ignore_patterns(".git", "__pycache__", "worktrees"))
            elif os.path.exists(src):
                shutil.copy(src, scratch)
        run("git", "init", "-q", cwd=scratch)
        readme, home, setup = (os.path.join(scratch, "README.md"), os.path.join(scratch, "docs", "wiki", "Home.md"),
                               os.path.join(scratch, "docs", "wiki", "How-to-use-Setup.md"))
        pages = [readme, home, setup]
        text = read(readme)
        if "<!-- template:begin -->" not in text:
            print("FAIL: %s has no template block to make stale" % readme)
            return 1
        with open(readme, "w", newline="") as handle:
            handle.write(re.sub(r"(<!-- template:begin -->\n)[^\n]*", r"\1Built with the [old/repo](https://github.com/old/repo) workflow loop.", text, count=1))
        text = read(setup)
        if "| `automation` |" not in text:
            print("FAIL: %s has no automation row to make stale" % setup)
            return 1
        with open(setup, "w", newline="") as handle:
            handle.write("\n".join(line for line in text.split("\n") if not line.startswith("| `automation` |")))
        before = [read(page) for page in pages]
        criteria = os.path.join(scratch, "skills", "workflow-docs", "scripts", "criteria.py")
        tables = run(sys.executable, criteria, "render", "--tables", cwd=scratch)
        if tables.returncode or not unchanged(pages, before):
            print("FAIL: render --tables changed README.md, Home.md or the stale page (exit %d): %s" % (tables.returncode, tables.stdout + tables.stderr))
            return 1
        full = run(sys.executable, criteria, "render", cwd=scratch)
        if full.returncode or unchanged(pages, before):
            print("FAIL: a plain render no longer repairs the stale blocks (exit %d): %s" % (full.returncode, full.stdout + full.stderr))
            return 1
        if unchanged(pages, before):  # negative control: after a render that does rewrite them, the same check must see a change
            print("FAIL: negative control: the unchanged check did not notice a render that rewrote README.md and the stale page")
            return 1
        audit = run(sys.executable, os.path.join(scratch, "skills", "workflow-docs", "scripts", "docs.py"), "audit", "--dry-run", cwd=scratch)
        if "Traceback" in audit.stderr:
            print("FAIL: docs.py audit raised: %s" % audit.stderr[-300:])
            return 1
        print("OK: render --tables left README.md, Home.md and the stale blocks alone; a plain render repaired them; the control saw the rewrite")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
