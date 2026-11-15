#!/usr/bin/env python3
"""The Tests renderings (DOC-9 page tables, the DOC-10 full Tests page) from the regression rows, and the file reading
the page format checks (pageformat.py) need. The rendering functions are pure; render() writes.

criteria.py render calls render(); docs.py check calls generated() and front(); setup runs `render.py blocks`, the one
insert of the marked blocks (the rest only refresh them). Each file is written to a temp file renamed into place,
printed as WROTE <file>. It runs git and nothing else.
"""
import glob
import json
import os
import re
import subprocess
import sys

import counting
import criteria
import pageformat
from deployments import link_of, regroup, topics_of

# No terminal: a git or gh prompt must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

SCENARIO = re.compile(r"^Given .+, when .+, then .+", re.I)
TESTS = ("Test", "Kind", "Guards", "Checks", "Last result")
FULL = ("Test", "Kind", "Guards", "Result", "Date", "Run", "Seen failing")
FORMAT = os.path.join(os.path.dirname(criteria.SHEET), "..", "..", "workflow-regression", "scripts", "tests.py")  # the one test format


def tests_format(held={}):
    """tests.py, the test format, loaded once; None, with a NOTE, if missing or broken."""
    import importlib.util
    if "m" not in held:
        sys.dont_write_bytecode, held["m"] = True, None
        try:
            spec = importlib.util.spec_from_file_location("regression_tests", FORMAT)
            held["m"] = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(held["m"])
            held["m"].fields, held["m"].issues_of, held["m"].entries  # too old
        except Exception as err:  # noqa: BLE001
            held["m"] = sys.stderr.write("NOTE: %s not found or broken (%s); Tests use a plain shape\n"
                                         % (os.path.normpath(FORMAT), type(err).__name__)) and None
    return held["m"]


def ran_of(root):
    """{row: (status, date, " FLAKY" when its 5th cell names the flipping commit, REG-9)}."""
    return {row[0]: (row[1], row[2], " FLAKY" if (row + [""] * 5)[4] else "") for row in criteria.tsv(root, "regression-runs.tsv")}


def table(root, ids, linked):
    """The Tests table of a page holding the requirements `ids` ((id, text) pairs)."""
    ran, rows, fmt = ran_of(root), {row[0]: row for row in criteria.tsv(root, "regression.tsv")}, tests_format()
    issues = fmt.issues_of(root) if fmt else {}
    fields = (lambda row: fmt.fields(row[:8], {}, ran, issues, True)) if fmt else (lambda row: plain(row, ran))
    return tests_table(ids, linked, criteria.defect_rows(root), rows, fields, ran)


def repo_of(root, text=""):
    """OWNER/REPO from the origin remote, else from a milestone URL in text; ''."""
    return pageformat.owner_repo(criteria.git("remote", "get-url", "origin", check=False)) or pageformat.owner_repo(text)


def tests_page(root):
    """The full Tests page (DOC-10), from tests.py's entries and the runs file's fourth column."""
    fmt = tests_format()
    groups = fmt.entries(root, markdown=True) if fmt else []
    return full_page(groups, {row[0]: row[3] for row in criteria.tsv(root, "regression-runs.tsv")}, repo_of(root), workflow_file(root))


def maps(root):
    """{skill: its ## Command map text}."""
    return {os.path.basename(os.path.dirname(path)): (read(path) or "").partition("## Command map")[2].split("\n## ")[0]
            for path in sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md")))}


def put(path, text):
    """Write text to a temp file beside path, rename it into place."""
    temp = "%s.%d.tmp" % (path, os.getpid())
    with open(temp, "w") as handle:
        handle.write(text)
    os.replace(temp, path)


def render(args):
    root = criteria.git("rev-parse", "--show-toplevel")
    linked, _ = criteria.test_rows(root)
    rules = criteria.rules()
    clash = clashes([row[0] for row in criteria.tsv(root, "regression.tsv") if row[1] != "draft"])
    if clash:
        sys.exit("REFUSED: two rows would share one Tests anchor: %s. Fix: rename one row id." % "; ".join(clash))
    # blocks first: a Tests rewrite keeps them
    stale = ["%s (%s block)" % x for x in (refresh(root, args.check) if config_of(root).get("criteria") and not getattr(args, "tables", False) else [])]
    out = []
    for rel in criteria.pages(root):
        slug = os.path.basename(rel)[:-3]
        if slug in pageformat.GENERATED:
            continue
        with open(os.path.join(root, rel)) as handle:
            text = handle.read()
        parts = criteria.sections(text)
        url = link_of(text, counting.sources(root).get(slug, ""))
        if url:  # a link-form page: ids come from the linked PRD, read now, never copied
            import prd
            body, _ = prd.read_link(url)
            if body is None or not parts or parts[-1][0] != "Tests":
                continue
            ids = [(m.group(1), m.group(4)) for n, ls in criteria.sections(body) if n == rules["sections"][1] for _, m in criteria.criteria_of(ls) if m]
        else:
            if [n for n, _ in parts if n not in (rules["usage"], rules["deploy"], rules["runbook"])] != rules["sections"] or parts[-1][0] != "Tests":
                continue  # a misplaced Runbook after Tests would be cut off: leave it for the check
            ids = [(m.group(1), m.group(4)) for _, m in criteria.criteria_of(dict(parts)[rules["sections"][1]]) if m]
        out.append((rel, text, text.partition("\n## Tests")[0] + "\n## Tests\n\n" + "\n".join(table(root, ids, linked)) + "\n"))
    if out:
        rel = os.path.join(criteria.folder_of(root), "Tests.md")
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
        with open(path) as handle:
            return handle.read()
    except OSError:
        return None


def generated(root):
    """(STALE, Tests, first differing line) when the Tests page differs from a fresh render (DOC-10)."""
    rel = os.path.join(criteria.folder_of(root), "Tests.md")
    held = read(os.path.join(root, rel))
    if held is None:
        return [("STALE", "Tests", "no %s. Fix: /workflow-docs render" % rel)]
    have, want = held.splitlines(), tests_page(root).splitlines()
    for number, (got, fresh) in enumerate(zip(have + [""] * len(want), want + [""] * len(have))):
        if got != fresh:
            return [("STALE", "Tests", "line %d is %s, a fresh render has %s. Fix: /workflow-docs render"
                     % (number + 1, pageformat.short(got), pageformat.short(fresh)))]
    return []


def front(root, names):
    """DOC-4 on Home, DOC-5 on the README front door, for these feature pages."""
    on, folder, out = criteria.rules()["format"], os.path.join(root, criteria.folder_of(root)), []
    readme, home = read(os.path.join(root, "README.md")) or "", read(os.path.join(folder, "Home.md"))
    if "home" in on and home is not None:
        existing = {name[:-3] for name in os.listdir(folder) if name.endswith(".md")}
        out += pageformat.home(home, names, existing, readme, repo_of(root, home), topics_of(root))
    if "frontdoor" in on and names:
        out += pageformat.frontdoor(readme, names)
    return out


def test_slug(name):
    return re.sub(r"[^a-z0-9-]", "-", name.lower())


def plain(row, ran):
    """The fields tests.py would give if missing: test, kind, guards, checks, runs, result, seen."""
    status, day = ran.get(row[0], ("not run", ""))[:2]
    guard = row[7] if row[6] == "defect" else row[3]
    return [row[0], row[6] if row[6] in ("defect", "workflow") else "requirement", guard or "-", row[5] or "-", row[1], (status + " " + day).strip(),
            row[4] if re.match(r"^\d{4}-\d\d-\d\d$", row[4]) else "no"]


def tests_table(ids, linked, defects, rows, fields, ran):
    """A feature page's Tests: one TESTS table in three parts: each requirement's rows (a 'not enforced' row when none
    passes), then the workflow tests (REG-1), then the defect tests, each in requirement order. `fields(row)` is
    tests.py's format for a row."""
    out, flows = [], []
    for key, _ in ids:
        names = linked.get(key, [])
        for name in names:
            (flows if rows[name][6] == "workflow" else out).append(fields(rows[name]))
        if not any(ran.get(name, ("",))[0] == "PASS" for name in names):
            out.append(["-", "requirement", key, "no passing test", "", "not enforced"])
    out += flows + [fields(rows[name]) for key, _ in ids for name in defects.get(key, [])]
    shown = [[x[0] if x[0] == "-" else "[%s](Tests#t-%s)" % (x[0], test_slug(x[0])), x[1], x[2],
              x[3] if x[0] == "-" else (x[3] if SCENARIO.match(x[3]) else x[3] + " (not yet Given/When/Then)"), x[5]] for x in out]
    return pageformat.table(TESTS, shown) if shown else []


def run_cell(value, repo, day="", flow="regression.yml"):
    """A URL is its Actions run; an empty cell, that day's CI runs; an old sha, its commit; else local."""
    if re.match(r"^https?://\S+$", value):
        return "[run](%s)" % value
    if re.match(r"^[0-9a-f]{7,40}$", value):
        return "[%s](https://github.com/%s/commit/%s)" % (value[:7], repo, value) if repo else value[:7]
    if not value and repo and re.match(r"^\d{4}-\d\d-\d\d$", day):
        return "[CI %s](https://github.com/%s/actions/workflows/%s?query=created%%3A%s)" % (day, repo, flow, day)
    return "local"


def full_page(groups, runs, repo, flow="regression.yml"):
    """docs/wiki/Tests.md: the marker, '# Tests', then per feature '## <Feature>' and a FULL table whose first cell
    carries the anchor feature pages link to. `groups` is tests.py's entries(); `runs` maps a row to its run."""
    out = [pageformat.MARKER, "# Tests", ""]
    for feature, lines in groups:
        rows = []
        for x in lines:
            result = re.match(r"^(\S+) (\d{4}-\d\d-\d\d)$", x[5])
            guard = x[2].split(": ", 1)[0] if x[1] == "requirement" else x[2]
            rows.append(['<a id="t-%s"></a>%s' % (test_slug(x[0]), x[0]), x[1], guard, result.group(1) if result else x[5],
                         result.group(2) if result else "-", run_cell(runs.get(x[0], ""), repo,
                         result.group(2) if result else "", flow), x[6]])
        out += ["## " + feature, ""] + pageformat.table(FULL, rows) + [""]
    return "\n".join(out if groups else out + ["No tests yet.", ""])


def clashes(names):
    """Row ids whose anchors collide, as 'a and b share t-x'."""
    seen, out = {}, []
    for name in names:
        key = test_slug(name)
        if key in seen and seen[key] != name:
            out.append("%s and %s share t-%s" % (seen[key], name, key))
        seen.setdefault(key, name)
    return out


# --- the Settings and Automation blocks on Home, and the README's template line
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
    """[(name, default, meaning)] from `settings.py reference`, the repo settings table; [] if unreadable."""
    path = os.path.join(SKILLS, "workflow-setup", "scripts", "settings.py")
    done = subprocess.run([sys.executable, path, "reference"], capture_output=True, text=True) if os.path.exists(path) else None
    rows, on = [], False
    for line in (done.stdout.splitlines() if done and done.returncode == 0 else []):
        if line.startswith("## "):
            on = line.strip() == "## Repo settings"
        found = re.match(r"^\| `(\w+)` \| (.+?) \| (.+) \|$", line) if on else None
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
    head = ["Name", "What it means", "How to set it", "Default", "This repo"]
    body = pageformat.table(head, rows) if rows else ["The settings reference is not installed here."]
    return "\n".join(["<!-- settings:begin -->", "## Settings", "",
                       "Every repo setting from the template's settings reference, with this repo's value from `.loop/config.json`.", ""]
                      + body + ["<!-- settings:end -->", ""])


def template_line(root):
    repo = config_of(root).get("template_repo")
    if not repo:
        done = subprocess.run(["git", "-C", SKILLS, "remote", "get-url", "origin"], capture_output=True, text=True)
        repo = pageformat.owner_repo(done.stdout) if done.returncode == 0 else ""
    repo = repo if repo and re.match(r"^[\w.-]+/[\w.-]+$", str(repo)) else TEMPLATE_REPO
    return "<!-- template:begin -->\nBuilt with the [%s](https://github.com/%s) workflow loop.\n<!-- template:end -->\n" % (repo, repo)


def with_blocks(text, blocks, insert=False):
    """text with each (name, block) replaced; with insert a missing one is added (template: after paragraph 1)."""
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
    """[(rel, blocks)] for the README and Home if they exist; only a DOC-4 Home gets new blocks."""
    out, home = [], os.path.join(criteria.folder_of(root), "Home.md")
    text = read(os.path.join(root, home)) or ""
    both = [("settings", settings_block(root)), ("automation", counting.automation_block(root))]
    if re.search(r"^## Features\s*$", text, re.M) or (block_re("settings").search(text) and not insert):
        out.append((home, both))
    if os.path.exists(os.path.join(root, "README.md")):
        out.append(("README.md", [("template", template_line(root))] + both))
    return out


def refresh(root, check=False, insert=False):
    """Write the blocks (check: only list): [(rel, name)] stale; a missing one only with insert."""
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
    """(STALE, Settings|Automation|README line, where and fix) for each block differing from a fresh render."""
    names = {"settings": "Settings", "automation": "Automation", "template": "README line", "topics": "Topics"}
    return [("STALE", names[name], "%s differs from a fresh render. Fix: /workflow-docs render" % where) for where, name in refresh(root, True)]


def perm_wiki_page(root, page):
    try:
        folder = __import__("docs").wiki_dir(root)
    except SystemExit:
        folder = "docs/wiki"
    try:
        with open(os.path.join(root, folder, page + ".md"), encoding="utf-8-sig") as handle:
            return handle.read().splitlines()
    except OSError:
        return []


def perm_needs(root, routine, page):
    """The (tool, text) pairs the Runbook's Steps and Full run name: a backticked command starting with a program,
    each https host as a WebFetch domain."""
    lines, inside, field, found = perm_wiki_page(root, page), False, "", []
    for line in lines:
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
    """({id: text}, owned, {id: sha8 agreed}) of a PRD's repo copy; owned unless another file is there (never touched)."""
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().replace("\r\n", "\n").split("\n")
    except OSError:
        return {}, True, {}
    try:
        with open(path[:-3] + ".base", encoding="utf-8") as handle:
            agreed = dict(x.split("\t") for x in handle.read().split("\n") if "\t" in x)
    except OSError:
        agreed = {}
    return {m.group(1): m.group(2) for m in (re.match(r"- ([A-Z]{2,5}-\d+): (.*)$", x) for x in lines) if m}, lines[0] == criteria.SYNC_MARK, agreed


if __name__ == "__main__":
    sys.argv[1:] in (["blocks"], ["--help"]) or sys.exit("usage: render.py blocks")
    if sys.argv[1:] == ["--help"]:
        sys.exit(print("usage: render.py blocks"))
    top = criteria.git("rev-parse", "--show-toplevel")
    print("\n".join("WROTE %s (%s block)" % x for x in (refresh(top, insert=True) if config_of(top).get("criteria") else [])) or "BLOCKS OK")
