#!/usr/bin/env python3
"""The numbers the docs state that the repo can check: skills, feature pages, a page's criteria and tests.

docs.py check, audit and publish call counts() through docs.counts(root). prose() is the text a reader sees: no fenced
or indented code, comments or code spans. At the end, moved here unchanged: docs.py's page map, render.py's cadence,
config_of, entries and automation_block, and real() (drops block-only commits).
"""
import ast
import fnmatch
import glob
import json
import os
import re
import subprocess
import sys

import criteria
import pageformat as pf

os.environ["GIT_TERMINAL_PROMPT"] = "0"  # no terminal: criteria (imported above) sets the rest, stdin included

WORDS = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
NOUNS = {"skill": "skill", "skills": "skill", "feature page": "page", "feature pages": "page", "criterion": "criteria",
         "criteria": "criteria", "test": "test", "tests": "test"}
# One word may sit between number and noun only if it means "all of them" ("eight workflow-ready skills"); any other
# ("two delivery skills") is a label, so nothing is read; "defect" is the one part read ("2 defect tests").
ALL = r"workflow(?:-ready)?|installed|available|bundled|shipped|listed|defect"
CLAIM = re.compile(r"(?<![-\w.,/#])(\d+|%s)[ \t]+(?:(%s)[ \t]+)?(skills?|feature pages?|criteri(?:on|a)|tests?)\b"
                   % ("|".join(WORDS), ALL), re.I | re.ASCII)
FENCE = re.compile(r"^ {0,3}(`{3,}(?=[^`]*$)|~{3,})(.*)$")
QUOTE = re.compile(r"^(?: {0,3}> ?)+")
BREAK = re.compile(r"^ {0,3}([-*_])(?: *\1){2,} *$")  # a thematic break, not an item
ITEM = re.compile(r"^( *)([-*+]|\d{1,9}[.)])( +(?=\S)|\s*$)")
NOT_A_COUNT = "<!-- not-a-count -->"
BOUND = re.compile(r"\b(up to|at most|at least|no more than|more than|fewer than|over|under)\s*$", re.I)
ID = re.compile(r"\b[A-Z]{2,5}-\d+\b")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def prose(text):
    """Prose lines as a reader sees them: no fenced or indented code, comments or code spans; None if a fence never
    closes. Indented code is CommonMark's: four columns past the list item's text (or margin), after a blank line; it
    stays an empty line, keeping paragraphs apart."""
    lines, fence, comment, blank, code, column = [], None, False, True, False, None
    for raw in text.splitlines():
        line = QUOTE.sub("", raw)
        was_blank, blank = blank, not line.strip()
        opener = FENCE.match(line)
        if fence is not None:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence) and not opener.group(2).strip():
                fence, blank = None, True
            continue
        flat = line.expandtabs(4)
        indent = len(flat) - len(flat.lstrip(" "))
        if not blank and not comment:
            code = indent >= (column or 0) + 4 and (was_blank or code)
            if code:
                lines.append("")
                continue
            rule = BREAK.match(flat)
            item = None if rule else ITEM.match(flat)
            if rule and indent < 4:
                column = None
            elif item and indent < (column or 0) + 4:
                gap = len(item.group(3)) if flat[item.end():].strip() else 0
                column = len(item.group(1) + item.group(2)) + (gap if 0 < gap <= 4 else 1)
            elif indent == 0 and (was_blank or opener or re.match(r"[#|]", flat)):
                column = None
        if opener and not comment:
            fence, code = opener.group(1), False
            continue
        line = re.sub(r"(`+)(?!`).*?(?<!`)\1(?!`)", "", line)
        marked = NOT_A_COUNT in line
        if comment:
            end = line.find("-->")
            comment, line = (True, "") if end < 0 else (False, line[end + 3:])
        line = re.sub(r"<!--.*?-->", "", line)
        if "<!--" in line:
            comment, line = True, line[:line.index("<!--")]
        lines.append(line + (" " + NOT_A_COUNT if marked else ""))
        blank = blank or bool(re.match(r" {0,3}#{1,6}(\s|$)", flat))
    return lines if fence is None else None


def text_of(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def counts(root, folder, rows, on):
    """Checkable numbers the docs state, as (COUNT, file, detail) rows. `folder`: wiki folder, `rows`: page map (.loop/docs.tsv),
    `on`: criteria setting."""
    top = os.path.realpath(root) + os.sep
    skills = len(glob.glob(os.path.join(root, "skills", "*", "SKILL.md")))
    wiki = os.path.join(root, folder)
    pages = [p for p in rows if p != "Home" and p not in pf.GENERATED and os.path.exists(os.path.join(wiki, p + ".md"))
             and not pf.is_guide(text_of(os.path.join(wiki, p + ".md")))]
    linked = criteria.test_rows(root)[0] if on else {}
    defects = criteria.defect_rows(root) if on else {}
    names = ["README.md"]
    if os.path.isdir(wiki):
        names += ["%s/%s" % (folder, n) for n in sorted(os.listdir(wiki)) if n.endswith(".md") and n[:-3] not in pf.GENERATED]
    names += sorted(os.path.relpath(n, root) for n in glob.glob(os.path.join(root, "skills", "*.md")))
    texts, ids = {}, {}
    for rel in names:
        full = os.path.realpath(os.path.join(root, rel))
        if full.startswith(top) and os.path.isfile(full):  # regular files in the repo
            texts[rel] = text_of(full)
            page = os.path.basename(rel)[:-3] if rel.startswith(folder + "/") else ""
            if on and page in pages:
                part, keep = [], False  # Requirements section
                for line in prose(texts[rel]) or []:
                    keep = bool(re.match(r"##\s+(Requirements|Criteria)\s*$", line)) or (keep and not line.startswith("## "))
                    part += [line] if keep else []
                ids[rel] = [m.group(1) for _, m in criteria.criteria_of(part) if m]
    known = {i for f in ids.values() for i in f}
    found = []
    for rel, text in texts.items():
        lines = prose(text)
        if lines is None:
            found.append(("COUNT", rel, "a code fence never closes, so its counts can't be read"))
            continue
        mine = ids.get(rel)
        own = set(mine or [])
        real = {"skill": skills or None, "page": len(pages) if on else None}
        if mine is not None:
            real.update(criteria=len(mine), defect=sum(len(defects.get(i, [])) for i in mine),
                        test=sum(len(linked.get(i, [])) + len(defects.get(i, [])) for i in mine))
        # A line naming this file's own criterion is skipped; one naming another page's still has its skills and pages
        # counts read; its criteria and tests counts are about that one.
        alone = lambda s: NOT_A_COUNT in s or own.intersection(ID.findall(s))
        other = lambda s: known.intersection(ID.findall(s))
        paras = []
        for line in lines:  # soft-wrapped lines joined; skipped ones alone
            new = not paras or not line.strip() or re.match(r"\s*([|#]|$)", paras[-1]) or re.match(r"\s*([-*+|#>]|\d+\.)", line) or any(f(x) for f in (alone, other) for x in (line, paras[-1]))
            paras.append(line) if new else paras.__setitem__(-1, paras[-1] + " " + line.strip())
        for line in paras:
            if alone(line):
                continue
            for match in CLAIM.finditer(line):
                said, word, noun = match.group(1).lower(), (match.group(2) or "").lower(), match.group(3).lower()
                if BOUND.search(line[:match.start()]) or said == "one":  # a limit ("up to 6"), or "a single test"
                    continue
                said = int(said) if said.isdigit() else WORDS.index(said) + 1
                if said != 1 and noun in ("skill", "feature page", "test", "criterion"):
                    continue  # "two test doubles"
                kind = NOUNS[noun]
                if word == "defect":
                    kind = "defect" if kind == "test" else ""
                want = None if kind in ("criteria", "test", "defect") and other(line) else real.get(kind)
                if want is not None and said != want:
                    found.append(("COUNT", rel, "says %s, the repo has %d" % (match.group(0), want)))
    return found


# docs.py's page map, moved here (size).
def map_path(root):
    return os.path.join(root, ".loop", "docs.tsv")


def map_rows(root):
    try:
        with open(map_path(root)) as fh:
            return [line.rstrip("\n").split("\t") + ["", ""] for line in fh if line.strip() and line[0] != "#"]
    except OSError:
        return []


def read_map(root):
    return {r[0]: [item.strip() for item in r[1].split(",") if item.strip()] for r in map_rows(root)}


def sources(root):
    """docs.tsv's optional third column: a page's PRD source (`url:<link>`, `mcp:<server>:<resource>`, or `page`)."""
    return {r[0]: s for r in map_rows(root) if (s := r[2].strip())}


def write_map(root, rows):
    held = sources(root)
    os.makedirs(os.path.dirname(map_path(root)), exist_ok=True)
    with open(map_path(root), "w") as fh:
        fh.write("# page<TAB>paths it describes, comma separated\n")
        for page in sorted(rows):
            fh.write("\t".join([page, ",".join(rows[page])] + ([held[page]] if page in held else [])) + "\n")


BLOCK = re.compile(r"<!-- (settings|automation|template):begin -->\n.*?<!-- \1:end -->\n", re.S)


def code_only(root, sha, files):
    """True when every file the commit changed is Python with the same syntax tree before and after, docstrings aside (#3122)."""
    def tree(ref, rel):
        try:
            node = ast.parse(git(root, "show", ref + ":" + rel).stdout)
        except (SyntaxError, ValueError):
            return None
        for n in ast.walk(node):
            body = getattr(n, "body", None)
            if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0].value, "value", None), str):
                body[:] = body[1:] or [ast.Pass()]
        return ast.dump(node)
    return bool(files) and all(f.endswith(".py") and tree(sha + "^", f) is not None and tree(sha + "^", f) == tree(sha, f) for f in files)


def real(root, changed, paths):
    """changed ('<sha> <subject>' lines) without the commits whose change to paths lies only inside the generated
    blocks of README.md or a Home.md: a block refresh says nothing about the pages mapped there."""
    if not changed:
        return changed
    names, shas = {}, [c.split()[0] for c in changed]  # one git call for all commits
    for chunk in git(root, "log", "--no-walk=unsorted", "--no-renames", "--format=%x01%h", "--name-only",
                     *shas, "--", *paths).stdout.split("\x01")[1:]:
        sha, *files = chunk.strip("\n").split("\n")
        names[sha] = [f for f in files if f]

    def blocks_only(sha, rel):
        old, new = git(root, "show", sha + "^:" + rel), git(root, "show", sha + ":" + rel)
        bare = lambda t: re.sub(r"\n{3,}", "\n\n", BLOCK.sub("", t)).strip()
        return not old.returncode and not new.returncode and bare(old.stdout) == bare(new.stdout)

    return [c for c, s in zip(changed, shas) if not (names.get(s) and (all(
        os.path.basename(rel) in ("README.md", "Home.md") and blocks_only(s, rel) for rel in names[s]) or code_only(root, s, names[s])))]


def cadence(cron):
    if cron == "off":
        return "off"
    f = cron.split()
    if len(f) == 5 and f[2:] == ["*", "*", "*"]:
        step = lambda x: x[2:] if x.startswith("*/") and x[2:].isdigit() else ""
        if step(f[1]):
            return "every %s hours" % step(f[1])
        if f[0].isdigit() and f[1].isdigit():
            return "daily at %02d:%02d" % (int(f[1]), int(f[0]))
        if f[1] == "*" and step(f[0]):
            return "every %s minutes" % step(f[0])
    return "cron `%s`" % cron


def config_of(root):
    try:
        with open(os.path.join(root, ".loop", "config.json")) as fh:
            held = json.load(fh)
        return held if isinstance(held, dict) else {}
    except (OSError, ValueError):
        return {}


BUILT_IN = (("health", "Checks the repo and files each finding.", "health_cron", "47 */4 * * *", "local:schedule"),
            ("regression", "Runs every regression row, files each failure.", "regression_cron", "17 */4 * * *", "github:regression.yml"),
            ("digest email", "Mails one digest per health round.", None, "", "local:schedule"))


def entries(root):
    """Built-in routines, then config's `automation` entries {name, does, cadence, runs: github:FILE | mac:LABEL |
    claude:TASK, enabled?, last_run?}; a same-named one replaces the built-in."""
    cfg, out = config_of(root), []
    for name, does, key, default, flow in BUILT_IN:
        mail = str(cfg.get("digest_mail", "cloudflare"))
        cron = "with each health round" if key is None else str(cfg.get(key, default))
        out.append({"name": name, "does": does, "cadence": cron, "runs": flow,
                    "enabled": mail != "off" if key is None else cron != "off"})
    for item in cfg.get("automation") or []:
        if isinstance(item, dict) and item.get("name"):
            out = [e for e in out if e["name"] != item["name"]] + [item]
    return out


def runbook_link(root, entry, wiki):
    """The wiki link to an entry's Runbook: its `runbook` key, else the .loop/routines.tsv routine named like it
    (health -> health-round); '' if none or no GitHub origin."""
    try:
        with open(os.path.join(root, ".loop", "routines.tsv"), encoding="utf-8") as fh:
            held = [line.split("\t")[:2] for line in fh if line.strip() and line[0] != "#" and "\t" in line]
    except OSError:
        return ""
    name = str(entry.get("runbook") or entry["name"])
    for routine, page in held:
        if wiki and (routine == name or routine.startswith(name + "-")):
            return "[%s](%s/%s#%s)" % (entry["name"], wiki, page.strip(), routine)
    return ""


def automation_block(root):
    rows = []
    origin = git(root, "remote", "get-url", "origin")
    slug = pf.owner_repo(origin.stdout) if origin.returncode == 0 else ""
    wiki = "https://github.com/%s/wiki" % slug if slug else ""
    for e in entries(root):
        kind, _, target = str(e.get("runs", "")).partition(":")
        on = e.get("enabled", True) is not False and str(e.get("cadence")) != "off"
        last, owed = str(e.get("last_run") or "docs.py automation"), "none"  # no live time: it would change every run
        if kind == "local":
            where, state = "this Mac's local schedule", "on" if on else "off"
        elif kind == "github":
            there = os.path.exists(os.path.join(root, ".github", "workflows", target))
            where, state = ("GitHub Actions (%s)" % target) if there else "not deployed", "on" if on and there else "off"
            owed = "run workflow-setup to write .github/workflows/" + target if on and not there else owed
        elif kind in ("mac", "claude"):
            where = "this Mac (launch agent %s)" % target if kind == "mac" else "Claude scheduled task %s" % target
            state, owed = "on (declared)" if on else "off (declared)", "confirm it is live: docs.py automation"
        else:
            where, state, owed = "not set", "off", 'add "runs": github:FILE, mac:LABEL or claude:TASK'
        if e["name"] == "digest email" and on and owed == "none":
            owed = "set the digest address and keys in the schedule's mail.env on the Mac (yours, outside git)"
        rows.append([runbook_link(root, e, wiki) or str(e["name"]), str(e.get("does", "")), state, cadence(str(e.get("cadence", ""))), where, last, owed])
    return "\n".join(["<!-- automation:begin -->", "## Automation", "",
                       "Health and regression, then each `automation` entry in `.loop/config.json`; to add one, add an entry.", ""] + pf.table(["Routine", "What it does", "State", "Cadence", "Runs on", "Last run", "Owed by you"], rows) + ["<!-- automation:end -->", ""])


# AUT-9: the permission rows a repo declares (audit.py permissions)
PERM_PROGRAMS = ("python3", "python", "gh", "git", "claude", "curl", "node")
PERM_PRIVATE = re.compile(r"(/Users/|/home/[A-Za-z]|[A-Za-z]:[\\/]+Users|\bsk-[A-Za-z0-9]{8}|\bghp_|\bxox[bp]-)")
PERM_FIELD = re.compile(r"^- \*\*([A-Za-z ]+):\*\*\s*(.*)$")


def perm_root_of(repo):
    return git(repo or ".", "rev-parse", "--show-toplevel").stdout.strip() or os.path.abspath(repo or ".")


def perm_rows(path):
    """The (line number, fields) of a tab file, comments and blanks skipped; [] if absent."""
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return [(n, line.rstrip("\r\n").split("\t")) for n, line in enumerate(fh, 1)
                    if line.strip() and not line.lstrip().startswith("#")]
    except OSError:
        return []


def perm_declared(root):
    """{routine: [(kind, rule, why)]} and the file's problems."""
    out, bad = {}, []
    for number, row in perm_rows(os.path.join(root, ".loop", "permissions.tsv")):
        routine, kind, rule = (row + ["", "", ""])[:3]
        if kind not in ("allow", "deny") or not routine or not re.match(r"^[A-Za-z]+\(.+\)$", rule):
            bad.append("BAD ROW permissions.tsv:%d (routine<TAB>allow|deny<TAB>Tool(spec)<TAB>why)" % number)
        elif PERM_PRIVATE.search(rule) or os.path.expanduser("~") in rule:
            bad.append("PRIVATE ROW permissions.tsv:%d holds a home path, a user name or a token: write it with ~ or a glob" % number)
        else:
            out.setdefault(routine, []).append((kind, rule, row[3] if len(row) > 3 else ""))
    return out, bad


def perm_matches(rule, tool, text):
    """Does rule `Tool(spec)` cover `text` for that tool: a prefix rule `x:*`, else a glob."""
    found = re.match(r"^([A-Za-z]+)\((.*)\)$", rule)
    if not found or found.group(1) != tool:
        return False
    spec = found.group(2)
    return text == spec[:-2] or text.startswith(spec[:-2] + " ") if spec.endswith(":*") else fnmatch.fnmatchcase(text, spec)


def ledger(root, rows=None):
    """The posted deltas {PAGE:ID: [side, issue, commented 1/0, sha8]} in <git common dir>/loop/deltas.tsv."""
    folder = os.path.join(os.path.abspath(criteria.git("rev-parse", "--git-common-dir", check=False) or os.path.join(root, ".git")), "loop")
    path = os.path.join(folder, "deltas.tsv")
    if rows is not None:
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("".join("\t".join([k] + v) + "\n" for k, v in sorted(rows.items())))
    try:
        with open(path, encoding="utf-8") as fh:
            return {r[0]: r[1:] for r in (x.rstrip("\n").split("\t") for x in fh) if len(r) == 5}
    except OSError:
        return {}
