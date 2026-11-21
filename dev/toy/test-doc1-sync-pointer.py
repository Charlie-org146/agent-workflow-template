#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/prdcopy.py skills/workflow-docs/scripts/pageformat.py
"""doc1-sync-pointer (#5308): the sync pointer is checked by requirement ID and meaning, never by a sentence. The PRD-sync
behaviour DOC-1's pointer named is requirement DOC-17. Its ID is followed through the pages' retirement lines ("- ID: moved to
ID") to the live requirement that now carries it, which must still say it syncs; docs.py must still have a sync command, the
How-to-use page must still name it, and DECISIONS.md must still record the pointer. Rewording any requirement keeps this green;
losing the behaviour, the command, the page line or the record turns it red."""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = "skills/workflow-docs/scripts/docs.py"
PAGES = "docs/wiki"
HOWTO = "docs/wiki/How-to-use-Documentation.md"
START = "DOC-17"


def read(root, rel):
    try:
        return open(os.path.join(root, rel), encoding="utf-8").read()
    except OSError:
        return ""


def live_block(root, rid, hops=5):
    """The text of the live requirement rid reaches, following 'moved to' / 'merged into' lines; '' when it reaches none."""
    folder = os.path.join(root, PAGES)
    names = sorted(n for n in os.listdir(folder) if n.endswith(".md") and not n.startswith("How-to-use")) if os.path.isdir(folder) else []
    text = "\n".join(read(root, PAGES + "/" + n) for n in names)
    for _ in range(hops):
        live = re.search(r"^- %s: \*\*.*?(?=^- [A-Z]{2,5}-\d+: |^#|\Z)" % re.escape(rid), text, re.M | re.S)
        if live:
            return live.group(0)
        moved = re.search(r"^- %s: (?:moved to|merged into) ([A-Z]{2,5}-\d+)" % re.escape(rid), text, re.M)
        if not moved:
            return ""
        rid = moved.group(1)
    return ""


def check(root):
    """The list of what is missing, empty when the sync pointer holds."""
    gone = []
    block = live_block(root, START)
    if not block:
        gone.append("%s reaches no live requirement" % START)
    elif not re.search(r"\bsync|in step", block, re.I):
        gone.append("the requirement %s reaches no longer says it syncs" % START)
    if not os.path.exists(os.path.join(root, DOCS)):
        gone.append("no docs.py")
    else:
        try:
            code = subprocess.run([sys.executable, os.path.join(root, DOCS), "sync", "--help"], capture_output=True, text=True, cwd=root, timeout=60).returncode
        except subprocess.TimeoutExpired:
            code = 1
        if code != 0:
            gone.append("docs.py has no sync command")
    if "docs.py sync" not in read(root, HOWTO):
        gone.append("the How-to-use page does not name docs.py sync")
    if "wiki-current: DOC-1 sync pointer" not in read(root, "DECISIONS.md"):
        gone.append("DECISIONS.md does not record the DOC-1 sync pointer")
    return gone


def fixture(**over):
    root = tempfile.mkdtemp()
    files = {
        PAGES + "/Documentation.md": "- DOC-1: moved to DOC-25\n- DOC-17: moved to DOC-2\n\n- DOC-2: **Reviewed 2026-11-20** Only I write\n  - An outside document may sync into it. [DOC-2]\n- DOC-3: **Unreviewed** other\n  - nothing here\n",
        HOWTO: "`docs.py sync`\n",
        "DECISIONS.md": "## wiki-current: DOC-1 sync pointer (2026-11-14)\n",
        DOCS: "import sys\nsys.exit(0 if sys.argv[1:2] == ['sync'] else 2)\n",
    }
    files.update(over)
    for rel, body in files.items():
        if body is None:
            continue
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        open(os.path.join(root, rel), "w", encoding="utf-8").write(body)
    return root


bad = 0


def expect(label, ok):
    global bad
    print(("PASS: " if ok else "FAIL: ") + label)
    bad += 0 if ok else 1


expect("the repo's sync pointer holds by ID" + "".join("; " + g for g in check(ROOT)), check(ROOT) == [])
expect("a fixture with the pointer in place passes", check(fixture()) == [])
expect("rewording the requirement keeps it green where the old DOC-1 sentence grep fails",
       check(fixture(**{PAGES + "/Documentation.md": "- DOC-17: moved to DOC-2\n- DOC-2: **Reviewed 2026-11-21** Wholly new words\n  - Syncing stays opt-in. [DOC-2]\n"})) == [])
expect("rewording to 'kept in step with an outside document' without the word sync stays green",
       check(fixture(**{PAGES + "/Documentation.md": "- DOC-17: moved to DOC-2\n- DOC-2: **Reviewed 2026-11-21** Wholly new words\n  - The repo copy is kept in step with an outside document. [DOC-2]\n"})) == [])
expect("negative control: a live home that no longer says it syncs fails",
       any("no longer says" in g for g in check(fixture(**{PAGES + "/Documentation.md": "- DOC-17: moved to DOC-2\n- DOC-2: **Unreviewed** Only I write\n  - Nothing else. [DOC-2]\n"}))))
expect("negative control: an ID that reaches no live requirement fails",
       any("reaches no live" in g for g in check(fixture(**{PAGES + "/Documentation.md": "- DOC-2: **Unreviewed** sync\n"}))))
expect("negative control: a retirement loop fails instead of spinning",
       any("reaches no live" in g for g in check(fixture(**{PAGES + "/Documentation.md": "- DOC-17: moved to DOC-2\n- DOC-2: moved to DOC-17\n"}))))
expect("negative control: a missing docs.py fails",
       any("no docs.py" in g for g in check(fixture(**{DOCS: None}))))
expect("negative control: a docs.py with no sync command fails",
       any("no sync command" in g for g in check(fixture(**{DOCS: "import sys\nsys.exit(2)\n"}))))
expect("negative control: a How-to-use page that drops docs.py sync fails",
       any("How-to-use" in g for g in check(fixture(**{HOWTO: "nothing\n"}))))
expect("negative control: DECISIONS.md without the record fails",
       any("DECISIONS" in g for g in check(fixture(**{"DECISIONS.md": "## other\n"}))))
sys.exit(1 if bad else 0)
