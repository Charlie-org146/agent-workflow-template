#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/ skills/workflow-docs/scripts/ skills/workflow-health/scripts/ skills/workflow-monitoring/scripts/
# reads: skills/workflow-regression/scripts/ skills/workflow-release/scripts/ skills/workflow-setup/scripts/
# Issue 2871: a script under skills/*/scripts that names a POSIX-only call (fcntl, os.getuid, os.killpg, os.getpgrp,
# os.O_NOFOLLOW, signal.SIGHUP, os.kill(pid, 0), os.WNOHANG) without a guard breaks native Windows, and nothing on a Linux
# lane saw it. A name is guarded when its line or one of the 3 lines above holds hasattr(, getattr(, os.name, sys.platform,
# "posix-only" or "windows:", when the line is a comment or docstring text, or when it is the try: import fcntl shim.
# Value: protects=a POSIX-only call never lands unguarded on main (issue 2871); fails_when=a script names one of the
# calls with no guard; why_new=the Windows fixes each landed after a break; seam=none; no_claim=a run on Windows
import os
import re
import sys
import tempfile

NAMES = {
    "fcntl": r"^\s*(?:import fcntl\b|from fcntl import)",
    "os.getuid": r"\bos\.getuid\b",
    "os.killpg": r"\bos\.killpg\b",
    "os.getpgrp": r"\bos\.getpgrp\b",
    "os.O_NOFOLLOW": r"\bos\.O_NOFOLLOW\b",
    "signal.SIGHUP": r"\bsignal\.SIGHUP\b",
    "os.kill(pid, 0)": r"\bos\.kill\([^,()]+,\s*0\)",
    "os.WNOHANG": r"\bos\.WNOHANG\b",
}
GUARD = re.compile(r"hasattr\(|getattr\(|\bos\.name\b|sys\.platform|posix-only|windows:")


def shim(lines, i):
    """True for `import fcntl` right under a try: (the shim; callers use the shim's fcntl name, not the module)."""
    return lines[i].strip() == "import fcntl" and i > 0 and lines[i - 1].strip() == "try:"


def scan(root):
    """Every unguarded use, as "relative/path.py:line name"."""
    found = []
    folder = os.path.join(root, "skills")
    for skill in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        scripts = os.path.join(folder, skill, "scripts")
        for name in sorted(os.listdir(scripts)) if os.path.isdir(scripts) else []:
            if not name.endswith(".py"):
                continue
            path = os.path.join(scripts, name)
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
            quoted = False
            for i, line in enumerate(lines):
                inside = quoted
                if line.count('"""') % 2:
                    quoted = not quoted
                code = line.split("#")[0]
                if inside or quoted and line.lstrip().startswith('"""') or line.lstrip().startswith(("#", '"', "'")) or not code.strip():
                    continue
                for label, pattern in NAMES.items():
                    if re.search(pattern, code) and not shim(lines, i) and not GUARD.search("\n".join(lines[max(0, i - 3):i + 1])):
                        found.append("%s:%d %s" % (os.path.relpath(path, root).replace(os.sep, "/"), i + 1, label))
    return found


def main():
    fails = 0

    def check(ok, message):
        nonlocal fails
        print(("PASS: " if ok else "FAIL: ") + message)
        fails += 0 if ok else 1

    real = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    bad = scan(real)
    check(not bad, "no script under skills/*/scripts names a POSIX-only call without a guard" + ("" if not bad else ": " + "; ".join(bad[:6])))
    with tempfile.TemporaryDirectory() as tmp:
        scripts = os.path.join(tmp, "skills", "demo", "scripts")
        os.makedirs(scripts)
        sample = {
            "fcntl": "import fcntl\nfcntl.flock(1, 2)\n",
            "os.getuid": "uid = os.getuid()\n",
            "os.killpg": "os.killpg(pid, 9)\n",
            "os.getpgrp": "group = os.getpgrp()\n",
            "os.O_NOFOLLOW": "flags = os.O_RDWR | os.O_NOFOLLOW\n",
            "signal.SIGHUP": "signal.signal(signal.SIGHUP, handler)\n",
            "os.kill(pid, 0)": "os.kill(pid, 0)\n",
            "os.WNOHANG": "done = os.waitpid(pid, os.WNOHANG)\n",
        }
        for label, text in sample.items():
            open(os.path.join(scripts, "demo.py"), "w").write("import os\nimport signal\n" + text)
            hit = scan(tmp)
            check(any(h.startswith("skills/demo/scripts/demo.py:") and h.endswith(" " + label) for h in hit), "%s with no guard fails the scan naming its file and line" % label)
            guarded = "import os\nimport signal\nif hasattr(os, 'fork'):  # posix-only branch\n    " + text.replace("\n", "\n    ").rstrip(" ")
            open(os.path.join(scripts, "demo.py"), "w").write(guarded)
            check(not scan(tmp), "%s behind a guard passes" % label)
        open(os.path.join(scripts, "demo.py"), "w").write("try:\n    import fcntl\nexcept ImportError:\n    fcntl = None\n")
        check(not scan(tmp), "import fcntl inside a try: shim passes")
        open(os.path.join(scripts, "demo.py"), "w").write("# os.getuid is POSIX-only\n\"\"\"os.killpg\"\"\"\n")
        check(not scan(tmp), "a comment or a docstring line naming a call passes")
    print("ALL PASS" if not fails else "%d FAILED" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
