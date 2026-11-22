"""DOC-25: each page kind has its fixed ## headings in order (KINDS); README and Home match. DOC-27: new-form features."""
import os
import re
import sys
import pageformat as pf

KINDS = {
    'front': ('What this is', 'System design', '+\\d+\\. .+', 'Requirements by feature'),
    'front-adopted': ('What this is', 'System design', "The template's principles", '+\\d+\\. .+', 'Requirements by feature'),
    'feature': ('Problem', '?Runbook', 'Requirements', 'Non-goals', 'Success metrics', '?Reference', '?Deployments', 'Revisions', 'Tests'),
    'howto': ("What it's for", 'How to reach or run it', 'URLs and deployments', '?Automations and schedules', '?Runbooks', 'Links'),
    'principles': ('+\\d+\\. .+',),
    'tests': ('+(?!Other$).+', 'Other'),
    'roadmap': ('+.+',),
}
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1")  # DEL-10: gh and git never wait on a prompt
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
    """DOC-15:"""
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
    """DEL-21:"""
    if cell.lstrip().startswith("- "):
        return cell.strip()
    parts, tag, out = [p.strip() for p in re.split(r";\s+(?![^()]*\))", cell.strip()) if p.strip()], "", []
    for part in reversed(parts):
        found = TAG.search(part)
        tag = found[1] if found else tag
        out.insert(0, "- %s%s" % (part[:found.start()] if found else part, ": " + tag if tag else ""))
    return "<br>".join(out)


def follows(cell):
    """The (source, tag) lines of a bullet Follows cell;"""
    return [(re.sub(r"[:] (%s)$" % TAGS, "", x[2:]), (re.search(r"[:] (%s)$" % TAGS, x) or [0, ""])[1]) for x in cell.split("<br>") if x.startswith("- ")]


def adoption(cell):
    """The share of a row's Follows lines tagged adopted (adapted, planned and own count 0);"""
    tags = [t for _, t in follows(cell)]
    return round(100 * tags.count("adopted") / len(tags)) if tags else None


def latest_full(slug, ids):
    """DEL-21:"""
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
    """DEL-21:"""
    ids = re.findall(r"\b[A-Z]{2,5}-\d+\b", (re.match(r"\[([^\]]*)\]", row) or [0, ""])[1])
    ran = [runs.get(t[0]) for t in tests if len(t) > 3 and t[3] in ids]
    ran = [r for r in ran if r in ("PASS", "FAIL")]
    return "%d%% (%d of %d)" % (round(100 * ran.count("PASS") / len(ran)), ran.count("PASS"), len(ran)) if ran else UNDATA


def tables(text, tests=(), runs=None, keep=False):
    """DOC-25, DEL-21:"""
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
    """The What this is section, written from DEL-19's text on the Delivery page;"""
    found = re.search(r"^- DEL-19: .*\n((?:  - .*\n?)*)", page or "", re.M)
    return found and "## What this is\n\n" + " ".join(re.sub(r"\s*\[[A-Z]{3}-\d+\]$", "", b[4:]) for b in found[1].splitlines()) + "\n"


def relink(text, slug):
    """Links to this repository's own pages and files name its owner now, whoever owned it"""
    return re.sub(r"https://github\.com/[\w.-]+/%s/" % re.escape(slug.split("/")[1]), "https://github.com/%s/" % slug, text) if slug.count("/") == 1 else text


def fresh(text, folder, read, slug="", keep=False):
    """README, Home or Principles with its generated parts current (What this is:"""
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
    """The front pages whose generated parts (tables, What this is) the render keeps, if not"""
    have = [rel for rel, _ in listed]
    return [(rel, []) for rel in ("README.md", folder + "/Home.md", folder + "/Principles.md") if rel not in have and os.path.exists(os.path.join(root, rel))]


HEADS = ("Problem", "Requirements", "Non-goals", "Success metrics", "Reference", "Revisions")
FEAT = re.compile(r"^- ([A-Z]+-\d+): \*\*(Unreviewed|Reviewed)([^*]*)\*\*")
NUM = re.compile(r"^(\d+\.\d+) \S")
LANDS = "2026-11-22"  # DOC-27.5: a Reviewed mark dated on or after this day needs its line in .loop/reviews.tsv


def blocks(text):
    """DOC-27: new-form features."""
    out, cur = [], None
    for line in text.splitlines():
        found = FEAT.match(line)
        if found:
            cur = [found[1], found[2], found[3].strip(), []]
            out.append(cur)
        elif cur and line.startswith("  - "):
            cur[3].append(line[4:].rstrip())
        elif line.strip():
            cur = None
    return [b for b in out if "### Problem" in b[3]]


def part(lines, name):
    """One ### part of a feature."""
    out, inside = [], False
    for x in lines:
        inside = x[4:] == name if x.startswith("### ") else inside
        out += [x] * (inside and not x.startswith("### "))
    return out


def feature(page, fid, mark, date, lines, slug, reviews):
    """DOC-27 findings of one feature."""
    at, out = "%s:%s" % (page, fid), []
    bad = lambda rule, why, fix, hard=True: out.append(("FORMAT" if hard or (mark == "Reviewed" and rule != "27.5") else "NOTE", at, "DOC-27 %s: %s. Fix: %s" % (rule, why, fix)))
    got = [x[4:] for x in lines if x.startswith("### ")]
    if got != list(HEADS):
        bad("27.1", "the sections are %s, not %s in order" % (got, list(HEADS)), "use the six sections in order")
    for name in ("Problem", "Non-goals"):
        if not [x for x in part(lines, name) if x.strip()]:
            bad("27.1", "%s is empty" % name, "write it, or None for Non-goals")
    head = lines[:lines.index("### Problem")] if "### Problem" in lines else []
    links = [pf.owner_repo(x) for x in head if x.startswith("Milestone:") and "/milestone/" in x]
    if not links or any(x != slug for x in links):
        bad("27.1", "its Milestone line is missing or does not link a milestone of %s" % slug, "add Milestone: [name](https://github.com/%s/milestone/N)" % slug)
    req = part(lines, "Requirements")
    cut = req.index("Non-functional") if "Non-functional" in req else len(req)
    if "Functional" not in req or "Non-functional" not in req or req.index("Functional") > cut:
        bad("27.1", "Requirements needs Functional, then Non-functional", "add both lines (Non-functional may say None)")
    nums = [(i, NUM.match(x)[1]) for i, x in enumerate(req) if NUM.match(x)]
    if len([n for i, n in nums if i < cut]) > 5:
        bad("27.2", "more than five functional requirements", "split the feature")
    metrics = {}
    for k, (i, n) in enumerate(nums):
        end = nums[k + 1][0] if k + 1 < len(nums) else len(req)
        seg = req[i:min(end, cut) if i < cut else end]
        mine = [x for x in seg if x.startswith("**Success metric %s.**" % n)]
        if len(mine) != 1:
            bad("27.2", "requirement %s has %d success metrics" % (n, len(mine)), "give it exactly one 'Success metric %s.'" % n, False)
        elif not any(x.startswith("Target **") for x in seg) or not any(x.startswith("Today **") for x in seg):
            bad("27.2", "the metric of %s has no target or no today value" % n, "add 'Target **x**' and 'Today **y**'", False)
        else:
            metrics[n] = (mine[0][len("**Success metric %s.**" % n):].strip(), [x for x in seg if x.startswith("Target **")][0][9:-2], [x for x in seg if x.startswith("Today **")][0][8:-2])
        cases = seg[seg.index("Test cases") + 1:] if "Test cases" in seg else []
        if not [c for c in cases if c.strip() and not NUM.match(c) and not c.startswith("Non-functional")]:
            bad("27.2", "requirement %s has no test case" % n, "add a Test cases list", False)
    table = {}
    for x in part(lines, "Success metrics"):
        cells = [c.strip() for c in x.split("|")]
        if len(cells) == 4 and NUM.match(cells[0] + " x"):
            table[cells[0]] = (cells[1], cells[2], cells[3])
    if metrics and table != metrics:
        bad("27.2", "the Success metrics table does not match the inline metrics (%s)" % ", ".join(sorted(set(table) ^ set(metrics)) or ["text differs"]), "make each line equal its inline metric")
    ref = part(lines, "Reference")
    pairs = [(ref[i], ref[i + 1] if i + 1 < len(ref) else "") for i, x in enumerate(ref) if x in ("adopted", "adapted", "own", "reference")]
    if not pairs or [x for x in ref if re.fullmatch(r"[a-z]+", x) and x not in ("adopted", "adapted", "own", "reference")]:
        bad("27.3", "Reference has no entry or an entry with no valid tag", "tag each source adopted, adapted, own or reference", False)
    for tag, text in pairs:
        if not re.match(r"\[[^\]]+\]\(https?://[^/)]+/[^)]*\)", text):
            bad("27.3", "a %s reference names no linked source" % tag, "start the entry with [source](https://...)", False)
    if mark == "Reviewed" and not reviews.get(fid):
        bad("27.5", "the Reviewed mark has no line in .loop/reviews.tsv naming the typed record", "run the mark command where the owner-words ledger is (a NOTE until %s)" % LANDS, bool(date) and date.split()[0] >= LANDS)
    return out


def reviewed(root, folder, command, ids, rec, common, day):
    """DOC-27.5: record check, reviews line."""
    if command != "review":
        return
    new = {b[0] for f in sorted(os.listdir(folder)) if f.endswith(".md") for b in blocks(open(os.path.join(folder, f), encoding="utf-8").read())}
    mine = [i for i in ids if i in new]
    ledger = os.path.join(common, "owner-words.tsv")
    row = next((r for r in (x.rstrip("\n").split("\t") for x in open(ledger, encoding="utf-8")) if len(r) == 5 and r[0] == rec), None) if rec and os.path.exists(ledger) else None
    for i in mine:
        if (rec and not (row and row[4].split(",") == [i] and row[2] in ("operation", "owner"))) or (not rec and len(ids) > 1):
            sys.exit("REFUSED: %s needs the owner's record naming exactly %s (record %s covers %s). Nothing was changed. Fix: sessions.py owner-words --from owner, for this one ID." % (i, i, rec or "none", row[4] if row else "nothing"))
    if mine:
        with open(os.path.join(root, ".loop", "reviews.tsv"), "a", encoding="utf-8") as fh:
            fh.writelines("%s\t%s\t%s\n" % (i, rec or "typed", day) for i in mine)


def principled(folder, fid):
    """DOC-27.1: one principle."""
    path = os.path.join(folder, "Principles.md")
    secs = re.split(r"(?m)^## ", open(path, encoding="utf-8").read())[1:] if os.path.exists(path) else []
    n = sum(bool(re.search(r"\[%s " % fid, x)) for x in secs)
    return [] if n == 1 or not secs else [("FORMAT", fid, "DOC-27 27.1: listed under %d principles. Fix: exactly one principle holds it" % n)]


def features(folder, page, text):
    """DOC-27 findings of a page."""
    found = blocks(text)
    if not found:
        return []
    import counting
    root = os.path.dirname(os.path.dirname(os.path.abspath(folder)))
    path = os.path.join(root, ".loop", "reviews.tsv")
    reviews = {r[0]: r[1] for r in (x.split("\t") for x in open(path, encoding="utf-8").read().splitlines() if x[:1] != "#") if len(r) > 1} if os.path.exists(path) else {}
    slug, out = counting.repo_slug(root), []
    for fid, mark, date, lines in found:
        out += feature(page, fid, mark, date, lines, slug, reviews) + principled(folder, fid)
    return out


BLOCK = re.compile(r"(<!-- steps -->)(.*?)(<!-- /steps -->)", re.S)


def steps():
    """DEL-19.4: steps from flow.py."""
    got = re.search(r"^STEPS = \(([^)]*)\)", open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts", "flow.py"), encoding="utf-8").read(), re.M)
    return "Steps: %s." % ", ".join(re.findall(r'"(\w+)"', got[1])) if got else "Steps: unreadable."


def stale(page, text):
    """DEL-19.4: a stale steps block."""
    found = BLOCK.search(text)
    return [("FORMAT", page, "Steps: DEL-19.4 the drawn steps '%s' differ from the code ('%s'). Fix: python3 sections.py steps --write" % (found[2], steps()))] if found and found[2] != steps() else []


def run(folder, readme, home, names):
    """DOC-25 findings for the README, Home and every wiki page, by the page's kind"""
    out = [("FORMAT", "%s:%d" % (n, i), "Sections: DOC-25 the principle tables have the columns %s (no Version, no Flow). Fix: run /workflow-docs render" % " | ".join(NEW))
           for n, t in (("README", readme), ("Home", home), ("Principles", open(os.path.join(folder, "Principles.md"), encoding="utf-8").read() if os.path.exists(os.path.join(folder, "Principles.md")) else ""))
           for i, x in enumerate(t.splitlines(), 1) if x.startswith("| Requirement | Summary") and "| Version | Flow |" in x]
    out += check("README", "front-adopted" if "## The template's principles" in readme else "front", readme) + check("Home", "front", home) + same(readme, home)
    for page in sorted(x[:-3] for x in os.listdir(folder) if x.endswith(".md")):
        kind = "howto" if page.startswith("How-to-use-") else {"Principles": "principles", "Tests": "tests", "Roadmap": "roadmap"}.get(page, "feature" if page in names else "")
        text = open(os.path.join(folder, page + ".md"), encoding="utf-8").read()
        out += (check(page, kind, text) + features(folder, page, text) + stale(page, text)) if kind else []
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["steps"]:
        for name in sys.argv[3:] or ["docs/wiki/Delivery.md"]:
            old = open(name, encoding="utf-8").read()
            new = BLOCK.sub(lambda m: m[1] + steps() + m[3], old)
            print(name, "stale" if new != old else "fresh")
            if "--write" in sys.argv and new != old:
                open(name, "w", encoding="utf-8").write(new)
