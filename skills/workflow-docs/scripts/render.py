#!/usr/bin/env python3
"""The Tests renderings (DOC-9 page tables, the DOC-10 full Tests page) from the regression rows, and the file reading
the page format checks (pageformat.py) need. Rendering functions are pure; render() writes.

criteria.py render calls render(); docs.py check calls generated() and front(); setup runs `render.py blocks`, the one
insert of the marked blocks (the rest only refresh them). Files are written via a temp file, printed as WROTE <file>.
It runs git only.
"""
import importlib
import json
import os
import re
import subprocess
import sys

import counting
import criteria as cr
import pageformat as pf
from deployments import link_of, regroup, topics_of

os.environ["GIT_TERMINAL_PROMPT"] = "0"  # no terminal: criteria (imported above) sets the rest, stdin included

SCENARIO = re.compile(r"^Given .+, when .+, then .+", re.I)
TESTS = ("Test", "Kind", "Guards", "Checks", "Last result")
FULL = ("Test", "Kind", "Guards", "Result", "Date", "Run", "Seen failing")
FORMAT = os.path.join(os.path.dirname(cr.SHEET), "..", "..", "workflow-regression", "scripts", "tests.py")


def tests_format(held={}):
    """tests.py loaded once; None, with a NOTE, if missing or broken."""
    import importlib.util as iu
    if "m" not in held:
        sys.dont_write_bytecode, held["m"] = True, None
        try:
            spec = iu.spec_from_file_location("regression_tests", FORMAT)
            mod = held["m"] = iu.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.fields, mod.issues_of, mod.entries
        except Exception as err:
            held["m"] = sys.stderr.write("NOTE: %s not found or broken (%s); Tests use a plain shape\n"
                                         % (os.path.normpath(FORMAT), type(err).__name__)) and None
    return held["m"]


def ran_of(root):
    """{row: (status, date, " FLAKY" if the 5th cell names a commit, REG-9)}."""
    return {row[0]: (row[1], row[2], " FLAKY" if (row + [""] * 5)[4] else "") for row in cr.tsv(root, "regression-runs.tsv")}


def table(root, ids, linked):
    """A page's Tests table for the requirements `ids` ((id, text) pairs)."""
    ran, rows, fmt = ran_of(root), {row[0]: row for row in cr.tsv(root, "regression.tsv")}, tests_format()
    issues = fmt.issues_of(root) if fmt else {}
    fields = (lambda row: fmt.fields(row[:8], {}, ran, issues, True)) if fmt else (lambda row: plain(row, ran))
    return tests_table(ids, linked, cr.defect_rows(root), rows, fields, ran)


def repo_of(root, text=""):
    """OWNER/REPO from the origin remote, else from a milestone URL in text; ''."""
    return pf.owner_repo(cr.git("remote", "get-url", "origin", check=False)) or pf.owner_repo(text)


def tests_page(root):
    """The full Tests page (DOC-10), from tests.py's entries and the runs file's 4th column."""
    fmt = tests_format()
    groups = fmt.entries(root, markdown=True) if fmt else []
    return full_page(groups, {row[0]: row[3] for row in cr.tsv(root, "regression-runs.tsv")}, repo_of(root), workflow_file(root))


def put(path, text):
    """Write text via a temp file renamed into place."""
    temp = "%s.%d.tmp" % (path, os.getpid())
    with open(temp, "w") as fh:
        fh.write(text)
    os.replace(temp, path)


def render(args):
    root = cr.git("rev-parse", "--show-toplevel")
    linked, _ = cr.test_rows(root)
    rules = cr.rules()
    clash = clashes([row[0] for row in cr.tsv(root, "regression.tsv") if row[1] != "draft"])
    if clash:
        sys.exit("REFUSED: two rows would share one Tests anchor: %s. Fix: rename one row id." % "; ".join(clash))
    # blocks first: a Tests rewrite keeps them
    stale = ["%s (%s block)" % x for x in (refresh(root, args.check) if config_of(root).get("criteria") and not getattr(args, "tables", False) else [])]
    out, idsof = [], lambda ls: [(m.group(1), m.group(4)) for _, m in cr.criteria_of(ls) if m]
    for rel in cr.pages(root):
        slug = os.path.basename(rel)[:-3]
        if slug in pf.GENERATED:
            continue
        text = read(os.path.join(root, rel))
        parts = cr.sections(text)
        url = link_of(text, counting.sources(root).get(slug, ""))
        if url:  # link form: ids come from the linked PRD, read now
            import prd
            body, _ = prd.read_link(url)
            if body is None or not parts or parts[-1][0] != "Tests":
                continue
            ids = [x for n, ls in cr.sections(body) if n == rules["sections"][1] for x in idsof(ls)]
        else:
            if [n for n, _ in parts if n not in (rules["usage"], rules["deploy"], rules["runbook"])] != rules["sections"] or parts[-1][0] != "Tests":
                continue  # a Runbook after Tests would be cut off: leave it to the check
            ids = idsof(dict(parts)[rules["sections"][1]])
        out.append((rel, text, text.partition("\n## Tests")[0] + "\n## Tests\n\n" + "\n".join(table(root, ids, linked)) + "\n"))
    if out:
        rel = os.path.join(cr.folder_of(root), "Tests.md")
        out.append((rel, read(os.path.join(root, rel)), tests_page(root)))
    for rel, text, fresh in out:
        if fresh != text:
            stale.append(rel)
            if not args.check:
                put(os.path.join(root, rel), fresh)
    for rel in stale:
        print("%s %s" % ("STALE" if args.check else "WROTE", rel))
    if not stale:
        print("TABLES OK")
    return 1 if stale and args.check else 0


def read(path):
    try:
        with open(path) as fh:
            return fh.read()
    except OSError:
        return None


def generated(root):
    """(STALE, Tests, first differing line) when the Tests page differs from a fresh render."""
    rel = os.path.join(cr.folder_of(root), "Tests.md")
    held = read(os.path.join(root, rel))
    if held is None:
        return [("STALE", "Tests", "no %s. Fix: /workflow-docs render" % rel)]
    have, want = held.splitlines(), tests_page(root).splitlines()
    for number, (got, fresh) in enumerate(zip(have + [""] * len(want), want + [""] * len(have))):
        if got != fresh:
            return [("STALE", "Tests", "line %d is %s, a fresh render has %s. Fix: /workflow-docs render"
                     % (number + 1, pf.short(got), pf.short(fresh)))]
    return []


def front(root, names):
    """DOC-4 on Home, DOC-5 on the README front door, for these pages."""
    on, folder, out = cr.rules()["format"], os.path.join(root, cr.folder_of(root)), []
    readme, home = read(os.path.join(root, "README.md")) or "", read(os.path.join(folder, "Home.md"))
    if "home" in on and home is not None:
        existing = {name[:-3] for name in os.listdir(folder) if name.endswith(".md")}
        out += pf.home(home, names, existing, readme, repo_of(root, home), topics_of(root))
    if "frontdoor" in on and names:
        out += pf.frontdoor(readme, names)
    return out


def test_slug(name):
    return re.sub(r"[^a-z0-9-]", "-", name.lower())


def plain(row, ran):
    """The fields tests.py would give: test, kind, guards, checks, runs, result, seen."""
    status, day = ran.get(row[0], ("not run", ""))[:2]
    guard = row[7] if row[6] == "defect" else row[3]
    return [row[0], row[6] if row[6] in ("defect", "workflow") else "requirement", guard or "-", row[5] or "-", row[1], (status + " " + day).strip(),
            row[4] if re.match(r"^\d{4}-\d\d-\d\d$", row[4]) else "no"]


def tests_table(ids, linked, defects, rows, fields, ran):
    """A page's Tests: one TESTS table: each requirement's rows (a 'not enforced' row when none passes), then the
    workflow tests (REG-1), then the defect tests. `fields(row)` is tests.py's format for a row."""
    out, flows = [], []
    for key, _ in ids:
        names = linked.get(key, [])
        for name in names:
            (flows if rows[name][6] == "workflow" else out).append(fields(rows[name]))
        if not any(ran.get(name, ("",))[0] == "PASS" for name in names):
            out.append(["-", "requirement", key, "no passing test", "", "not enforced"])
    out += flows + [fields(rows[name]) for key, _ in ids for name in defects.get(key, [])]
    shown = [[x[0] if x[0] == "-" else "[%s](Tests#t-%s)" % (x[0], test_slug(x[0])), x[1], x[2],
              x[3] if x[0] == "-" or SCENARIO.match(x[3]) else x[3] + " (not yet Given/When/Then)", x[5]] for x in out]
    return pf.table(TESTS, shown) if shown else []


def run_cell(value, repo, day="", flow="regression.yml"):
    """A URL is its Actions run; empty, that day's CI runs; a sha, its commit; else local."""
    if re.match(r"^https?://\S+$", value):
        return "[run](%s)" % value
    if re.match(r"^[0-9a-f]{7,40}$", value):
        return "[%s](https://github.com/%s/commit/%s)" % (value[:7], repo, value) if repo else value[:7]
    if not value and repo and re.match(r"^\d{4}-\d\d-\d\d$", day):
        return "[CI %s](https://github.com/%s/actions/workflows/%s?query=created%%3A%s)" % (day, repo, flow, day)
    return "local"


def full_page(groups, runs, repo, flow="regression.yml"):
    """docs/wiki/Tests.md: marker, '# Tests', then per feature '## <Feature>' and a FULL table whose first cell is the
    anchor pages link to. `groups`: tests.py's entries(); `runs`: a row to its run."""
    out = [pf.MARKER, "# Tests", ""]
    for feature, lines in groups:
        rows = []
        for x in lines:
            result = re.match(r"^(\S+) (\d{4}-\d\d-\d\d)$", x[5])
            status, day = result.groups() if result else (x[5], "")
            guard = x[2].split(": ", 1)[0] if x[1] == "requirement" else x[2]
            rows.append(['<a id="t-%s"></a>%s' % (test_slug(x[0]), x[0]), x[1], guard, status, day or "-",
                         run_cell(runs.get(x[0], ""), repo, day, flow), x[6]])
        out += ["## " + feature, ""] + pf.table(FULL, rows) + [""]
    return "\n".join(out if groups else out + ["No tests yet.", ""])


def clashes(names):
    """Row ids whose anchors collide: 'a and b share t-x'."""
    seen, out = {}, []
    for name in names:
        key = test_slug(name)
        if key in seen and seen[key] != name:
            out.append("%s and %s share t-%s" % (seen[key], name, key))
        seen.setdefault(key, name)
    return out


# the Settings and Automation blocks on Home, the README's template line
SKILLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_REPO = "jcl2018/agent-workflow-template"  # last resort
MARKS = ("settings", "automation", "template")


def block_re(name):
    return re.compile(r"<!-- %s:begin -->\n.*?<!-- %s:end -->\n" % (name, name), re.S)


config_of = counting.config_of
def workflow_file(root):
    """The regression routine's workflow file, else regression.yml (#3839)."""
    for e in counting.entries(root):
        if e.get("name") == "regression" and str(e.get("runs")).startswith("github:"):
            return e["runs"][7:] or "regression.yml"
    return "regression.yml"


def reference():
    """[(name, default, meaning)] from `settings.py reference`; [] if unreadable."""
    path = os.path.join(SKILLS, "workflow-setup", "scripts", "settings.py")
    done = subprocess.run([sys.executable, path, "reference"], capture_output=True, text=True) if os.path.exists(path) else None
    rows, on = [], False
    for line in (done.stdout.splitlines() if done and done.returncode == 0 else []):
        if line.startswith("## "):
            on = line.strip() == "## Repo settings"
        found = on and re.match(r"^\| `(\w+)` \| (.+?) \| (.+) \|$", line)
        if found:
            rows.append((found.group(1), found.group(2).strip("`"), found.group(3)))
    return rows


def parsed(text):
    if text == "(empty)":
        return ""
    try:
        return json.loads(text)
    except ValueError:
        return text


def shown(value):
    return "(empty)" if value == "" else (value if isinstance(value, str) else json.dumps(value))


def settings_block(root):
    cfg, rows = config_of(root), []
    for name, default, meaning in reference():
        if name == "topics" and "topics" not in cfg:
            continue
        over = name in cfg and cfg[name] != parsed(default)
        rows.append(["`%s`" % name, meaning, 'set "%s" in .loop/config.json' % name, "`%s`" % default,
                     "**overridden:** `%s`" % shown(cfg[name]) if over else "default"])
    body = pf.table(["Name", "What it means", "How to set it", "Default", "This repo"], rows) if rows else ["The settings reference is not installed here."]
    return "\n".join(["<!-- settings:begin -->", "## Settings", "",
                       "Every repo setting from the template's settings reference, with this repo's value from `.loop/config.json`.", ""]
                      + body + ["<!-- settings:end -->", ""])


def template_line(root):
    repo = config_of(root).get("template_repo")
    if not repo:
        done = subprocess.run(["git", "-C", SKILLS, "remote", "get-url", "origin"], capture_output=True, text=True)
        repo = pf.owner_repo(done.stdout) if done.returncode == 0 else ""
    repo = repo if repo and re.match(r"^[\w.-]+/[\w.-]+$", str(repo)) else TEMPLATE_REPO
    return "<!-- template:begin -->\nBuilt with the [%s](https://github.com/%s) workflow loop.\n<!-- template:end -->\n" % (repo, repo)


def with_blocks(text, blocks, insert=False):
    """text with each (name, block) replaced; insert adds missing ones (template: after paragraph 1)."""
    for name, block in blocks:
        pattern = block_re(name)
        if pattern.search(text):
            text = pattern.sub(lambda _: block, text, 1)
        elif not insert:
            continue
        elif name == "template":
            head, sep, rest = text.partition("\n\n")
            text = head + "\n\n" + block + ("\n" + rest if sep else "")
        else:
            text = text.rstrip("\n") + "\n\n" + block
    return text


def front_files(root, insert=False):
    """[(rel, blocks)] for README and Home if present; only a DOC-4 Home gets new blocks."""
    out, home = [], os.path.join(cr.folder_of(root), "Home.md")
    text = read(os.path.join(root, home)) or ""
    both = [("settings", settings_block(root)), ("automation", counting.automation_block(root))]
    if re.search(r"^## Features\s*$", text, re.M) or (block_re("settings").search(text) and not insert):
        out.append((home, both))
    if os.path.exists(os.path.join(root, "README.md")):
        out.append(("README.md", [("template", template_line(root))] + both))
    return out


def refresh(root, check=False, insert=False):
    """Write the blocks (check: only list): [(rel, name)] stale; missing ones only with insert."""
    stale = []
    for rel, blocks in front_files(root, insert):
        held = read(os.path.join(root, rel)) or ""
        for name, block in blocks:
            found = block_re(name).search(held)
            if (found and found.group(0) != block) or (insert and not found):
                stale.append((rel, name))
        fresh = with_blocks(held, blocks, insert)
        grouped = regroup(fresh, topics_of(root)) if os.path.basename(rel) == "Home.md" else fresh
        if grouped != fresh:
            stale.append((rel, "topics"))
            fresh = grouped
        if fresh != held and not check:
            put(os.path.join(root, rel), fresh)
    return stale


def stale_blocks(root):
    """(STALE, Settings|Automation|README line, where and fix) per block unlike a fresh render."""
    names = dict(settings="Settings", automation="Automation", template="README line", topics="Topics")
    return [("STALE", names[name], "%s differs from a fresh render. Fix: /workflow-docs render" % where) for where, name in refresh(root, True)]


def perm_wiki_page(root, page):
    try:
        folder = importlib.import_module("docs").wiki_dir(root)
    except SystemExit:
        folder = "docs/wiki"
    try:
        with open(os.path.join(root, folder, page + ".md"), encoding="utf-8-sig") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def perm_needs(root, routine, page):
    """(tool, text) pairs the Runbook's Steps and Full run name: backticked commands starting with a program, https
    hosts as WebFetch domains."""
    inside, field, found = False, "", []
    for line in perm_wiki_page(root, page):
        if line.startswith("### "):
            inside = line[4:].strip() == routine
        elif line.startswith("## "):
            inside = False
        elif inside:
            match = counting.PERM_FIELD.match(line)
            field = match.group(1) if match else field
            if field in ("Steps", "Full run"):
                for span in re.findall(r"`([^`]+)`", line):
                    if " " in span and span.split(" ", 1)[0] in counting.PERM_PROGRAMS:
                        found.append(("Bash", " ".join(span.split())))
                found += [("WebFetch", "domain:" + host) for host in re.findall(r"https?://([A-Za-z0-9.-]+)", line)]
    return found


def mirror_of(path):
    """({id: text}, owned, {id: sha8 agreed}) of a PRD's repo copy; not owned if another file is there."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().replace("\r\n", "\n").split("\n")
    except OSError:
        return {}, True, {}
    try:
        with open(path[:-3] + ".base", encoding="utf-8") as fh:
            agreed = dict(x.split("\t") for x in fh.read().split("\n") if "\t" in x)
    except OSError:
        agreed = {}
    return {m.group(1): m.group(2) for m in (re.match(r"- ([A-Z]{2,5}-\d+): (.*)$", x) for x in lines) if m}, lines[0] == cr.SYNC_MARK, agreed


if __name__ == "__main__":
    if sys.argv[1:] == ["--help"]:
        sys.exit(print("usage: render.py blocks"))
    sys.argv[1:] == ["blocks"] or sys.exit("usage: render.py blocks")
    top = cr.git("rev-parse", "--show-toplevel")
    print("\n".join("WROTE %s (%s block)" % x for x in (refresh(top, insert=True) if config_of(top).get("criteria") else [])) or "BLOCKS OK")
