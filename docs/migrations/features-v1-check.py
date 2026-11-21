#!/usr/bin/env python3
"""Proof for goal migrate-features (shares no code with features-v1.py): python3 docs/migrations/features-v1-check.py check

usage: check [--base REF] [--skip IDS] [--allow PATHS] [--source SHA]
One-shot: meaningful only before this migration merges (afterwards BASE is the migrated main). Unpacks the committed HEAD with git archive into a temporary directory (no worktree is registered), then proves the five done
lines against BASE (default: git merge-base HEAD origin/main) and the frozen source. It writes nothing to the tracked tree.
"""
import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ID = r"[A-Z]{2,5}-\d+"
SENTENCE = "release gate (review.py check_reviews) now lists every Unreviewed requirement, the 27 migrated and DOC-27 and DOC-28, as not Reviewed"
BLOCK = re.compile(r"^  - (Feature markers v1|Reference: .*|Line \d+: metric .*; test .*)$")
ENTRY = re.compile(r"^- (%s): \*\*(Unreviewed|Reviewed \d{4}-\d\d-\d\d)\*\* (\S.*?)(?: <!-- reviewed \w+ -->)?$" % ID)
fails = []


def run(*a, cwd=None, raw=False):
    p = subprocess.run(list(a), capture_output=True, cwd=cwd)
    return p.stdout if raw else (p.stdout.decode() if p.returncode == 0 else None)


def show(ref, rel):
    t = run("git", "show", "%s:%s" % (ref, rel), raw=True)
    return t.decode() if t else None


def ok(name, good, why=""):
    print(("PASS " if good else "FAIL ") + name + ("" if good else ": " + why))
    if not good:
        fails.append(name)


def units(text):
    """{id: sha of title and sub-bullets} for the entries under ## Requirements (own parse, whitespace normalised)."""
    out, head, fence, lines = {}, "", False, text.replace("\r\n", "\n").split("\n")
    for k, line in enumerate(lines):
        fence ^= line.startswith("```")
        if not fence and line.startswith("## "):
            head = line[3:].strip()
        m = ENTRY.match(line) if head == "Requirements" and not fence else None
        if m:
            parts = [m[3]]
            for x in lines[k + 1:]:
                if not x.strip() or not x[:1].isspace():
                    break
                parts.append(x.strip()[2:] if x.strip().startswith("- ") else x.strip())
            out[m[1]] = hashlib.sha256(" <br> ".join(" ".join(p.split()) for p in parts).encode()).hexdigest()[:12]
    return out


def strip_blocks(lines):
    out, k = [], 0
    while k < len(lines):
        if lines[k].rstrip("\r") == "" and k + 1 < len(lines) and lines[k + 1].rstrip("\r") == "  - Feature markers v1":
            k += 1
            while k < len(lines) and BLOCK.match(lines[k].rstrip("\r")):
                k += 1
            continue
        out.append(lines[k])
        k += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check"])
    ap.add_argument("--base")
    ap.add_argument("--skip", default="DOC-27,DOC-28")
    ap.add_argument("--allow", default="")
    ap.add_argument("--source", default="48ac06e7d")
    a = ap.parse_args()
    if not re.fullmatch(r"(%s(,%s)*)?" % (ID, ID), a.skip) or not re.fullmatch(r"[0-9a-f]{7,40}", a.source) or (a.base and not re.fullmatch(r"[A-Za-z0-9._/@~^][A-Za-z0-9._/@~^-]*", a.base)) or not re.fullmatch(r"[A-Za-z0-9._/,-]*", a.allow):
        sys.exit("REFUSED: bad argument")
    root = (run("git", "rev-parse", "--show-toplevel") or "").strip() or sys.exit("REFUSED: not in a git repository")
    os.chdir(root)
    st = run("git", "status", "--porcelain", "--untracked-files=no")
    if st is None or st:
        sys.exit("REFUSED: git status failed or tracked files are dirty; commit first, check reads the committed HEAD")
    base = a.base or (run("git", "merge-base", "HEAD", "origin/main") or "").strip() or sys.exit("REFUSED: no base: pass --base")
    skip = set(filter(None, a.skip.split(",")))
    tip = (run("git", "rev-parse", "origin/main") or "").strip()
    if tip and tip != base:
        print("WARN origin/main moved past BASE %s; checking against BASE" % base[:9])
    head = run("git", "rev-parse", "HEAD").strip()
    tmp = tempfile.mkdtemp(prefix="features-v1-check-")
    try:
        tarfile.open(fileobj=io.BytesIO(run("git", "archive", "--format=tar", "HEAD", raw=True))).extractall(tmp, filter="data")
        rep = open(os.path.join(tmp, "docs/migrations/features-v1-report.md"), encoding="utf-8").read()
        rows = [x.split("\t") for x in rep.split("```text\n")[1].split("\n```")[0].split("\n") if x]
        feats = {m[1]: (m[2], m[3]) for m in re.finditer(r"^\| (%s) \| \S+ \| ([0-9a-f]{12}) \| ([0-9a-f]{12}) \|" % ID, rep, re.M)}
        pages = sorted(f for f in os.listdir(os.path.join(tmp, "docs/wiki")) if f.endswith(".md"))
        if run("git", "cat-file", "-e", a.source + "^{commit}") is None:
            sys.exit("REFUSED: frozen source %s is not in this clone" % a.source)
        # done line 1: every ID, page and text hash against the frozen source and the report
        src, now = {}, {}
        for f in pages:
            t = show(a.source, "docs/wiki/" + f)
            src.update(units(t or ""))
            now.update(units(open(os.path.join(tmp, "docs/wiki", f), encoding="utf-8", newline="").read()))
        want = {k: v for k, v in src.items() if k not in skip}
        ok("1 inventory: the report's IDs equal the frozen source's", set(feats) == set(want), ", ".join(sorted(set(feats) ^ set(want))))
        ok("1 hashes: before equals after equals the frozen source and HEAD", all(feats.get(k) == (v, v) and now.get(k) == v for k, v in want.items()),
           ", ".join(k for k, v in want.items() if feats.get(k) != (v, v) or now.get(k) != v))
        ok("1 skipped IDs present on HEAD", all(k in now for k in skip), ", ".join(k for k in skip if k not in now))
        # done line 2: changed files and a byte proof of every page
        diff = run("git", "diff", "--name-only", base, "HEAD")
        if diff is None:
            sys.exit("REFUSED: git diff failed")
        changed = [x for x in diff.split("\n") if x]
        names = {r[1] for r in rows}
        allowed = lambda x: (x.startswith("docs/migrations/") or x.startswith(".loop/goals/migrate-features.") or x == ".loop/kept/migrate-features.tsv"
                             or (x.startswith("docs/wiki/") and x[10:-3] in names) or x in a.allow.split(","))
        extra = [x for x in changed if not allowed(x)]
        ok("2 every changed file is a named page, the report, the scripts, a goal record or an allowed path", not extra, ", ".join(extra))
        print("changed outside the pages and the migration: " + (", ".join(x for x in changed if not x.startswith("docs/wiki/") and not x.startswith("docs/migrations/")) or "none"))
        bad = []
        for n in sorted(names):
            rel = "docs/wiki/%s.md" % n
            new = open(os.path.join(tmp, rel), encoding="utf-8", newline="").read().split("\n")
            new = strip_blocks(new)
            for r in rows:
                if r[1] != n:
                    continue
                pat = ("- %s: **Unreviewed** " % r[2]) if r[0] == "entry" else "Review: **Unreviewed**"
                for i, x in enumerate(new):
                    if x.rstrip("\r").startswith(pat):
                        new[i] = r[6] + ("\r" if x.endswith("\r") else "")
                        break
            if "\n".join(new) != show(base, rel):
                bad.append(n)
        ok("2 each page, blocks stripped and marks restored, equals BASE byte for byte", not bad, ", ".join(bad))
        # done line 3: counts follow from unchanged Revisions (inside the pages), the regression table and the Principles table
        ok("3 test rows and Follows cells untouched (regression.tsv, Principles.md)", not [x for x in changed if x in (".loop/regression.tsv", "docs/wiki/Principles.md")])
        blocks = 0
        for n in names:
            t = open(os.path.join(tmp, "docs/wiki/%s.md" % n), encoding="utf-8", newline="").read()
            blocks += len(re.findall(r"^  - Feature markers v1\r?$", t, re.M))
        ok("3 one marker block per migrated feature", blocks == len(want), "%d blocks, %d features" % (blocks, len(want)))
        broken = []
        for n in names:
            ls = open(os.path.join(tmp, "docs/wiki/%s.md" % n), encoding="utf-8", newline="").read().replace("\r\n", "\n").split("\n")
            for k, x in enumerate(ls):
                m = ENTRY.match(x)
                if not m or m[1] in skip:
                    continue
                subs = 0
                while k + 1 + subs < len(ls) and ls[k + 1 + subs].startswith("  ") and ls[k + 1 + subs].strip():
                    subs += 1
                at = k + 1 + subs
                got = []
                for y in ls[at + 3:]:
                    if not re.match(r"^  - Line \d+: metric .*; test .*$", y):
                        break
                    got.append(y)
                if not (ls[at] == "" and ls[at + 1] == "  - Feature markers v1" and ls[at + 2].startswith("  - Reference: ") and [int(re.match(r"  - Line (\d+):", y)[1]) for y in got] == list(range(1, subs + 1))):
                    broken.append(m[1])
        ok("3 every block has a Reference and one numbered Line per requirement line", not broken, ", ".join(broken))
        # done line 4: marks
        left = []
        for f in os.listdir(os.path.join(tmp, "docs/wiki")):
            if f.endswith(".md"):
                for x in open(os.path.join(tmp, "docs/wiki", f), encoding="utf-8").read().split("\n"):
                    if re.match(r"^- %s: \*\*Reviewed" % ID, x) or x.startswith("Review: **Reviewed"):
                        left.append(f + ": " + x[:40])
        ok("4 no Reviewed mark remains outside the report", not left, "; ".join(left))
        old = set()
        for f in pages:
            for x in (show(base, "docs/wiki/" + f) or "").replace("\r\n", "\n").split("\n"):
                m = re.match(r"^- (%s): \*\*Reviewed \d{4}-\d\d-\d\d\*\*" % ID, x)
                if (m and m[1] not in skip) or x.startswith("Review: **Reviewed"):
                    old.add(x)
        ok("4 the report lists every old mark found on BASE (%d)" % len(old), old == {r[6] for r in rows} and len(rows) == len(old), "%d on BASE, %d in the report" % (len(old), len(rows)))
        notes = open(os.path.join(tmp, ".loop/goals/migrate-features.md"), encoding="utf-8").read()
        ok("4 the PR notes hold the major-gate sentence", SENTENCE in notes)
        # done line 5: a second run on a clone changes nothing
        clone = os.path.join(tmp, "clone")
        run("git", "clone", "-q", "--local", "--no-hardlinks", root, clone)
        again = subprocess.run([sys.executable, "docs/migrations/features-v1.py", "run", "--base", base, "--skip", a.skip], cwd=clone, capture_output=True, text=True)
        status = run("git", "status", "--porcelain", cwd=clone)
        ok("5 a second run exits 0 and leaves an empty diff", again.returncode == 0 and status == "", (again.stdout + again.stderr)[-200:] or "git status failed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("CHECK %s on HEAD %s against BASE %s" % ("FAILED (%d)" % len(fails) if fails else "OK", head[:9], base[:9]))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
