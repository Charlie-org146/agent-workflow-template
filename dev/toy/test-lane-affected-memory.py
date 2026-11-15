#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/lanes_cli.py
# reads: skills/workflow-regression/scripts/narrow.py
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/slots.py
"""lane-affected-memory (#4151): `lanes_cli.py affected` keeps its memory bounded and gives the same answer.

A toy repo whose one row reaches 400 files of 300 KB (120 MB of text) and 30 small rows that share them; `affected` runs for
a deleted file and an unmapped one, the two cases that scan every reached file's text. The process's peak memory must stay
under 100 MB (holding every text, as it did, passes 120 MB), and the output must be the known answer."""
import os
import subprocess
import sys
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.environ.get("LANES_SCRIPTS_DIR") or os.path.join(root, "skills", "workflow-regression", "scripts")  # another copy of the scripts, to prove the test can fail
BOUND = 100  # MB
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


DRIVER = r'''
import os, sys
sys.path.insert(0, sys.argv[1])
import lanes_cli
sys.argv = ["lanes_cli.py", "affected", "--root", os.getcwd(), "gone.txt", "other/new.txt"]
try:
    lanes_cli.main()
except SystemExit:
    pass
if os.name == "nt":
    import ctypes
    from ctypes import wintypes
    class C(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("pf", wintypes.DWORD), ("peak", ctypes.c_size_t)] + [("x%d" % i, ctypes.c_size_t) for i in range(7)]
    c = C(); c.cb = ctypes.sizeof(c)
    k = ctypes.windll.kernel32; k.GetCurrentProcess.restype = wintypes.HANDLE
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(C), wintypes.DWORD]
    ctypes.windll.psapi.GetProcessMemoryInfo(k.GetCurrentProcess(), ctypes.byref(c), c.cb)
    peak = c.peak
else:
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024)
print("PEAK_MB %d" % (peak // 1000000), file=sys.stderr)
'''

with tempfile.TemporaryDirectory() as repo:
    os.makedirs(os.path.join(repo, ".loop"))
    os.makedirs(os.path.join(repo, "scripts"))
    os.makedirs(os.path.join(repo, "data"))
    os.makedirs(os.path.join(repo, "other"))
    open(os.path.join(repo, "other", "new.txt"), "w").close()
    for n in range(400):
        with open(os.path.join(repo, "data", "f%d.txt" % n), "w") as handle:
            handle.write(("line %d of filler text that names nothing\n" % n) * 7000)
    rows = []
    for n in range(30):
        name = "scripts/row%d.sh" % n
        with open(os.path.join(repo, name), "w") as handle:
            handle.write("#!/bin/bash\n# reads: data/\ncat data/f0.txt\n")
        rows.append("row%d\tland\tbash %s\tREG-7" % (n, name))
    with open(os.path.join(repo, ".loop", "regression.tsv"), "w") as handle:
        handle.write("\n".join(rows) + "\n")
    subprocess.run(["git", "init", "-q", repo], check=True)
    start = time.time()
    done = subprocess.run([sys.executable, "-c", DRIVER, scripts], cwd=repo, capture_output=True, text=True)
    took = time.time() - start
    peak = int(done.stderr.rsplit("PEAK_MB", 1)[1].split()[0]) if "PEAK_MB" in done.stderr else -1
    lines = done.stdout.replace("\\", "/").splitlines()
    print("peak %d MB in %.0f s" % (peak, took))
    check("affected finishes", done.returncode == 0 and bool(lines))
    check("peak memory stays under %d MB" % BOUND, 0 < peak < BOUND)
    check("it picks the rows that name the deleted file, none here, and notes both paths",
          any(l.startswith("DELETED gone.txt") for l in lines) and any(l.startswith("UNMAPPED other/new.txt") for l in lines)
          and lines[0].startswith("AFFECTED"))
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import narrow  # noqa: E402

check("a text that imports a deleted module names it, and a longer module name does not",
      narrow.names("from a import b
import os, gone
", "x/gone.py") and not narrow.names("import gonex
", "x/gone.py"))
sys.exit(1 if fails else 0)
