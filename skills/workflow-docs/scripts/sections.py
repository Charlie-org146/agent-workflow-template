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
UNSEEN, UNDATA = "not measured: no references recorded yet", "not measured: no data yet"


TAG = re.compile(r"[:] (adopted|adapted|planned|own)\b[^;<]*$")
TAGS = "adopted|adapted|planned|own"


def bullets(cell):
    """DEL-21: a Follows cell as "- source: tag" lines joined by <br>; an old "a; b: adapted" cell is migrated (an untagged source takes the tag to its right)."""
    if cell.lstrip().startswith("- "):
        return cell.strip()
    parts, tag, out = [p.strip() for p in re.split(r";\s+(?![^()]*\))", cell.strip()) if p.strip()], "", []
    for part in reversed(parts):
        found = TAG.search(part)
        tag = found[1] if found else tag
        out.insert(0, "- %s%s" % (part[:found.start()] if found else part, ": " + tag if tag else ""))
    return "<br>".join(out)


def follows(cell):
    """The (source, tag) lines of a bullet Follows cell; tag is "" when a line has none."""
    return [(re.sub(r"[:] (%s)$" % TAGS, "", x[2:]), (re.search(r"[:] (%s)$" % TAGS, x) or [0, ""])[1]) for x in cell.split("<br>") if x.startswith("- ")]


def adoption(cell):
    """The share of a row's Follows lines tagged adopted (adapted, planned and own count 0); None with no lines."""
    tags = [t for _, t in follows(cell)]
    return round(100 * tags.count("adopted") / len(tags)) if tags else None


def latest_full(slug, ids):
    """DEL-21: {test id: state} of the latest finished regression run on main whose results cover most tests (a full run, not a row or lane run), read from its results-* artifacts with gh; None when none can be read."""
    import json, subprocess, tempfile
    got = subprocess.run(["gh", "run", "list", "-R", slug, "--workflow", "regression", "--branch", "main", "--limit", "12", "--json", "databaseId,conclusion"], capture_output=True, text=True)
    for run in (json.loads(got.stdout) if got.returncode == 0 and got.stdout.strip() else []):
        if run["conclusion"] not in ("success", "failure"):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["gh", "run", "download", str(run["databaseId"]), "-R", slug, "-p", "results-*", "-D", tmp], capture_output=True, text=True)
            rows = [x.split("\t") for d, _, fs in os.walk(tmp) for f in fs for x in open(os.path.join(d, f), encoding="utf-8").read().splitlines() if x[:1] != "#"]
        results = {x[0]: x[1] for x in rows if len(x) > 1}
        if len(set(results) & set(ids)) * 5 >= len(ids) * 4:
            return results
    return None


def confidence(row, tests, runs):
    """DEL-21: the share of the requirement's tests (rows of .loop/regression.tsv naming it or an ID it absorbs) that PASS on the latest run; not measured with none."""
    ids = re.findall(r"\b[A-Z]{2,5}-\d+\b", (re.match(r"\[([^\]]*)\]", row) or [0, ""])[1])
    ran = [runs.get(t[0]) for t in tests if len(t) > 3 and t[3] in ids]
    ran = [r for r in ran if r in ("PASS", "FAIL")]
    return "%d%% (%d of %d)" % (round(100 * ran.count("PASS") / len(ran)), ran.count("PASS"), len(ran)) if ran else UNDATA


def tables(text, tests=(), runs=None, keep=False):
    """DOC-25, DEL-21: each principle table in the new columns; Follows as a tagged bullet list, Adoption computed from it, Confidence from the tests (keep: an existing figure is kept), one score line under it."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        head = [c.strip() for c in SPLIT.split(lines[i].strip()[1:-1])] if lines[i].startswith("| Requirement | Summary") else []
        if head not in (OLD, NEW):
            out.append(lines[i]); i += 1; continue
        out += ["| " + " | ".join(NEW) + " |", lines[i + 1]]; rows = []; i += 2
        while i < len(lines) and lines[i].startswith("|"):
            c = [x.strip() for x in SPLIT.split(lines[i].strip()[1:-1])]
            rows.append([c[0] + " (" + c[5] + ")"] + c[1:4] + ["", ""] if head == OLD else c); i += 1
        scores = []
        for c in rows:
            c[2] = bullets(c[2])
            scores.append(adoption(c[2]))
            c[4] = UNSEEN if scores[-1] is None else "%d%%" % scores[-1]
            was = c[5] if keep and re.match(r"\d+% \(\d+ of \d+\)$|not measured", c[5]) else ""
            c[5] = was or confidence(c[0], tests, runs or {})
            out.append("| " + " | ".join(c) + " |")
        while i < len(lines) and (lines[i] == "" or lines[i].startswith("Adoption: ")):
            i += 1
        seen = [s for s in scores if s is not None]
        out += ["", "Adoption: %s." % ("%d%% (the average of this principle's rows)" % round(sum(seen) / len(seen)) if seen else UNSEEN), ""]
    return "\n".join(out)


def what(page):
    """The What this is section, written from DEL-19's text on the Delivery page; None when the page has no DEL-19."""
    found = re.search(r"^- DEL-19: .*\n((?:  - .*\n?)*)", page or "", re.M)
    return found and "## What this is\n\n" + " ".join(re.sub(r"\s*\[[A-Z]{3}-\d+\]$", "", b[4:]) for b in found[1].splitlines()) + "\n"


def relink(text, slug):
    """Links to this repository's own pages and files name its owner now, whoever owned it when the page was written."""
    return re.sub(r"https://github\.com/[\w.-]+/%s/" % re.escape(slug.split("/")[1]), "https://github.com/%s/" % slug, text) if slug.count("/") == 1 else text


def fresh(text, folder, read, slug="", keep=False):
    """README, Home or Principles with its generated parts current (What this is: only its first paragraph; later ones are the owner's); text with no System design section is left alone."""
    tests = [x.split("\t") for x in (read(os.path.join(os.path.dirname(os.path.dirname(folder)), ".loop", "regression.tsv")) or "").splitlines()[1:]]
    runs = None if keep or slug.count("/") != 1 else latest_full(slug, [t[0] for t in tests])
    text = relink(tables(text, tests, runs or {}, keep or runs is None), slug)
    if "\n## System design" not in text:
        return text
    block = what(read(os.path.join(folder, "Delivery.md")))
    if not block:  # no DEL-19 in this repo: What this is stays as written
        return text
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
