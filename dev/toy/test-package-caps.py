#!/usr/bin/env python3
# windows: ok
# reads: dev/package.py docs/wiki/How-to-use-Guardrails.md
"""dev/package.py's caps: a script of 20,480 bytes or more, or a 100th file, makes it fail; the real tree stays inside both.
GRD-21: the package-limits table on How-to-use-Guardrails is there, and none of ours is looser than Agensi's."""
import importlib.util
import os
import re
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
spec = importlib.util.spec_from_file_location("package", os.path.join(root, "dev", "package.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def failures_of(run):
    package.failures.clear()
    run()
    return [str(f) for f in package.failures]


def script(folder, size):
    os.makedirs(os.path.join(folder, "skills", "workflow-x", "scripts"), exist_ok=True)
    text = "#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n"
    path = os.path.join(folder, "skills", "workflow-x", "scripts", "big.py")
    with open(path, "w", newline="\n") as handle:
        handle.write(text + "#" * (size - len(text) - 1) + "\n")
    return "skills/workflow-x/scripts/big.py"


with tempfile.TemporaryDirectory() as tmp:
    ok = failures_of(lambda: package.check_scripts(tmp, [script(tmp, package.MAX_SCRIPT - 1)]))
    check("a script of 20,479 bytes passes", not ok)
    big = failures_of(lambda: package.check_scripts(tmp, [script(tmp, package.MAX_SCRIPT)]))
    check("a script of 20,480 bytes fails", any("20 KB" in f for f in big))

with tempfile.TemporaryDirectory() as tmp:
    names = []
    for n in range(package.MAX_FILES + 1):
        name = "f%03d.md" % n
        with open(os.path.join(tmp, name), "w") as handle:
            handle.write("x\n")
        names.append(name)
    check("100 files pass the size rule", not [f for f in failures_of(lambda: package.check_files(tmp, names[:package.MAX_FILES])) if "files" in f])
    check("a 101st file fails it", any("101" in f for f in failures_of(lambda: package.check_files(tmp, names))))

shipped = package.walk(root)
check("the real tree ships at most 100 files (%d)" % len(shipped), len(shipped) <= package.MAX_FILES)
long = [r for r in shipped if r.endswith(".py") and len(package.read(root, r)) >= package.MAX_SCRIPT]
check("every real script is under 20,480 bytes" + (": " + ", ".join(long) if long else ""), not long)

UNIT = {"MB": 1024 * 1024, "KB": 1024}
HOWTO = os.path.join(root, "docs", "wiki", "How-to-use-Guardrails.md")


def figure(cell):
    m = re.match(r"([\d,]+)\s*(files|MB|KB|bytes|characters)\b", cell)
    return (int(m.group(1).replace(",", "")) * UNIT.get(m.group(2), 1), m.group(2) in UNIT or m.group(2)) if m else None


def limits_problems(text):
    """What is wrong with the package-limits table in TEXT: missing, a date missing, ours looser than Agensi's, or ours not dev/package.py's."""
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in text.splitlines()
            if l.startswith("| ") and "|---" not in l and not l.startswith("| Limit")]
    head = re.search(r"^\| Limit \| Agensi's figure \| Ours \| Date Agensi's page was read \|$", text, re.M)
    if not head or len(rows) < 3:
        return ["the package-limits table is missing"]
    bad, want = [], {"Files per package (upload from an agent)": package.MAX_FILES,
                     "Package size (upload from an agent": package.MAX_BYTES, "Script size": package.MAX_SCRIPT}
    for row in [r for r in rows if len(r) >= 4 and r[0] not in ("You say",)]:
        if not re.fullmatch(r"20\d\d-\d\d-\d\d", row[3]):
            continue
        theirs, ours = figure(row[1]), figure(row[2])
        if theirs and ours and theirs[1] in (ours[1], "KB", "MB") and ours[0] > theirs[0]:
            bad.append("%s: ours %s is looser than Agensi's %s" % (row[0], row[2], row[1]))
        for label, value in want.items():
            if row[0].startswith(label) and (not ours or ours[0] != value):
                bad.append("%s: ours is not dev/package.py's %d" % (row[0], value))
    for label in want:
        if not [r for r in rows if r[0].startswith(label) and len(r) >= 4 and re.fullmatch(r"20\d\d-\d\d-\d\d", r[3])]:
            bad.append("no dated row for " + label)
    return bad


doc = open(HOWTO, encoding="utf-8").read()
check("the package-limits table is there, dated, and none of ours is looser than Agensi's", not limits_problems(doc))
check("control: no table fails", any("missing" in b for b in limits_problems(doc.replace("| Limit |", "| Item |"))))
check("control: ours looser (101 files) fails", any("looser" in b for b in limits_problems(doc.replace("| 100 files (MAX_FILES)", "| 101 files (MAX_FILES)", 1))))
check("control: ours looser (6 MB) fails", any("looser" in b for b in limits_problems(doc.replace("5,000,000 bytes for the whole package", "6 MB for the whole package", 1))))
check("control: no date fails", any("no dated row" in b for b in limits_problems(doc.replace("| 2026-11-18 |", "| |"))))
sys.exit(1 if fails else 0)
