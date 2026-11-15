#!/usr/bin/env python3
"""The repo's copy of an external PRD (DOC-17), and docs.py sync. `.loop/prd/PAGE.md` is the last agreed version, in the repo's layout;
every check reads it, never the source. normalise() brings a source's layout to the repo's, block() is the page's generated PRD block,
link_page() the docs check of a page with a source, sync() compares source and copy with what both last agreed: one side changed is a
DELTA, both a CONFLICT, nothing is overwritten, --accept PAGE:ID=repo|source writes one side over the other. Imports are lazy."""
import os
import re

SYNC_MARK = "<!-- prd-sync: owned -->"
BEGIN, END = "<!-- prd:begin -->", "<!-- prd:end -->"
HEADS = ("Problem", "Requirements", "Non-goals", "Success metrics")
EMPTY = {"Problem": "Not written in the source.", "Non-goals": "None", "Success metrics": "Not written in the source."}
NAMES = {"problem": "Problem", "summary": "Problem", "overview": "Problem", "background": "Problem", "requirements": "Requirements",
         "functional": "Requirements", "non-functional": "Requirements", "nonfunctional": "Requirements", "new requirements": "Requirements",
         "non-goals": "Non-goals", "non goals": "Non-goals", "nongoals": "Non-goals", "out of scope": "Non-goals",
         "success metrics": "Success metrics", "success": "Success metrics", "metrics": "Success metrics"}
KEYS = sorted(NAMES, key=len, reverse=True)
ITEM = re.compile(r"^(\s*)(?:[-*]\s+|\d+[.)]\s+|\|\s*)?\**([A-Z]{2,5}-\d+)\**\s*[:|.\u2013\u2014-]*\s*(.*)$")
MARK = r"(?:\*\*|\()(Un)?[Rr]eviewed(?:\s+(\d{4}-\d\d-\d\d))?(?:\*\*|\))"
KIND = re.compile(r"^(Functional|Non-?functional)\s*:?\s*", re.I)


def path_of(root, page):
    return os.path.join(root, ".loop", "prd", page + ".md")


def tidy(line):
    """A line with the html a Notion export writes (b, i, u, code, br) as markdown."""
    return re.sub(r"</?[iu]>|<br\s*/?>", "", re.sub(r"</?b>", "**", re.sub(r"</?code>", "`", line)))


def item_line(ident, rest, first=""):
    """(`- ID: **Reviewed DATE** Kind: title`, whether the first sub-bullet was the title) from what follows an id: the kind stays in
    the title, the mark comes before or after it, and an id line with no title takes its first sub-bullet, as Notion writes it."""
    rest = " ".join(re.sub(r"<!--.*?-->", " ", rest).replace("|", " ").split())
    kind, mark = KIND.match(rest), "Unreviewed"
    rest = rest[kind.end():] if kind else rest
    for pattern in (r"^(?:[A-Z][\w -]{0,24}:\s*)?%s\s*[:\u2013\u2014-]?\s*" % MARK, r"\s*%s\s*$" % MARK):
        found = re.search(pattern, rest)
        if found:
            mark = "Reviewed " + found.group(2) if not found.group(1) and found.group(2) else "Unreviewed"
            rest = (rest[:found.start()] + " " + rest[found.end():]).strip()
            break
    title = rest or first
    if kind and not title.lower().startswith(kind.group(1).lower()):
        title = "%s: %s" % (kind.group(1), title)
    return ("- %s: **%s** %s" % (ident, mark, title) if title else None), not rest and bool(first)


def normalise(text):
    """{section: [lines]} of a source in the repo's layout: `NL-1 Functional: (Reviewed 2026-11-10) text`, or Notion's `**NL-1**
    Functional: (Reviewed ...)` over a `Functional: text` sub-bullet, becomes `- NL-1: **Reviewed 2026-11-10** Functional: text`; a
    `New requirements` heading adds to Requirements; other headings (Runbook, Deployments) and anything before the first are skipped."""
    out, mine, seen, fenced = {name: [] for name in HEADS}, None, set(), False
    lines = [tidy(x) for x in text.replace("\r\n", "\n").split("\n")]
    for number, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        heading = re.match(r"^(#{1,4})\s+(.*?)\s*#*\s*$", line) if not fenced else None
        if heading:
            low = re.sub(r"[^\w -]", "", heading.group(2)).strip().lower()
            mine = next((NAMES[k] for k in KEYS if low == k or low.startswith(k + " ")), None if heading.group(1) == "#" else "skip")
            continue
        found = ITEM.match(line) if mine in (None, "Requirements") else None
        if found and found.group(2) not in seen:
            subs = []
            for sub in lines[number + 1:]:
                if sub.strip() and len(sub) - len(sub.lstrip()) <= len(found.group(1)):
                    break
                if sub.strip() and not ITEM.match(sub):
                    subs.append(sub.strip().lstrip("-* ").strip())
            made, used = item_line(found.group(2), found.group(3), subs[0] if subs else "")
            if made:
                seen.add(found.group(2))
                out["Requirements"] += [made] + ["  - " + x for x in subs[used:]]
            continue
        if mine in ("Problem", "Non-goals", "Success metrics") and line.strip():
            out[mine].append(line.rstrip())
    return out


def sections(parts, sep="\n\n"):
    """The four sections as `## Name` and their lines, an empty one with a placeholder."""
    return sep.join("## %s\n%s" % (name, "\n".join(parts.get(name) or [EMPTY.get(name, "None")])) for name in HEADS)


def compose(parts, source):
    """The copy's text: the sync mark, the source, then the four sections."""
    return "%s\n<!-- source: %s -->\n%s\n" % (SYNC_MARK, source, sections(parts))


def split(text):
    """{section: [lines]} of a copy, by its `## ` headings."""
    out, now = {}, None
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.startswith("## "):
            now = out.setdefault(line[3:].strip(), [])
        elif now is not None:
            now.append(line)
    return {name: "\n".join(lines).strip("\n").split("\n") for name, lines in out.items()}


def copy_of(root, page):
    """The copy's text when .loop/prd/PAGE.md exists and names at least one requirement, else None."""
    try:
        with open(path_of(root, page), encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return None
    return text if re.search(r"(?m)^- [A-Z]{2,5}-\d+: ", text) else None


def block(copy):
    """The generated part of the wiki page: the copy's four sections between the prd markers."""
    return "%s\n%s\n%s\n" % (BEGIN, sections(split(copy)), END)


def with_block(text, copy):
    """text with its prd block set to the copy's: replaced where it stands, else put before the first section."""
    fresh, held = block(copy), re.search(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", text, re.S)
    if held:
        return text[:held.start()] + fresh + text[held.end():]
    at = text.find("\n## ")
    return text.rstrip("\n") + "\n\n" + fresh if at < 0 else text[:at].rstrip("\n") + "\n\n" + fresh + text[at:]


def read(root, page, source):
    """(PRD text, None) of a page that has a source: its copy when there is one, else the source read now (never a guess)."""
    import prd
    copy = copy_of(root, page)
    return (copy, None) if copy else prd.read_link(source)


def set_item(copy, ident, lines):
    """The copy with requirement `ident` set to `lines` (its line and sub-bullets), appended when new, removed when None."""
    parts, kept, placed = split(copy), [], False
    ahead = parts.get("Requirements", [])
    skip = False
    for line in ahead:
        mine = re.match(r"^- %s: " % re.escape(ident), line)
        if mine or (skip and line[:1].isspace() and line.strip()):
            if mine and lines is not None and not placed:
                kept += lines
                placed = True
            skip = True
            continue
        skip = False
        kept.append(line)
    if lines is not None and not placed:
        kept = [x for x in kept if x.strip() and x != "None"] + lines
    parts["Requirements"] = kept
    head = copy.split("\n## ")[0].rstrip("\n")
    return head + "\n" + sections(parts) + "\n"


def link_page(root, page, text, link, parts, numbered, rule, seen, linked, on):
    """Trouble for a page with a source, as (kind, page, detail): ids come from its copy, else the source read now (UNREAD when neither
    reads); the four PRD sections may stand on the page only as the block generated from the copy."""
    import criteria
    import deployments as D
    import pageformat as pf
    found, mine = [], [x for x in (rule["runbook"], rule["deploy"], "Tests") if x]
    shown = D.link_of(text)
    if shown != link:
        found.append(("FORMAT", page, "DOC-1 the 'PRD: <source>' line must show where the PRD lives (got %s, docs.tsv says %s). "
                      "Fix: write 'PRD: %s' under the title" % (shown or "no line", link, link)))
    have, copy = [name for name, _ in parts], copy_of(root, page)
    if copy and have[:4] == list(rule["sections"][:4]):
        have = have[4:]
        if block(copy) not in text.replace("\r\n", "\n"):
            found.append(("STALE", page, "its PRD block differs from .loop/prd/%s.md. Fix: docs.py render" % page))
    elif copy:
        found.append(("STALE", page, "has no PRD block from .loop/prd/%s.md. Fix: docs.py render" % page))
    if have != [x for x in mine if x in have] or "Tests" not in have:
        found.append(("SECTIONS", page, "have %s, want only %s, in that order, after the 'PRD: <link>' line%s. Fix: move the PRD "
                      "text to the linked document" % (", ".join(have) or "none", ", ".join(mine), " and its PRD block" * bool(copy))))
        return found
    body, why = read(root, page, link)
    if body is None:
        return [("UNREAD", page, "the linked PRD %s cannot be read (%s) and %s has no copy. Fix: run docs.py sync where its reader is set; "
                 "its ids and the Tests table stay unchecked, so this is not a pass" % (link, why, ".loop/prd/%s.md" % page))]
    ids = []
    for name, lines in criteria.sections(body):
        if name == rule["sections"][1]:
            for line, match, _ in criteria.blocks(lines):
                if match and match.group(1) in seen:
                    found.append(("DUPLICATE", page, "%s is also in %s" % (match.group(1), seen[match.group(1)])))
                elif match:
                    seen[match.group(1)] = page
                    ids.append((match.group(1), match.group(4)))
    if not ids:
        found.append(("CRITERION", page, "the linked PRD has no '- ID: **Unreviewed** text' line under %s" % rule["sections"][1]))
    if "deployments" in on and rule["deploy"] in numbered:
        found += D.deployments(page, rule["deploy"], numbered[rule["deploy"]][1], rule["page_cols"], rule["delivery_cols"], rule["access"])
    if "runbook" in on and rule["runbook"] in numbered:
        found += pf.runbook(page, rule["runbook"], numbered[rule["runbook"]][1], rule["fields"])
    if "tests" in on:
        found += [x for x in [pf.stale(page, "Tests", numbered["Tests"][0], numbered["Tests"][1], criteria.table(root, ids, linked))] if x]
    return found


def texts(lines):
    """{id: plain text} of requirement lines (marks and sub-bullets left out), the way both sides are compared."""
    from entry import requirements
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


def kind_of(side):
    return "CONFLICT" if side == "both sides" else "DELTA"


def what(side):
    return "both sides changed" if side == "both sides" else side + " changed"


def sync(root, dry=False, accept=(), opened=False):
    import counting
    import prd
    from criteria import sha
    from entry import req_key
    from prd import out as post
    from render import mirror_of
    held = counting.ledger(root)
    if opened:
        print("".join("%s %s %s (review: %s)\n" % (kind_of(v[0]), k.replace(":", ": "), what(v[0]), v[1]) for k, v in held.items()), end="")
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
        parts = normalise(body)
        want_blocks = blocks_of(parts["Requirements"])
        want, path = texts(parts["Requirements"]), path_of(root, page)
        _, mine, agreed = mirror_of(path)
        if not want or not mine:
            print("SKIPPED %s: %s" % (page, "no ids in the source" if not want else "its copy is not sync's own"))
            continue
        if not os.path.exists(path):
            if not dry:
                write(path, compose(parts, source), {i: sha(t) for i, t in want.items()})
                print("SYNCED %s: %d requirement(s) from %s; docs.py render shows them on the page" % (page, len(want), source))
            continue
        with open(path, encoding="utf-8") as handle:
            copy = handle.read().replace("\r\n", "\n")
        if "\n## Requirements" not in copy:
            print("SKIPPED %s: its copy is from before the repo's layout; delete .loop/prd/%s.md and .base, then sync again" % (page, page))
            continue
        have = texts(split(copy).get("Requirements", []))
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
                copy = set_item(copy, ident, want_blocks.get(ident))
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
            if parts[name] and parts[name] != split(copy).get(name):
                print("NOTE %s: its %s differs in the source; the copy keeps the agreed text (edit .loop/prd/%s.md to change it)" % (page, name, page))
        found, marks = [], {}
        mine_blocks = blocks_of(split(copy).get("Requirements", []))
        for ident in sorted(set(have) | set(want), key=req_key):
            r, s, b = have.get(ident), want.get(ident), agreed.get(ident) or None
            if r != s:
                found.append((ident, "both sides" if (sha(r) != b) == (sha(s) != b) else "the repo" if sha(r) != b else "the source", r, s))
            elif r is not None and ident in want_blocks and mark_of(mine_blocks[ident][0]) != mark_of(want_blocks[ident][0]) and not dry:
                marks[ident] = mark_of(want_blocks[ident][0])  # same text: the review mark follows the source
        for ident, mark in marks.items():
            first = re.sub(r"^(- [A-Z]{2,5}-\d+: )(?:\*\*.*?\*\* )?", lambda hit: "%s**%s** " % (hit.group(1), mark), mine_blocks[ident][0])
            copy = set_item(copy, ident, [first] + mine_blocks[ident][1:])
        if marks:
            write(path, copy, {i: h for i, h in agreed.items() if h})
            print("MARKED %s: %s follow the source's review marks" % (page, ", ".join(marks)))
        same, new = same + (not found), new + len(found)
        for ident, side, r, s in found:
            print("%s %s: %s %s (repo: %s | source: %s)" % (kind_of(side), page, ident, what(side), (r or "-")[:160], (s or "-")[:160]))
        if dry:
            continue
        for key in [k for k in held if k.startswith(page + ":") and k.split(":")[1] not in [f[0] for f in found]]:
            post("LOOP_GH", "issue", "close", held.pop(key)[1], "--comment", "Resolved.")
        for ident, side, r, s in found:
            key, text = "%s:%s" % (page, ident), "%s in %s %s: %s.\nRepo copy: %s\nSource: %s\nAccept one: docs.py sync --accept %s:%s=repo|source" % (
                kind_of(side).title(), page, ident, what(side), r or "-", s or "-", page, ident)
            row = held.get(key) or [side, "", "0", ""]
            if row[1] and row[3] != sha(text):
                post("LOOP_GH", "issue", "comment", row[1], "--body", text)
                row[2] = "0"
            elif not row[1]:
                for stone in (["--milestone", page], []):
                    ok, made = post("LOOP_GH", "issue", "create", "--title", "%s %s %s: %s" % (kind_of(side), page, ident, what(side)), "--body", text, *stone)
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
