"""DOC-25: each page kind has its fixed ## headings in order; README and Home match.

KINDS maps a page kind to one regex per heading, each matching a whole heading. A "?" prefix makes a heading optional,
a "+" prefix one or more. A page kind with a heading missing, extra, renamed or out of order fails the docs check;
README and Home share the "front" row.
"""
import re

KINDS = {
    'front': ('System design', '+\\d+\\. .+', 'Requirements by feature'),
    'front-adopted': ('System design', "The template's principles", '+\\d+\\. .+', 'Requirements by feature'),
    'feature': ('Problem', '?Runbook', 'Requirements', 'Non-goals', 'Success metrics', 'Revisions', 'Tests'),
    'howto': ("What it's for", 'How to reach or run it', 'URLs and deployments', '?Automations and schedules', '?Runbooks', 'Links'),
    'principles': ('+\\d+\\. .+',),
    'tests': ('+(?!Other$).+', 'Other'),
    'roadmap': ('+.+',),
}
LINK = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/wiki/")


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
        if t == "*":
            return None
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
            out.append(LINK.sub("", line.strip()))
    return out


def same(readme, home):
    a, b = [x for _, x in heads(readme)], [x for _, x in heads(home)]
    bad = [("FORMAT", "Home:1", "Sections: DOC-25 README and Home have the same sections in order (README %s, Home %s). Fix: make them match" % (a, b))] * (a != b)
    return bad + [("FORMAT", "Home:%d" % n, "Sections: DOC-25 '%s' is the same on README and Home. Fix: copy it from the README" % x)
                  for n, x in heads(home) if x in a and body(readme, x) != body(home, x)]
