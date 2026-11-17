#!/usr/bin/env python3
"""The optional Deployments section of a feature page (DOC-14): a Page table and/or a Delivery table, nothing else.
commands.md's rules block names the section, headers and Access words, and each column's rule. Pure: lines in, FORMAT
findings out (pageformat.bad's shape); a secret-bearing value is never echoed: links read <link>, addresses <address>.
The live-link and promoted-build check runs in the deploying repo. criteria.py's page rules (rules, criteria_max, SHEET)
sit at the end, moved here unchanged.
"""
import json
import os
import re
import sys

import pageformat as pf
from pageformat import RULE, bad, short, tables

PAGE_COLS = ("Page", "Link", "Access", "Shows", "Live build")
DELIVERY_COLS = ("Delivery", "Channel", "Recipients", "What's sent", "Status")
URL = re.compile(r"^https://[^\s@/?#;]+(/[^\s?#;]*)?(\?[^\s#=]*)?(#[^\s=]*)?$")  # no user, no key=value
SHA = re.compile(r"^`[0-9a-f]{7,40}`$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)*")


def slurp(path):
    with open(path) as handle:
        return handle.read()


def deployments(page, name, lines, page_cols=PAGE_COLS, delivery_cols=DELIVERY_COLS, access=("public", "sign-in")):
    """DOC-14: a Page table and/or a Delivery table, nothing else."""
    hide = lambda text: short(re.sub(r"\S*://\S*", "<link>", EMAIL.sub("<address>", str(text))))
    fail = lambda number, *rest: bad(page, number, name, 14, *rest)
    runs, other = tables(lines)
    text = dict(lines)
    found = []
    for number, header, rows in runs:
        found.append([number, header, [], bool(RULE.match(text.get(number + 1, "").strip()))])
        for row_no, row in rows:
            if tuple(row) in (tuple(page_cols), tuple(delivery_cols)):
                found.append([row_no, row, [], False])
            elif all(re.match(r"^:?-+:?$", c) for c in row) and not found[-1][2] and not found[-1][3]:
                found[-1][3] = True
            else:
                found[-1][2].append((row_no, row))
    fix_head = "use '%s' or '%s'" % (" | ".join(page_cols), " | ".join(delivery_cols))
    out = [fail(number, "only a Page table, a Delivery table and blank lines", hide(line), "remove it")
           for number, line in other]
    if not found and not other:
        out.append(fail(lines[0][0] if lines else 1, "a Page or Delivery table with at least one row",
                       "an empty section", "add a table, or remove the section"))
    seen = set()
    for number, header, rows, ruled in found:
        kind = "Page" if tuple(header) == tuple(page_cols) else "Delivery" if tuple(header) == tuple(delivery_cols) else ""
        if not kind:
            out.append(fail(number, "a table header of exactly the Page or Delivery columns", hide(" | ".join(header)), fix_head))
            continue
        if kind in seen:
            out.append(fail(number, "at most one %s table" % kind, "a second one", "merge its rows into the first"))
        seen.add(kind)
        if not ruled:
            out.append(fail(number, "a separator row under the %s header" % kind, "none", "add |---|---|---|---|---|"))
        if not rows:
            out.append(fail(number, "at least one row in the %s table" % kind, "none", "add a row, or remove the table"))
        cols = page_cols if kind == "Page" else delivery_cols
        for row_no, row in rows:
            if len(row) != len(cols):
                out.append(fail(row_no, "%d cells in each %s row" % (len(cols), kind), len(row),
                               "one cell per column; escape a | inside a cell as \\|"))
                continue
            cell = dict(zip(cols, row))
            empty = [c for c in cols if not cell[c]]
            if empty:
                out.append(fail(row_no, "every %s cell filled" % kind, "empty %s" % ", ".join(empty), "fill it"))
            elif kind == "Page":
                if not URL.match(cell[cols[1]]):
                    out.append(fail(row_no, "Page Link a full https URL with no user, password or token", "another link",
                                   "give the plain https:// link"))
                if cell[cols[2]] not in access:
                    out.append(fail(row_no, "Page Access %s" % " or ".join(access), hide(cell[cols[2]]),
                                   "say who can open it: %s" % " or ".join(access)))
                if not SHA.match(cell[cols[4]]):
                    out.append(fail(row_no, "Page Live build a 7 to 40 hex sha in backticks", hide(cell[cols[4]]),
                                   "write the sha from the page's build.txt in backticks"))
            elif any(EMAIL.search(c) for c in row):
                out.append(fail(row_no, "Delivery Recipients a group, never an address", "an email address",
                               "name the group instead"))
    return out


# The page rules of criteria.py, moved here unchanged; criteria.py imports them back.
CRITERIA_MAX_DEFAULT = 10
SHEET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "commands.md")


def howto_book(root, folder, page, name):
    """The Runbook(s) section's lines on the feature's How-to-use page: where a routine's runbook may live (DOC-16, DOC-18)."""
    try:
        text = slurp(os.path.join(root, folder, HOWTO + page + ".md"))
    except OSError:
        return []
    return next((lines for n, _, lines in pf.parts(text) if n in (name, name + "s")), [])


def howto_runbook(root, page, rule, book):
    """#4666: a How-to-use page's Runbooks take the DOC-16 routine shape only for a routine the repo schedules on that page."""
    try:
        pages = {row[1] for _, row in registry(root) if len(row) > 1}
    except OSError:
        pages = set()
    return pf.runbook(HOWTO + page, rule["runbook"], book, rule["fields"]) if page in pages | {p for _, p, _ in custom(root)} else []


def has_runbook(books, page, routine):
    return any(line.rstrip() == "### " + routine for _, line in books[page])


def no_runbook(page, name, routine, source):
    return bad(page, 1, name, 16, "a '### %s' runbook, the routine %s gives this page" % (routine, source), "none",
               "add the Runbook section with '### %s' and its fields" % routine)


def registry(root):
    """The numbered, tab-split rows of .loop/routines.tsv, without comments."""
    with open(os.path.join(root, ".loop", "routines.tsv"), encoding="utf-8-sig") as handle:
        return [(n, line.rstrip("\n").split("\t")) for n, line in enumerate(handle, 1) if line.strip() and not line.lstrip().startswith("#")]


def owed(root, books, name):
    """DOC-16: every routine in .loop/routines.tsv (`routine<TAB>page`, # lines are comments) and each own routine of the
    config's `automation` list (custom) has its '### routine' runbook on its page. `books` maps each page to its Runbook
    section's lines ([] when none). No file, no registry."""
    out = []
    try:
        rows = registry(root)
    except FileNotFoundError:
        rows = []
    except (OSError, ValueError) as error:
        return [bad("routines.tsv", 1, "Runbook", 16, "a readable routine registry", short(getattr(error, "strerror", None) or "not UTF-8 text"), "fix .loop/routines.tsv")]
    seen = set()
    for number, row in rows:
        routine, page = (row + ["", ""])[:2]
        if routine in seen:
            out.append(bad("routines.tsv", number, "Runbook", 16, "each routine once", short(routine), "remove the duplicate row"))
        seen.add(routine)
        if page not in books:
            out.append(bad("routines.tsv", number, "Runbook", 16, "a routine on a feature page", short(routine), "name a page from .loop/docs.tsv in .loop/routines.tsv"))
        elif not has_runbook(books, page, routine):
            out.append(no_runbook(page, name, routine, ".loop/routines.tsv"))
    return out + custom_owed(root, books, name, seen)


BUILT_IN = ("health", "regression", "digest email")
POINTER = "In %s, fast-forward to origin/main, then read %s's Runbook section %s and follow it exactly."


def custom(root):
    """(routine, page, runs) per non-built-in `automation` entry of .loop/config.json: "page" owns its Runbook, "routine"
    names the '### ' heading (default its name)."""
    try:
        with open(os.path.join(root, ".loop", "config.json")) as handle:
            items = json.load(handle).get("automation")
    except (OSError, ValueError, AttributeError):
        return []
    return [(str(e.get("routine") or e["name"]), str(e.get("page") or ""), str(e.get("runs") or "")) for e in items or []
            if isinstance(e, dict) and e.get("name") and e["name"] not in BUILT_IN]


def custom_owed(root, books, name, seen):
    """DOC-16 for the config's own routines: each names a page with its '### routine' runbook."""
    out = []
    for routine, page, _ in custom(root):
        if routine in seen:
            out.append(bad("config.json", 1, "Runbook", 16, "each routine once", short(routine), "remove or rename the duplicate automation entry"))
        seen.add(routine)
        if page not in books:
            out.append(bad("config.json", 1, "Runbook", 16, "a feature page for the routine", short(routine),
                           'add "page": "<Page>" (a page from .loop/docs.tsv) to its automation entry'))
        elif not has_runbook(books, page, routine):
            out.append(no_runbook(page, name, routine, "the config's automation entry"))
    return out


def prompts(root, repo, wiki_dir="docs/wiki"):
    """(routine, line) per routine, routines.tsv first then the config's own: the one-line prompt a scheduler holds."""
    pairs = []
    try:
        pairs = [tuple((row + [""])[:2]) for _, row in registry(root)]
    except (OSError, ValueError):
        pass
    pairs += [(r, p) for r, p, _ in custom(root)]
    return [(r, POINTER % (repo, "%s/%s.md" % (wiki_dir, p), r)) for r, p in pairs if p]


def unserved(books, seen, name):
    """DOC-16: each routine's Serves field (continuation lines too) names requirement ids, each on some page."""
    out = []
    for page, lines in books.items():
        fields, cur = [], None
        for number, line in lines:
            head = re.match(r"^- \*\*Serves:\*\*(.*)$", line)
            if head:
                cur = [number, head.group(1)]
                fields.append(cur)
            elif line.startswith(("- ", "#")):
                cur = None
            elif line[:1].isspace() and cur:
                cur[1] += " " + line.strip()
        for number, text in fields:
            ids = re.findall(r"[A-Z]{2,5}-\d+", text)
            if not ids:
                out.append(bad(page, number, name, 16, "a Serves field naming a requirement id such as DOC-14", short(text), "name the ids the routine serves"))
            for key in ids:
                if key not in seen:
                    out.append(bad(page, number, name, 16, "a Serves id that a page defines", key, "name a requirement from a feature page"))
    return out


def rules():
    """The page rules from the template sheet's rules block; refuses when it is missing or incomplete."""
    try:
        with open(SHEET) as handle:
            block = re.search(r"^```rules\n(.*?)^```", handle.read(), re.M | re.S)
        found = {k.strip(): v.strip() for k, v in (x.split(":", 1) for x in block.group(1).splitlines() if ":" in x)}
        listed = lambda key, default: [x.strip() for x in found.get(key, default).split(",") if x.strip()]
        on = listed("format", ",".join(pf.CHECKS))
        if set(on) - set(pf.CHECKS):
            raise ValueError
        return {"sections": listed("sections", found["sections"]), "problem_lines": int(found["problem_lines"]),
                "metrics_lines": int(found["metrics_lines"]), "usage": found.get("usage_section", "Usage"),
                "review": found["review_line"], "milestone": found["milestone_line"], "format": on,
                "banned": listed("problem_banned", pf.BANNED),
                "groups": listed("requirement_groups", ", ".join(pf.GROUPS)),
                "runbook": found.get("runbook_section", "Runbook"),
                "fields": listed("runbook_fields", "Serves, Schedule, Steps, Full run, Output, Never, Check"),
                "deploy": found.get("deployments_section", "Deployments"), "access": listed("deployments_access", "public, sign-in"),
                "page_cols": listed("deployments_page", ", ".join(PAGE_COLS)),
                "delivery_cols": listed("deployments_delivery", ", ".join(DELIVERY_COLS))}
    except (OSError, AttributeError, KeyError, ValueError):
        sys.exit("REFUSED: the rules block of skills/workflow-docs/references/commands.md is missing or broken.")


def criteria_max(root):
    """`criteria_max` in .loop/config.json, CRITERIA_MAX_DEFAULT when absent. A bad value refuses."""
    path = os.path.join(root, ".loop", "config.json")
    try:
        with open(path) as handle:
            value = json.load(handle).get("criteria_max", CRITERIA_MAX_DEFAULT)
    except (OSError, ValueError, AttributeError):
        value = CRITERIA_MAX_DEFAULT
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 50:
        sys.exit("REFUSED: criteria_max is %r in %s. Fix: set it to a whole number from 1 to 50, or remove it for the default %d."
                 % (value, path, CRITERIA_MAX_DEFAULT))
    return value


# --- the owner's recorded words (criteria.py review|unreview --owner-record ID): sessions.py owner-words writes the
# record in the operation session, never a worker. It counts for its IDs or pages, once per command; reviews.tsv logs
# it as "record ID: TEXT".

def owner_rows(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return [line.rstrip("\n").split("\t") for line in handle]
    except OSError:
        return []


def owner_words(args, git):
    """The record's text, or exit with nothing changed: no such record, an uncovered ID or page, or a record used."""
    common = os.path.join(os.path.abspath(git("rev-parse", "--git-common-dir")), "loop")
    found = [row for row in owner_rows(os.path.join(common, "owner-words.tsv")) if len(row) == 5 and row[0] == args.owner_record]
    if not found:
        sys.exit("REFUSED: no owner-words record %s. Nothing was changed. Fix: the operation session records the owner's "
                 "message with sessions.py owner-words." % args.owner_record)
    record = found[-1]
    left = sorted(set(args.ids) - set(record[4].split(",")))
    if left:
        sys.exit("REFUSED: record %s does not cover %s (it covers %s). Nothing was changed." % (
            args.owner_record, ", ".join(left), record[4]))
    for row in owner_rows(os.path.join(common, "reviews.tsv")):
        if len(row) > 3 and row[1] == args.command and row[3].startswith("record %s:" % args.owner_record):
            sys.exit("REFUSED: record %s was already used for %s. Nothing was changed. Fix: the operation session "
                     "records the owner's message again." % (args.owner_record, args.command))
    return "record %s: %s" % (args.owner_record, " ".join(json.loads(record[3]).split()))


# --- link-form feature pages (DOC-1, DOC-2) and Home's Topic column (DOC-4) ---

LINK = re.compile(r"^PRD:\s*(\S+)\s*$")


def link_of(text, listed=""):
    """Where a link-form page's PRD lives, else None: the docs.tsv source (`url:<link>` or `mcp:<server>:<resource>`; `page`
    or empty means on the page) or the page's own 'PRD: <source>' line before its first section (a bare link is a url)."""
    import prd
    if listed and listed != "page":
        return listed
    found = next((m.group(1) for m in (LINK.match(x.strip()) for x in prd.head(text)) if m), None)
    return found if found is None or found.startswith(("url:", "mcp:")) else "url:" + found


from prdcopy import link_page  # noqa: E402,F401  (moved: the docs check of a page that has a source reads its copy)


UNREAD = set()  # link-form pages whose link could not be read in this run


def linked(root, page, text):
    import counting
    return link_of(text, counting.sources(root).get(page, ""))


def topics_of(root):
    """The `topics` setting as {topic: [pages]}, or {} when none (Home then has no Topic column)."""
    import counting
    topics = counting.config_of(root).get("topics")
    return {str(k): [str(x) for x in v] for k, v in topics.items() if isinstance(v, list)} if isinstance(topics, dict) else {}


def regroup(text, topics):
    """Home's features table with a leading Topic column, rows grouped by topic (setting order, then Other) and by name;
    text unchanged when there is no such table or no topics."""
    lines = text.split("\n")
    start = next((i for i, x in enumerate(lines) if x.startswith("| Feature") or x.startswith("| Topic")), None)
    if not topics or start is None:
        return text
    end = start
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    rows = [r[-4:] for r in map(pf.cells, lines[start + 2:end]) if len(r) in (4, 5)]
    name = lambda r: r[0].strip("[]").split("](")[0]
    order = pf.topic_order(topics)
    rows.sort(key=lambda r: (order.index(pf.topic_of(name(r), topics)), name(r)))
    table = pf.table(("Topic",) + pf.HOME, [[pf.topic_of(name(r), topics)] + r for r in rows])
    return "\n".join(lines[:start] + table + lines[end:])


HOWTO = "How-to-use-"
PARTS = ("What it's for", "How to reach or run it", "URLs and deployments", "Automations and schedules", "Runbooks", "Links")


def mapped(root, rows, folder):
    """rows plus each How-to-use-<Feature> page, mapped to its feature's paths (it has no docs.tsv row, #4542)."""
    out = dict(rows)
    for page, paths in rows.items():
        if page != "Home" and page not in pf.GENERATED and os.path.isfile(os.path.join(root, folder, HOWTO + page + ".md")):
            out.setdefault(HOWTO + page, paths)
    return out


def howto(root, folder, features):
    """DOC-18 trouble as (kind, page, detail): no How-to-use page, one off the skeleton, or a feature page that doesn't link it."""
    found = []
    for page in features:
        name, path = HOWTO + page, os.path.join(root, folder, HOWTO + page + ".md")
        if not os.path.isfile(path):
            found.append(("HOWTO", page, "DOC-18 the feature has no How-to-use page. Fix: write %s/%s.md with the sections %s" % (folder, name, ", ".join(PARTS))))
            continue
        lines = [x.strip() for x in slurp(path).splitlines() if x.strip()]
        heads = [x[3:] for x in lines if x.startswith("## ")]
        if "# " + pf.heading_of(page) not in lines:
            found.append(("HOWTO", name, "DOC-18 the title is '# %s'. Fix: use that title" % pf.heading_of(page)))
        order = [PARTS.index(h) for h in heads if h in PARTS]
        if len(order) != len(heads) or order != sorted(set(order)):
            found.append(("HOWTO", name, "DOC-18 sections are %s, in that order, each once, none other (got %s). Fix: rename, reorder or remove" % (" · ".join(PARTS), short(", ".join(heads)))))
        feature = slurp(os.path.join(root, folder, page + ".md"))
        if not linked(root, page, feature):
            import milestones
            found += milestones.howto_items(name, slurp(path), feature)
        if not linked(root, page, feature) and "How to use: [%s](%s)" % (name, name) not in feature.splitlines():
            found.append(("HOWTO", page, "DOC-18 the page doesn't link its How-to-use page. Fix: add the line 'How to use: [%s](%s)' under its title" % (name, name)))
    return found
