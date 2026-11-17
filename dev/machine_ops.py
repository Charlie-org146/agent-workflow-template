"""Helpers for machine.py: repo lookups, the operation session's hooks, the peer link, backup and restore. Standard library only."""
import json
import os
import re
import hashlib
import shutil
import subprocess
import sys

CLONE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SK = os.path.join(CLONE, "skills")


def git(repo, *args):
    done = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


def repo_of(path):
    top = git(path, "rev-parse", "--show-toplevel")
    return os.path.realpath(top) if top else ""


def inside(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root + os.sep)


def read(path):
    try:
        return open(path).read()
    except OSError:
        return None


def in_repo(path):  # the nearest folder that exists decides: a dotfiles repo holding the home folder counts too
    folder = os.path.dirname(os.path.realpath(path))
    while folder and not os.path.isdir(folder):
        folder = os.path.dirname(folder)
    return bool(repo_of(folder))


def hook_gap(c):  # the operation session's reply and govern hooks live in the repo's machine-local Claude settings
    if not c.repo:
        return ""
    text = read(os.path.join(c.repo, ".claude", "settings.local.json")) or ""
    return "" if "govern_hook" in text else "run: machine.py apply --repo <your repo>"


def hook_do(c):
    if c.repo and hook_gap(c):
        subprocess.run([sys.executable, os.path.join(SK, "workflow-setup", "scripts", "setup.py"), "--reply-hook"], cwd=c.repo, capture_output=True)


def peer_gap(c):
    try:
        doc = json.load(open(c.peer_path))
    except (OSError, ValueError):
        return "run: machine.py apply --peer NAME"
    ok = isinstance(doc, dict) and all(re.fullmatch(r"[a-z0-9-]{1,30}", str(doc.get(k) or "")) for k in ("self", "peer"))
    return "" if ok else "run: machine.py apply --peer NAME"


OWNER_ONLY = "owner-only, never copied or created by setup: ~/.workflow-loop/mail.env, ~/.workflow-loop/mail-to, the private-names lists (private-names*), account logins (claude, gh auth login), the permission mode and registering tasks in the app"


def backup_set(c):  # (relative path, absolute path) of every restorable file; secrets and private-names lists are never listed
    out = []
    for rel in ("machine.json", "peer.json", "flow.json"):
        if os.path.isfile(os.path.join(c.loop, rel)):
            out.append(("loop/" + rel, os.path.join(c.loop, rel)))
    for base, tag in ((c.routines, "loop/routines"), (c.tasks, "tasks")):
        for root, _, files in os.walk(base):
            if any(x in root for x in ("locks", "logs", "old-task-folders")):
                continue
            for f in files:
                if f.endswith((".md", ".py")) and ".bak" not in f:
                    full = os.path.join(root, f)
                    out.append((tag + "/" + os.path.relpath(full, base).replace(os.sep, "/"), full))
    return sorted(out)


def vault(c, folder):
    folder = os.path.realpath(folder)
    if in_repo(folder) or inside(folder, CLONE) or any(r and inside(folder, r) for r in [c.repo, c.loop]):
        print("REFUSED: %s is inside a repo or the loop folder; give a folder no repo holds" % c.show(folder))
        return None
    return folder


def backup(c, folder):
    folder = vault(c, folder)
    if not folder:
        return 1
    files = backup_set(c)
    for rel, full in files:
        dst = os.path.join(folder, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(full, dst)
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "MANIFEST"), "w").write("".join(rel + "\n" for rel, _ in files))
    print("BACKED UP %d files to %s" % (len(files), c.show(folder)))
    print(OWNER_ONLY)
    return 0


def restore(c, folder):
    folder = os.path.realpath(folder)
    manifest = read(os.path.join(folder, "MANIFEST"))
    if manifest is None:
        print("REFUSED: %s holds no MANIFEST; it is not a machine.py backup" % c.show(folder))
        return 1
    n = 0
    for rel in manifest.split():
        top, _, rest = rel.partition("/")
        base = c.tasks if top == "tasks" else c.loop
        path = os.path.normpath(os.path.join(base, rest))
        name = os.path.basename(path)
        if ".." in rel or name.startswith(("mail", "private-names")) or not inside(path, base):
            continue
        text = read(os.path.join(folder, rel))
        if text is not None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", newline="\n").write(text)
            n += 1
    print("RESTORED %d files from %s; now run: machine.py apply --repo <your repo>, then machine.py check" % (n, c.show(folder)))
    print(OWNER_ONLY)
    return 0

WIN = " [unverified on Windows]"


def cadence(name):  # every 4 hours; the minute is staggered by the name so repos do not start together
    return "%d */4 * * *" % (int(hashlib.sha1(name.encode()).hexdigest()[:4], 16) % 60)


def checklist(c, tasks):
    steps = ["mail login: create ~/.workflow-loop/mail.env (SMTP_USER, SMTP_PASSWORD; SMTP_HOST, SMTP_PORT if not Gmail; mode 600) and ~/.workflow-loop/mail-to (one address) | verify: %s ~/.workflow-loop/routines/send-mail.py --check" % c.py,
             "account logins: claude, and gh auth login | verify: claude --version; gh auth status",
             "private names: one pattern per line in ~/.workflow-loop/private-names | verify: machine.py check",
             "permission mode: choose a mode that never asks (bypass) for each task in the app, then machine.py record-task NAME bypass | verify: machine.py check"]
    steps.append("start the operation session: open a Claude session in your repo and run its routine (~/.workflow-loop/routines/operation-session.md); the peer's session is named in ~/.workflow-loop/peer.json | verify: machine.py check")
    steps += ["register task %s in the app at \"%s\" with the no-prompt mode | verify: machine.py check" % (t, cron) for t, cron in tasks]
    if c.win:
        steps.append("Windows: install Git for Windows (sh hooks) and Python (py -3); junctions need developer mode, else a copy is used" + WIN)
    return ["owner steps (setup cannot do these):"] + ["%d. %s" % (n, s) for n, s in enumerate(steps, 1)]


def tasks_of(its):  # (task name, its cron) for every task item
    out = []
    for name, text, *_ in its:
        if name.startswith("task:"):
            found = re.search(r'at "([^"]+)"', text)
            out.append((name[5:], found.group(1) if found else cadence(name[5:].replace("-health-regression", ""))))
    return out
