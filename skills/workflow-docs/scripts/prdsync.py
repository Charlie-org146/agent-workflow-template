#!/usr/bin/env python3
"""docs.py sync (DOC-17), moved here from audit.py: each external PRD against its copy .loop/prd/PAGE.md and the last agreement.
The source is read only where a reader can reach it (prd.read_link: LOOP_PRD_READER, a file or an http page; otherwise `not
connected`, nothing changes). Its layout is brought to the repo's first (prdcopy.normalise). A requirement added or changed on one
side is a DELTA (an issue and a comment, never an overwrite); one changed on both sides is a CONFLICT, the same delta naming both
texts. --accept PAGE:ID=repo|source writes that side's block over the other, that id only."""
import os
import re

import counting
import prd
import prdcopy
from criteria import sha
from entry import req_key, requirements
from prd import out as post
from render import mirror_of


def texts(lines):
    """{id: plain text} of requirement lines (marks and sub-bullets left out), the way both sides are compared."""
    return requirements("\n".join(lines))


def blocks_of(lines):
    """{id: [line and its sub-bullets]} of Requirements lines."""
    out, last = {}, None
    for line in lines:
        found = re.match(r"^- ([A-Z]{2,5}-\d+): ", line)
        if found:
            last = out.setdefault(found.group(1), [line])
        elif last is not None and line[:1].isspace() and line.strip():
            last.append(line.rstrip())
        else:
            last = None
    return out


def mark_of(line):
    """The review mark of a requirement line (`Reviewed 2026-11-10` or `Unreviewed`), or empty."""
    found = re.match(r"^- [A-Z]{2,5}-\d+: \*\*(.*?)\*\* ", line)
    return found.group(1) if found else ""


def write(path, text, agreed):
    """The copy (LF) and its baseline: `ID<TAB>sha8` of each agreed text."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for name, body in ((path, text), (path[:-3] + ".base", "".join("%s\t%s\n" % item for item in agreed.items() if item[1]))):
        with open(name, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)


def sync(root, dry=False, accept=(), opened=False):
    held = counting.ledger(root)
    if opened:
        print("".join("%s %s %s (review: %s)\n" % ("CONFLICT" if v[0] == "both sides" else "DELTA", k.replace(":", ": "),
                                                    "both sides changed" if v[0] == "both sides" else v[0] + " changed", v[1]) for k, v in held.items()), end="")
        return 0
    listed = [(p, s) for p, s in sorted(counting.sources(root).items()) if s.startswith(("url:", "mcp:")) and re.fullmatch(r"\w[\w-]*", p)]
    if not listed:
        print("NO EXTERNAL PRDS: no url: or mcp: source in .loop/docs.tsv")
    same = new = away = 0
    for page, source in listed:
        body, why = prd.read_link(source)
        if body is None:
            print("not connected: %s (%s): %s" % (page, source, why))
            away += 1
            continue
        parts = prdcopy.normalise(body)
        want_blocks = blocks_of(parts["Requirements"])
        want, path = texts(parts["Requirements"]), prdcopy.path_of(root, page)
        _, mine, agreed = mirror_of(path)
        if not want or not mine:
            print("SKIPPED %s: %s" % (page, "no ids in the source" if not want else "its copy is not sync's own"))
            continue
        if not os.path.exists(path):
            if not dry:
                write(path, prdcopy.compose(parts, source), {i: sha(t) for i, t in want.items()})
                print("SYNCED %s: %d requirement(s) from %s" % (page, len(want), source))
            continue
        with open(path, encoding="utf-8") as handle:
            copy = handle.read().replace("\r\n", "\n")
        if "\n## Requirements" not in copy:  # a copy written before the repo's layout: its lines become requirements
            copy = prdcopy.compose({"Requirements": ["- %s: **Unreviewed** %s" % item for item in texts(copy.split("\n")).items()]}, source)
            print("UPGRADED %s: its copy now holds the repo's four sections" % page)
        have = texts(prdcopy.split(copy).get("Requirements", []))
        for item in (a for a in accept if not dry and a.split(":")[0] == page):
            ident, _, side = item.partition(":")[2].partition("=")
            r, s = have.get(ident), want.get(ident)
            if r == s or side not in ("repo", "source"):
                print("NO DELTA %s: %s" % (page, ident))
                continue
            keep = r if side == "repo" else s
            ok, why = post("LOOP_PRD_WRITER", source, "replace" if r else "remove", ident, input=r or "") if side == "repo" else (True, "")
            if not ok:
                print("not connected: %s (%s): %s" % (page, source, why))
                continue
            if side == "source":
                copy = prdcopy.set_item(copy, ident, want_blocks.get(ident))
            for side_of in (want, have):
                if keep:
                    side_of[ident] = keep
                else:
                    side_of.pop(ident, None)
            agreed[ident] = sha(keep) or ""
            write(path, copy, {i: h for i, h in agreed.items() if h})
            row = held.pop("%s:%s" % (page, ident), None)
            if row:
                post("LOOP_GH", "issue", "close", row[1], "--comment", "Accepted: %s." % side)
            print("ACCEPTED %s: %s, the %s's text" % (page, ident, side))
        for name in ("Problem", "Non-goals", "Success metrics"):
            if parts[name] and parts[name] != prdcopy.split(copy).get(name):
                print("NOTE %s: its %s differs in the source; the copy keeps the agreed text (edit .loop/prd/%s.md to change it)" % (page, name, page))
        found, marks = [], {}
        mine_blocks = blocks_of(prdcopy.split(copy).get("Requirements", []))
        for ident in sorted(set(have) | set(want), key=req_key):
            r, s, b = have.get(ident), want.get(ident), agreed.get(ident) or None
            if r != s:
                found.append((ident, "both sides" if (sha(r) != b) == (sha(s) != b) else "the repo" if sha(r) != b else "the source", r, s))
            elif r is not None and ident in want_blocks and mark_of(mine_blocks[ident][0]) != mark_of(want_blocks[ident][0]) and not dry:
                marks[ident] = mark_of(want_blocks[ident][0])  # same text: the review mark follows the source
        for ident, mark in marks.items():
            first = re.sub(r"^(- [A-Z]{2,5}-\d+: )(?:\*\*.*?\*\* )?", lambda hit: "%s**%s** " % (hit.group(1), mark), mine_blocks[ident][0])
            copy = prdcopy.set_item(copy, ident, [first] + mine_blocks[ident][1:])
        if marks:
            write(path, copy, {i: h for i, h in agreed.items() if h})
            print("MARKED %s: %s follow the source's review marks" % (page, ", ".join(marks)))
        same, new = same + (not found), new + len(found)
        for ident, side, r, s in found:
            print("%s %s: %s %s (repo: %s | source: %s)" % ("CONFLICT" if side == "both sides" else "DELTA", page, ident,
                  "both sides changed" if side == "both sides" else side + " changed", (r or "-")[:160], (s or "-")[:160]))
        if dry:
            continue
        for key in [k for k in held if k.startswith(page + ":") and k.split(":")[1] not in [f[0] for f in found]]:
            post("LOOP_GH", "issue", "close", held.pop(key)[1], "--comment", "Resolved.")
        for ident, side, r, s in found:
            key, text = "%s:%s" % (page, ident), "%s in %s %s: %s.\nRepo copy: %s\nSource: %s\nAccept one: docs.py sync --accept %s:%s=repo|source" % (
                "Conflict" if side == "both sides" else "Delta", page, ident, "both sides changed" if side == "both sides" else side + " changed",
                r or "-", s or "-", page, ident)
            row = held.get(key) or [side, "", "0", ""]
            if row[1] and row[3] != sha(text):
                post("LOOP_GH", "issue", "comment", row[1], "--body", text)
                row[2] = "0"
            elif not row[1]:
                for stone in (["--milestone", page], []):
                    ok, made = post("LOOP_GH", "issue", "create", "--title", "%s %s %s: %s" % (
                        "CONFLICT" if side == "both sides" else "DELTA", page, ident, "both sides changed" if side == "both sides" else side + " changed"),
                        "--body", text, *stone)
                    if ok:
                        break
                if not ok:
                    print("not connected: %s %s (gh): %s" % (page, ident, made[:100]))
                    away += 1
                    continue
                row[1] = made.split("\n")[-1]
            if row[2] != "1":
                ok, why = post("LOOP_PRD_WRITER", source, "comment", input=text)
                row[2] = "1" if ok else "0"
                print("POSTED %s %s: %s%s" % (page, ident, row[1], "" if ok else " (not connected to %s: %s)" % (source, why[:80])))
            held[key] = [side, row[1], row[2], sha(text)]
    if not dry:
        counting.ledger(root, held)
    print("SYNC: %d in step, %d with a delta, %d not connected" % (same, new, away))
    return 1 if dry and new else 0
