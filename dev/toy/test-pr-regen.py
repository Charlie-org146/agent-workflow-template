#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/regen.py skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/scripts/goal.py
"""pr-regen (DEL-25.4): generated files are made the same way every time and never rewritten at PR time.

Done: at goal.py pr, fit.regen only CHECKS the generated files (START.md, CLAUDE.md and AGENTS.md, the wiki pages). On a
current tree HEAD is unchanged and nothing is written; a stale START.md is refused with REGEN_STALE, the file named and the
ordered Fix, HEAD and the tree untouched; running the Fix clears it and a second run is a no-op; a page that needs an agent
is named as such; the version bump runs after the check, so a bump (pr_bumps_version on) is the only commit pr can make.
The fixture is a clone of this checkout's committed HEAD. usage: test-pr-regen.py"""
import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-delivery", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import regen as made  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


tmp = tempfile.mkdtemp(prefix="pr-regen-")
home = os.path.join(tmp, "home")
os.makedirs(home)
env = dict(os.environ, HOME=home, USERPROFILE=home, GIT_TERMINAL_PROMPT="0", PYTHONDONTWRITEBYTECODE="1", LOOP_ROLE="worker")
for var in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
    env.pop(var, None)
clone = os.path.join(tmp, "clone")
subprocess.run(["git", "clone", "-q", "--no-hardlinks", root, clone], check=True, capture_output=True, env=env)
SLUG = "toy-regen"
subprocess.run(["git", "checkout", "-q", "-b", "loop/" + SLUG], cwd=clone, check=True, capture_output=True, env=env)
subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=clone, check=True, capture_output=True, env=env)  # the base is this very head: no page is the goal's own  # a goal's branch: only its own pages count


class G:
    """The slice of goal.py that fit.regen and regen.regen use."""

    def git(self, *args, check=True):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(args), cwd=clone,
                              capture_output=True, text=True, env=env).stdout.strip()

    quick_wiki = False  # after the first case the wiki tool (about 35 s a run) is answered "current"

    def run(self, args, cwd=None, check=False):
        if self.quick_wiki and args[1:2] and args[1].endswith("wiki.py"):
            return subprocess.CompletedProcess(args, 0, "WIKI CURRENT: no stale page for %s" % SLUG, "")
        return subprocess.run(args, cwd=cwd or clone, capture_output=True, text=True, env=env)

    def no(self, text):
        sys.exit("REFUSED: " + text)


g = G()
head = g.git("rev-parse", "HEAD")
entry = os.path.join(root, "skills", "workflow-docs", "scripts", "entry.py")


def real_entry(args):
    return subprocess.run(args, cwd=clone, capture_output=True, text=True, env=env)


def regen(call=None):
    """(HEAD regen returned or None when it refused, what it printed or refused with)."""
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            got = (call or made.regen)(g, SLUG)
    except SystemExit as stop:
        return None, str(stop.code)
    return got, out.getvalue()


def tree_clean():
    return not g.git("status", "--porcelain")


# the real wiki tool, read-only: whatever it finds (a bare clone has no releases, so it may call a page stale), it writes nothing
made.check(g, SLUG)
check(g.git("rev-parse", "HEAD") == head and tree_clean(), "the real wiki.py prepare (no --commit) and entry.py check write nothing and commit nothing")
g.quick_wiki = True

# a current tree: nothing is written, HEAD is the same, no note
got, said = regen()
check(got == head and g.git("rev-parse", "HEAD") == head and tree_clean() and "REGEN_STALE" not in said, "a current tree: regen returns the same HEAD, writes nothing and prints no note (%s)" % said[:120])

# a stale START.md: refused, never rewritten, the head unchanged
start = os.path.join(clone, ".loop", "START.md")
with open(start, "a", newline="\n") as handle:
    handle.write("\nA hand edit the generator does not make.\n")
g.git("commit", "-qam", "stale START.md")
stale_head = g.git("rev-parse", "HEAD")
before = open(start, newline="").read()
got, said = regen()
check(got is None and said.startswith("REFUSED: REGEN_STALE") and ".loop/START.md" in said, "a stale START.md is refused, the file named: %s" % said[:120])
check(all(token in said for token in ("1. python3 skills/workflow-docs/scripts/entry.py write", "2. python3 skills/workflow-release/scripts/wiki.py prepare %s --commit" % SLUG, "3. git commit", "4. re-run the lane")) and
      said.index("1. python3") < said.index("2. python3") < said.index("3. git commit") < said.index("4. re-run"), "the refusal's Fix is the four steps, in order, naming commands that exist")
check(g.git("rev-parse", "HEAD") == stale_head and tree_clean() and open(start, newline="").read() == before, "regen changes no file and makes no commit")
check("quick.py" not in said, "the refusal names no file that adopted repos lack (dev/ is not shipped)")

# the Fix clears it, and a second run is a no-op
done = real_entry([sys.executable, entry, "write"])
g.git("commit", "-qam", "regenerated")
fixed = g.git("rev-parse", "HEAD")
got, said = regen()
check(done.returncode == 0 and got == fixed and "REGEN_STALE" not in said, "after the Fix (entry.py write, commit) regen is quiet at the new HEAD")
got2, said2 = regen()
check(got2 == fixed and g.git("rev-parse", "HEAD") == fixed and tree_clean() and "REGEN_STALE" not in said2, "a second run changes nothing")

# a page that needs an agent is named as such (the wiki tool's line is stubbed)
real_run = g.run
g.run = lambda args, cwd=None, check=False: (subprocess.CompletedProcess(args, 1, "REWRITE Home: STALE (its sources changed)\nNEXT: update Home\n", "")
                                            if args[1:2] and args[1].endswith("wiki.py") else real_run(args, cwd, check))
got, said = regen()
check(got == fixed and "Home (needs an agent to rewrite)" in said and said.startswith("NOTE: REGEN_STALE"), "a REWRITE page is named in the note as needing an agent, and regen still returns HEAD: %s" % said[:120])
g.run = real_run

# fit.regen is the shipped check for every repo, an adopted one too: it names the stale file and commits nothing (DEL-25.4)
try:
    import fit
except ImportError as err:
    print("NOTE: the fit.regen case did NOT run here (%s); it runs on Mac, Linux and CI" % err)
else:
    with open(start, "a", newline=chr(10)) as handle:
        handle.write(chr(10) + "Another hand edit." + chr(10))
    g.git("commit", "-qam", "stale again")
    stale = g.git("rev-parse", "HEAD")
    got, said = regen(fit.regen)
    check(got is None and g.git("rev-parse", "HEAD") == stale and tree_clean() and said.startswith("REFUSED: REGEN_STALE"), "fit.regen refuses the stale START.md and commits nothing, with or without a dev/ folder")

# the order in goal.py pr: the check first, the version bump after it (so a bump is the only commit pr may make)
text = open(os.path.join(scripts, "goal.py"), encoding="utf-8").read()
check(re.search(r"head = role\.bump_version\(ME, state, fit\.regen\(ME, slug\)\)", text) is not None, "goal.py pr runs fit.regen before role.bump_version")
fit_text = open(os.path.join(scripts, "fit.py"), encoding="utf-8").read()
check("made.regen(g, slug)" in fit_text and "dev(" not in fit_text, "fit.regen calls the shipped regen.regen and no dev/ loader is left")

shutil.rmtree(tmp, ignore_errors=True)
print("FAIL: %d case(s): %s" % (len(failed), "; ".join(failed)[:300]) if failed else "ALL PASS")
sys.exit(1 if failed else 0)
