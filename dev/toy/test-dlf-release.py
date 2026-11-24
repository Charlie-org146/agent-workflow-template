#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/release.py skills/workflow-delivery/scripts/dlf.py skills/workflow-release/scripts/release_docs.py skills/workflow-delivery/scripts/dlf_cut.py
"""DLF-1.4 at the release step: the debt gate before a cut fails CLOSED. With workflow-delivery missing beside workflow-release the cut
is refused with a clear line (never skipped); with it present and the release's issue clean the gate lets the cut go on; with an open
line it refuses. Temp home, a fake gh on PATH, no network."""
import json
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
home = tempfile.mkdtemp()
fake, top, runs = (os.path.join(home, n) for n in ("fake", "repo", "runs"))
for d in (fake, top + "/.loop", runs, home + "/bin"):
    os.makedirs(d)
os.symlink(os.path.join(root, "dev", "toy", "dlf-gh"), home + "/bin/gh")
open(home + "/names", "w").write("acmesecret\n")
json.dump({"owner_login": "boss"}, open(top + "/.loop/config.json", "w"))
open(top + "/.loop/queue.md", "w").write("# Goal queue\n")
os.environ.update(HOME=home, PATH=home + "/bin" + os.pathsep + os.environ["PATH"], DLF_FAKE_DIR=fake, LOOP_PRIVATE_NAMES=home + "/names")
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
import release  # noqa: E402
import release_docs  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


real = release_docs.DELIVERY
release_docs.DELIVERY = os.path.join(home, "no-delivery-skill")
said = release_docs.debt(top, "g1", runs)
check(said.startswith("the deliver-first ledger can't be read") and "workflow-delivery" in said, "finding 9: with workflow-delivery missing the debt gate refuses with a clear line: %s" % said[:80])
release_docs.DELIVERY = real
check(release_docs.debt(top, "g1", runs) == "", "with the delivery skill present and no issue for the release the gate lets the cut go on")
import dlf  # noqa: E402
dlf.file_line(top, runs, "g1", "default", "break", "other", "b1", "a break", "words", "rec")
check(release_docs.debt(top, "g1", runs).startswith("Release default has 1 open deliver-first line"), "an open line makes the gate refuse with the list")
sys.exit(1 if failed else 0)
