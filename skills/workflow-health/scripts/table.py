"""The findings table (HLT-3): every WARN, FAIL and UNREAD finding on one row, feature first.

Columns: Feature (the docs.tsv page it is about, else Other), Group, Rule, Severity, Finding and Issue (the open health
issue filed for it, `report only` for a rule that is never filed, `not filed`, or `not read` when the issue list was not
read). check prints it after the report's header; file prints it again after filing, with the issues it just opened; the
digest shows the last one in the saved report. Pure formatting apart from reading the issue list issues.py caches.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issues as IS  # noqa: E402
import report as G  # noqa: E402

OTHER = "Other"  # a finding that fits no feature page
HEAD = ("| Feature | Group | Rule | Severity | Finding | Issue |", "|---|---|---|---|---|---|")
BAD = ("FAIL", "UNREAD", "WARN")
MAX_ROWS = 50  # rows the digest shows: its comment stays well under GitHub's size limit
MARK = re.compile(r"<!-- loop-health (.+?)(?: evidence=\w+)?(?: placed=\S*)? -->")


def report_only():
    try:
        import file as F
        return F.REPORT_ONLY
    except Exception:  # file.py not installed beside this one
        return ()


def cell(text):
    return " ".join(str(text or "").split()).replace("|", "\\|")


def filed(root, fresh=False):
    """{marker key: issue number} of the open health issues, or None when the list was not read. Uses the list check
    already read; fresh reads it again (after file has opened issues)."""
    key = (root, "health")
    if fresh:
        IS.CACHE.pop(key, None)
        IS.CACHE.pop((root, "held"), None)
    if key not in IS.CACHE:
        if not fresh:
            return None
        IS.fetch(root, "health")
    found = IS.CACHE.get(key, (None, ""))[0]
    if found is None:
        return None
    out = {}
    for issue in sorted(found, key=lambda one: one["number"]):
        match = MARK.search(issue.get("body") or "")
        if match and IS.is_health(issue):
            out.setdefault(IS.posix(match.group(1)), issue["number"])
    return out


def about(root, item, cache):
    """The page a finding is about. A finding about an issue (#N, as finding-age gives) takes that issue's feature from the
    health list check already read, never a listing of every open issue."""
    subject = str(item.get("subject") or "").strip()
    if subject.startswith("#") and subject[1:].isdigit():
        pages = cache.setdefault("pages", IS.features(root))
        held = (IS.CACHE.get((root, "health")) or (None, ""))[0] or []
        group = next((IS.feature_group(i, pages) for i in held if str(i.get("number")) == subject[1:]), IS.NO_FEATURE)
        return None if group == IS.NO_FEATURE else group
    return IS.feature_of(root, item, cache)


def rows_of(rows, root, numbers):

    """[(feature, group, rule, severity, finding, issue)] sorted by feature (Other last), group order, severity."""
    cache, out, quiet = {}, [], report_only()
    order = {name: n for n, name in enumerate(G.ORDER)}
    for item in rows:
        if item.get("state") not in BAD:
            continue
        try:
            page = about(root, item, cache)
        except Exception:  # an unreadable page map never breaks the report
            page = None
        rule = G.rule_of(item)
        finding = "details stay local" if item["family"] == "mine" else "%s: %s" % (item.get("subject"), item.get("detail"))
        keys = [IS.key_of(item)] + IS.legacy(item)
        number = next((numbers[k] for k in keys if numbers and k in numbers), None)
        issue = "#%d" % number if number else "report only" if item["rule"] in quiet else "not read" if numbers is None else "not filed"
        out.append(((page is None, (page or "").lower(), order.get(item["family"], 99), BAD.index(item["state"])),
                    (page or OTHER, G.TITLE.get(item["family"], item["family"]), rule, item["state"], finding, issue)))
    return [one for _, one in sorted(out, key=lambda pair: pair[0])]


def lines(rows, root, numbers):
    table = rows_of(rows, root, numbers)
    if not table:
        return ["FINDINGS: none"]
    return ["FINDINGS (%d)" % len(table), ""] + list(HEAD) + ["| %s |" % " | ".join(cell(c) for c in one) for one in table] + [""]


def insert(text, rows, root):
    """The report with the findings table after its header (the first two lines)."""
    return text[:2] + [""] + lines(rows, root, filed(root)) + text[2:]


def show(rows, root):
    """After file: the same table, naming the issues it just opened."""
    print("\n".join([""] + lines(rows, root, filed(root, fresh=True))))


def from_report(text, most=MAX_ROWS):
    """The last findings table in a saved report, its first `most` rows and a line naming the rest, or []."""
    lines_in, start = text.splitlines(), None
    for n, line in enumerate(lines_in):
        if line.startswith("FINDINGS"):
            start = n
    if start is None:
        return []
    out = [lines_in[start]]
    for line in lines_in[start + 1:]:
        if not (line.startswith("|") or not line.strip()) or (out[-1].startswith("|") and not line.strip()):
            break
        out.append(line)
    rows = [line for line in out if line.startswith("|")][2:]
    out = out[:len(out) - len(rows)] + rows[:most] if rows else out
    while out and not out[-1].strip():
        out.pop()
    return out + (["", "%d more findings: run health.py check" % (len(rows) - most)] if len(rows) > most else [])

