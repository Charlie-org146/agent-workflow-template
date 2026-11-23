#!/usr/bin/env python3
"""DEL-25.1 and DEL-25.2: the quick checks a push runs through the pre-commit framework (.pre-commit-config.yaml).

  quick.py run                               the three checks in one process on one clock: the pre-commit hook `quick`
  quick.py lint | docs-check | size-limits   run one check; exit 1 with: REFUSED: <name> failed: <what>. Fix: <command>
  quick.py install                           write .pre-commit-config.yaml when absent and install the pre-push hook (Mac and Linux)
  quick.py doctor                            say whether this clone's push path is wired (exit 1 with an ordered Fix if not)

The whole run has the limit of the "quick checks" row of clock.py (default 1 minute, o755); a run over it prints clock's
`missed (was Xm, limit Ym)` line. The private-name scan is NOT here: it stays the git-native pre-push stub that seed.py writes.
"""
import importlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, text=True).stdout.strip() or os.getcwd()
DEFAULT = 60
WARN = 19000
SELF = os.path.join("skills", "workflow-delivery", "scripts", "quick.py")
CONFIG = (
    "# DEL-25.1: one hook, one clock. The private-name scan is the git-native pre-push stub (pre-commit keeps it as pre-push.legacy).\n"
    "default_install_hook_types: [pre-push]\n"
    "default_stages: [pre-push]\n"
    "repos:\n"
    "  - repo: local\n"
    "    hooks:\n"
    "      - id: quick\n"
    "        name: quick checks\n"
    "        language: system\n"
    "        entry: python3 " + SELF.replace(os.sep, "/") + " run\n"
    "        pass_filenames: false\n"
    "        always_run: true\n"
    "        verbose: true\n")


def run(args, timeout=300):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)


def clock():
    """The clock module of v110-fast-clock, or None when it is not in this tree."""
    for part in ("workflow-delivery", "workflow-monitoring"):
        sys.path.append(os.path.join(SKILLS, part, "scripts"))
    try:
        return importlib.import_module("clock")  # optional: v110-fast-clock may not be in this tree
    except Exception:  # not built yet, or it does not import here
        return None


def config():
    try:
        with open(os.path.join(ROOT, ".loop", "config.json"), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def limit():
    """(seconds, where it came from): the clock table's value, else the 1-minute default of DEL-25.2."""
    module = clock()
    try:
        seen = module.limit(config(), "quick checks", "") if module and hasattr(module, "limit") else None
    except Exception:
        seen = None
    if isinstance(seen, (int, float)) and not isinstance(seen, bool) and seen > 0:
        return seen, "clock table"
    return DEFAULT, "DEL-25.2 default; clock not present" if module is None else "DEL-25.2 default"


def base_ref():
    return "origin/" + str(config().get("base") or "main")


def changed():
    """Files this push changes against the configured base branch; every tracked file when there is no base to compare."""
    base = run(["git", "merge-base", "HEAD", base_ref()])
    names = run(["git", "diff", "--name-only", "--diff-filter=d", base.stdout.strip() + "...HEAD"]) if not base.returncode else None
    names = names or run(["git", "ls-files"])
    return [n for n in names.stdout.splitlines() if n]


def check_lint():
    bad = []
    files = changed()
    for name in [n for n in files if n.endswith(".py")]:
        try:
            with open(os.path.join(ROOT, name), "rb") as handle:
                compile(handle.read(), name, "exec")  # in memory: no bytecode file is written
        except (SyntaxError, ValueError, OSError) as err:
            bad.append("%s: %s" % (name, str(err)[:80]))
    for name in [n for n in files if n.endswith(".sh")]:
        done = run(["bash", "-n", name]) if os.path.exists(os.path.join(ROOT, name)) else None
        if done and done.returncode:
            bad.append("%s: %s" % (name, (done.stderr.strip().splitlines() or ["syntax error"])[-1][:80]))
    return "; ".join(bad[:5]), "python3 -m py_compile <file>, then push again"


def check_docs():
    """docs.py check and entry.py check. A page stale only by commits since its stamp is restamped by wiki.py prepare (DOC-2), not a push's."""
    bad = []
    for part, command in (("docs.py check", ("workflow-docs", "scripts", "docs.py")),
                          ("entry.py check", ("workflow-docs", "scripts", "entry.py"))):
        done = run([sys.executable, os.path.join(SKILLS, *command), "check"])
        restamp = lambda l: l.startswith("STALE ") and (" commits since the page" in l or " commit since the page" in l)
        found = [l for l in done.stdout.splitlines() if l.strip() and not restamp(l) and not l.startswith(("DOCS OK", "ENTRY OK"))]
        if done.returncode and (found or done.stderr.strip() or not done.stdout.strip()):  # any non-zero exit that is not only restamp lines, a crash or an unknown line included
            why = found[0] if found else (done.stderr.strip().splitlines() or ["exit %d with no output" % done.returncode])[-1]
            bad.append("%s: %s" % (part, why[:100]))
    return "; ".join(bad), "python3 skills/workflow-docs/scripts/entry.py write (or docs.py audit), commit, push again"


def check_size():
    package = os.path.join(ROOT, "dev", "package.py")
    done = run([sys.executable, package, "--static"]) if os.path.exists(package) else None
    bad = [] if not done or not done.returncode else [(done.stdout.strip().splitlines() or ["package.py exit %d" % done.returncode])[-1][:120]]
    for name in [n for n in changed() if n.endswith(".py") and "skills/" in n]:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as handle:
            size = len(handle.read().replace(b"\r\n", b"\n"))
        before = run(["git", "show", base_ref() + ":" + name])
        was = len(before.stdout.encode()) if not before.returncode else 0
        if size >= WARN > was:
            bad.append("%s is %d bytes and newly over %d" % (name, size, WARN))
    return "; ".join(bad[:4]), "python3 dev/package.py --static; shrink the file named above, push again"


CHECKS = {"lint": check_lint, "docs-check": check_docs, "size-limits": check_size}


def doctor():
    """The push path: pre-commit installed, its pre-push hook present, and a private-name call on that path. Never installs anything."""
    common = os.path.join(ROOT, run(["git", "rev-parse", "--git-common-dir"]).stdout.strip())  # hooks live in the common dir, not a worktree's
    hooks = run(["git", "config", "core.hooksPath"]).stdout.strip() or os.path.join(common, "hooks")
    push = os.path.join(hooks, "pre-push")
    text = open(push, encoding="utf-8", errors="replace").read() if os.path.exists(push) else ""
    legacy = os.path.join(hooks, "pre-push.legacy")
    scans = "private.py" in text or (os.path.exists(legacy) and "private.py" in open(legacy, encoding="utf-8", errors="replace").read())
    problems, notes = [], []
    if os.name == "nt":  # pre-commit cannot run the stub's #!/bin/sh there, which would refuse every push: it is not installed
        notes.append("NOTE: the quick checks run through pre-commit on macOS and Linux; here run python3 %s run by hand before a push." % SELF)
        if "pre-commit" in text:
            problems.append("pre-commit's hook is installed here and would refuse every push. Fix, in order: "
                            "1. pre-commit uninstall --hook-type pre-push 2. python3 skills/workflow-setup/scripts/setup.py --git-hooks")
        scans = "private.py" in text
    else:
        if run(["git", "config", "core.hooksPath"]).stdout.strip():
            problems.append("core.hooksPath is set, which pre-commit refuses; git config --unset-all core.hooksPath")
        if "pre-commit" not in text:
            problems.append("pre-commit is not installed here. Fix: pipx install pre-commit==4.0.1, then python3 %s install" % SELF)
    if not scans:
        problems.append("no private-name scan on the push path. Fix, in order: 1. pre-commit uninstall --hook-type pre-push "
                        "2. python3 skills/workflow-setup/scripts/setup.py --git-hooks 3. pre-commit install --hook-type pre-push (never -f)"
                        if os.name != "nt" else "no private-name scan on the push path. Fix: python3 skills/workflow-setup/scripts/setup.py --git-hooks")
    print("\n".join(notes + ["REFUSED: doctor: " + p for p in problems]) or "DOCTOR OK: pre-commit and the private-name scan are on the push path")
    return 1 if problems else 0


def install():
    """Write .pre-commit-config.yaml when absent and install the pre-push hook; never overwrites a hook."""
    path = os.path.join(ROOT, ".pre-commit-config.yaml")
    if not os.path.exists(path):
        with open(path, "w", newline="\n") as handle:
            handle.write(CONFIG)
        print("wrote .pre-commit-config.yaml")
    if os.name == "nt":
        print("NOTE: the quick checks run through pre-commit on macOS and Linux; here run python3 %s run by hand." % SELF)
        return 0
    done = run(["pre-commit", "install", "-t", "pre-push"]) if shutil.which("pre-commit") else None
    if done is None or done.returncode:
        print("REFUSED: install: pre-commit is not installed or refused. Fix: pipx install pre-commit==4.0.1, then python3 %s install" % SELF)
        return 1
    print("QUICK install: ok (pre-push hook installed)")
    return 0


def main(argv):
    if argv[1:2] == ["doctor"]:
        return doctor()
    if argv[1:2] == ["install"]:
        return install()
    names = list(CHECKS) if argv[1:2] == ["run"] else argv[1:2]
    if not names or any(n not in CHECKS for n in names):
        print("usage: quick.py run | lint | docs-check | size-limits | install | doctor", file=sys.stderr)
        return 2
    seconds, where = limit()
    print("limit: %dm (%s)" % (seconds // 60, where))
    began = time.time()
    for name in names:
        mine = time.time()
        bad, fix = CHECKS[name]()
        if bad:
            print("REFUSED: %s failed: %s. Fix: %s" % (name, bad, fix))
            return 1
        print("QUICK %s: ok (%.1fs)" % (name, time.time() - mine))
    total = time.time() - began
    if total > seconds:
        module = clock()
        line = module.check_missed("quick checks", total, config()) if module and hasattr(module, "check_missed") else None
        print("QUICK %s" % (line or "missed (was %dm, limit %dm): the quick checks took %.0fs" % (round(total / 60), seconds // 60, total)))
    return 0  # a slow run is reported, never refused


if __name__ == "__main__":
    sys.exit(main(sys.argv))
