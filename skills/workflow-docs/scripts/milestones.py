#!/usr/bin/env python3
"""Milestone sync (DOC-17): a repo's GitHub milestones against an external Milestones page, both ways, opt-in; called by `docs.py sync`.
A repo opts in with `milestones_source` in .loop/config.json (`url:<link>` or `mcp:<server>:<resource>`); a milestone is `- TITLE: state | due`
on the page and from `gh api` on GitHub, compared with .loop/milestones.md. A delta or CONFLICT is posted once as an issue and a page
comment; nothing is overwritten. `docs.py sync --accept milestones:TITLE=repo|source` writes one side's text to the other.
Below: DOC-19 How-to checks and DOC-20 revisions (criteria.py revise, retire, migrate, guard)."""
import json
import os
import re
import sys
from os.path import join

import counting
import criteria as cr
import pageformat as pf
import prd
from criteria import put, sha
from prd import out as post

KEY = "milestones:"
LINE = re.compile(r"^[-*] (.+): ((?:open|closed) \| (?:no due|due \d{4}-\d\d-\d\d))$")
API = "repos/{owner}/{repo}/milestones"


def parse(text):
    """{title: 'state | due'} of the `- TITLE: state | due` lines; the first of a repeated title wins."""
    found = {}
    for raw in text.splitlines():
        match = LINE.match(raw.strip())
        if match and "\t" not in match.group(1):
            found.setdefault(match.group(1).strip(), match.group(2))
    return found


def repo_side():
    """({title: text}, {title: number}, None) of the repo's milestones, or (None, None, why)."""
    ok, text = post("LOOP_GH", "api", API + "?state=all&per_page=100", "--paginate")
    if not ok:
        return None, None, text[:100]
    have, nums, at, decoder = {}, {}, 0, json.JSONDecoder()
    try:
        while at < len(text):
            if text[at].isspace():
                at += 1
                continue
            page, at = decoder.raw_decode(text, at)
            for item in page:
                title, state, due = item["title"], item["state"], item.get("due_on")
                if isinstance(title, str) and "\t" not in title and state in ("open", "closed"):
                    have[title.strip()] = "%s | %s" % (state, "due " + due[:10] if due else "no due")
                    nums[title.strip()] = item["number"]
    except (ValueError, TypeError, KeyError, AttributeError):
        return None, None, "gh printed something that is not a list of milestones"
    return have, nums, None


def backlog(page, held={}):
    """DOC-17: the milestone "Backlog: PAGE" for a page's delta issues, created when missing, "" when gh cannot list or make it."""
    title = "Backlog: " + page
    if title not in held:
        have = repo_side()[0]
        held[title] = title if have is not None and (title in have or post("LOOP_GH", "api", "-X", "POST", API, "-f", "title=" + title)[0]) else ""
    return held[title]


def to_repo(title, number, text):
    """(ok, why) of making the repo's milestone `title` read `text`: created, or edited by its number."""
    state, _, due = text.partition(" | ")
    args = ["-f", "title=" + title, "-f", "state=" + state, "-F" if due == "no due" else "-f", "due_on=null" if due == "no due" else "due_on=%sT00:00:00Z" % due[4:]]
    return post("LOOP_GH", "api", "-X", "PATCH" if number else "POST", "%s/%s" % (API, number) if number else API, *args)


def sync(root, args):
    source = counting.config_of(root).get("milestones_source")
    if not isinstance(source, str) or not source.startswith(("url:", "mcp:")):
        held = counting.ledger(root)  # a repo that dropped its source keeps no milestone rows, and none is listed
        if not args.dry_run and any(k.startswith(KEY) for k in held):
            counting.ledger(root, {k: v for k, v in held.items() if not k.startswith(KEY)})
        return 0
    if args.open:
        return 0
    dry, path = args.dry_run, join(root, ".loop", "milestones.md")
    body, why = prd.read_link(source)
    if body is None:
        print("not connected: milestones (%s): %s" % (source, why))
        return 0
    want = parse(body)
    have, nums, why = repo_side()
    if have is None:
        print("not connected: milestones (gh): %s" % why)
        return 0
    if not want:
        print("SKIPPED milestones: no `- TITLE: state | due` line in the source")
        return 0
    gone = [t for t in have if t not in want and have[t].startswith("closed")]
    for title in gone:
        want[title] = have[title]
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            mine = handle.read()
        if not mine.startswith(cr.SYNC_MARK):
            print("SKIPPED milestones: .loop/milestones.md is not sync's own")
            return 0
        agreed = parse(mine)
    else:
        agreed = {t: x for t, x in have.items() if want.get(t) == x}
    start, held = dict(agreed), counting.ledger(root)
    for item in (a for a in args.accept if not dry and a.startswith(KEY)):
        title, _, side = item[len(KEY):].rpartition("=")
        r, s = have.get(title), want.get(title)
        if r == s or side not in ("repo", "source"):
            print("NO DELTA milestones: %s" % title)
            continue
        keep = (s or r.replace("open", "closed", 1)) if side == "source" else r
        ok, why = to_repo(title, nums.get(title), keep) if side == "source" else post("LOOP_PRD_WRITER", source, "replace" if r else "remove", title, input=r or "")
        if not ok:
            print("not connected: milestones (%s): %s" % ("gh" if side == "source" else source, why[:100]))
            continue
        for held_side in (have, want, agreed):
            if keep:
                held_side[title] = keep
            else:
                held_side.pop(title, None)
        row = held.pop(KEY + title, None)
        if row:
            post("LOOP_GH", "issue", "close", row[1], "--comment", "Accepted: %s." % side)
        print("ACCEPTED milestones: %s, the %s's text" % (title, side))
    found = []
    for title in sorted(set(have) | set(want)):
        r, s, a = have.get(title), want.get(title), agreed.get(title)
        if r == s:
            if title in gone:  # closed and not on the page: nothing agreed, so a reopen is the repo's change alone
                agreed.pop(title, None)
            else:
                agreed[title] = r
        else:
            found.append((title, "both sides" if (r != a) == (s != a) else "the repo" if r != a else "the source", r, s))
    for title in [t for t in agreed if t not in have and t not in want]:
        del agreed[title]
    for title, side, r, s in found:
        print("%s milestones: %s %s changed (repo: %s | source: %s)" % ("CONFLICT" if side == "both sides" else "DELTA", title, side, r or "-", s or "-"))
    print("MILESTONES: %d in step, %d with a delta" % (len(have.keys() | want.keys()) - len(found), len(found)))
    if dry:
        return 1 if found else 0
    for key in [k for k in held if k.startswith(KEY) and k[len(KEY):] not in [f[0] for f in found]]:
        post("LOOP_GH", "issue", "close", held.pop(key)[1], "--comment", "Resolved.")
    for title, side, r, s in found:
        key, text = KEY + title, "Delta in milestones %s: %s changed.\nRepo: %s\nSource: %s\nAccept one: docs.py sync --accept milestones:%s=repo|source" % (
            title, side, r or "-", s or "-", title)
        row = held.get(key) or [side, "", "0", ""]
        if row[1] and row[3] != sha(text):
            post("LOOP_GH", "issue", "comment", row[1], "--body", text)
            row[2] = "0"
        elif not row[1]:
            ok, made = post("LOOP_GH", "issue", "create", "--title", "DELTA milestones %s: %s changed" % (title, side), "--body", text)
            if not ok:
                print("not connected: milestones %s (gh): %s" % (title, made[:100]))
                continue
            row[1] = made.split("\n")[-1]
        if row[2] != "1":
            ok, why = post("LOOP_PRD_WRITER", source, "comment", input=text)
            row[2] = "1" if ok else "0"
            print("POSTED milestones %s: %s%s" % (title, row[1], "" if ok else " (not connected to %s: %s)" % (source, why[:80])))
        held[key] = [side, row[1], row[2], sha(text)]
    counting.ledger(root, held)
    if agreed != start or not os.path.exists(path):
        put(path, source, agreed, {t: sha(x) for t, x in agreed.items()})
    return 0


ITEM = re.compile(r"^- ([A-Z]{2,5}-\d+): ?\S")


def howto_items(name, text, feature):
    """DOC-19: the How-to-use page holds one '- ID: how it is delivered' item per functional requirement of its feature page, and none else."""
    have, top, sub = {}, "", ""
    for line in feature.splitlines():
        top, sub = (line[3:].strip(), "") if line.startswith("## ") else (top, line[4:].strip() if line.startswith("### ") else sub)
        hit = re.match(r"^- ([A-Z]{2,5}-\d+):", line)
        if hit and top == "Requirements":
            have[hit.group(1)] = sub
    items = {m.group(1) for m in map(ITEM.match, text.splitlines()) if m}
    out = []
    for kind, ids, fix in (("no item for the functional requirement", sorted(k for k, v in have.items() if v == "Functional" and k not in items),
                            "add '- ID: how it is delivered' under 'How to reach or run it'"),
                           ("an item for an ID its feature page lacks:", sorted(items - set(have)), "remove it or fix the ID")):
        out += [("HOWTO", name, "DOC-19 %s %s. Fix: %s" % (kind, ", ".join(ids), fix))] * bool(ids)
    return out


# --- How-to-use Kinds (DOC-19, #4677): every delivered row names a Kind, and the page carries that Kind's block ---
KHEAD = "| Component | Kind | What it is | How a user uses it |"
ROUTINE = "Scheduled routine"
KINDS = {
    "Site/URL": ["URLs", "Served by", "Check", "Deploy"],
    "Skill": ["Say", "Command"],
    "Command": ["Command", "Dry run", "Reads", "Writes", "Exit codes"],
    "API/file contract": ["Path", "Fields", "Example", "Writer", "Reader"],
    ROUTINE: [],  # its runbook fields are DOC-16's: pageformat.runbook checks them
    "Deployment": ["Target", "Deploy", "Rollback", "Check"],
    "Message/channel": ["Trigger", "Recipients", "Subject", "Resend"],
    "Playbook": ["Steps", "Templates", "Stop rules"],
}
FIELD = re.compile(r"^- \*\*([A-Z][A-Za-z ]*):\*\*\s*(.*)$")
ADDRESS = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
NAMED = re.compile(r"`(?:python3? )?([\w./-]+\.(?:py|sh)) ([a-z][\w-]*)")


def part(text, name):
    """The lines under '## name', up to the next '## ' heading."""
    head = "\n## %s\n" % name
    return text.split(head, 1)[1].split("\n## ", 1)[0] if head in text else ""


def blocks(body):
    """{heading: {field: text}} for each '### ' block of a section's text (indented lines continue a field)."""
    found, cur, last = {}, None, None
    for line in body.splitlines():
        if line.startswith("### "):
            cur, last = line[4:].strip(), None
            found[cur] = {}
        elif cur is not None and FIELD.match(line):
            last, text = FIELD.match(line).groups()
            found[cur][last] = found[cur].get(last, "") + text
        elif cur is not None and last and line[:1].isspace():
            found[cur][last] += " " + line.strip()
    return found


def delivered(text):
    """(header line, [(component, kind, cell count)]) of the page's What's delivered table."""
    block = text.split("\n### What's delivered\n", 1)[1].split("\n## ", 1)[0].split("\n### ", 1)[0] if "\n### What's delivered\n" in text else ""
    lines = [x.rstrip() for x in block.splitlines() if x.startswith("|")]
    out = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        out.append((cells[0].replace("`", ""), cells[1] if len(cells) > 1 else "", len(cells)))
    return (lines[0] if lines else ""), out


def kinds(name, text, on_page=()):
    """DOC-19: (kind, page, detail) findings for a How-to-use page's What's delivered table and the block each row needs."""
    out, bad = [], lambda why: out.append(("HOWTO", name, "DOC-19 %s" % why))
    header, table = delivered(text)
    if header != KHEAD:
        bad("the What's delivered header is '%s' (got '%s'). Fix: use that header" % (KHEAD, header))
    if not table:
        bad("What's delivered holds no row. Fix: add a row for each component, with its Kind")
    reach, books_here = blocks(part(text, "How to reach or run it")), blocks(part(text, "Runbooks"))
    wanted = set()
    for component, kind, cells in table:
        if cells != 4:
            bad("row '%s' has %d cells, not 4" % (component, cells))
        if kind not in KINDS:
            bad("row '%s': Kind '%s' is not one of %s. Fix: name one Kind" % (component, kind, ", ".join(KINDS)))
            continue
        if kind == ROUTINE:
            wanted.add(component)
            found = books_here.get(component) if component in books_here else ({} if component in on_page else None)
        else:
            wanted.add("%s: %s" % (kind, component))
            found = reach.get("%s: %s" % (kind, component))
        if found is None:
            bad("row '%s' (%s) has no block. Fix: add '### %s' under %s" % (component, kind, component if kind == ROUTINE else "%s: %s" % (kind, component),
                                                                      "Runbooks" if kind == ROUTINE else "How to reach or run it"))
            continue
        for field in ([] if component in on_page else KINDS[kind]):
            if len(found.get(field, "").strip()) < 3:
                bad("block '%s' has no '%s' field of 3 characters or more. Fix: add '- **%s:** text' (write 'none' when there is none)" % (component, field, field))
        if kind == "Skill" and not found.get("Command", "").lstrip().startswith("`/"):
            bad("block '%s': a Skill's Command is its exact /command in backticks" % component)
        if ADDRESS.search(" ".join(found.values())):
            bad("block '%s' holds an address. Fix: name a role, not a person" % component)
    for heading in list(reach) + list(books_here):
        if heading not in wanted and heading != "When something goes wrong":
            bad("block '%s' has no row in What's delivered. Fix: add its row or remove the block" % heading)
    return out


def unlisted(feature, how):
    """DOC-19: the commands a feature page names in backticks that its How-to-use page does not hold."""
    body = "\n".join(x for x in feature.split("\n## Tests", 1)[0].splitlines() if not x.startswith("Milestone:"))
    names = {"%s %s" % m.groups() for m in NAMED.finditer(body)}
    return sorted(n for n in names if n not in how)


# --- DOC-20: revisions (criteria.py revise, retire, migrate, guard) ---
NINE = ("Delivery", "Setup", "Regression", "Automation", "Documentation", "Guardrails", "Health", "Machines", "Monitoring")
IDS = r"[A-Z]{2,5}-\d+"


def no(code, why):
    sys.exit("[%s] %s. No changes written." % (code, why))


def record(rid, slug, *names):
    """Owner-words record rid as 'rid: "first 12 words"' when it lists slug and one of names, else None."""
    try:
        with open(join(os.path.abspath(cr.git("rev-parse", "--git-common-dir")), "loop", "owner-words.tsv"), encoding="utf-8") as fh:
            rows = [x.rstrip("\n").split("\t") for x in fh]
    except OSError:
        rows = []
    for r in rows:
        if len(r) == 5 and r[0] == rid and slug in r[4].split(",") and set(names) & set(r[4].split(",")):
            return '%s: "%s"' % (rid, pf.enc(" ".join(json.loads(r[3]).split()[:12])))


def put(text, tab, ret):
    """The page with its Revisions section rebuilt: Retired first, then one table per ID."""
    got = (["### Retired\n\n" + "\n".join("- %s: %s" % kv for kv in sorted(ret.items()))] if ret else []) + [
        "### %s\n\n%s" % (k, "\n".join(pf.table(pf.RHEAD, tab[k]))) for k in sorted(tab, key=lambda k: (k[:2], int(k.split("-")[1])))]
    block = "## Revisions\n\n" + "\n\n".join(got) + "\n"
    if "\n## Revisions\n" in text:
        head, rest = text.split("\n## Revisions\n", 1)
        return head + "\n" + block + ("\n## " + rest.split("\n## ", 1)[1] if "\n## " in rest else "")
    top, mid, rest = text.partition("\n## Tests")
    return top.rstrip("\n") + "\n\n" + block + mid + rest


def save(path, old, new):
    if cr.slurp(path) != old:
        no("REV-ROW", "%s changed while it was read" % path)
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    os.replace(path + ".tmp", path)


def slug_of(args):
    return args.goal or cr.git("branch", "--show-current").replace("loop/", "", 1)


def revise(args):
    """Change a requirement's text (revise) or drop it (retire --as), keeping every earlier text as a revision row."""
    root, key = cr.git("rev-parse", "--show-toplevel"), args.id
    for rel in cr.pages(root):
        text = cr.slurp(join(root, rel))
        lines = text.split("\n")
        hit = [(n, m) for n, x in enumerate(lines) for m in [cr.LINE.match(x)] if m and m.group(1) == key]
        if hit:
            break
    else:
        no("REV-ROW", "no live requirement " + key)
    (n, m), page, below = hit[0], os.path.basename(rel)[:-3], cr.subs(lines, hit[0][0])
    said = record(args.owner_record, slug_of(args), key, page)
    tab, ret, _ = pf.revs(dict(cr.sections(text)).get("Revisions") or [])
    if not said or key not in tab:
        no("REV-RECORD" if not said else "REV-ROW", "need an owner record naming %s and %s or %s" % (slug_of(args), key, page) if not said else "%s has no table. Fix: criteria.py migrate" % key)
    rows, old = tab[key], pf.unit(m.group(4), below)
    if args.command == "retire":
        form = re.sub(r"^(merged|moved):", lambda x: x.group(1) + (" into " if x.group(1) == "merged" else " to "), args.as_)
        live = {x.group(1) for r in cr.pages(root) for x in map(cr.LINE.match, cr.slurp(join(root, r)).split("\n")) if x}
        if not re.match(r"^(Retired|(merged into|moved to) %s)$" % IDS, form) or form[-1].isdigit() and form.split()[-1] not in live - {key}:
            no("IDS-MISSING", "--as is Retired, merged:ID or moved:ID with a live ID")
        ret[key], fresh, subs = form, old, []
    else:
        body = open(args.text_file, encoding="utf-8").read().splitlines() if args.text_file else [args.text]
        subs = ["  - " + re.sub(r"^\s*-\s*", "", x).strip() for x in body[1:] if x.strip()] if args.text_file else below
        fresh = pf.unit(body[0].strip(), subs)
        if fresh == old:
            no("REV-NOOP", key + " already reads so")
    rows.insert(0, ["r%d" % (len(rows) + 1), cr.today(), fresh, pf.enc(" ".join(args.why.split())), said])
    lines[n:n + 1 + len(below)] = [] if args.command == "retire" else ["- %s: **Unreviewed** %s" % (key, body[0].strip())] + subs
    save(join(root, rel), text, put("\n".join(lines), tab, ret))
    print(("RETIRED %s as %s" % (key, ret[key])) if args.command == "retire" else "REVISED %s r%d->r%d (now Unreviewed, awaits review)" % (key, len(rows) - 1, len(rows)))
    return 0


def migrate(args):
    """Give each requirement of the nine pages its first revision row, r1, from its current text."""
    root, rule, plans = cr.git("rev-parse", "--show-toplevel"), cr.rules(), []
    for rel in cr.pages(root):
        page, text = os.path.basename(rel)[:-3], cr.slurp(join(root, rel))
        body = dict(cr.sections(text))
        if page not in (args.page or NINE) or not body.get(rule["sections"][1]):
            continue
        said = record(args.owner_record, slug_of(args), page)
        tab, ret, _ = pf.revs(body.get(rule["revs"]) or [])
        day = re.search(r"\d{4}-\d\d-\d\d", next((x for x in text.split("\n") if x.startswith("Review:")), ""))
        for _, m, below in cr.blocks(body[rule["sections"][1]]):
            if m and m.group(1) not in tab | ret.keys():
                tab[m.group(1)] = [["r1", m.group(3) or (day and day.group(0)) or cr.today(), pf.unit(m.group(4), below),
                                    "migration r1; date from " + ("its Reviewed stamp" if m.group(3) else "the page Review line" if day else "the run day"), said]]
        if not said:
            no("REV-RECORD", "need an owner record naming %s and %s" % (slug_of(args), page))
        plans.append((rel, text, put(text, tab, ret)))
    for rel, text, fresh in [x for x in plans if x[1] != x[2]]:
        save(join(root, rel), text, fresh)
        print("MIGRATED " + rel)
    print("MIGRATE OK")
    return 0


def guard(args):
    """GUARD OK, or exit 1 naming each Reviewed requirement of the branch whose text changed with no done line or owner record behind it."""
    root = cr.git("rev-parse", "--show-toplevel")
    base = args.base or next((r for r in ("origin/main", "main") if cr.git("rev-parse", "--verify", "-q", r, check=False)), "origin/main")
    if not cr.git("rev-parse", "--verify", "-q", base + "^{commit}", check=False):
        sys.exit("[GUARD-BASE] cannot read %s (shallow: %s). Fix: git fetch origin main" % (base, cr.git("rev-parse", "--is-shallow-repository", check=False)))
    slug, rule, sec = args.slug or cr.git("branch", "--show-current").replace("loop/", "", 1), cr.rules(), cr.rules()["sections"][1]
    goal = cr.git("show", "HEAD:.loop/goals/%s.md" % slug, check=False).split("## Done lines", 1)[-1].split("\n## ", 1)[0]
    bad = []
    for rel in cr.git("diff", "--name-only", base + "...HEAD", "--", cr.folder_of(root)).split():
        was, now = (dict(cr.sections(cr.git("show", "%s:%s" % (r, rel), check=False))) for r in (base, "HEAD"))
        mine = lambda d: {m.group(1): (m.group(2), pf.unit(m.group(4), b)) for _, m, b in cr.blocks(d.get(sec) or []) if m}
        old, new, page = mine(was), mine(now), os.path.basename(rel)[:-3]
        have, rows = (pf.revs(d.get(rule["revs"]) or [])[0] for d in (now, was))
        for key, (mark, text) in old.items():
            fresh = have.get(key, [])[:len(have.get(key, [])) - len(rows.get(key, []))]
            if mark == "Unreviewed" or new.get(key, ("", ""))[1] == text or re.search(r"(?<![A-Z0-9-])%s(?!\d)" % key, goal) or any(
                    record(r[4].split(":")[0], slug, key, page) for r in fresh if len(r) == 5):
                continue
            bad.append("%s (%s): %s changed. Worker fix: revert it, or goal.py finding %s \"%s <gap>\" --requirement %s. Owner fix: an owner record "
                       "naming %s and %s or %s, then criteria.py revise" % (key, page, "text" if key in new else "removed", slug, key, key, slug, key, page))
    sys.exit("GUARD REFUSED " + "\nGUARD REFUSED ".join(bad)) if bad else print("GUARD OK")
    return 0


def add_parsers(sub):
    for name, func in (("revise", revise), ("retire", revise), ("migrate", migrate), ("guard", guard)):
        item = sub.add_parser(name)
        item.set_defaults(func=func)
        if name == "guard":
            item.add_argument("base", nargs="?", default="")
            item.add_argument("slug", nargs="?", default="")
            continue
        item.add_argument("--owner-record", required=True)
        item.add_argument("--goal", default="")
        if name == "migrate":
            item.add_argument("--page", action="append")
            continue
        item.add_argument("id")
        item.add_argument("--why", required=True)
        item.add_argument("--as", dest="as_", help="retired, merged:ID or moved:ID") if name == "retire" else [
            item.add_argument("--text", default=""), item.add_argument("--text-file", default="")]
