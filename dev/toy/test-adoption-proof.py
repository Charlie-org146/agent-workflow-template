#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-setup/scripts/setup.py skills/workflow-setup/scripts/agents.py skills/workflow-setup/scripts/sync.py
"""adoption (v1.0.0 item 4): setup's adoption is proven by one case per request, each a plain exit code (0 passes), run as
`python3 dev/toy/test-adoption-proof.py CASE`. Nothing here touches GitHub or a real connector: gh, git hooks and the
connectors are fakes in temp folders. Cases: stamp (#2877), ... (added as each lands)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS = os.path.join(ROOT, "skills")


def run(cmd, cwd, env=None, text=None):
    done = subprocess.run(cmd, cwd=cwd, env=env, input=text, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def git(cwd, *args):
    return run(["git", *args], cwd)[1].strip()


def repo(tmp, name="adopted"):
    path = os.path.join(tmp, name)
    os.makedirs(path)
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.email", "toy@example.test")
    git(path, "config", "user.name", "toy")
    with open(os.path.join(path, "app.py"), "w") as handle:
        handle.write("print('hi')\n")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "init")
    return path


def package(tmp, version="9.8.7"):
    """A copy of the skills with the stamp an installed package carries (workflow-package.json beside them)."""
    target = os.path.join(tmp, "pkg", "skills")
    shutil.copytree(SKILLS, target, ignore=shutil.ignore_patterns("__pycache__"))
    with open(os.path.join(target, "workflow-package.json"), "w") as handle:
        json.dump({"version": version}, handle)
    return target


def env_of(tmp):
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
    env.update(HOME=tmp, USERPROFILE=tmp, LOOP_NO_GIT_HOOKS="1", GH_PROMPT_DISABLED="1")
    return env


def case_stamp():
    """#2877: a repo set up by an installed package carries its template_version, so update --apply has nothing to stamp."""
    with tempfile.TemporaryDirectory() as tmp:
        skills, adopted = package(tmp), repo(tmp)
        code, out = run([sys.executable, os.path.join(skills, "workflow-setup", "scripts", "setup.py"), "--no-health", "--no-issues"],
                        adopted, env_of(tmp))
        branch = git(adopted, "show", "workflow-setup:.loop/config.json")
        held = json.loads(branch).get("template_version")
        print("setup exit %d; template_version %r" % (code, held))
        return code == 0 and held == "9.8.7"


CASES = {"stamp": case_stamp}

if __name__ == "__main__":
    names = sys.argv[1:] or sorted(CASES)
    bad = [n for n in names if not CASES[n]()]
    print("FAILED: " + ", ".join(bad) if bad else "ALL PASS")
    raise SystemExit(1 if bad else 0)
