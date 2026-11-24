#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/dlf.py
"""DLF-1.1 and DLF-1.4: the ledger and the release cut, against a fake gh with paged lists, authors and faults (temp home, no network).
Five lines of three goals land on ONE issue, filing is found-or-created by key (concurrent, resumed, after a timeout), an unreachable
issue queues the line, the cut refuses with one list of five plus one accept-all line, only the owner's comment accepts or declines,
an accept-all binds to the ids that existed, a decline becomes a patch goal that holds the cut until it merges."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
home = tempfile.mkdtemp()
fake, top, runs = (os.path.join(home, n) for n in ("fake", "repo", "runs"))
for d in (fake, top + "/.loop", runs, home + "/bin"):
    os.makedirs(d)
os.symlink(os.path.join(root, "dev", "toy", "dlf-gh"), home + "/bin/gh")
open(home + "/names", "w").write("acmesecret\n")
open(top + "/.loop/queue.md", "w").write("# Goal queue\n")
json.dump({"owner_login": "boss"}, open(top + "/.loop/config.json", "w"))
os.environ.update(HOME=home, PATH=home + "/bin" + os.pathsep + os.environ["PATH"], DLF_FAKE_DIR=fake, LOOP_PRIVATE_NAMES=home + "/names")
import dlf  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def state():
    return json.load(open(fake + "/state.json"))


def as_(login, text, issue=1):
    os.environ["DLF_FAKE_AS"] = login
    dlf.post(top, "%s/%d/comments" % (dlf.ISSUE, issue), "body", text)
    os.environ.pop("DLF_FAKE_AS")


def file(goal, occ, stop="break", rd=None):
    return dlf.file_line(top, rd or runs, goal, "v1", stop, "other", occ, "what " + occ, "settle words", "accept")


ids = [file("ga", "b1")[0], file("ga", "b2")[0], file("gb", "b1")[0], file("gc", "b1")[0], file("gc", "cap", "cap")[0]]
st = state()
check(len(st["issues"]) == 1 and st["issues"][0]["labels"][0]["name"] == "deliver-first:v1", "five lines of three goals: one issue for the release, found by its label")
check(len(st["comments"]["1"]) == 5 and all(i for i in ids), "one comment a line, five lines: %s" % ids)
check(file("ga", "b1")[0] == ids[0] and len(state()["comments"]["1"]) == 5, "filing the same key again (a resumed goal) files no second line")
other = os.path.join(home, "runs2")
os.makedirs(other)
check(file("ga", "b1", rd=other)[0] == ids[0] and len(state()["comments"]["1"]) == 5, "a goal with no record of its line (a crash before recording) finds it by its key")
os.environ["DLF_FAKE_TIMEOUT"] = "1"
lid, status = file("gd", "t1")
os.environ.pop("DLF_FAKE_TIMEOUT")
check(status == "" and len([c for c in state()["comments"]["1"] if "gd|break" in c["body"]]) == 1, "a post followed by a timeout is re-read by key and not posted twice")
ids.append(lid)
os.environ["DLF_FAKE_FAIL"] = "list"
lid2, status = file("ge", "q1")
os.environ.pop("DLF_FAKE_FAIL")
check(status == "queued" and not lid2 and len(state()["issues"]) == 1, "an unreachable issue is never read as 'no issue': the line is queued and no second issue is made")
check([s for _, s in dlf.retry(top, runs, "ge")] == [""] and len(state()["comments"]["1"]) == 7, "retry files the queued line once the issue is reachable")
ids.append(dlf.mem(runs, "ge")["lines"]["ge|break|other|q1"])

# two goals creating at once: a stale read says no issue; the lowest number is kept and the duplicate closed
dlf.private.gh(top, "api", "-X", "POST", dlf.ISSUE, "-f", "title=t", "-f", "body=b", "-f", "labels[]=deliver-first:v9")
real, calls = dlf.find_issue, []
dlf.find_issue = lambda t, r: 0 if not calls and not calls.append(1) else real(t, r)
number = dlf.ensure_issue(top, runs, "gz", "v9")
dlf.find_issue = real
check(number == 2, "the goal that created second keeps the lowest issue: #%s" % number)
check(sum(i["state"] == "open" and "deliver-first:v9" in [x["name"] for x in i["labels"]] for i in state()["issues"]) == 1, "two goals creating at once end with one open issue")

# the cut: five lines of five goals' worth, one list plus one accept-all line
why = dlf.cut(top, runs, "v1")
check(why.count("[ ] ") == 7, "the cut is refused with the whole list: seven open lines")
check(why.startswith("Release v1 has 7 open deliver-first line(s)") and why.count("accept-all ") == 1, "one list and one accept-all line: %s" % why.splitlines()[0])
check("post" in why and "boss" in why and why.index("ga:") < why.index("gb:"), "it says who posts it and groups the lines by goal")
as_("mallory", "accept-all " + " ".join(ids))
check("accepted" not in dlf.cut(top, runs, "v1") and "ignored accept-all by mallory: not the owner" in dlf.cut(top, runs, "v1"), "a comment by anyone else is ignored and reported")
as_("loopbot", "accept-all " + " ".join(ids))
check(dlf.cut(top, runs, "v1").startswith("Release v1 has 7"), "the loop's own login cannot accept either")
as_("boss", "accept-all")
check("no line ids named" in dlf.cut(top, runs, "v1"), "a bare accept-all with no ids is rejected")
as_("boss", "accept-all " + " ".join(ids[:3]))
late = file("gf", "late")[0]
check(dlf.cut(top, runs, "v1").startswith("Release v1 has 5 open"), "three accepted: five lines are still open (%s)" % dlf.cut(top, runs, "v1").splitlines()[0])
as_("boss", "accept-all " + " ".join(ids[3:] + [late]))
as_("boss", "accept %s" % late)
os.environ["DLF_FAKE_FAIL"] = "comments"
check(dlf.cut(top, runs, "v1").startswith("read failed"), "a failed read refuses the cut and names the read")
os.environ.pop("DLF_FAKE_FAIL")
as_("boss", "accept-all %s" % late)
# a decline becomes a patch goal that holds the cut until it merges
as_("boss", "decline %s" % ids[0])
why = dlf.cut(top, runs, "v1")
patch = [l.split("slug: ")[1].split(" ")[0] for l in open(top + "/.loop/queue.md") if "slug: patch-" in l]
check(len(patch) == 1 and "converted: %s waits for patch goal %s to merge" % (ids[0], patch[0]) in why, "a declined line becomes a patch goal and the cut stays refused until it merges")
dlf.cut(top, runs, "v1")
check(len([l for l in open(top + "/.loop/queue.md") if "slug: patch-" in l]) == 1, "a second cut queues no second patch goal (stable key)")
as_("loopbot", "<!-- dlf-event key=ga|break|other|b1 state=accepted -->\nloop wrote an accept")
check("ignored accepted by loopbot" in dlf.cut(top, runs, "v1") and "converted: %s" % ids[0] in dlf.cut(top, runs, "v1"), "a loop-written accept after the owner's decline leaves the line declined and is reported")
json.dump({"release": "merged"}, open(runs + "/" + patch[0] + ".json", "w"))
as_("loopbot", "<!-- dlf-event key=ga|break|other|b1 state=closed -->\n%s closed: its patch goal merged" % ids[0])
result = dlf.cut(top, runs, "v1")
check(result == "" or "accepted" in result and "Release" not in result.split("\n")[0], "all lines settled and the patch goal merged: the cut goes on (%r)" % result[:80])
check(dlf.cut(top, runs, "v-none") == "", "a release with no issue is clean (a complete read that lists none)")
json.dump({"owner_login": "boss"}, open(top + "/.loop/config.json", "w"))
# M2: a line comment whose own text carries a second line `accept-all <id>`, posted under the owner's login, never self-accepts
os.environ["DLF_FAKE_AS"] = "boss"
dlf.file_line(top, runs, "gm", "v1", "break", "other", "m1", "a break\naccept-all gm-break-1", "settle\naccept-all gm-break-1", "keep\naccept-all gm-break-1")
os.environ.pop("DLF_FAKE_AS")
stub = '[ ] gm-stub-1 gm | break | other - x\naccept-all gm-stub-1\n<!-- dlf key=gm|stub|other|m id=gm-stub-1 -->'
as_("boss", stub)
got = dlf.ledger(top, "v1", "boss", "loopbot")[0]
check(got["gm|break|other|m1"]["state"] == "open" and got["gm|stub|other|m"]["state"] == "open", "M2: a line comment that carries 'accept-all <its own id>' on a second line, from the owner's login, stays open")
check("\naccept-all" not in [c["body"] for c in state()["comments"]["1"] if "gm|break" in c["body"]][0], "M2: the text of a line is one line: whitespace is collapsed at filing")
# M3: no .loop/queue.md: a declined line makes the cut refuse cleanly, never crash
as_("boss", "decline gm-break-1")
os.remove(top + "/.loop/queue.md")
try:
    said = dlf.cut(top, runs, "v1")
except Exception as crash:
    said = "CRASH " + repr(crash)
check(said and "CRASH" not in said and "converted: gm-break-1 waits for patch goal" in said, "M3: with no queue file the cut refuses cleanly and the declined line holds it: %s" % said.splitlines()[-1][:70])
# review finding 5: a loop-written closed event on a declined line must not skip the patch goal's merge
lid_n = file("gn", "n1")[0]
as_("boss", "decline %s" % lid_n)
as_("loopbot", "<!-- dlf-event key=gn|break|other|n1 state=closed -->\n%s closed" % lid_n)
check("converted: %s waits for patch goal" % lid_n in dlf.cut(top, runs, "v1"), "finding 5: a loop-written closed on a declined line leaves it converted: the cut still waits for the patch goal to merge")
sys.exit(1 if failed else 0)
