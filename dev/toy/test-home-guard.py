#!/usr/bin/env python3
# windows: ok
# reads: dev/toy/homeguard.py dev/toy/reap.sh dev/toy/test-settings.sh
"""home-guard (issue 4393): a toy never reads or writes the owner's real ~/.workflow-loop. The harness (reap.sh) snapshots
that folder when a toy starts and fails the toy at exit with a LEAK line when anything there changed; every toy that sets
HOME also sets USERPROFILE, because Python's expanduser reads USERPROFILE on Windows.

Never touches the real folder: TOY_REAL_WL points the guard at a throwaway one. usage: test-home-guard.py [guard|isolate]"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LEG = sys.argv[1] if len(sys.argv) > 1 else ""
fails = 0


def check(name, ok, extra="", leg="guard"):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok or (LEG and LEG != leg) else 1


def toy(tmp, name, body):
    """Run a one-line toy that sources the harness, with TOY_REAL_WL at tmp/wl; (exit code, stderr)."""
    path = os.path.join(tmp, name)
    open(path, "w", newline="\n").write('#!/bin/bash\n# windows: ok\nhere="%s"\n. "$here/dev/toy/reap.sh"\n%s\n' % (root.replace("\\", "/"), body))
    done = subprocess.run(["bash", path], capture_output=True, text=True, env=dict(os.environ, TOY_REAL_WL=os.path.join(tmp, "wl")))
    return done.returncode, done.stderr + done.stdout


with tempfile.TemporaryDirectory() as tmp:
    os.makedirs(os.path.join(tmp, "wl"))
    open(os.path.join(tmp, "wl", "flow.json"), "w").write('{"limit": 600}')
    code, said = toy(tmp, "quiet.sh", "true")
    check("a toy that leaves the real folder alone passes the guard", code == 0 and "LEAK" not in said, said)
    code, said = toy(tmp, "writes.sh", 'echo \'{"limit": 99}\' > "$TOY_REAL_WL/flow.json"')
    check("a toy that rewrites a file there fails with a LEAK line", code != 0 and "LEAK" in said and "flow.json" in said, said)
    open(os.path.join(tmp, "wl", "flow.json"), "w").write('{"limit": 600}')
    code, said = toy(tmp, "adds.sh", 'echo x > "$TOY_REAL_WL/new.json"')
    check("a toy that adds a file there fails with a LEAK line", code != 0 and "LEAK" in said and "new.json" in said, said)
    os.makedirs(os.path.join(tmp, "wl", "lanes"), exist_ok=True)
    code, said = toy(tmp, "lanes.sh", 'echo x > "$TOY_REAL_WL/lanes/ticket-1.tmp"')
    check("another lane's tickets under lanes/ are not a leak", code == 0 and "LEAK" not in said, said)
    os.makedirs(os.path.join(tmp, "wl", "schedule", "log"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "wl", "schedule", "repo", "tree"), exist_ok=True)
    open(os.path.join(tmp, "wl", "schedule", "repos.json"), "w").write("[]")
    code, said = toy(tmp, "sched.sh", 'echo x > "$TOY_REAL_WL/schedule/log/tick.log"; echo x > "$TOY_REAL_WL/schedule/repo/health-report.txt"; echo x > "$TOY_REAL_WL/schedule/repo/tree/f"')
    check("the scheduler's own log, health reports and trees under schedule/ are not a leak", code == 0 and "LEAK" not in said, said)
    code, said = toy(tmp, "sched-reg.sh", 'echo x > "$TOY_REAL_WL/schedule/repos.json"')
    check("a toy that writes the real schedule/ registry fails with a LEAK line (#4683)", code != 0 and "LEAK" in said and "schedule/repos.json" in said, said)
    open(os.path.join(tmp, "wl", "schedule", "repos.json"), "w").write("[]")
    code, said = toy(tmp, "sched-new.sh", 'mkdir -p "$TOY_REAL_WL/schedule/toyrepo" && echo x > "$TOY_REAL_WL/schedule/toyrepo/entry.json"')
    check("a toy that adds an entry under the real schedule/ fails with a LEAK line (#4683)", code != 0 and "LEAK" in said and "schedule/toyrepo" in said, said)
    shutil.rmtree(os.path.join(tmp, "wl", "schedule", "toyrepo"), ignore_errors=True)
    # the registry: another session adds a real repo, a toy adds a fixture in the temp folder (#4760)
    reg = os.path.join(tmp, "wl", "schedule", "repos.json")
    open(reg, "w").write('{"repos": {}}')
    code, said = toy(tmp, "reg-other.sh", 'printf \'{"repos": {"real": {"path": "/srv/work/real"}}}\' > "$TOY_REAL_WL/schedule/repos.json"; cp "$TOY_REAL_WL/schedule/repos.json" "$TOY_REAL_WL/schedule/repos.json.bak-2026-11-17"')
    check("another session's change to the registry (a real repo, a backup) is not a leak (#4760)", code == 0 and "LEAK" not in said, said)
    open(reg, "w").write('{"repos": {}}')
    code, said = toy(tmp, "reg-toy.sh", 'd=$(mktemp -d); printf \'{"repos": {"fixture": {"path": "%s"}}}\' "$d" > "$TOY_REAL_WL/schedule/repos.json"')
    check("a toy that registers a fixture repo in the temp folder fails with a LEAK line (#4760)", code != 0 and "LEAK" in said and "schedule/repos.json#fixture" in said, said)
    open(reg, "w").write('{"repos": {}}')
    # skills-main: another session moves the checkout (clean afterwards); a toy leaves a modified or an untracked file
    sm = os.path.join(tmp, "wl", "skills-main")
    os.makedirs(os.path.join(sm, ".loop"), exist_ok=True)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.test", "-c", "core.autocrlf=false"]
    open(os.path.join(sm, ".loop", "START.md"), "w", newline="\n").write("v1\n")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "v1"]):
        subprocess.run(git + args, cwd=sm, check=True, capture_output=True)
    gm = 'cd "$TOY_REAL_WL/skills-main" && '
    code, said = toy(tmp, "sm-other.sh", gm + 'echo v2 > .loop/START.md && git add -A && git -c user.name=t -c user.email=t@example.test commit -qm v2')
    check("another session moving ~/.workflow-loop/skills-main (START.md rewritten, clean again) is not a leak (#4760)", code == 0 and "LEAK" not in said, said)
    code, said = toy(tmp, "sm-edit.sh", gm + 'echo mine >> .loop/START.md')
    check("a toy that edits a file in skills-main fails with a LEAK line (#4760)", code != 0 and "LEAK" in said and "skills-main/.loop/START.md" in said, said)
    subprocess.run(git + ["checkout", "-q", "--", "."], cwd=sm, check=True, capture_output=True)
    code, said = toy(tmp, "sm-new.sh", gm + 'echo x > stray.txt')
    check("a toy that adds a file to skills-main fails with a LEAK line (#4760)", code != 0 and "LEAK" in said and "skills-main/stray.txt" in said, said)
    os.remove(os.path.join(sm, "stray.txt"))
    path = os.path.join(tmp, "strict.sh")
    open(path, "w", newline="\n").write('#!/bin/bash\n# windows: ok\nhere="%s"\n. "$here/dev/toy/reap.sh"\necho x > "$TOY_REAL_WL/lanes/ticket-2.tmp"\n' % root.replace("\\", "/"))
    done = subprocess.run(["bash", path], capture_output=True, text=True, env=dict(os.environ, TOY_REAL_WL=os.path.join(tmp, "wl"), TOY_GUARD_STRICT="1"))
    check("strict mode judges lanes/ too, for a fresh home", done.returncode != 0 and "lanes/ticket-2.tmp" in done.stderr + done.stdout, done.stderr)
    code, said = toy(tmp, "pool.sh", 'case "$LOOP_LANES_DIR" in "$TOY_REAL_WL"*|"") exit 3;; esac')
    check("the harness points LOOP_LANES_DIR at a temp lane pool (#4555)", code == 0, said)
    code, said = toy(tmp, "flow.sh", 'case "$LOOP_FLOW" in "$TOY_REAL_WL"*|"") exit 3;; esac; [ "$LOOP_HEALTH" != "" ] || exit 4')
    check("the harness points LOOP_FLOW and LOOP_HEALTH at temp paths", code == 0, said)

def unpaired(text):
    return bool(re.search(r"(?<![A-Za-z_])HOME[=\"]|\"HOME\"|'HOME'|\bHOME=", text)) and "USERPROFILE" not in text


check("control: a toy text that sets HOME alone is found", unpaired("export HOME=/tmp/x"), "", "isolate")
check("control: a toy text that sets HOME and USERPROFILE is not", not unpaired("export HOME=/tmp/x USERPROFILE=/tmp/x"), "", "isolate")
bad = []
for path in sorted(glob.glob(os.path.join(root, "dev", "toy", "test-*"))):
    if not path.endswith((".sh", ".py")) or path.endswith("test-home-guard.py"):
        continue
    if unpaired(open(path, encoding="utf-8", errors="replace").read()):
        bad.append(os.path.basename(path))
check("every toy that sets HOME also sets USERPROFILE (Python's expanduser reads it on Windows)", not bad, ", ".join(bad), "isolate")
sys.exit(1 if fails else 0)
