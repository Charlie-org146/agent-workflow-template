#!/usr/bin/env python3
"""Word-for-word check for DEL-3 (goal v120-del3-text).

  v120-del3-text-check.py [--delivery PATH] [--source PATH]   check the live page against the source; exit 0 on OK, 1 on any finding
  v120-del3-text-check.py --body [--delivery PATH]            print the revise text file (title line, then the tagged lines)
  v120-del3-text-check.py --selftest                          prove the check passes on a faithful page and fails on four broken ones

The source is `.loop/goals/v120-del3-text.source.md` (its sha256 is pinned below). Its non-blank lines are the expected lines in order; a source
line starting with `- ` (DEL-3.1's five list lines) loses that `- ` (the revise command strips it too). The live lines are the sub-bullets under
the `- DEL-3:` requirement line with the leading `  - ` and the trailing ` [DEL-3]` removed, nothing else. The first row of the `### DEL-3`
revision table must hold the same text, built with the docs tool's own `pageformat.unit`.
"""
import hashlib
import os
import re
import subprocess
import sys

SHA = "bd3be682e232246073a08b71109769b55d1d01f609051674850d40966a087fc4"
TAG = " [DEL-3]"
TITLE = re.compile(r"^- DEL-3: (?:\*\*(?:Reviewed [0-9-]+|Unreviewed)\*\* )?(.*?)(?: <!-- reviewed [0-9a-f]+ -->)?$")


def root():
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()


def pageformat(top):
    sys.path.insert(0, os.path.join(top, "skills", "workflow-docs", "scripts"))
    import pageformat
    return pageformat


def read(path):
    return open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")


def expected(source):
    """The source's non-blank lines in order, a leading `- ` removed."""
    return [re.sub(r"^- ", "", x) for x in source.split("\n") if x.strip()]


def live(page):
    """(title, sub-bullet texts, revision-table first row text cell or None) of DEL-3 on the page."""
    lines, title, subs, i = page.split("\n"), None, [], 0
    for i, x in enumerate(lines):
        m = TITLE.match(x)
        if m:
            title = m.group(1)
            break
    else:
        return None, [], None
    for x in lines[i + 1:]:
        if not x.startswith("  - "):
            break
        subs.append(x[4:])
    cell, start = None, None
    for j, x in enumerate(lines):
        if x.strip() == "### DEL-3":
            start = j
            break
    if start is not None:
        rows = [x for x in lines[start + 1:start + 8] if re.match(r"^\| r\d+ \|", x)]
        cell = rows[0].strip().strip("|").split("|")[2].strip() if rows else None
    return title, subs, cell


def check(page, source, pf):
    found = []
    want = expected(source)
    title, subs, cell = live(page)
    if title is None:
        return ["no `- DEL-3:` requirement line"]
    got = []
    for x in subs:
        if not x.endswith(TAG):
            found.append("sub-bullet without the tag: " + x[:60])
        got.append(x[:-len(TAG)] if x.endswith(TAG) else x)
    if got != want:
        n = next((k for k in range(min(len(got), len(want))) if got[k] != want[k]), min(len(got), len(want)))
        found.append("line %d differs (live %d lines, source %d lines): live %r, source %r" % (
            n + 1, len(got), len(want), (got[n] if n < len(got) else None) and got[n][:70], (want[n] if n < len(want) else None) and want[n][:70]))
    expect_cell = pf.unit(title, ["  - " + x + TAG for x in want])
    if cell != expect_cell:
        found.append("the first revision row does not equal the live lines (it reads %r)" % ((cell or "none")[:70]))
    return found


def build(source, title="It stops only for decisions that are mine, and asks them clearly"):
    want = expected(source)
    return "\n".join(["- DEL-3: **Reviewed 2026-11-22** %s <!-- reviewed 00000000 -->" % title] + ["  - " + x + TAG for x in want]
                     + ["- DEL-17: next", "", "### DEL-3", "", "| rev | date | text | why | approved |", "|---|---|---|---|---|",
                        "| r7 | 2026-11-22 | %s | why | o1: \"x\" |" % pageformat(root()).unit(title, ["  - " + x + TAG for x in want]), ""])


def selftest(source, pf):
    good, bad = build(source), []
    if check(good, source, pf):
        return ["a faithful page fails: %s" % check(good, source, pf)]
    lines = good.split("\n")
    word = good.replace("never asked twice", "never asked once", 1) if "never asked twice" in good else good.replace(" the ", " a ", 1)
    drop = "\n".join(lines[:3] + lines[4:])
    add = "\n".join(lines[:3] + ["  - An extra line." + TAG] + lines[3:])
    cell = good.replace("| why |", "| why |", 1).replace("| r7 |", "| r7 |", 1)
    cell = re.sub(r"(\| r7 \| 2026-11-22 \| )([^|]*?)( \| why)", lambda m: m.group(1) + m.group(2).replace(" the ", " a ", 1) + m.group(3), good, count=1)
    for name, text in (("one word changed", word), ("one line dropped", drop), ("one line added", add), ("revision row differs", cell)):
        if text != good and check(text, source, pf):
            continue
        bad.append("control not failing: " + name)
    return bad


def main():
    args, top = sys.argv[1:], root()
    arg = lambda k, d: args[args.index(k) + 1] if k in args else d
    delivery, src = arg("--delivery", os.path.join(top, "docs", "wiki", "Delivery.md")), arg("--source", os.path.join(top, ".loop", "goals", "v120-del3-text.source.md"))
    source = read(src)
    if hashlib.sha256(source.encode("utf-8")).hexdigest() != SHA:
        print("FAIL: the source's sha256 is not " + SHA)
        return 1
    if "|" in source or "<" in source:
        print("FAIL: the source holds a `|` or `<` (the page would escape it)")
        return 1
    pf = pageformat(top)
    if "--selftest" in args:
        bad = selftest(source, pf)
        print("\n".join("FAIL: " + x for x in bad) or "SELFTEST OK: a faithful page passes; one word changed, one line dropped, one line added and a differing revision row each fail")
        return 1 if bad else 0
    page = read(delivery)
    if "--body" in args:
        title = live(page)[0]
        print("\n".join([title] + [x + TAG for x in expected(source)]))
        return 0
    found = check(page, source, pf)
    print("\n".join("FAIL: " + x for x in found) or "WORD FOR WORD OK: %d lines, the revision row equals them" % len(expected(source)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
