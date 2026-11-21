#!/usr/bin/env python3
"""One-shot (goal migrate-features): move every live requirement into the feature format in place.

usage: python3 docs/migrations/features-v1.py run [--base REF] [--skip IDS]
Each entry keeps its text; its Reviewed mark is cleared and a block of `  - ` bullets follows it (outside its hashed text).
Everything is built in memory and every text hash is checked before any file is written. The proof is features-v1-check.py.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

ID = r"[A-Z]{2,5}-\d+"
REPORT = "docs/migrations/features-v1-report.md"
BLOCK = re.compile(r"^  - (Feature markers v1|Reference: .*|Line \d+: metric .*; test .*)$")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def bail(why):
    sys.exit("REFUSED: " + why)


def clean(s, n=60):
    s = s or ""
    while True:
        t = s.replace("|", "/").replace("<!--", "").replace("-->", "")
        if t == s:
            return re.sub(r"\s+", " ", s).strip()[:n]
        s = t


def plain(s):
    s = re.sub(r"\[([^\]]*)\]\(https?://[^)]*\)", r"\1", s or "")
    return "; ".join(re.sub(r"^\s*- ", "", x).strip() for x in re.split(r"<br\s*/?>", s) if x.strip())


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def entries(cr, lines):
    out, head, fence = [], "", False
    for k, line in enumerate(lines):
        fence ^= line.startswith("```")
        if not fence and line.startswith("## "):
            head = line[3:].strip()
        m = cr.LINE.match(line) if head == "Requirements" and not fence else None
        if m:
            out.append((k, m, cr.subs(lines, k)))
    return out


def metrics(lines):
    got, on = [], False
    for line in lines:
        if line.startswith("## "):
            on = line[3:].strip() == "Success metrics"
        elif on and line.startswith("- "):
            got.append(line)
    return got


def follows(pf, root):
    seen = {}
    for line in open(os.path.join(root, "docs/wiki/Principles.md"), encoding="utf-8").read().split("\n"):
        m = re.match(r"\| \[(%s) " % ID, line)
        if m:
            cells = pf.cells(line)
            seen.setdefault(m[1], []).append(cells[2] if len(cells) > 2 else "")
    return {k: v[0] for k, v in seen.items() if len(v) == 1}


def log_rows():
    """{key: [(date, record id)]} from the shared reviews log: the date and the owner-record id only, never the free text."""
    rows = {}
    try:
        path = os.path.join(os.path.abspath(git("rev-parse", "--git-common-dir").strip()), "loop", "reviews.tsv")
        for line in open(path, encoding="utf-8"):
            c = line.rstrip("\n").split("\t")
            if len(c) > 3 and c[1] == "review" and re.fullmatch(r"\d{4}-\d\d-\d\d", c[0][:10]):
                m = re.search(r"record (o\d+)", c[3])
                for key in c[2].split(","):
                    rows.setdefault(key.strip(), []).append((c[0][:10], m[1] if m else "no record id"))
    except (OSError, AttributeError):
        pass
    return rows


def record(log, key, day):
    got = [r for r in log.get(key, []) if r[0] <= day] or log.get(key, [])
    return "%s %s" % got[-1] if got else "record not available"


def build(root, base, skip, cr, pf, prd):
    """(pages {rel: text}, features, marks) built in memory; refuses before any write."""
    tests, _ = cr.test_rows(root)
    refs, log, pages, feats, marks, ids = follows(pf, root), log_rows(), {}, [], [], set()
    known = {r[6] for r in kept_rows(root)}
    for rel in cr.pages(root):
        raw = open(os.path.join(root, rel), encoding="utf-8", newline="").read()
        eol = "\r\n" if "\r\n" in raw else "\n"
        text = raw.replace("\r\n", "\n")
        lines, name = text.split("\n"), os.path.basename(rel)[:-3]
        ents = [e for e in entries(cr, lines) if e[1][1] not in skip]
        old = git("show", "%s:%s" % (base, rel))
        if old is None:
            bail("%s is not on %s" % (rel, base))
        onbase = set(old.replace("\r\n", "\n").split("\n"))
        top = re.compile(r"^Review: \*\*Reviewed (\d{4}-\d\d-\d\d)\*\*")
        page_mark = next(((k, top.match(x)) for k, x in enumerate(lines[:12]) if top.match(x)), None)
        if not ents and not page_mark:
            continue
        sm, out, k, pos = metrics(lines), [], 0, {e[0]: e for e in ents}
        while k < len(lines):
            if k not in pos:
                out.append(lines[k])
                k += 1
                continue
            _, m, subs = pos[k]
            key = m[1]
            if not subs:
                bail("%s has no sub-bullet" % key)
            ids.add(key)
            before = pf.unit(m[4], subs)
            line = lines[k]
            if m[2] != "Unreviewed":
                if line not in (known or onbase):
                    bail("%s holds a Reviewed mark that is not %s" % (key, "in the report" if known else "on " + base))
                marks.append(("entry", name, key, m[3], m[5] or "-", record(log, key, m[3]), line))
                line = re.sub(r" <!-- reviewed \w+ -->$", "", re.sub(r"\*\*Reviewed \d{4}-\d\d-\d\d\*\*", "**Unreviewed**", line, count=1))
            tok = re.compile(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9-])" % re.escape(key))
            hit = [str(i + 1) for i, b in enumerate(sm) if tok.search(b)]
            met = "Success metric %s of this page" % ", ".join(hit) if hit else "missing"
            n = len(tests.get(key, []))
            tst = "%d linked rows, see Tests" % n if n else "missing"
            ref = clean(plain(refs.get(key, "")), 400)
            ref = "reference missing" if ref in ("", "-", "—") else ref
            block = ["", "  - Feature markers v1", "  - Reference: " + ref]
            block += ["  - Line %d: metric %s; test %s" % (i + 1, met, tst) for i in range(len(subs))]
            out.append(line)
            out += lines[k + 1:k + 1 + len(subs)]
            k += 1 + len(subs)
            if k < len(lines) and lines[k] == "" and k + 1 < len(lines) and BLOCK.match(lines[k + 1]):
                k += 1
                while k < len(lines) and BLOCK.match(lines[k]):
                    k += 1
            out += block
            feats.append([key, name, before, None, len(subs), met != "missing", n, ref, key])
        text2 = "\n".join(out)
        if page_mark:
            if lines[page_mark[0]] not in (known or onbase):
                bail("%s has a Reviewed Review line that is not %s" % (rel, "in the report" if known else "on " + base))
            marks.append(("page", name, "-", page_mark[1][1], clean(re.sub(r"^.*?(<!-- prd .*?-->).*$", r"\1", lines[page_mark[0]]), 90), record(log, name, page_mark[1][1]), lines[page_mark[0]]))
            text2, why = prd.unreview_text(text2, name)
            if why:
                bail(why)
        nl2 = text2.split("\n")
        after = {e[1][1]: pf.unit(e[1][4], e[2]) for e in entries(cr, nl2)}
        for f in feats:
            if f[1] == name and f[3] is None:
                if after.get(f[0]) != f[2]:
                    bail("the text of %s changed" % f[0])
                f[3] = f[2]
        pages[rel] = text2.replace("\n", eol)
    want = set()
    for rel in cr.pages(root):
        t = (git("show", "%s:%s" % (base, rel)) or "").replace("\r\n", "\n").split("\n")
        want |= {e[1][1] for e in entries(cr, t) if e[1][1] not in skip}
    if want != ids:
        bail("the requirements differ from %s: %s" % (base, ", ".join(sorted(want ^ ids))))
    return pages, feats, marks


def report(feats, marks, skip, kept):
    seen = {(r[0], r[1], r[2]): r for r in kept}
    seen.update({(r[0], r[1], r[2]): r for r in marks})
    rows = list(seen.values())
    out = ["# Feature migration report (features-v1)", "",
           "Written by `docs/migrations/features-v1.py run`; it holds no run date, so a re-run writes the same bytes.", "",
           "## Features", "", "| ID | Page | Text hash before | Text hash after | Lines | Metric | Test rows | Reference |", "|---|---|---|---|---|---|---|---|"]
    out += ["| %s | %s | %s | %s | %d | %s | %d | %s |" % (f[0], f[1], sha(f[2]), sha(f[3]), f[4], "linked" if f[5] else "missing", f[6], f[7]) for f in feats]
    out += ["", "## Old marks cleared", "", "| Kind | Page | ID | Date | Seal or lock | Review-log row (context only, not proof) |", "|---|---|---|---|---|---|"]
    out += ["| %s | %s | %s | %s | %s | %s |" % tuple(r[:6]) for r in rows]
    out += ["", "## To split (more than five lines)", ""]
    out += ["- %s (%s): %d lines" % (f[0], f[1], f[4]) for f in sorted(feats, key=lambda f: -f[4]) if f[4] > 5] or ["- none"]
    perline = sum(f[4] for f in feats)
    out += ["", "## Skipped (already in the new format)", "", "- " + (", ".join(sorted(skip)) or "none"), "", "## Totals", "",
            "- features migrated: %d" % len(feats), "- requirement marks cleared: %d" % sum(r[0] == "entry" for r in rows),
            "- page-level marks cleared: %d" % sum(r[0] == "page" for r in rows),
            "- features to split: %d" % sum(f[4] > 5 for f in feats), "- lines: %d" % perline,
            "- lines with metric missing, by line: %d, by ID: %d" % (sum(f[4] for f in feats if not f[5]), sum(not f[5] for f in feats)),
            "- lines with test missing, by line: %d, by ID: %d" % (sum(f[4] for f in feats if not f[6]), sum(not f[6] for f in feats)),
            "- features with reference missing: %d" % sum(f[7] == "reference missing" for f in feats),
            "", "## Original mark lines (read by the check)", "", "```text"]
    out += ["\t".join(r) for r in rows] + ["```", ""]
    return "\n".join(out)


def kept_rows(root):
    try:
        t = open(os.path.join(root, REPORT), encoding="utf-8").read()
        return [tuple(x.split("\t")) for x in t.split("```text\n")[1].split("\n```")[0].split("\n") if x]
    except (OSError, IndexError):
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run"])
    ap.add_argument("--base")
    ap.add_argument("--skip", default="DOC-27,DOC-28")
    a = ap.parse_args()
    if not re.fullmatch(r"(%s(,%s)*)?" % (ID, ID), a.skip) or (a.base and not re.fullmatch(r"[A-Za-z0-9._/@~^][A-Za-z0-9._/@~^-]*", a.base)):
        bail("bad --base or --skip")
    root = (git("rev-parse", "--show-toplevel") or "").strip() or bail("not in a git repository")
    base = a.base or (git("merge-base", "HEAD", "origin/main") or "").strip() or bail("no base: pass --base")
    skip = set(filter(None, a.skip.split(",")))
    sys.path.insert(0, os.path.join(root, "skills/workflow-docs/scripts"))
    import criteria as cr
    import pageformat as pf
    import prd
    pages, feats, marks = build(root, base, skip, cr, pf, prd)
    text = report(feats, marks, skip, kept_rows(root))
    todo = {rel: t for rel, t in pages.items() if open(os.path.join(root, rel), encoding="utf-8", newline="").read() != t}
    cur = os.path.join(root, REPORT)
    if not os.path.exists(cur) or open(cur, encoding="utf-8", newline="").read() != text:
        todo[REPORT] = text
    dirty = git("status", "--porcelain", "--", *todo) if todo else ""
    if dirty is None:
        bail("git status failed")
    if dirty:
        bail("these paths have uncommitted changes:\n" + dirty)
    tmp, done = "", []
    try:
        if todo:
            os.makedirs(os.path.join(root, "docs/migrations"), exist_ok=True)
            tmp = tempfile.mkdtemp(prefix=".features-v1-", dir=os.path.join(root, "docs/migrations"))
        for i, (rel, t) in enumerate(sorted(todo.items(), key=lambda x: x[0] == REPORT)):
            part = os.path.join(tmp, "%d.tmp" % i)
            open(part, "w", encoding="utf-8", newline="").write(t)
            todo[rel] = part
        for rel, part in sorted(todo.items(), key=lambda x: x[0] == REPORT):
            os.replace(part, os.path.join(root, rel))
            done.append(rel)
    except Exception as e:
        sys.exit("REFUSED: write failed (%s). Touched: %s. Recover: git checkout -- %s%s" % (
            e, ", ".join(done) or "none", " ".join(r for r in done if r != REPORT) or ".", "; delete " + REPORT if REPORT in done else ""))
    finally:
        tmp and shutil.rmtree(tmp, ignore_errors=True)
    print("MIGRATED %d features on %d pages, %d marks cleared; wrote %d files (base %s)" % (len(feats), len(pages), len(marks or kept_rows(root)), len(done), base[:9]))


if __name__ == "__main__":
    main()
