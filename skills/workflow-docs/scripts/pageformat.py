#!/usr/bin/env python3
"""The page format (DOC-4..DOC-23): the checks docs.py check runs on Home, the README and each feature page. Pure: text in, findings out.
A finding is ("FORMAT", "<Page>:<line>", "<Section>: DOC-n <what> (got <value>). Fix: <how>"); CHECKS (the template's `format` key) says which run."""
import os
import re

GENERATED = {"Tests"}  # pages render writes: never mapped, never a feature page
GUIDE = "<!-- workflow-docs guide -->"  # marks a guide page: mapped and kept fresh, not a feature page
CHECKS = ("home", "frontdoor", "usage", "bullets", "problem", "tests", "deployments", "runbook")  # deployments: deployments.py
BANNED = "script, function, regex, json, tsv, stdout"
MARKER = "<!-- workflow-docs -->"
HOME = ("Feature", "What it does", "How to use", "Milestone")
OTHER = "Other"  # the topic of a feature none lists


def topic_of(name, topics):
    """The topic that lists this page."""
    return next((topic for topic, pages in topics.items() if name in pages), OTHER)


def topic_order(topics):
    return list(topics) + [OTHER]
RULE = re.compile(r"^\|(\s*:?-+:?\s*\|)+$")
PATH = re.compile(r"(?<![\w/])/[\w.-]+/")
EXT = re.compile(r"\.(py|sh|json|tsv|md)\b")
ME = re.compile(r"\b(I|[Mm]y|[Mm]e)\b")


def is_guide(text):
    return GUIDE in (text or "").splitlines()


def bad(page, line, section, rule, what, got, fix):
    return ("FORMAT", "%s:%d" % (page, line), "%s: DOC-%d %s (got %s). Fix: %s" % (section, rule, what, got, fix))


def short(text):
    text = " ".join(str(text).split())
    return "'%s'" % (text if len(text) <= 60 else text[:57] + "...")


def words(text):
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text).replace("`", "").split()


def sentences(text):
    return len(re.findall(r"[.!?] (?=[A-Z])", " ".join(words(text)))) + 1


def slug(text):
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def owner_repo(text):
    found = re.search(r"github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?(?:/milestone/\d+|/?$)", text.strip(), re.M)
    return found.group(1) if found else ""


def parts(text):
    out, fenced = [("", 1, [])], False
    for number, line in enumerate(text.splitlines(), 1):
        fenced = fenced != line.startswith("```")
        if not fenced and line.startswith("## "):
            out.append((line[3:].strip(), number, []))
        else:
            out[-1][2].append((number, line))
    return out


def cells(line):
    return [item.strip() for item in re.split(r"(?<!\\)\|", line.strip()[1:-1])]


def table(header, rows):
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(x) + " |" for x in rows]


def tables(numbered):
    found, other, last = [], [], None
    for number, line in numbered:
        if line.startswith("|"):
            if last != number - 1:
                found.append((number, cells(line), []))
            elif not RULE.match(line.strip()) or found[-1][2]:
                found[-1][2].append((number, cells(line)))
            last = number
        elif line.strip():
            other.append((number, line))
    return found, other


def heading_of(page):
    return "How to use " + page.replace("-", " ")


def anchors(readme):
    return {slug(line[4:]) for name, _, lines in parts(readme) if name == "How to use"
            for _, line in lines if line.startswith("### How to use ")}


def unblocked(text):
    return re.sub(r"<!-- (settings|automation|template|diagram):begin -->\n.*?<!-- \1:end -->\n", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def home(text, features, existing, readme, repo, topics=None):
    out, seen, keys, last = [], [], anchors(readme), -1
    lines = list(enumerate(unblocked(text).splitlines(), 1))
    body = [(n, x) for n, x in lines if x.strip() and x.strip() != MARKER]
    found, other = tables([(n, x) for n, x in lines if not x.startswith(("# ", "## Features")) and x.strip() != MARKER])
    if not body or not body[0][1].startswith("# ") or "## Features" not in [x.strip() for _, x in body]:
        out.append(bad("Home", 1, "Features", 4, "Home is the marker, '# title' and '## Features'", short(body[0][1] if body else ""),
                       "write '# <repo>', then '## Features', then the features table"))
    for number, line in other:
        out.append(bad("Home", number, "Features", 4, "a line outside the features table", short(line), "move it to the README or a feature page"))
    with_topic = len(found) == 1 and tuple(found[0][1]) == ("Topic",) + HOME
    want_head = ("Topic",) + HOME if with_topic else HOME
    topics = topics if with_topic else None
    if len(found) != 1 or tuple(found[0][1]) != want_head:
        return out + [bad("Home", found[0][0] if found else 1, "Features", 4, "one table with the header | %s |" % " | ".join(want_head),
                          "%d tables%s" % (len(found), ", header " + short(" | ".join(found[0][1])) if found else ""),
                          "use exactly that header, in one table")]
    for number, row in found[0][2]:
        topic, row = (row[0], row[1:]) if with_topic and len(row) == 5 else (None, row)
        page = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", row[0]) if len(row) == 4 else None
        if not page or page.group(1) != page.group(2) or page.group(1) not in existing:
            out.append(bad("Home", number, "Features", 4, "the Feature cell links an existing page as [X](X)", short(row[0]),
                           "name a page from .loop/docs.tsv"))
            continue
        name = page.group(1)
        seen.append(name)
        if topics:
            order, held = topic_order(topics), topic_of(name, topics)
            if topic != held or order.index(held) < last:
                out.append(bad("Home", number, "Features", 4, "the Topic cell names the page's topic and rows are grouped by topic",
                               short(topic or ""), "write %s here and keep each topic's rows together, in the order of the topics setting" % held))
            last = max(last, order.index(held)) if held in order else last
        if name not in features:
            out.append(bad("Home", number, "Features", 4, "a row for a page that is not a feature page", name, "remove the row"))
        link = re.match(r"^\[[^\]]+\]\(https://github\.com/([\w.-]+/[\w.-]+)#([\w-]+)\)$", row[2])
        wiki = re.match(r"^\[[^\]]+\]\(https://github\.com/([\w.-]+/[\w.-]+)/wiki/How-to-use-%s\)$" % re.escape(name), row[2])
        want = slug(heading_of(name))
        if wiki and not (repo and wiki.group(1).lower() != repo.lower()):
            pass
        elif not link or (repo and link.group(1).lower() != repo.lower()) or link.group(2) != want or want not in keys:
            out.append(bad("Home", number, "Features", 4, "How to use links the page How-to-use-%s" % name,
                           short(row[2]), "link [%s](https://github.com/%s/wiki/How-to-use-%s); the README needs no '### %s' heading (DOC-18)" % (heading_of(name), repo or "OWNER/REPO", name, heading_of(name))))
    for name in features:
        count = seen.count(name)
        if count != 1:
            out.append(bad("Home", found[0][0], "Features", 4, "one row per feature page", "%d rows for %s" % (count, name),
                           "give %s exactly one row" % name))
    return out


LIST = re.compile(r"^\| (\d) \| ([^|]+) \| ([^|]+) \| [a-z,]+ \|$", re.M)
IDREF = re.compile(r"\b([A-Z]{2,5}-\d+)\b( \(planned)?")


def frontdoor(page, text, listing, ids, readme=True):
    want, out = LIST.findall(listing.partition("## The eight principles")[2]), []
    fail = lambda at, what, got, fix: out.append(bad(page, at, "Principles", 23, what, got, fix))
    head, secs = parts(unblocked(text))[0], parts(unblocked(text))[1:]
    extra = [x for x in head[2][1:] if x[1].strip()]
    if readme and (len(extra) != 1 or "/wiki/Home" not in extra[0][1]):
        fail(1, "the title and one link to the wiki Home", "%d lines" % len(extra), "keep one [wiki](.../wiki/Home) line")
    names = ["%s. %s" % (n, name.strip()) for n, name, _ in want]
    for (name, at, lines), (n, _, sentence) in zip(secs + [("", 1, [])] * len(want), want):
        if name != names[int(n) - 1]:
            fail(at, "section '%s'" % names[int(n) - 1], short(name), "keep the eight principle sections, in order, and no other")
            continue
        body = [x for x in lines if x[1].strip()]
        if len(body) != 3 or words(body[0][1]) != words(sentence) or "principle-0%s-" % n not in body[1][1] or not body[2][1].startswith("Enforced by:"):
            fail(at, "its sentence from the health list, a diagram line, an 'Enforced by:' line", "%d lines" % len(body), "copy the list")
            continue
        for found, planned in IDREF.findall(body[2][1]):
            if found not in ids and not planned:
                fail(body[2][0], "an ID that exists or is marked (planned: ...)", found, "mark it '%s (planned: <goal>)' or remove it" % found)
    if len(secs) > len(want):
        fail(secs[len(want)][1], "no section after the eight principles", short(secs[len(want)][0]), "move it to the wiki")
    return out


FIELD = re.compile(r"^- \*\*([A-Z][A-Za-z ]*):\*\*\s*(.*)$")
ROUTINE = re.compile(r"^[a-z][a-z0-9-]*$")


def runbook(page, name, lines, fields):
    out, subs, cur, titles = [], [], None, set()
    for number, line in lines:
        if not line.strip():
            continue
        if line.startswith("### "):
            cur = [number, line[4:].strip(), {}, None]
            subs.append(cur)
            if cur[1] in titles:
                out.append(bad(page, number, name, 16, "each routine once", short(cur[1]), "merge the two subsections"))
            titles.add(cur[1])
        elif cur is None:
            out.append(bad(page, number, name, 16, "a '### <routine>' heading before any field", short(line), "start each routine with '### <name>'"))
        elif FIELD.match(line):
            key, text = FIELD.match(line).groups()
            if key in cur[2]:
                out.append(bad(page, number, name, 16, "each field once under %s" % cur[1], "'%s' again" % key, "merge the two lines"))
            cur[2][key] = cur[2].get(key, "") + text
            cur[3] = key
        elif line[:1].isspace() and cur[3]:
            cur[2][cur[3]] += " " + line.strip()
        else:
            out.append(bad(page, number, name, 16, "only '- **Field:** text' lines, with indented continuation", short(line),
                           "write it as a field of the routine, or remove it"))
    if not subs:
        out.append(bad(page, lines[0][0] if lines else 1, name, 16, "at least one '### <routine>' subsection", "none", "add one, or remove the section"))
    for number, title, found, _ in subs:
        if not ROUTINE.match(title):
            out.append(bad(page, number, name, 16, "a routine name of lowercase letters, digits and hyphens", short(title), "rename the heading"))
        for field in fields:
            if len(found.get(field, "").strip()) < 5:
                out.append(bad(page, number, name, 16, "a '%s' field of 5 characters or more under %s" % (field, title),
                               short(found.get(field, "none")), "add '- **%s:** <what an agent must know>'" % field))
        for extra in sorted(set(found) - set(fields)):
            out.append(bad(page, number, name, 16, "only the fields %s" % ", ".join(fields), "'%s'" % extra, "remove or rename it"))
    return out


ROW_NAMED = re.compile(r"Deployments row:\s*`?([^`;,.)\n]+?)`?\s*(?=[;,.)]|$)")


def linked(page, name, runbook, deploy):
    rows = {c.strip().strip("`") for _, line in deploy for c in line.split("|")[1:2] if line.lstrip().startswith("|")}
    out, text = [], ""
    for number, line in runbook + [(0, "")]:  # the sentinel flushes the last Output
        if line.startswith("- **Output:**"):
            text, at = line, number
        elif text and line[:1].isspace():
            text += " " + line.strip()
        elif text:
            for named in map(str.strip, ROW_NAMED.findall(text)):
                if named not in rows:
                    out.append(bad(page, at, name, 16, "the Deployments row the Output names exists", short(named),
                                   "name a row of the Deployments tables, or drop the Deployments row clause"))
            text = ""
    return out


GROUPS = ["Functional", "Non-functional"]


def bullets(page, name, lines, line_re, strict, groups_want=GROUPS):
    out, held, groups = [], [], []
    say = lambda number, what, got, fix: out.append(bad(page, number, name, 7, what, short(got), fix))
    for number, line in lines:
        if not line.strip():
            continue
        if line.startswith("### "):
            groups.append([number, line[4:].strip(), 0, 0])
            held.append((number, None, []))  # ends the requirement above
        elif line.startswith("  - ") and held and held[-1][1]:
            held[-1][2].append((number, line[4:]))
        elif line.startswith("  - ") or line[:1].isspace():
            say(number, "a sub-bullet is '  - ' (two spaces) right under a requirement line", line,
                "indent it by exactly two spaces under its requirement")
        elif strict and (not groups or (line.strip() != "None" and not line_re.match(line))):
            say(number, "only requirement lines, their sub-bullets or 'None' under ### Functional and ### Non-functional",
                line, "move it into a requirement, or remove it")
        else:
            held.append((number, line_re.match(line), []))
            if groups:
                groups[-1][3 if line.strip() == "None" else 2] += 1
    if strict and [g[1] for g in groups] != groups_want:
        say(groups[0][0] if groups else 1, "Requirements is '### Functional' then '### Non-functional'",
            ", ".join(g[1] for g in groups) or "none", "group the requirements under exactly those two headings, in order")
    for number, title, reqs, nones in groups if strict else []:
        if (reqs and nones) or nones > 1 or not (reqs or nones):
            say(number, "a group holds requirements or the single line 'None'", "%d requirements, %d None" % (reqs, nones),
                "write 'None' alone when %s has no requirement" % title)
    for number, match, subs in held if strict else []:
        if not match:
            continue
        if not subs:
            say(number, "%s has at least one sub-bullet" % match.group(1), "none", "split its wording into '  - ' bullets under it")
        if match.group(2) == "Unreviewed" and len(words(match.group(4))) > 20:
            say(number, "an Unreviewed requirement line is at most 20 words", "%d words" % len(words(match.group(4))),
                "make it a title and move the detail into sub-bullets")
    return out


def problem(page, name, lines, most, banned):
    out, said = [], [(n, x) for n, x in lines if x.strip()]
    first = said[0][0] if said else 1
    for number, line in said:
        if not line.startswith("- "):
            out.append(bad(page, number, name, 8, "each line is a '- ' bullet", short(line), "write it as a bullet"))
        hit = ("`" in line and "`") or (PATH.search(line) or EXT.search(line) or [None])[0] or next(
            (w for w in banned if re.search(r"\b%ss?\b" % re.escape(w), line, re.I)), None)
        if hit:
            out.append(bad(page, number, name, 8, "the problem is said without code internals", short(hit),
                           "say what goes wrong for the person, not how the code works"))
    if not 1 <= len(said) <= most:
        out.append(bad(page, first, name, 8, "1 to %d bullets" % most, "%d lines" % len(said), "say the problem in 1 to %d bullets" % most))
    if said and not any(ME.search(line) for _, line in said):
        out.append(bad(page, first, name, 8, "at least one bullet in the first person (I, my, me)", "none",
                       "say it from the user's side: 'I can't ...'"))
    return out


def stale(page, name, start, lines, fresh):
    have = [(n, x) for n, x in lines if x.strip()] + [(start, "end")]
    want = [x for x in fresh if x.strip()]
    at = next((i for i, line in enumerate(want + [None]) if i >= len(have) - 1 or have[i][1] != line), None)
    if at is None or (at == len(want) and len(have) - 1 == len(want)):
        return None
    return ("TESTS", "%s:%d" % (page, have[at][0]), "%s: DOC-9 the table differs from a fresh render (got %s). "
            "Fix: /workflow-docs render" % (name, short(have[at][1])))


RET = re.compile(r"^- ([A-Z]{2,5}-\d+): (Retired|merged into ([A-Z]{2,5}-\d+)|moved to ([A-Z]{2,5}-\d+))$")
RHEAD = ["rev", "date", "text", "why", "approved"]


def enc(text):
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("<br>", "\\<br>")


def unit(text, below):
    return " <br> ".join(" ".join(enc(re.sub(r"^- ", "", p.strip())).split()) for p in [text] + list(below))


def revs(lines):
    tab, ret, bad, cur = {}, {}, [], None
    for line in lines:
        if line.startswith("### "):
            cur = line[4:].strip()
            re.match(r"[A-Z]{2,5}-\d+$", cur) and tab.setdefault(cur, [])
        elif cur == "Retired" and line.startswith("- "):
            hit = RET.match(line)
            ret.__setitem__(hit.group(1), hit.group(2)) if hit else bad.append(line[:40])
        elif cur in tab and line.startswith("|") and not RULE.match(line.strip()) and cells(line) != RHEAD:
            tab[cur].append(cells(line))
    return tab, ret, bad


def revcheck(page, live, lines, base):
    out = []
    bad = lambda code, why: out.append(("REVISION" if code[0] == "R" else "IDS", page, "[%s] %s" % (code, why)))
    tab, ret, errs = revs(lines or [])
    ids, src = base or (set(), None)
    btab, bret, _ = revs(src or [])
    [bad("REV-ROW", "bad Retired: " + e) for e in errs]
    [bad("IDS-REUSE", "%s is live and Retired" % k) for k in set(live) & set(ret) | set(bret) & set(live)]
    for k in sorted(live) if lines is not None else []:
        rows = tab.get(k) or []
        if not rows or any(len(c) != 5 or not all(c) or not re.match(r"o\d+: ", c[4]) for c in rows) or [c[0] for c in rows] != ["r%d" % n for n in range(len(rows), 0, -1)]:
            bad("REV-ROW", "%s rows are not r%d..r1 newest first (two heads?)" % (k, len(rows)))
        elif " ".join(rows[0][2].split()) != live[k]:
            bad("REV-ROW", "%s: %s differs from its line. Fix: criteria.py revise" % (k, rows[0][0]))
    if src is not None and lines is None:
        bad("REV-GONE", "Revisions section removed")
    for k in sorted(ids | set(bret)):
        if k not in live and k not in ret:
            bad("IDS-MISSING", "%s is gone. Fix: restore it or criteria.py retire" % k)
    for k, old in btab.items():
        if old and tab.get(k, [])[-len(old):] != old:
            bad("REV-ROW", "%s: %s changed since the base (append-only). Fix: add r%d" % (k, old[0][0], len(old) + 1))
    return out
