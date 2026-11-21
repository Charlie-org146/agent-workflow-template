#!/usr/bin/env python3
# reads: skills/workflow-docs/scripts/sections.py skills/workflow-docs/scripts/pageformat.py skills/workflow-docs/scripts/render.py
# reads: README.md docs/wiki/Home.md docs/wiki/Principles.md .loop/regression.tsv .loop/regression-runs.tsv
# windows: ok
"""DEL-21 (o291, o293): a principle table's Follows cell is a tagged bullet list, Adoption is the adopted sources over all sources (a bullet can name several),
Confidence is the share of the requirement's tests passing on the latest run, and docs check refuses an untagged line.
Value: protects=the Adoption and Confidence columns are computed, never typed, and a Follows line always carries a tag;
fails_when=an old 'a; b: adapted' cell is not migrated, the score counts adapted or planned as adopted, a failing test does not
lower Confidence, or an untagged line passes docs check; why_new=adoption read one trailing tag so it was 0% and Confidence was blank;
seam=none; no_claim=how the pages read."""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TOP, "skills", "workflow-docs", "scripts"))
sys.dont_write_bytecode = True
import sections as s  # noqa: E402

fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += not ok


old = "[A](https://a.test); [B](https://b.test): adapted"
new = s.bullets(old)
check("an old cell with one trailing tag becomes one tagged bullet per source", new == "- [A](https://a.test): adapted<br>- [B](https://b.test): adapted")
check("an old own tag stays own, and a source's own tag is kept", s.bullets("[A](u): adopted; [B](v): own today") == "- [A](u): adopted<br>- [B](v): own")
check("a bullet cell is migrated to itself", s.bullets(new) == new)
check("Adoption is the adopted lines over all lines", s.adoption("- [A](u): adopted<br>- [B](v): adapted<br>- [C](w): planned") == 33 and s.adoption("- [A](u): adopted") == 100)
check("negative control: adapted and planned lines count 0, and no lines is not measured", s.adoption("- [A](u): adapted<br>- [B](v): planned") == 0 and s.adoption("") is None)
mixed = "- [A](u): adapted; [B](v): adopted"
check("each source on a bullet counts with its own tag", s.follows(mixed) == [("[A](u)", "adapted"), ("[B](v)", "adopted")] and s.adoption(mixed) == 50)
check("single-source bullets keep their main values, including own", all(s.adoption(cell) == value for cell, value in [
    ("- A: adopted", 100), ("- A: adapted", 0), ("- A: planned", 0), ("- A: own", 0),
    ("- A: adopted<br>- B: adapted<br>- C: planned<br>- D: own", 25)]))
for source in ("[A; B](u)", "[A: adopted; B](u)", "[A](https://a.test/x; y)", "A; B"):
    cell = "- %s: adapted; [C](v): adopted" % source
    check("negative control: a semicolon inside source %s does not split" % source,
          s.follows("- %s: adapted" % source) == [(source, "adapted")] and
          s.follows(cell) == [(source, "adapted"), ("[C](v)", "adopted")] and s.adoption(cell) == 50)
check("negative control: an unknown tag does not split a bullet", s.follows("- A: unknown; B: adopted") == [("A: unknown; B", "adopted")])
for cell, sources, share in [
        ("- a: adopted; b: adapted; c: planned", 3, 33), ("- a: adopted; b: adapted; c", 1, 0), ("- a: adopted;", 1, 0),
        ("- a: adopted;b: adapted", 1, 0), ("- [A: adopted; B](u: adapted", 1, 0), ("- a: Adopted; b: adapted", 1, 0),
        ("- a: adopted; ; b: adapted", 1, 0), ("- a: adopted; b: unknown; c: adapted", 1, 0), ("- a: adopted; [b: adapted", 1, 0),
        ("- a: adopted; [a): adapted", 1, 0), ("- a: adopted (v2); b: adapted", 1, 0), ("- a: adopted; b", 1, 0),
        ("- [outer [inner] label: adopted; tail](u): adapted", 1, 0)]:
    check("edge case %s gives %d source(s) and %d" % (cell, sources, share), len(s.follows(cell)) == sources and s.adoption(cell) == share)
for cell, sources, share in [
        (r"- [A\] label](u): adapted; [B](v): adopted", 2, 50), ("- `x: adopted; y`: adapted; [B](v): adopted", 2, 50),
        ("- `tool: adopted; extra`: adapted; [B](v): adapted", 2, 0), ("- `a: adopted; b: adapted", 1, 0),
        ("-  A: adopted", 1, 100), ("- : adopted", 1, 100)]:
    check("review case %s gives %d source(s) and %d" % (cell, sources, share), len(s.follows(cell)) == sources and s.adoption(cell) == share)
check("a long semicolon-heavy bullet is read in one pass", len(s.follows("- " + "a; " * 20000 + "z: adopted")) == 1 and len(s.follows("- " + "a; " * 20000 + "b: adapted; c: adopted")) == 2)

# An independent count of the sources on a Follows cell, made outside follows(): strip bracket and parenthesis pairs from the inside
# out, then count ': <tag>' at a '; ', a line break or the end; a bullet with no tag counts one. It disagrees with follows() on a
# bullet with two or more tagged parts that follows() reads as one (for example 'a: adopted; b: adapted; c'); a single-token
# half-tagged bullet such as 'a: adopted; b' is not flagged, and the hand-counted cells below say what is right.
INNER, TOKEN = re.compile(r"\[[^\[\]]*\]|\([^()]*\)"), re.compile(r": (?:adopted|adapted|planned|own)(?=; |<br>|$)")


def expected(cell):
    total = 0
    for bullet in cell.split("<br>"):
        if bullet.startswith("- "):
            text = bullet[2:]
            while INNER.search(text):
                text = INNER.sub("", text)
            total += max(1, len(TOKEN.findall(text)))
    return total


def main_reading(cell):  # main's counter read one source per bullet
    return len([b for b in cell.split("<br>") if b.startswith("- ")])


with open(os.path.join(TOP, "README.md"), encoding="utf-8") as readme:
    cells = [c.strip() for line in readme.read().split("\n") if line.startswith("|") for c in s.SPLIT.split(line.strip()[1:-1]) if c.strip().startswith("- ")]
check("README: at least one Follows cell was found", len(cells) > 0)
for cell in cells:
    if expected(cell) != len(s.follows(cell)):
        print("MISMATCH: expected %d source(s), follows() gave %d (brackets stripped by innermost pairs): %s" % (expected(cell), len(s.follows(cell)), cell[:90]))
        fails += 1
check("README: the independent source count equals follows() on every Follows cell (%d cells)" % len(cells), all(expected(c) == len(s.follows(c)) for c in cells))
check("negative control: the README check fails on main's one-source reading of a two-source cell, and passes on follows()",
      expected(mixed) == 2 and main_reading(mixed) != expected(mixed) and len(s.follows(mixed)) == expected(mixed))
check("negative control: the README check flags a half-tagged bullet with two tagged parts", expected("- a: adopted; b: adapted; c") != len(s.follows("- a: adopted; b: adapted; c")))
for name, cell, sources, share in [
        ("HLT-2 shaped", "- [A](u): adapted; [B](v): adopted<br>- [C](w): adopted", 3, 67),
        ("MCH-1 shaped", "- [A](u): adopted; [B](v): adapted<br>- [C](w): own<br>- [D](x): planned", 4, 25),
        ("DEL-1 shaped, grouped references count once", "- [A](u), [B](v), [C](w): adopted<br>- [D](x): adapted<br>- E: own", 3, 33),
        ("nested brackets", "- [outer [inner] label: adopted; tail](u): adapted", 1, 0),
        ("half-tagged", "- a: adopted; b: adapted; c", 1, 0)]:
    check("hand-counted cell %s: %d source(s), %d" % (name, sources, share), len(s.follows(cell)) == sources and s.adoption(cell) == share)
tests = [["t1", "land", "x", "DEL-1"], ["t2", "land", "x", "DEL-1"], ["t3", "land", "x", "DEL-2"], ["t4", "land", "x", "OTHER"]]
runs = {"t1": "PASS", "t2": "FAIL", "t3": "PASS"}
row = "[DEL-1 Every change (absorbs DEL-2)](https://x.test/wiki/Delivery) ([DEL-1 flow](f.svg))"
check("Confidence is the passing share of the requirement's tests, absorbed IDs included", s.confidence(row, tests, runs) == "67% (2 of 3)")
check("negative control: a failing test lowers it, and no tests is not measured", s.confidence(row, tests, dict(runs, t1="FAIL")) == "33% (1 of 3)" and s.confidence("[ZZ-9 none](u)", tests, runs) == s.UNDATA)
table = "| Requirement | Summary | Follows | Feature | Adoption | Confidence |\n|---|---|---|---|---|---|\n| ROW | text | - [A](u): adopted<br>- [B](v): adapted | F | 0% |  |\n".replace("ROW", row)
done = s.tables(table, tests, runs)
check("tables computes Adoption and Confidence into the row and a score line under the table", "| 50% | 67% (2 of 3) |" in done and "Adoption: 50% " in done)
check("negative control: a typed Confidence is overwritten, and kept only when the check asks", "| 50% | 67% (2 of 3) |" in s.tables(table.replace("0% |  |", "0% | 99% (1 of 1) |"), tests, runs) and "99% (1 of 1)" in s.tables(table.replace("0% |  |", "0% | 99% (1 of 1) |"), tests, runs, True))

# docs check: a copy of this repo's front pages, one Follows line left untagged
import render  # noqa: E402

tmp = tempfile.mkdtemp()
try:
    for rel in ("README.md", ".loop/config.json", "skills/workflow-health/references/commands.md"):
        os.makedirs(os.path.dirname(os.path.join(tmp, rel)) or tmp, exist_ok=True)
        shutil.copy(os.path.join(TOP, rel), os.path.join(tmp, rel))
    shutil.copytree(os.path.join(TOP, "docs", "wiki"), os.path.join(tmp, "docs", "wiki"))
    names = sorted(x[:-3] for x in os.listdir(os.path.join(tmp, "docs", "wiki")) if x.endswith(".md") and not x.startswith(("How-to", "Home", "Principles", "Tests", "Roadmap")))
    found = lambda: [x for x in render.front(tmp, names) if "Follows" in x[2]]
    check("docs check accepts the tagged Follows lists of this repo's README", not found())
    readme = open(os.path.join(tmp, "README.md"), encoding="utf-8", newline="").read()
    bad = re.sub(r"(<br>- \[[^\]]*\]\([^)]*\)): (adopted|adapted)", r"\1", readme, 1)
    check("the untagged-line sample differs from the README", bad != readme)
    open(os.path.join(tmp, "README.md"), "w", encoding="utf-8", newline="").write(bad)
    check("negative control: docs check refuses a Follows line with no tag", len(found()) == 1)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASS" if not fails else "%d FAILED" % fails)
sys.exit(1 if fails else 0)
