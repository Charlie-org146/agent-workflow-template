"""DOC-25: each page kind has its fixed ## headings in order; README and Home match.

KINDS maps a page kind to one regex per heading, each matching a whole heading. A "?" prefix makes a heading optional,
a "+" prefix one or more. A page kind with a heading missing, extra, renamed or out of order fails the docs check;
README and Home share the "front" row.
"""
import os
import re

KINDS = {
    'front': ('What this is', 'System design', '+\\d+\\. .+', 'Requirements by feature'),
    'front-adopted': ('What this is', 'System design', "The template's principles", '+\\d+\\. .+', 'Requirements by feature'),
    'feature': ('Problem', '?Runbook', 'Requirements', 'Non-goals', 'Success metrics', '?Deployments', 'Revisions', 'Tests'),
    'howto': ("What it's for", 'How to reach or run it', 'URLs and deployments', '?Automations and schedules', '?Runbooks', 'Links'),
    'principles': ('+\\d+\\. .+',),
    'tests': ('+(?!Other$).+', 'Other'),
    'roadmap': ('+.+',),
}
LINK = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/(?:wiki/|blob/main/docs/wiki/)|\(docs/wiki/")


def heads(text):
    out, fenced = [], False
    for n, line in enumerate(text.splitlines(), 1):
        fenced = fenced != line.startswith("```")
        if not fenced and line.startswith("## "):
            out.append((n, line[3:].strip()))
    return out


def first_gap(toks, found):
    i = 0
    for t in toks:
        pat, hit = t[1:] if t[0] in "?+" else t, lambda p: i < len(found) and re.fullmatch(p, found[i][1])
        if not hit(pat):
            if t[0] == "?":
                continue
            return (found[i][0], pat, found[i][1]) if i < len(found) else (0, pat, "nothing")
        i += 1
        while t[0] == "+" and hit(pat):
            i += 1
    return (found[i][0], "no more sections", found[i][1]) if i < len(found) else None


def check(page, kind, text):
    gap = first_gap(KINDS[kind], heads(text))
    return [("FORMAT", "%s:%d" % (page, gap[0]), "Sections: DOC-25 the %s sections in order, next '%s' (got %s). Fix: add, rename, remove or move the section" % (kind, gap[1], gap[2]))] if gap else []


def body(text, name):
    out, inside = [], False
    for line in text.splitlines():
        inside = line[3:].strip() == name if line.startswith("## ") else inside
        if inside and line.strip() and not line.startswith(("## ", "![")):
            out.append(LINK.sub(lambda m: "(" * m[0].startswith("("), line.strip()))
    return out


def same(readme, home):
    a, b = [x for _, x in heads(readme)], [x for _, x in heads(home)]
    bad = [("FORMAT", "Home:1", "Sections: DOC-25 README and Home have the same sections in order (README %s, Home %s). Fix: make them match" % (a, b))] * (a != b)
    return bad + [("FORMAT", "Home:%d" % n, "Sections: DOC-25 '%s' is the same on README and Home. Fix: copy it from the README" % x)
                  for n, x in heads(home) if re.match(r"\d+\. ", x) and x in a and body(readme, x) != body(home, x)]


def targets(root, folder, read, block_re, both):
    """DOC-15: each generated block lives on its How-to-use page, under the page's own section, once it carries the markers."""
    out = []
    for name, block in both:
        rel = os.path.join(folder, "How-to-use-%s.md" % ("Setup" if name == "settings" else "Automation"))
        if block_re(name).search(read(os.path.join(root, rel)) or ""):
            out.append((rel, [(name, block.replace("\n## ", "\n### ", 1))]))
    return out


OLD = "Requirement Summary Follows Feature Version Flow".split()
NEW = "Requirement Summary Follows Feature Adoption Confidence".split()
SPLIT = re.compile(r"(?<!\\)\|")


def adoption(follows):
    """The share of a row's Follows tags that say adopted (adapted and own count 0)."""
    tags = re.findall(r"\b(adopted|adapted|own)\b", follows)
    return round(100 * tags.count("adopted") / len(tags)) if tags else 0


def tables(text):
    """DOC-25: each principle table in the new columns, Adoption computed from Follows, the figure link in the Requirement cell, one score line under it."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        head = [c.strip() for c in SPLIT.split(lines[i].strip()[1:-1])] if lines[i].startswith("| Requirement | Summary") else []
        if head not in (OLD, NEW):
            out.append(lines[i]); i += 1; continue
        out += ["| " + " | ".join(NEW) + " |", lines[i + 1]]; scores = []; i += 2
        while i < len(lines) and lines[i].startswith("|"):
            c = [x.strip() for x in SPLIT.split(lines[i].strip()[1:-1])]
            if head == OLD:
                c = [c[0] + " (" + c[5] + ")"] + c[1:4] + ["", ""]
            c[4] = "%d%%" % adoption(c[2]); scores.append(adoption(c[2]))
            out.append("| " + " | ".join(c) + " |"); i += 1
        while i < len(lines) and (lines[i] == "" or lines[i].startswith("Adoption: ")):
            i += 1
        out += ["", "Adoption: %d%% (the average of this principle's rows)." % round(sum(scores) / len(scores)), ""]
    return "\n".join(out)


def what(page):
    """The What this is section, written from DEL-19's text on the Delivery page."""
    found = re.search(r"^- DEL-19: .*\n((?:  - .*\n?)*)", page or "", re.M)
    return "## What this is\n\n" + " ".join(re.sub(r"\s*\[[A-Z]{3}-\d+\]$", "", b[4:]) for b in (found[1].splitlines() if found else [])) + "\n"


def fresh(text, folder, read):
    """README, Home or Principles with its generated parts current (What this is: only its first paragraph; later ones are the owner's); text with no System design section is left alone."""
    text = tables(text)
    if "\n## System design" not in text:
        return text
    block = what(read(os.path.join(folder, "Delivery.md")))
    return re.sub(r"\n## What this is(?:\n\n[^\n]+(?:\n[^\n]+)*)?", lambda _: "\n" + block.rstrip("\n"), text, 1) if "\n## What this is\n" in text else text.replace("\n## System design", "\n" + block + "\n## System design", 1)


def pages(root, folder, listed):
    """The front pages whose generated parts (tables, What this is) the render keeps, if not listed already."""
    have = [rel for rel, _ in listed]
    return [(rel, []) for rel in ("README.md", folder + "/Home.md", folder + "/Principles.md") if rel not in have and os.path.exists(os.path.join(root, rel))]


def run(folder, readme, home, names):
    """DOC-25 findings for the README, Home and every wiki page, by the page's kind."""
    out = [("FORMAT", "%s:%d" % (n, i), "Sections: DOC-25 the principle tables have the columns %s (no Version, no Flow). Fix: run /workflow-docs render" % " | ".join(NEW))
           for n, t in (("README", readme), ("Home", home), ("Principles", open(os.path.join(folder, "Principles.md"), encoding="utf-8").read() if os.path.exists(os.path.join(folder, "Principles.md")) else ""))
           for i, x in enumerate(t.splitlines(), 1) if x.startswith("| Requirement | Summary") and "| Version | Flow |" in x]
    out += check("README", "front-adopted" if "## The template's principles" in readme else "front", readme) + check("Home", "front", home) + same(readme, home)
    for page in sorted(x[:-3] for x in os.listdir(folder) if x.endswith(".md")):
        kind = "howto" if page.startswith("How-to-use-") else {"Principles": "principles", "Tests": "tests", "Roadmap": "roadmap"}.get(page, "feature" if page in names else "")
        out += check(page, kind, open(os.path.join(folder, page + ".md"), encoding="utf-8").read()) if kind else []
    return out
