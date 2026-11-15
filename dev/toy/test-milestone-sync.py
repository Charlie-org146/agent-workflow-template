#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/milestones.py skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/counting.py
"""milestone-sync (DOC-17): a repo opts in to keeping its GitHub milestones in step with an external Milestones page by setting
milestones_source in .loop/config.json. docs.py sync then compares each milestone, by title, state and due date, with what both sides
last agreed on: a change from either side is a DELTA, a milestone that differs on both is a CONFLICT, neither is overwritten, each is
posted once as an issue and once as a comment on the page, and --accept milestones:TITLE=repo|source writes that side to the other. A
repo with no milestones_source is never visited. The fake gh, reader and writer here keep their state in files: the real GitHub and
Notion are never used."""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, "skills", "workflow-docs", "scripts", "docs.py")
bad = 0

FAKE_GH = '''import json, os, sys
args = sys.argv[1:]
open(os.environ["TOY_LOG"], "a").write(json.dumps(["gh"] + args) + "\\n")
if os.environ.get("TOY_GH_FAIL"):
    sys.exit("gh: not logged in")
items = json.load(open(os.environ["TOY_MS"]))
if args[0] == "api":
    method = args[args.index("-X") + 1] if "-X" in args else "GET"
    if method == "GET":
        print(json.dumps(items[:2]) + "\\n" + json.dumps(items[2:]))
    else:
        fields = {a.split("=")[0]: a.split("=", 1)[1] for a in args if "=" in a and not a.startswith("repos")}
        due = None if fields["due_on"] == "null" else fields["due_on"]
        if method == "POST":
            items.append({"number": len(items) + 1, "title": fields["title"], "state": fields["state"], "due_on": due})
        else:
            for item in items:
                if item["number"] == int(next(a for a in args if a.startswith("repos")).rsplit("/", 1)[1]):
                    item.update(state=fields["state"], due_on=due)
        json.dump(items, open(os.environ["TOY_MS"], "w"))
if args[:2] == ["issue", "create"]:
    n = sum(1 for x in open(os.environ["TOY_LOG"]) if '"issue", "create"' in x)
    print("https://example.test/issues/%d" % n)
'''
FAKE_READER = '''import os, sys
if os.environ.get("TOY_READER_FAIL"):
    sys.exit(1)
sys.stdout.write(open(os.environ["TOY_PAGE"]).read())
'''
FAKE_WRITER = '''import json, os, sys
action, text = sys.argv[2:], sys.stdin.read()
open(os.environ["TOY_LOG"], "a").write(json.dumps(["writer"] + action + [text]) + "\\n")
if action[0] in ("replace", "remove"):
    lines = open(os.environ["TOY_PAGE"]).read().split("\\n")
    keep = [x for x in lines if not x.startswith("- %s: " % action[1])]
    if action[0] == "replace":
        keep.append("- %s: %s" % (action[1], text))
    open(os.environ["TOY_PAGE"], "w").write("\\n".join(keep))
'''


def ok(good, text):
    global bad
    print(("PASS: " if good else "FAIL: ") + text)
    bad += not good


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as handle:
        handle.write(text)


def read(path):
    with open(path, newline="") as handle:
        return handle.read()


def due(day):
    return day + "T00:00:00Z"


with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    subprocess.run(["git", "init", "-q", "-b", "main", repo], capture_output=True)
    log, page, ms = (os.path.join(tmp, name) for name in ("calls.log", "page.md", "ms.json"))
    for name, text in (("gh.py", FAKE_GH), ("reader.py", FAKE_READER), ("writer.py", FAKE_WRITER)):
        write(os.path.join(tmp, name), text)
    ENV = {"TOY_LOG": log, "TOY_PAGE": page, "TOY_MS": ms, "LOOP_GH": "%s %s" % (sys.executable, os.path.join(tmp, "gh.py")),
           "LOOP_PRD_READER": "%s %s" % (sys.executable, os.path.join(tmp, "reader.py")),
           "LOOP_PRD_WRITER": "%s %s" % (sys.executable, os.path.join(tmp, "writer.py"))}
    config, copy = os.path.join(repo, ".loop", "config.json"), os.path.join(repo, ".loop", "milestones.md")

    def sync(*args, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("LOOP_PRD_", "LOOP_GH", "TOY_"))}
        env.update(ENV)
        env.update(extra)
        done = subprocess.run([sys.executable, DOCS, "sync", *args], cwd=repo, env=env, capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    def calls(*words):
        try:
            return [x for x in read(log).splitlines() if all(w in x for w in words)]
        except OSError:
            return []

    def milestones():
        return {m["title"]: (m["state"], (m["due_on"] or "")[:10]) for m in json.load(open(ms))}

    items = [("v1", "open", "2026-12-01"), ("v2", "open", None), ("v0", "closed", "2026-01-01"), ("Beta: 1=2", "open", None)]
    write(ms, json.dumps([{"number": i + 1, "title": t, "state": s, "due_on": due(d) if d else None} for i, (t, s, d) in enumerate(items[:3])]))
    write(page, "# Milestones\n\n- v1: open | due 2026-12-01\n- v2: open | no due\n")

    write(config, json.dumps({"base": "main"}))
    code, out = sync()
    ok(code == 0 and "ilestone" not in out and not calls(), "a repo with no milestones_source prints nothing about milestones and calls neither gh, reader nor writer")
    code, out = sync("--open")
    ok(code == 0 and "ilestone" not in out and not os.path.exists(copy) and not calls(), "--open with no source is quiet too and writes nothing")

    write(config, json.dumps({"base": "main", "milestones_source": "mcp:toy:milestones"}))
    code, out = sync()
    ok(code == 0 and "DELTA" not in out and "CONFLICT" not in out and "3 in step" in out and "v0" not in out and not calls("issue") and not calls("writer"),
       "the first sync with the sides alike raises no delta, and a closed milestone missing from the page is the same as absent")
    ok(os.path.exists(copy) and "- v1: open | due 2026-12-01" in read(copy) and not calls('"POST"') and not calls('"PATCH"'), "it writes the agreed copy and changes neither side")

    items = json.load(open(ms))
    items[1]["due_on"] = due("2027-01-15")
    write(ms, json.dumps(items))
    before = read(page), read(copy)
    code, out = sync("--dry-run")
    ok(code == 1 and "DELTA milestones: v2 the repo changed (repo: open | due 2027-01-15 | source: open | no due)" in out,
       "a milestone changed only on GitHub is a DELTA naming the title, the repo as the side and both texts, and --dry-run exits 1")
    ok(not calls("issue") and not calls("writer") and (read(page), read(copy)) == before, "--dry-run posts and writes nothing")
    code, out = sync()
    ok(code == 0 and "DELTA milestones: v2 the repo changed" in out and read(page) == before[0] and milestones()["v2"] == ("open", "2027-01-15") and not calls('"PATCH"'),
       "a delta overwrites neither side")
    ok(len(calls("issue", "create")) == 1 and "DELTA milestones v2" in calls("issue", "create")[0] and "--milestone" not in calls("issue", "create")[0]
       and len(calls("writer", "comment")) == 1 and "2027-01-15" in calls("writer", "comment")[0], "a new delta is posted once as an issue and once as a comment on the page")
    sync()
    ok(len(calls("issue", "create")) == 1 and len(calls("writer", "comment")) == 1, "a second sync posts nothing more")

    write(page, read(page).replace("- v1: open | due 2026-12-01", "- v1: closed | due 2026-12-01"))
    code, out = sync()
    ok("DELTA milestones: v1 the source changed (repo: open | due 2026-12-01 | source: closed | due 2026-12-01)" in out and len(calls("issue", "create")) == 2,
       "a milestone changed only on the page is a DELTA naming the source, posted as its own issue")
    write(page, read(page).replace("- v2: open | no due", "- v2: closed | no due"))
    code, out = sync()
    ok("CONFLICT milestones: v2 both sides changed" in out and milestones()["v2"] == ("open", "2027-01-15") and "- v2: closed | no due" in read(page) and len(calls("issue", "comment")) == 1,
       "a milestone that differs on both sides is a CONFLICT, overwritten on neither, and its issue is commented again")

    code, out = sync("--accept", "milestones:v1=source")
    patch = calls('"PATCH"')
    ok("ACCEPTED milestones: v1, the source's text" in out and milestones()["v1"] == ("closed", "2026-12-01") and len(patch) == 1 and "milestones/1" in patch[0]
       and len(calls('"issue", "close"')) == 1 and milestones()["v2"] == ("open", "2027-01-15"),
       "accepting the source edits only that GitHub milestone, by its number, and closes its issue")
    code, out = sync("--accept", "milestones:v2=repo")
    ok("ACCEPTED milestones: v2, the repo's text" in out and "- v2: open | due 2027-01-15" in read(page) and calls("writer", "replace", "v2") and len(calls('"issue", "close"')) == 2,
       "accepting the repo writes only that milestone to the page through the writer and closes its issue")
    code, out = sync()
    ok(code == 0 and "0 with a delta" in out and "DELTA" not in out and "CONFLICT" not in out and not [x for x in sync("--open")[1].splitlines() if "milestones" in x],
       "after both are accepted the sides agree and no milestone delta stays open")

    write(page, read(page).rstrip("\n") + "\n- v3: open | due 2027-03-01\n")
    code, out = sync()
    ok("DELTA milestones: v3 the source changed" in out, "a milestone added on the page is a DELTA from the source")
    code, out = sync("--accept", "milestones:v3=source")
    ok("ACCEPTED milestones: v3" in out and milestones().get("v3") == ("open", "2027-03-01") and calls('"POST"'), "accepting an added milestone from the source creates it on GitHub")

    items = json.load(open(ms))
    items.append({"number": 9, "title": "Beta: 1=2", "state": "open", "due_on": None})
    write(ms, json.dumps(items))
    code, out = sync()
    ok("DELTA milestones: Beta: 1=2 the repo changed (repo: open | no due | source: -)" in out, "a milestone added on GitHub is a DELTA from the repo, even with a colon and an equals sign in its title")
    code, out = sync("--accept", "milestones:Beta: 1=2=repo")
    ok("ACCEPTED milestones: Beta: 1=2, the repo's text" in out and "- Beta: 1=2: open | no due" in read(page) and "0 with a delta" in sync()[1],
       "accepting it writes the line to the page, splitting the title from the side on the last equals sign")

    before = read(page), read(copy), len(calls())
    write(page, read(page).rstrip("\n") + "\n- v4: open | due 2027-05-01\n")
    code, out = sync(TOY_GH_FAIL="1")
    ok(code == 0 and "not connected: milestones (gh)" in out and "DELTA" not in out and read(copy) == before[1] and "v4" not in read(copy),
       "with gh unreachable sync says not connected, changes nothing and exits 0")
    code, out = sync(TOY_READER_FAIL="1")
    ok(code == 0 and "not connected: milestones (mcp:toy:milestones)" in out and read(copy) == before[1], "with the page unreachable sync says not connected, changes nothing and exits 0")
    code, out = sync("--accept", "milestones:v4=source", TOY_GH_FAIL="1")
    ok(code == 0 and "not connected" in out and "ACCEPTED" not in out, "accepting with gh unreachable says not connected and accepts nothing")

    write(config, json.dumps({"base": "main"}))
    count = len(calls())
    code, out = sync()
    ok(code == 0 and "ilestone" not in out and len(calls()) == count, "a repo that drops its milestones_source is no longer visited")

    scripts = os.path.join(ROOT, "skills", "workflow-docs", "scripts")
    texts = [read(os.path.join(scripts, name)) for name in ("milestones.py", "docs.py")]
    ok(not any(re.search(r"notion\.(so|site|com)|[0-9a-f]{32}", text) for text in texts), "the template's milestone code names no page link or id")

raise SystemExit(1 if bad else 0)
