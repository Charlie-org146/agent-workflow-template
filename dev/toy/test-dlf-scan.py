#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/private.py skills/workflow-delivery/scripts/dlf_cut.py
"""DLF-1.3 (the privacy rule it keeps): every text deliver-first writes outside the run record goes through the one filing
routine's private-name scan. One case per outside write path (a line comment, an event comment, the cap line, a patch-goal
conversion, the release issue body) with a planted name: nothing is written, the text stays in the run record, and the
routine says so. A negative control (the same call, no planted name) writes. A mutation control (the scan forced clean)
writes the planted name, so each case can fail. Temp home, a fake gh on PATH, no network."""
import json
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
home = tempfile.mkdtemp()
fake = os.path.join(home, "fake")
os.makedirs(fake)
os.makedirs(os.path.join(home, "bin"))
os.symlink(os.path.join(root, "dev", "toy", "dlf-gh"), os.path.join(home, "bin", "gh"))
open(os.path.join(home, "names"), "w").write("# the planted list\nacmesecret\n")
os.environ.update(HOME=home, USERPROFILE=home, PATH=os.path.join(home, "bin") + os.pathsep + os.environ["PATH"], DLF_FAKE_DIR=fake,
                  LOOP_PRIVATE_NAMES=os.path.join(home, "names"))
import dlf  # noqa: E402
import dlf_cut  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def posts():
    calls = [json.loads(x) for x in open(os.path.join(fake, "calls.log"))] if os.path.exists(os.path.join(fake, "calls.log")) else []
    return [" ".join(c) for c in calls if "POST" in c]


def reset():
    for name in ("state.json", "calls.log"):
        if os.path.exists(os.path.join(fake, name)):
            os.remove(os.path.join(fake, name))


top, runs = os.path.join(home, "repo"), os.path.join(home, "runs")
os.makedirs(os.path.join(top, ".loop"))
os.makedirs(runs)
open(os.path.join(top, ".loop", "queue.md"), "w").write("# Goal queue\n")

PATHS = {
    "a line comment": lambda bad: dlf.file_line(top, runs, "g1", "v1", "break", "other", "b1", "a break %s" % bad, "accept", "keep"),
    "an event comment": lambda bad: (dlf.ensure_issue(top, runs, "g1", "v1"), dlf_cut.post_event(top, runs, "g1", "v1", "g1|break|other|b1", "closed", "g1-break-1 closed %s" % bad)) and "",
    "the cap line": lambda bad: dlf.cap_line(top, runs, "g1" + bad, "v1", 480, 240, 240, 480),
    "a patch-goal conversion": lambda bad: (dlf_cut.convert(top, runs, "g1", "v1", "g1|break|other|b1", "g1-break-1", "fix %s" % bad, "settle"), ""),
    "the release issue body": lambda bad: dlf.file_line(top, runs, "g1", "v1" + bad, "break", "other", "b2", "a break", "accept", "keep"),
}
for name, call in PATHS.items():
    for bad, planted in (("acmesecret", True), ("", False)):
        reset()
        open(os.path.join(top, ".loop", "queue.md"), "w").write("# Goal queue\n")
        for f in os.listdir(runs):
            os.remove(os.path.join(runs, f))
        call(bad)
        if planted:
            check(not any("acmesecret" in p for p in posts()), "%s: a planted name is never written to GitHub" % name)
            check(not any("acmesecret" in l for l in open(os.path.join(top, ".loop", "queue.md"))), "%s: nor to the queue" % name)
            kept = json.dumps(dlf.mem(runs, "g1")) + json.dumps(dlf.mem(runs, "g1acmesecret"))
            check("acmesecret" in kept, "%s: the text stays in the run record" % name)
        else:
            written = bool(posts()) or "patch" in open(os.path.join(top, ".loop", "queue.md")).read()
            check(written, "%s: the same call without the name writes (negative control)" % name)
        reset()
        real = dlf.private.scan
        dlf.private.scan = lambda *a, **k: {"state": "clean", "hits": [], "note": ""}
        try:
            call(bad) if planted else None
            wrote = any("acmesecret" in p for p in posts()) or any("acmesecret" in l for l in open(os.path.join(top, ".loop", "queue.md")))
        finally:
            dlf.private.scan = real
        planted and check(wrote, "%s: with the scan forced clean the name is written, so this case can fail (mutation control)" % name)

reset()
os.environ["LOOP_PRIVATE_NAMES"] = os.path.join(home, "missing")
dlf.file_line(top, runs, "g1", "v1", "break", "other", "b3", "a break", "accept", "keep")
check(not posts(), "no private-name list: nothing is written (the scan fails closed)")
sys.exit(1 if failed else 0)
