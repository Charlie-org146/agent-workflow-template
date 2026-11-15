#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/batch.py
"""batch.py roadmap: the Roadmap page from docs/ROADMAP.md, the open issues and the run records, in a throwaway repo with a
gh-shaped issues file. No network, no model."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
script = os.path.join(root, "skills", "workflow-monitoring", "scripts", "batch.py")
docs = os.path.join(root, "skills", "workflow-docs", "scripts", "docs.py")
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


SOURCE = """# Roadmap

## v1.0.0

### Size caps

| Issue or goal | Outcome | Blocks |
|---|---|---|

### Windows-safe

| Issue or goal | Outcome | Blocks |
|---|---|---|
| #10 | closed row | nothing |
| #11 | open row | merges |
| #12 | row a running goal names | merges |
| #20 | a hand row on a Backlog issue | nothing |
| #21 | a hand row on a To-do issue | nothing |
| `queued-goal` | a goal waiting in the queue | the rollout |

## Rollout

- `migrate-one`: first repo.
"""
ISSUES = [
    {"number": 11, "title": "Open hand row issue", "labels": [], "milestone": None},
    {"number": 12, "title": "Another hand row issue", "labels": [], "milestone": None},
    {"number": 13, "title": "size of a script", "labels": [{"name": "health:size"}], "milestone": None},
    {"number": 14, "title": "waits for v1.1", "labels": [], "milestone": {"title": "Backlog: Setup"}},
    {"number": 15, "title": "To-do: prove it on a Mac", "labels": [], "milestone": None},
    {"number": 20, "title": "backlog with a hand row", "labels": [], "milestone": {"title": "Backlog: X"}},
    {"number": 21, "title": "To-do: hand row to-do", "labels": [], "milestone": None},
    {"number": 23, "title": "already run", "labels": [], "milestone": None},
    {"number": 24, "title": None, "labels": []},
    "junk",
]


def build():
    top = tempfile.mkdtemp(prefix="roadmap-toy-")
    subprocess.run(["git", "init", "-q", top], check=True)
    for folder in ("docs/wiki", ".loop", ".git/loop/runs"):
        os.makedirs(os.path.join(top, folder))
    files = {"docs/ROADMAP.md": SOURCE, "docs/wiki/Foo.md": "# Foo\n\n- FOO-1: **Unreviewed** a requirement nobody read\n",
             ".loop/queue.md": "# Goal queue\n\n- slug: queued-goal | goal: waits | done: x\n- slug: finished-goal | goal: Fix #23 | done: x\n",
             ".git/loop/runs/live-goal.json": json.dumps({"slug": "live-goal", "status": "running", "goal": "Fix #12 now, edit C:\\Users\\bob\\code and /home/bob/x"}),
             ".git/loop/runs/finished-goal.json": json.dumps({"slug": "finished-goal", "status": "done", "goal": "Fix #23"}),
             ".git/loop/runs/odd.json": json.dumps({"slug": ["a"], "status": "running", "goal": "g"}),
             "issues.json": json.dumps(ISSUES)}
    for name, text in files.items():
        with open(os.path.join(top, name), "w") as handle:
            handle.write(text)
    return top


top = build()
done = subprocess.run([sys.executable, script, "roadmap", "--issues", os.path.join(top, "issues.json")], cwd=top, capture_output=True, text=True)
page = done.stdout
groups, _, after = page.partition("## After v1.0")
rows = {line.split("|")[1].strip(): line for line in page.splitlines() if line.startswith("| #") or line.startswith("| `")}

check("the page prints and exits 0", done.returncode == 0 and page.startswith("<!-- workflow-docs -->"))
check("closed: a hand row whose issue is not open drops out", "| #10 " not in page and "closed row" not in page)
check("status: in flight, queued and open", "in flight" in rows.get("#12", "") and "queued" in rows.get("`queued-goal`", "") and "| open |" in rows.get("#11", ""))
check("backlog: a Backlog milestone issue sits under after v1.0, not in a group", "#14" in after and "#14" not in groups and "### Backlog: Setup" in after)
check("priority: every group row ends with an empty Priority", all(rows[k].rstrip().endswith("|  |") for k in ("#11", "#12", "#13")) and "Priority" in page)
check("by label: a size issue lands in Size caps", "#13" in groups.split("### Windows-safe")[0])
check("unreviewed: a page's Unreviewed requirement is listed", "| Foo | FOO-1 |" in page)
before, _, todos = groups.partition("## Off-machine")
check("to-do: a To-do issue is listed apart and in no group", "prove it on a Mac" in todos and "prove it on a Mac" not in before)
check("hand row on a Backlog or To-do issue: listed once, apart", page.count("#20") == 1 and page.count("#21") == 1 and "#20" in after)
check("finished: a goal already run is not queued", "| #23 | already run | v1.0.0 | open |" in page)
check("paths: a home path in a goal's text never reaches the page", "bob" not in page and "~" in page)
odd = os.path.join(top, "odd.json")
with open(odd, "w") as handle:
    handle.write("null")
again = subprocess.run([sys.executable, script, "roadmap", "--issues", odd, "--out", "nodir/x.md"], cwd=top, capture_output=True, text=True)
check("odd input: a null issues file and a new --out folder are handled, not a traceback", again.returncode == 0 and "Traceback" not in again.stderr and os.path.exists(os.path.join(top, "nodir", "x.md")))
check("rollout: the Rollout section is copied", "## Rollout" in page and "`migrate-one`" in page)

with open(os.path.join(top, ".loop", "docs.tsv"), "w") as handle:
    handle.write("Foo\tsrc\nRoadmap\tdocs/ROADMAP.md\n")
with open(os.path.join(top, ".loop", "config.json"), "w") as handle:
    json.dump({"wiki_dir": "docs/wiki", "criteria": False}, handle)
subprocess.run([sys.executable, script, "roadmap", "--issues", os.path.join(top, "issues.json"), "--out", "docs/wiki/Roadmap.md"], cwd=top, capture_output=True, text=True)
checked = subprocess.run([sys.executable, docs, "check"], cwd=top, capture_output=True, text=True)
check("the written Roadmap guide page passes docs.py check", "Roadmap" not in checked.stdout.replace("Roadmap\tdocs", "") or "FORMAT Roadmap" not in checked.stdout)

print("ROADMAP TOY: %d failed" % fails if fails else "ROADMAP TOY OK")
sys.exit(1 if fails else 0)
