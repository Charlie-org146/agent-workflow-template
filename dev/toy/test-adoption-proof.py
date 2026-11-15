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


FAKE_GH = """import os, subprocess, sys
a = sys.argv[1:]
if a[:2] == ["auth", "status"]:
    sys.exit(1 if os.environ.get("TOY_GH_OUT") else 0)
if a[:2] == ["repo", "list"]:
    print("o/one private 2026-11-14T00:00:00Z")
    print("o/two public 2026-11-13T00:00:00Z")
    sys.exit(0)
if a[:2] == ["repo", "clone"]:
    sys.exit(subprocess.run(["git", "clone", "-q", os.path.join(os.environ["TOY_BARES"], a[2].split("/")[-1] + ".git"), a[3]]).returncode)
sys.exit(1)
"""


def fake_gh(tmp):
    """A gh that answers auth status, repo list and repo clone from local bare repos; first on PATH and in LOOP_GH."""
    folder = os.path.join(tmp, "fakebin")
    os.makedirs(folder)
    script = os.path.join(folder, "fakegh.py")
    with open(script, "w") as handle:
        handle.write(FAKE_GH)
    wrapper = os.path.join(folder, "gh.cmd" if os.name == "nt" else "gh")
    with open(wrapper, "w") as handle:
        handle.write('@"%s" "%s" %%*\r\n' % (sys.executable, script) if os.name == "nt" else '#!/bin/sh\nexec "%s" "%s" "$@"\n' % (sys.executable, script))
    os.chmod(wrapper, 0o755)
    env = env_of(tmp)
    env.update(PATH=folder + os.pathsep + os.environ["PATH"], LOOP_GH="%s %s" % (sys.executable, script), LOOP_NO_ISSUES="1", LOOP_NO_HEALTH="1",
               TOY_BARES=os.path.join(tmp, "bares"), GIT_AUTHOR_NAME="toy", GIT_AUTHOR_EMAIL="toy@example.test",
               GIT_COMMITTER_NAME="toy", GIT_COMMITTER_EMAIL="toy@example.test")
    return env


def tool(tmp, skill, script):
    skills = os.path.join(tmp, "pkg", "skills")
    if not os.path.isdir(skills):
        package(tmp)
    return os.path.join(skills, skill, "scripts", script)


def case_prereq():
    """#1408: one checklist before anything is written, each gap with its exact fix, printed by setup itself."""
    with tempfile.TemporaryDirectory() as tmp:
        env = fake_gh(tmp)
        unattended = tool(tmp, "workflow-monitoring", "unattended.py")
        code, out = run([sys.executable, unattended, "prerequisites"], tmp, env)
        env["TOY_GH_OUT"] = "1"
        gap_code, gap = run([sys.executable, unattended, "prerequisites"], tmp, env)
        del env["TOY_GH_OUT"]
        _, setup = run([sys.executable, tool(tmp, "workflow-setup", "setup.py"), "--no-health", "--no-issues"], repo(tmp), env)
        print(out.strip().replace("\n", " | "), "||", gap_code, gap.strip().replace("\n", " | "))
        return ("OK gh signed in" in out and "OK git" in out and gap_code == 1 and "MISSING gh signed in. Fix: run gh auth login --web" in gap
                and "PREREQUISITES:" in setup and setup.index("PREREQUISITES:") < setup.index("WROTE the adoption"))


def home(tmp):
    """A machine that matches the golden first adoption: two followed repos on the installed version, the private settings, one
    copy of each hook in the operation repo."""
    folder = os.path.join(tmp, ".workflow-loop")
    os.makedirs(folder)
    followed = [repo(tmp, "followed-%d" % n) for n in (1, 2)]
    for path in followed:
        os.makedirs(os.path.join(path, ".loop"))
        with open(os.path.join(path, ".loop", "config.json"), "w") as handle:
            json.dump({"template_version": "9.8.7"}, handle)
    with open(os.path.join(folder, "repos"), "w") as handle:
        handle.write("".join(p + "\n" for p in followed))
    with open(os.path.join(folder, "flow.json"), "w") as handle:
        handle.write("{}")
    with open(os.path.join(folder, "private-names"), "w") as handle:
        handle.write("# names\nsecret-project\n")
    operation = repo(tmp, "operation")
    os.makedirs(os.path.join(operation, ".claude"))
    with open(os.path.join(operation, ".claude", "settings.local.json"), "w") as handle:
        json.dump({"hooks": {"a": "reply_hook.py", "b": "govern_hook.py"}}, handle)
    return operation


def case_replay():
    """#1408: the replay walks the golden steps, stops at the first mismatch naming what differs, and never passes a step it
    cannot observe."""
    gold = os.path.join(ROOT, "dev", "toy", "adoption-golden.tsv")
    with tempfile.TemporaryDirectory() as tmp:
        env = fake_gh(tmp)
        operation = home(tmp)
        unattended = tool(tmp, "workflow-monitoring", "unattended.py")
        code, out = run([sys.executable, unattended, "replay", "--golden", gold], operation, env)
        print(out.strip())
        full = code == 2 and all("STEP %d OK" % n in out for n in range(1, 8)) and "STEP 8 MISMATCH" in out
        os.remove(os.path.join(tmp, ".workflow-loop", "private-names"))
        code3, out3 = run([sys.executable, unattended, "replay", "--golden", gold], operation, env)
        print(out3.strip())
        return full and code3 == 1 and "STEP 2 OK" in out3 and "STEP 3 MISMATCH" in out3 and "0 private pattern(s)" in out3 and "STEP 4" not in out3


def case_connectors():
    """#1410: each connector a followed repo's PRDs name is listed as connected, needs sign-in or missing, read-only."""
    with tempfile.TemporaryDirectory() as tmp:
        env = fake_gh(tmp)
        operation = home(tmp)
        wiki = os.path.join(tmp, "followed-1", "docs", "wiki")
        os.makedirs(wiki)
        with open(os.path.join(wiki, "Mail.md"), "w") as handle:
            handle.write("The digest goes by email, and the calendar shows the week.")
        probe = os.path.join(tmp, "probe.py")
        with open(probe, "w") as handle:
            handle.write("import sys; sys.exit({'mail': 0, 'calendar': 3}.get(sys.argv[1], 1))")
        unattended = tool(tmp, "workflow-monitoring", "unattended.py")
        before = sorted(os.listdir(os.path.join(tmp, "followed-1")))
        env["LOOP_CONNECTOR_PROBE"] = "%s %s" % (sys.executable, probe)
        code, out = run([sys.executable, unattended, "connectors"], operation, env)
        del env["LOOP_CONNECTOR_PROBE"]
        _, none = run([sys.executable, unattended, "connectors"], operation, env)
        print(out.strip().replace("\n", " | "), "||", none.strip().replace("\n", " | "))
        return (code == 1 and "OK followed-1 mail: connected" in out and "MISSING followed-1 calendar: needs sign-in. Fix:" in out
                and "MISSING followed-1 mail: missing" in none and sorted(os.listdir(os.path.join(tmp, "followed-1"))) == before)


def case_adopt():
    """#1409: one pass lists my recent repos, clones the chosen ones into one folder, follows them, sets each up and ends with
    each one's template_version."""
    with tempfile.TemporaryDirectory() as tmp:
        env = fake_gh(tmp)
        os.makedirs(os.path.join(tmp, "bares"))
        for name in ("one", "two"):
            git(tmp, "clone", "-q", "--bare", repo(tmp, "src-" + name), os.path.join(tmp, "bares", name + ".git"))
        operation = repo(tmp, "operation")
        board = tool(tmp, "workflow-monitoring", "board.py")
        _, listed = run([sys.executable, board, "repos", "adopt", "--recent", "5"], operation, env)
        into = os.path.join(tmp, "clones")
        code, out = run([sys.executable, board, "repos", "adopt", "o/one", "o/two", "--into", into], operation, env)
        _, shown = run([sys.executable, board, "repos", "list"], operation, env)
        print(listed.strip().replace("\n", " | "), "||", out.strip().replace("\n", " | "), "||", shown.strip().replace("\n", " | "))
        return ("o/one private" in listed and "o/two public" in listed and code == 0
                and "ADOPTED o/one: setup exit 0, template_version 9.8.7" in out and "ADOPTED o/two: setup exit 0, template_version 9.8.7" in out
                and "one" in shown and "two" in shown and os.path.isdir(os.path.join(into, "one", ".git")))


def case_scope():
    """#1411: a private-name line can be scoped (@public, @repos=a,b): a name only one repo may hold is refused only elsewhere."""
    with tempfile.TemporaryDirectory() as tmp:
        env = env_of(tmp)
        env["LOOP_PRIVATE_NAMES"] = os.path.join(tmp, "names")
        with open(env["LOOP_PRIVATE_NAMES"], "w") as handle:
            handle.write("# names\n@repos=beta secretbeta\n@public secretpublic\ncommonsecret\n")
        private, seen = tool(tmp, "workflow-delivery", "private.py"), {}
        for name in ("alpha", "beta"):
            path = repo(tmp, name)
            with open(os.path.join(path, "s.txt"), "w") as handle:
                handle.write("x secretbeta y\n")
            git(path, "add", "s.txt")
            seen[name] = (run([sys.executable, private, "check"], path, env)[1], run([sys.executable, private, "hook", "staged"], path, env))
        print({k: (v[0].strip(), v[1][0]) for k, v in seen.items()})
        return ("2 patterns" in seen["alpha"][0] and seen["alpha"][1][0] == 0 and "3 patterns" in seen["beta"][0]
                and seen["beta"][1][0] != 0 and "matches list line 2" in seen["beta"][1][1])


CASES = {"stamp": case_stamp, "prereq": case_prereq, "replay": case_replay, "connectors": case_connectors, "adopt": case_adopt, "scope": case_scope}


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(CASES)
    bad = [n for n in names if not CASES[n]()]
    print("FAILED: " + ", ".join(bad) if bad else "ALL PASS")
    raise SystemExit(1 if bad else 0)
