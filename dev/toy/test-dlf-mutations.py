#!/usr/bin/env python3
# windows: ok
# reads: skills/ dev/toy/dlf-gh dev/toy/test-dlf-stops.py dev/toy/test-dlf-wire.py dev/toy/test-dlf-budget.py dev/toy/test-dlf-ledger.py dev/toy/test-dlf-scan.py dev/toy/test-dlf-release.py
"""DLF-1 done line 1: each rule has a mutation control. A copy of the skills is broken one rule at a time (one line of the shipped code),
the toy that guards that rule is run against the broken copy and must FAIL, and the unbroken copy must pass first. So each case fails on
a fixture that breaks only that rule. No network; each run uses its own temp home."""
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
copy = tempfile.mkdtemp(prefix="dlf-mut-")
shutil.copytree(os.path.join(root, "skills"), os.path.join(copy, "skills"), symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
os.makedirs(os.path.join(copy, "dev", "toy"))
for name in os.listdir(os.path.join(root, "dev", "toy")):
    if name.startswith("test-dlf-") or name == "dlf-gh":
        shutil.copy2(os.path.join(root, "dev", "toy", name), os.path.join(copy, "dev", "toy", name))
D, R = "skills/workflow-delivery/scripts/dlf.py", "skills/workflow-release/scripts/release.py"
G = "skills/workflow-delivery/scripts/goal.py"
MUTATIONS = [  # (rule, file, the line to break, its broken form, the toy that guards it)
    ("DLF-1.1 a stop becomes a line", D, 'return "continue", lid or status', 'return "wait", "broken"', "wire"),
    ("DLF-1.1 a plan past its cap is its own stop", G, '"plan" if re.search(', '"choice" if re.search(', "wire"),
    ("DLF-1.2 the budget rises by the rule", D, "min(spent + left, 2 * estimate)", "held", "budget"),
    ("DLF-1.2 both limits keep their raise", D, "                held[name] = new\n", "", "budget"),
    ("DLF-1.2 a cap line is filed in the same check as a raise", D, "            if on and est and capped:", "            elif on and est and capped:", "wire"),
    ("DLF-1.2 past the cap one line is filed", D, "            if on and est and capped:", "            if False:", "wire"),
    ("DLF-1.3 a loosened test waits", D, "            return True\n    return False", "            pass\n    return False", "stops"),
    ("DLF-1.3 an unknown class waits", D, ' or cls and cls not in SAFETY + ("other",)', "", "stops"),
    ("DLF-1.3 every outside write is scanned", D, 'if got["state"] not in ("clean", "off"):', "if False:", "scan"),
    ("DLF-1.3 auto_approve never skips the table", G, "    if held is not None:\n        return held and", "    if False:\n        return held and", "wire"),
    ("DLF-1.3 a pending result with no PENDING line is classified", G, 'pending or [why or "a pending decision with no context"] * (result == "pending")', "pending", "wire"),
    ("DLF-1.4 the cut refuses while a line is open", D, 'if l["state"] == "open"), key=', "if False), key=", "ledger"),
    ("DLF-1.4 only the owner accepts", D, 'elif who == owner and l["state"] in ("open", "accepted")', 'elif l["state"] in ("open", "accepted")', "ledger"),
    ("DLF-1.4 no owner login fails closed", D, "if lines and not owner:", "if False:", "ledger"),
    ("DLF-1.4 a queued line stays until filed", D, '    todo = mem(runs, slug)["queue"]\n', '    held = mem(runs, slug)\n    todo, held["queue"] = held["queue"], []\n    keep(runs, slug, held)\n', "ledger"),
    ("DLF-1.1 a failed second lookup queues", D, "    if lowest is None:\n        return None\n", "", "ledger"),
    ("DLF-1.1 a different choice at the same position is a new line", G, "hashlib.sha1(p.encode()).hexdigest()[:6]", '""', "wire"),
    ("DLF-1.3 a secret in a pending decision is never held or printed", G, '    return redact("%s left this for you', '    return str("%s left this for you', "wire"),
    ("DLF-1.3 the cut refuses while a refused text is held", D, '* bool(held.get("local"))', "* False", "ledger"),
    ("DLF-1.1 a failed read queues, a scan failure keeps local", D, 'len(mem(runs, slug)["local"]) > n0', 'mem(runs, slug)["local"]', "ledger"),
    ("DLF-1.4 queued lines are re-filed", D, "    retry(top, runs, slug)\n    subject = classify(", "    subject = classify(", "ledger"),
    ("DLF-1.4 the debt gate fails closed", R, "    if not os.path.isfile(path):", "    if False:", "release"),
    ("DLF-1.5 the setting turns a scope off", D, "if isinstance((held.get(scope) or {}).get(ident), bool):", "if False:", "wire"),
]


def run(toy):
    return subprocess.run([sys.executable, os.path.join(copy, "dev", "toy", "test-dlf-%s.py" % toy)], capture_output=True, text=True, timeout=600).returncode


failed = []
for toy in sorted({m[4] for m in MUTATIONS}):
    ok = run(toy) == 0
    print(("PASS: " if ok else "FAIL: ") + "the unbroken copy passes test-dlf-%s.py" % toy)
    ok or failed.append(toy)
for rule, path, old, new, toy in MUTATIONS:
    full = os.path.join(copy, path)
    text = open(full).read()
    if old not in text:
        print("FAIL: %s: the line to break is not in %s" % (rule, path))
        failed.append(rule)
        continue
    open(full, "w").write(text.replace(old, new, 1))
    try:
        red = run(toy) != 0
    finally:
        open(full, "w").write(text)
    print(("PASS: " if red else "FAIL: ") + "%s: broken alone, test-dlf-%s.py fails" % (rule, toy))
    red or failed.append(rule)
sys.exit(1 if failed else 0)
