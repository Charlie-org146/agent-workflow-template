#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/permissions.py
"""AUT-9: permissions.py write and check. Each case builds a throwaway repo with one routine (a Runbook on a page) and
runs the script; the broken copies prove each finding can fire."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
script = os.path.join(root, "skills", "workflow-docs", "scripts", "permissions.py")
fails = 0

PAGE = """# Feature

## Runbook

### round
- **Steps:** Run `python3 skills/x/scripts/round.py go` then `gh auth status`, and read https://api.example.com/v1.
- **Full run:** the whole round.
- **Never:** never push.
"""
ROWS = [
    ("round", "allow", "Bash(python3 skills/x/scripts/*)", "the round"),
    ("round", "allow", "Bash(gh auth status)", "probe"),
    ("round", "allow", "WebFetch(domain:api.example.com)", "the api"),
    ("round", "deny", "Bash(git push:*)", "Never: push"),
]


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def repo(rows=ROWS, settings=None, page=PAGE):
    top = tempfile.mkdtemp(prefix="perm-toy-")
    subprocess.run(["git", "init", "-q", top], check=True)
    os.makedirs(os.path.join(top, ".loop"))
    os.makedirs(os.path.join(top, "docs", "wiki"))
    with open(os.path.join(top, ".loop", "routines.tsv"), "w") as handle:
        handle.write("round\tFeature\n")
    with open(os.path.join(top, "docs", "wiki", "Feature.md"), "w") as handle:
        handle.write(page)
    if rows is not None:
        with open(os.path.join(top, ".loop", "permissions.tsv"), "w") as handle:
            handle.write("".join("\t".join(row) + "\n" for row in rows))
    if settings is not None:
        os.makedirs(os.path.join(top, ".claude"))
        with open(os.path.join(top, ".claude", "settings.json"), "w") as handle:
            json.dump(settings, handle)
    return top


def run(top, command):
    done = subprocess.run([sys.executable, script, command, "--repo", top], capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def settings_of(top):
    with open(os.path.join(top, ".claude", "settings.json")) as handle:
        return json.load(handle)


top = repo()
code, out = run(top, "check")
check("not written: rows the settings lack are reported and exit 1", code == 1 and out.count("NOT WRITTEN") == 4)
code, out = run(top, "write")
check("write: the rows land in .claude/settings.json", code == 0 and "WRITTEN: 4" in out and len(settings_of(top)["permissions"]["allow"]) == 3)
code, out = run(top, "check")
check("good: a written, covered routine is PERMISSIONS OK", code == 0 and "PERMISSIONS OK" in out)

top = repo(settings={"model": "x", "permissions": {"allow": ["Bash(ls:*)"], "ask": ["Bash(rm:*)"]}})
run(top, "write")
held = settings_of(top)
check("write keeps a foreign key, rule and list", held["model"] == "x" and "Bash(ls:*)" in held["permissions"]["allow"] and held["permissions"]["ask"] == ["Bash(rm:*)"])
before = json.dumps(held)
code, out = run(top, "write")
check("write twice changes nothing", "CURRENT" in out and json.dumps(settings_of(top)) == before)

top = repo(rows=[("other", "allow", "Bash(ls:*)", "x")])
code, out = run(top, "check")
check("undeclared: a routine with no rows is reported", code == 1 and "UNDECLARED round" in out)

top = repo(rows=None)
code, out = run(top, "check")
check("no permissions file: a NOTE, not a failure", code == 0 and "NOTE" in out)

top = repo(rows=ROWS[:1] + ROWS[3:])
run(top, "write")
code, out = run(top, "check")
check("uncovered: a Runbook command and site no allow row covers", code == 1 and "UNCOVERED" in out and "gh auth status" in out and "api.example.com" in out)

top = repo(rows=ROWS + [("round", "allow", "Bash(git push origin main)", "wrong")])
run(top, "write")
code, out = run(top, "check")
check("conflict: an allow a deny covers", code == 1 and "CONFLICT round" in out)

for bad in ("Bash(cat /Users/someone/x)", "Bash(cat C:\\Users\\someone\\x)", "Bash(echo ghp_abcdefgh)"):
    top = repo(rows=[("round", "allow", bad, "x")])
    code, out = run(top, "write")
    check("private row refused: " + bad.split("(")[1][:12], code == 1 and "PRIVATE ROW" in out and not os.path.exists(os.path.join(top, ".claude", "settings.json")))

top = repo(settings={"permissions": {}})
with open(os.path.join(top, ".claude", "settings.json"), "w") as handle:
    handle.write("{not json")
code, out = run(top, "write")
check("unreadable settings: refused, nothing written", code == 1 and "REFUSED" in out)

top = tempfile.mkdtemp(prefix="perm-toy-")
subprocess.run(["git", "init", "-q", top], check=True)
code, out = run(top, "check")
check("a repo with no routines passes", code == 0 and "PERMISSIONS OK" in out)

docs = os.path.join(root, "skills", "workflow-docs", "scripts", "docs.py")
top = repo(rows=[("other", "allow", "Bash(ls:*)", "x")])
with open(os.path.join(top, ".loop", "docs.tsv"), "w") as handle:
    handle.write("Feature" + chr(9) + "src" + chr(10))
with open(os.path.join(top, ".loop", "config.json"), "w") as handle:
    json.dump({"wiki_dir": "docs/wiki", "criteria": False}, handle)
done = subprocess.run([sys.executable, docs, "check"], cwd=top, capture_output=True, text=True)
check("docs check prints the PERMISSIONS finding for an undeclared routine", "PERMISSIONS permissions.tsv: UNDECLARED round" in done.stdout)

print("PERMISSIONS TOY: %d failed" % fails if fails else "PERMISSIONS TOY OK")
sys.exit(1 if fails else 0)
