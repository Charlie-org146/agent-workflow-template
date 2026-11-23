#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/quick.py .pre-commit-config.yaml
"""quick-checks (DEL-25.1, DEL-25.2): a push runs lint, the docs check and the size limits through the pre-commit framework.

Cases: the config declares three python hooks and no private-name hook; each check passes on a clean fixture and is refused
on a fixture that breaks only its own rule (a syntax error, a stale docs check, a script newly over 19,000 bytes); each
check prints its time; the 1-minute default and the missed line; the absent-clock path; a REAL pre-push hook call (no push is made) with pre-commit 4.0.1
(installed into a temporary virtualenv: this toy needs network and exits 77, skipped, when the install fails offline, never failing) runs the
three checks, calls the git-native pre-push stub exactly once (pre-commit keeps it as pre-push.legacy and feeds it every
pushed ref), and a planted word on the SECOND ref of a two-ref push is still refused; quick.py doctor refuses a clone
with no scan on the push path and names the ordered Fix. The clock module is a stub that exists only inside this toy.
usage: test-quick-checks.py"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.dont_write_bytecode = True
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def sh(args, cwd, env=None, check_rc=False, stdin=None):
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env, input=stdin)
    if check_rc and done.returncode:
        raise SystemExit("FAIL: %s: %s" % (" ".join(args), done.stderr.strip() or done.stdout.strip()))
    return done


tmp = tempfile.mkdtemp(prefix="quick-checks-")
home = os.path.join(tmp, "home")
os.makedirs(home)
env = dict(os.environ, HOME=home, USERPROFILE=home, GIT_TERMINAL_PROMPT="0", PYTHONDONTWRITEBYTECODE="1")
for var in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "PRE_COMMIT_HOME"):
    env.pop(var, None)
PY = sys.executable


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as handle:
        handle.write(text)


def git(cwd, *args):
    return sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd, env, True).stdout.strip()


def fixture(name, docs_rc=0, entry_rc=0, docs_code=None):
    repo = os.path.join(tmp, name)
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    os.makedirs(os.path.join(repo, "dev"))
    os.makedirs(os.path.join(repo, "skills", "workflow-delivery", "scripts"))
    shutil.copy(os.path.join(root, "skills", "workflow-delivery", "scripts", "quick.py"), os.path.join(repo, "skills", "workflow-delivery", "scripts", "quick.py"))
    shutil.copy(os.path.join(root, ".pre-commit-config.yaml"), repo)
    write(os.path.join(repo, "dev", "package.py"), "import sys\nsys.exit(0)\n")  # the real packager is checked on this repo below
    for stub, rc in (("docs.py", docs_rc), ("entry.py", entry_rc)):
        write(os.path.join(repo, "skills", "workflow-docs", "scripts", stub), "import sys\nprint('STALE x: fixture')\nsys.exit(%d)\n" % rc)
    if docs_code:
        write(os.path.join(repo, "skills", "workflow-docs", "scripts", "docs.py"), docs_code)
    write(os.path.join(repo, "skills", "workflow-docs", "scripts", "ok.py"), "x = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


QUICK = os.path.join("skills", "workflow-delivery", "scripts", "quick.py")


def quick(repo, name):
    return sh([PY, os.path.join(repo, QUICK), name], repo, env)


# 1. the config
text = open(os.path.join(root, ".pre-commit-config.yaml"), encoding="utf-8").read()
ids = re.findall(r"^\s+- id: (\S+)", text, re.M)
check(ids == ["quick"], "the config declares exactly one hook, quick: %s" % ids)
check(text.count("language: system") == 1 and text.count("pass_filenames: false") == 1 and text.count("verbose: true") == 1, "the hook is language system (no virtualenv is built on a first push), takes no filenames and shows its time")
check("entry: python3 skills/workflow-delivery/scripts/quick.py run" in text, "the entry is the one shipped command quick.py run")
check("default_install_hook_types: [pre-push]" in text, "the hook runs at the pre-push stage")
check("private" not in re.sub(r"#.*", "", text), "no private-name hook is declared in the config (the git-native stub is the scan)")

# 2. each check passes clean and is refused on a fixture that breaks only its rule
clean = fixture("clean")
for name in ("lint", "docs-check", "size-limits"):
    done = quick(clean, name)
    check(done.returncode == 0 and re.search(r"^QUICK %s: ok \(\d+\.\ds\)$" % name, done.stdout, re.M) is not None, "%s passes clean and prints its time: %s" % (name, done.stdout.strip().splitlines()[-1:]))
check("limit: 1m (DEL-25.2 default; clock not present)" in quick(clean, "lint").stdout, "with no clock module the 1-minute default is used and says so")
bad = fixture("bad-lint")
write(os.path.join(bad, "skills", "workflow-docs", "scripts", "broken.py"), "def (:\n")
git(bad, "add", "-A")
git(bad, "commit", "-q", "-m", "broken")
done = quick(bad, "lint")
check(done.returncode == 1 and "REFUSED: lint failed: skills/workflow-docs/scripts/broken.py" in done.stdout and "Fix:" in done.stdout, "lint refuses a syntax error and names the file and a Fix: %s" % done.stdout.strip()[-120:])
check(not any(n.endswith((".pyc", ".pyo")) or n == "__pycache__" for n in os.listdir(os.path.join(bad, "skills", "workflow-docs", "scripts"))), "lint writes no bytecode")
check(quick(bad, "size-limits").returncode == 0 and quick(bad, "docs-check").returncode == 0, "the syntax error breaks only lint")
stale = fixture("bad-docs", docs_rc=1)
done = quick(stale, "docs-check")
check(done.returncode == 1 and "REFUSED: docs-check failed" in done.stdout and "Fix: python3 skills/workflow-docs/scripts/entry.py write" in done.stdout, "docs-check refuses a failing docs check with a Fix: %s" % done.stdout.strip()[-100:])
check(quick(stale, "lint").returncode == 0, "a failing docs check breaks only docs-check")
crash = fixture("crash-docs", docs_code="import sys\nsys.stderr.write('Traceback: boom' + chr(10))\nsys.exit(1)\n")
done = quick(crash, "docs-check")
check(done.returncode == 1 and "REFUSED: docs-check failed" in done.stdout, "a docs check that exits non-zero with only a stderr message is refused: %s" % done.stdout.strip()[-100:])
silent = fixture("silent-docs", docs_code="import sys\nsys.exit(2)\n")
check(quick(silent, "docs-check").returncode == 1, "a docs check that exits non-zero with no output at all is refused")
notes_only = fixture("notes-only-docs", docs_code="import sys\nprint('UNTESTED Home: nothing')\nprint('NOTE: something')\nsys.exit(1)\n")
check(quick(notes_only, "docs-check").returncode == 1, "a non-zero docs check whose only output is UNTESTED or NOTE lines is refused")
lookalike = fixture("lookalike-docs", docs_code="import sys\nprint('IDS Home: a line that mentions 1 commit since the page but is not a STALE restamp line')\nsys.exit(1)\n")
check(quick(lookalike, "docs-check").returncode == 1, "only lines that START with STALE are restamp lines: another line that mentions the phrase is refused")
restamp = fixture("restamp-docs", docs_code="import sys\nprint('STALE Home: 3 commits since the page: abc')\nsys.exit(1)\n")
check(quick(restamp, "docs-check").returncode == 0, "a page stale only by commits since its stamp passes (the restamp is DOC-2's), while a real STALE line is refused above")
big = fixture("bad-size")
write(os.path.join(big, "skills", "workflow-docs", "scripts", "big.py"), "x = 1\n" + "# " + "y" * 19100 + "\n")
git(big, "add", "-A")
git(big, "commit", "-q", "-m", "big")
done = quick(big, "size-limits")
check(done.returncode == 1 and "big.py is 19" in done.stdout and "newly over 19000" in done.stdout, "size-limits refuses a script newly over 19,000 bytes: %s" % done.stdout.strip()[-100:])
check(quick(big, "lint").returncode == 0, "an over-size script breaks only size-limits")
grown = fixture("grow-size")
write(os.path.join(grown, "skills", "workflow-docs", "scripts", "big.py"), "x = 1\n" + "# " + "y" * 19100 + "\n")
git(grown, "add", "-A")
git(grown, "commit", "-q", "-m", "big on main")
git(grown, "update-ref", "refs/remotes/origin/main", "HEAD")
write(os.path.join(grown, "skills", "workflow-docs", "scripts", "big.py"), "x = 1\n" + "# " + "y" * 19300 + "\n")
git(grown, "add", "-A")
git(grown, "commit", "-q", "-m", "grow")
check(quick(grown, "size-limits").returncode == 0, "a script already over 19,000 on the base branch may grow (control: only a NEWLY crossing script is refused)")
cfgbase = fixture("cfg-base")
os.makedirs(os.path.join(cfgbase, ".loop"))
write(os.path.join(cfgbase, ".loop", "config.json"), '{"base": "trunk"}')
git(cfgbase, "add", "-A")
git(cfgbase, "commit", "-q", "-m", "config")
git(cfgbase, "update-ref", "refs/remotes/origin/trunk", "HEAD~1")
write(os.path.join(cfgbase, "skills", "workflow-docs", "scripts", "broken.py"), "def (:" + chr(10))
git(cfgbase, "add", "-A")
git(cfgbase, "commit", "-q", "-m", "broken")
check(quick(cfgbase, "lint").returncode == 1, "the base branch comes from the config (trunk here), not a fixed origin/main")

# 3. the limit: one run, one clock, the missed line, the clock stub
slow = fixture("slow")
done = quick(slow, "run")
check(done.returncode == 0 and all(("QUICK %s: ok" % n) in done.stdout for n in ("lint", "docs-check", "size-limits")), "run does the three checks in one process: %s" % done.stdout.strip().splitlines()[-1:])
write(os.path.join(slow, "skills", "workflow-delivery", "scripts", "clock.py"),
      "def limit(cfg, step, size, usual=None):\n    return 0.001\n\n\ndef check_missed(name, seconds, cfg):\n    return 'missed (was 9m, limit 0m): stub'\n")
done = quick(slow, "run")
check("(clock table)" in done.stdout and "QUICK missed (was 9m, limit 0m): stub" in done.stdout and done.returncode == 0, "a clock module's limit is read and named, and its missed line is printed, never a refusal: %s" % done.stdout.strip().splitlines()[-2:])
broken = fixture("clock-broken")
write(os.path.join(broken, "skills", "workflow-delivery", "scripts", "clock.py"), "raise RuntimeError('does not import')\n")
done = quick(broken, "run")
check(done.returncode == 0 and "limit: 1m (DEL-25.2 default" in done.stdout, "a clock module that does not import never crashes a push: it falls back to 1 minute")
nobranch = fixture("no-origin")
git(nobranch, "update-ref", "-d", "refs/remotes/origin/main")
write(os.path.join(nobranch, "skills", "workflow-docs", "scripts", "broken.py"), "def (:\n")
git(nobranch, "add", "-A")
git(nobranch, "commit", "-q", "-m", "broken")
git(nobranch, "update-ref", "-d", "refs/remotes/origin/main")
done = quick(nobranch, "lint")
check(done.returncode == 1 and "broken.py" in done.stdout, "with no origin/main (a new branch) every tracked file is checked, not none")

alone = sh([PY, os.path.join(root, QUICK)], root, env)
check(alone.returncode == 0 and alone.stdout.startswith("usage: quick.py"), "quick.py run with no arguments prints its usage and exits 0 (the package's every-script-runs-alone rule)")
check(sh([PY, os.path.join(root, QUICK), "nonsense"], root, env).returncode == 2, "an unknown command still exits 2")

# 3a. a typical goal: the real three checks on this repo's own tree finish inside DEL-25.2's default limit
began = time.time()
real = sh([PY, os.path.join(root, QUICK), "run"], root, env)
took = time.time() - began
check(took < 60 and "QUICK lint: ok" in real.stdout, "the real quick checks on this repo's tree finish in %.0fs, inside the 60-second default limit" % took)

# 3b. seed.hook_state: a pre-commit shim over our stub counts as installed; one over nothing of ours stays foreign
sys.path.insert(0, os.path.join(root, "skills", "workflow-setup", "scripts"))
import seed  # noqa: E402
hooks = os.path.join(tmp, "seedhooks")
os.makedirs(hooks)
fake_private = os.path.join(tmp, "private.py")
write(fake_private, "x = 1\n")
ours = "#!/bin/sh\n# " + seed.MARK + "\nS='" + fake_private + "'\n"
shim = "#!/usr/bin/env bash\n# File generated by pre-commit: https://pre-commit.com\nexit 0\n"
write(os.path.join(hooks, "pre-push"), ours)
check(seed.hook_state(os.path.join(hooks, "pre-push")) == "installed", "seed: our stub alone is installed")
write(os.path.join(hooks, "pre-push"), shim)
write(os.path.join(hooks, "pre-push.legacy"), ours)
os.chmod(os.path.join(hooks, "pre-push.legacy"), 0o755)  # pre-commit keeps the hook it moves executable
check(seed.hook_state(os.path.join(hooks, "pre-push")) == "installed", "seed: a pre-commit shim over our stub (kept as .legacy) is installed, so setup does not report it foreign")
if os.name != "nt":
    os.chmod(os.path.join(hooks, "pre-push.legacy"), 0o644)
    check(seed.hook_state(os.path.join(hooks, "pre-push")) == "foreign", "seed: a legacy stub that is not executable is never counted, since the shim would not run it")
    os.chmod(os.path.join(hooks, "pre-push.legacy"), 0o755)
os.remove(os.path.join(hooks, "pre-push.legacy"))
check(seed.hook_state(os.path.join(hooks, "pre-push")) == "foreign", "seed: a pre-commit shim with no legacy stub is foreign")
write(os.path.join(hooks, "pre-push"), "#!/bin/sh\nexit 0\n")
check(seed.hook_state(os.path.join(hooks, "pre-push")) == "foreign", "seed: any other hook is foreign")

# 4. doctor
def doctor(repo):
    return sh([PY, os.path.join(repo, QUICK), "doctor"], repo, env)


STUB = "#!/bin/sh\npython3 skills/workflow-delivery/scripts/private.py hook push\n"
if os.name == "nt":
    done = doctor(clean)
    check(done.returncode == 1 and "REFUSED: doctor: no private-name scan on the push path" in done.stdout and "NOTE: native Windows keeps the git-native push stub only" in done.stdout,
          "Windows: doctor prints the one-line note (the stub alone, no pre-commit) and still refuses a clone with no scan: %s" % done.stdout.strip().splitlines()[:1])
    write(os.path.join(clean, ".git", "hooks", "pre-push"), STUB)
    done = doctor(clean)
    check(done.returncode == 0 and "NOTE: native Windows keeps the git-native push stub only" in done.stdout  and "REFUSED" not in done.stdout,
          "Windows: with the stub in place doctor passes, says pre-commit is not installed here, and installs nothing: %s" % done.stdout.strip()[:100])
    check(not os.path.exists(os.path.join(clean, ".git", "hooks", "pre-push.legacy")), "Windows: doctor installed nothing and moved no hook")
    write(os.path.join(clean, ".git", "hooks", "pre-push"), "#!/usr/bin/env python\n# File generated by pre-commit: https://pre-commit.com\n")
    done = doctor(clean)
    check(done.returncode == 1 and "1. pre-commit uninstall --hook-type pre-push 2. python3 skills/workflow-setup/scripts/setup.py --git-hooks" in done.stdout,
          "Windows: a pre-commit hook found there is refused with the ordered Fix (uninstall, then the stub)")
    print("NOTE: the pre-commit 4.0.1 hook case runs on Mac and Linux only (native Windows keeps the push stub alone); it did NOT run here")
    print("FAIL: %d case(s): %s" % (len(failed), "; ".join(failed)[:300]) if failed else "ALL PASS")
    shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(1 if failed else 0)
done = doctor(clean)
check(done.returncode == 1 and "pre-commit uninstall --hook-type pre-push" in done.stdout and "setup.py --git-hooks" in done.stdout
      and done.stdout.index("pre-commit uninstall") < done.stdout.index("--git-hooks") < done.stdout.rindex("pre-commit install") and "never -f" in done.stdout,
      "doctor refuses a clone with no scan on the push path and names the ordered Fix, never -f: %s" % done.stdout.strip().splitlines()[-1:])

# 5. a REAL push through pre-commit 4.0.1 (needs network)
venv = os.path.join(tmp, "venv")
made = sh([PY, "-m", "venv", venv], tmp, env)
bindir = os.path.join(venv, "Scripts" if os.name == "nt" else "bin")
got = sh([os.path.join(bindir, "python"), "-m", "pip", "install", "-q", "pre-commit==4.0.1"], tmp, env) if not made.returncode else made
if got.returncode:
    print("SKIP: the real-push case needs network to install pre-commit==4.0.1 into a temporary virtualenv and it failed: %s" % (got.stderr.strip().splitlines() or ["?"])[-1][:200])
    print("FAIL: %d case(s) before the install" % len(failed) if failed else "SKIP: offline, exit 77")
    sys.exit(1 if failed else 77)
precommit = os.path.join(bindir, "pre-commit")
renv = dict(env, PATH=bindir + os.pathsep + env.get("PATH", ""), PRE_COMMIT_HOME=os.path.join(tmp, "pc-home"))
work = fixture("push", docs_rc=0)
calls = os.path.join(work, "scan-calls.txt")
hook = os.path.join(work, ".git", "hooks", "pre-push")
write(hook, "#!/bin/sh\necho call >> '%s'\ncat | while read lref lsha rref rsha; do case \"$lref\" in *planted*) echo 'private-name scan: planted word in '$lref >&2; exit 1;; esac; done\n" % calls.replace("\\", "/"))
os.chmod(hook, 0o755)
done = sh([precommit, "install", "--hook-type", "pre-push"], work, renv)
check(done.returncode == 0 and os.path.exists(hook + ".legacy"), "pre-commit install keeps the git-native stub as pre-push.legacy: %s" % (done.stdout + done.stderr).strip()[-120:])
git(work, "commit", "-q", "--allow-empty", "-m", "one")
# no push in any toy: git's own call of the pre-push hook is made here with the lines git would send it on stdin (no remote exists)
ZERO = "0" * 40
tip = git(work, "rev-parse", "HEAD")


def hook_run(refs):
    lines = "".join("refs/heads/%s %s refs/heads/%s %s\n" % (ref, tip, ref, ZERO) for ref in refs)
    return sh([hook, "origin", "file:///nowhere"], work, renv, stdin=lines)


done = hook_run(["main"])
out = done.stdout + done.stderr
check(done.returncode == 0 and "QUICK lint: ok" in out and "QUICK docs-check: ok" in out and "QUICK size-limits: ok" in out, "the pre-push hook pre-commit installed runs the one quick hook, which does lint, docs-check and size-limits: rc %d %s" % (done.returncode, out.strip()[-120:]))
check(os.path.exists(calls) and open(calls).read().count("call") == 1, "the git-native scan stub ran exactly once for the hook call")
done = hook_run(["main", "first", "planted-second"])
check(done.returncode != 0 and "planted word in" in (done.stdout + done.stderr), "a planted word on the SECOND ref of a two-ref call is refused by the scan: %s" % (done.stdout + done.stderr).strip()[-120:])
done = hook_run(["main", "first"])
check(done.returncode == 0, "the control two-ref call with no planted word goes through")

print(open(os.path.join(tmp, "pc-home", "pre-commit.log")).read()[-2500:]) if failed and os.path.exists(os.path.join(tmp, "pc-home", "pre-commit.log")) else None
shutil.rmtree(tmp, ignore_errors=True)
print("FAIL: %d case(s): %s" % (len(failed), "; ".join(failed)[:300]) if failed else "ALL PASS")
sys.exit(1 if failed else 0)
