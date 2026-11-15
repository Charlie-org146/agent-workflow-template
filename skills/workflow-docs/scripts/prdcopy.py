#!/usr/bin/env python3
"""The repo's copy of an external PRD (DOC-17): `.loop/prd/PAGE.md` holds the last agreed version in the repo's own layout, and every
check reads it, never the source. normalise() brings a source's layout to the repo's; block() is the part of the wiki page generated
from the copy (Problem, Requirements, Non-goals, Success metrics between prd:begin and prd:end); read() gives a page's PRD text, the
copy when there is one; link_page() is the docs check of a page that has a source (moved here from deployments.py). Pure text in and
out, plus the one file read in copy_of. Imports are lazy: criteria.py and deployments.py import this module."""
import os
import re

SYNC_MARK = "<!-- prd-sync: owned -->"
BEGIN, END = "<!-- prd:begin -->", "<!-- prd:end -->"
HEADS = ("Problem", "Requirements", "Non-goals", "Success metrics")
EMPTY = {"Problem": "Not written in the source.", "Non-goals": "None", "Success metrics": "Not written in the source."}
NAMES = {"problem": "Problem", "summary": "Problem", "overview": "Problem", "background": "Problem",
         "requirements": "Requirements", "functional": "Requirements", "non-functional": "Requirements", "nonfunctional": "Requirements",
         "new requirements": "Requirements", "non-goals": "Non-goals", "non goals": "Non-goals", "nongoals": "Non-goals",
         "out of scope": "Non-goals", "success metrics": "Success metrics", "success": "Success metrics", "metrics": "Success metrics"}
ITEM = re.compile(r"^(\s*)(?:[-*]\s+|\d+[.)]\s+|\|\s*)?\**([A-Z]{2,5}-\d+)\**\s*[:|.–—-]*\s*(.*)$")
MARK = re.compile(r"^(?:[A-Z][\w -]{0,24}:\s*)?(?:\*\*|\()(Un)?[Rr]eviewed(?:\s+(\d{4}-\d\d-\d\d))?(?:\*\*|\))\s*[:–—-]?\s*(.*)$")
FLAT = re.compile(r"^(?:Functional|Non-?functional)\s*:\s*", re.I)


def path_of(root, page):
    return os.path.join(root, ".loop", "prd", page + ".md")


def item_line(ident, rest):
    """`- ID: **Reviewed DATE** title` (or Unreviewed) from what follows an id in a source, or None when it holds no title."""
    rest = re.sub(r"<!--.*?-->", " ", rest.strip().strip("|").strip())
    found = MARK.match(FLAT.sub("", rest))
    mark, title = ("Reviewed " + found.group(2) if found and not found.group(1) and found.group(2) else "Unreviewed",
                   found.group(3)) if found else ("Unreviewed", FLAT.sub("", rest))
    title = " ".join(title.replace("|", " ").split())
    return "- %s: **%s** %s" % (ident, mark, title) if title else None


def normalise(text):
    """{section: [lines]} of a source in the repo's layout; Requirements lines are `- ID: **mark** title` with their sub-bullets.
    `NL-1 Functional: (Reviewed 2026-11-10) text` is a requirement, a `New requirements` heading adds to Requirements, a
    heading the repo has no section for is skipped, and an id line outside any heading is a requirement."""
    out, mine, seen, fenced = {name: [] for name in HEADS}, None, set(), False
    lines = text.replace("\r\n", "\n").split("\n")
    for number, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        heading = re.match(r"^(#{1,4})\s+(.*?)\s*#*\s*$", line) if not fenced else None
        if heading:
            mine = NAMES.get(re.sub(r"[^\w -]", "", heading.group(2)).strip().lower(), None if heading.group(1) == "#" else "skip")
            continue
        found = ITEM.match(line) if mine in (None, "Requirements") else None
        if found and found.group(2) not in seen:
            made = item_line(found.group(2), found.group(3))
            if made:
                seen.add(found.group(2))
                out["Requirements"].append(made)
                for sub in lines[number + 1:]:
                    if sub.strip() and len(sub) - len(sub.lstrip()) <= len(found.group(1)):
                        break
                    if sub.strip() and not ITEM.match(sub):
                        out["Requirements"].append("  - " + sub.strip().lstrip("-* ").strip())
            continue
        if mine in ("Problem", "Non-goals", "Success metrics") and line.strip():
            out[mine].append(line.rstrip())
    return out


def compose(parts, source):
    """The copy's text: the sync mark, the source, then the four sections."""
    body = "".join("## %s\n%s\n\n" % (name, "\n".join(parts.get(name) or [EMPTY.get(name, "None")])) for name in HEADS)
    return "%s\n<!-- source: %s -->\n%s" % (SYNC_MARK, source, body.rstrip("\n") + "\n")


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
    parts = split(copy)
    return BEGIN + "\n" + "\n\n".join("## %s\n%s" % (name, "\n".join(parts.get(name) or [EMPTY.get(name, "None")])) for name in HEADS) + "\n" + END + "\n"


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
    return head + "\n" + "".join("## %s\n%s\n\n" % (name, "\n".join(parts.get(name) or [EMPTY.get(name, "None")])) for name in HEADS).rstrip("\n") + "\n"


def link_page(root, page, text, link, parts, numbered, rule, seen, linked, on):
    """Trouble for a page that has a source, as (kind, page, detail). Ids come from the page's copy, else from the source read now
    (UNREAD, never a pass, when neither can be read); the four PRD sections may stand on the page only as the block generated
    from the copy."""
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
