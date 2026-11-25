#!/usr/bin/env python3
"""Check the package against the Agensi rules and build the ZIP.

usage: package.py [--root DIR] [--out FILE] [--timeout SECONDS]

The ZIP holds the skills, shared/ (the files every skill reads), PACKAGE.json (the version from VERSION, a hash of every
skill file and the newest changelog entries, which update.py reads) and the same stamp as shared/workflow-package.json.

Checks run in the order of the roadmap's rule table. Every failure is printed as
`FAIL <rule>: <what>`. One failure means no ZIP and exit 1.

Never hangs: each script's --help run gets no stdin (/dev/null) and CHILD_SECONDS (PACKAGE_CHILD_SECONDS, else 30), in its own process group that is
killed when the time is up, and copies keep symlinks as links. The whole run has a hard bound (--timeout, else
PACKAGE_TIMEOUT, else 300 seconds): when it is hit, package.py kills any child, prints one line
`TIMEOUT: package.py stopped after N seconds waiting on <what>` and exits 3. SIGTERM, SIGINT and SIGHUP also kill the
child's group before exiting, and the ZIP is written to a .part file beside --out and renamed, so a stopped run leaves no
half ZIP. An inherited ignore of SIGINT or SIGHUP (nohup) is kept.

Safety output: no line ever prints matched text, a private pattern or a path holding a match. A Safety failure reads
`FAIL Safety: <kind> in <where>, line <n>`: kind is secret, obfuscation or encoded text, instruction aimed at the agent,
dangerous command, or private prefix #k (k: entry k of leak_prefixes in $LOOP_FLOW, else ~/.workflow-loop/flow.json);
where is the path, or `a path matching <kind>` when the path itself matches (one `private prefix #k in a path` line
names the lowest k). Any other failure keeps its rule text and withholds the part read from a file or a child when it,
or the text it was cut from, holds a match: find it locally with the lists below and your leak_prefixes, fix it, rerun.
A TIMEOUT or STOPPED label that holds a match reads `a shipped file (name withheld)`. An unexpected error prints its
type on stderr and exits 4, never a traceback. Exit codes: 0 pass, 1 refused, 3 timeout, 4 unexpected error. CI has no
private list, so it reports only the built-in kinds. Changed in v1.1.0: this Safety form (before, the match and the
pattern were printed), one line for a path matching several prefixes, the withheld notices and exit 4.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import zipfile

SHIPPED = ["skills", "listing.json", "README.md", "LICENSE"]
BAD_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".pytest_cache", ".mypy_cache", "vendor"}
MAX_FILES, MAX_BYTES, MAX_SCRIPT = 200, 5000000, 20 * 1024
STATIC = False
SECRETS = [r"AKIA[0-9A-Z]{16}", r"gh[pousr]_[A-Za-z0-9]{30,}", r"sk-[A-Za-z0-9]{20,}", r"xox[baprs]-[A-Za-z0-9-]{10,}",
           r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"\s]{8,}"]
OBFUSCATION = [r"base64\.b64decode", r"b64decode", r"\bexec\s*\(", r"\beval\s*\(", r"\bmarshal\b", r"\bpickle\b",
               r"codecs\.decode", r"\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){5,}", r"[A-Za-z0-9+/]{100,}={0,2}", r"__import__"]
AGENT_AIMED = [r"(?i)ignore (all |any )?(previous|prior|above) instructions", r"(?i)do not (tell|inform|mention to) the user",
               r"(?i)without (telling|asking|informing) the user", r"(?i)dangerously-skip-permissions", r"bypassPermissions",
               r"(?i)disregard (your|the) (system|safety)", r"(?i)you must (secretly|silently) "]
DANGEROUS = [r"\bos\.system\(", r"chmod\s+777", r"\brm\s+-rf\s+/(\s|$)", r"\b(curl|wget)\b[^\n|]*\|\s*(ba)?sh\b"]
INJECTION = [r"(?i)ignore previous instructions", r"(?i)do not tell the user", r"(?i)\bsecretly\b"]
SHARED = {"skills/loop-files.md": "shared/loop-files.md"}  # in a pack, only shared/ reaches every skill
LIMITS = {"tags": 10, "keywords": 10, "use_cases": 8}
try:
    CHILD_SECONDS = max(1, int(os.environ.get("PACKAGE_CHILD_SECONDS") or 30))
except ValueError:
    CHILD_SECONDS = 30
failures = []
waiting = {"on": "starting", "child": None, "part": None, "lone": None, "stopping": False}
STOP_SIGNALS = [getattr(signal, n) for n in ("SIGALRM", "SIGTERM", "SIGINT", "SIGHUP") if hasattr(signal, n)]


def wait_on(what):
    waiting["on"] = "a shipped file (name withheld)" if hit(what) else what


def stop(line, code):
    """Kill the running child's group, drop a half-written ZIP, print one line and exit at once."""
    if waiting["stopping"]:  # a second signal while stopping: the first one finishes the job
        return
    waiting["stopping"] = True
    child = waiting["child"]
    if child is not None:
        kill_group(child)
    for path in (waiting["part"],):
        try:
            if path:
                os.remove(path)
        except OSError:
            pass
    if waiting["lone"]:
        shutil.rmtree(waiting["lone"], ignore_errors=True)
    if line:
        os.write(1, (line + "\n").encode("utf-8", "replace"))  # never print() in a handler: it may interrupt one
    os._exit(code)


def on_timeout(seconds):
    return lambda *_: stop("TIMEOUT: package.py stopped after %d seconds waiting on %s" % (seconds, waiting["on"]), 3)


def on_signal(signum, frame):
    stop("STOPPED: package.py got signal %d while waiting on %s" % (signum, waiting["on"]), 128 + signum)


def arm(seconds):
    """The hard bound: SIGALRM where it exists, else a timer thread (Windows). Outside kills also stop the child."""
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, on_timeout(seconds))
        signal.alarm(max(1, seconds))
    else:
        timer = threading.Timer(max(1, seconds), on_timeout(seconds))
        timer.daemon = True
        timer.start()
    for name in ("SIGTERM", "SIGINT", "SIGHUP"):
        if hasattr(signal, name) and signal.getsignal(getattr(signal, name)) is not signal.SIG_IGN:  # keep nohup's ignore
            signal.signal(getattr(signal, name), on_signal)


def kill_group(proc):
    try:
        if hasattr(os, "killpg"):
            os.killpg(proc.pid, signal.SIGKILL)
        else:  # Windows: the child and its whole tree
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except (OSError, ProcessLookupError, subprocess.SubprocessError):
        pass


def run_alone(cmd, cwd, what):
    """Run one child with no stdin and a time limit; kill its whole process group when the limit is hit."""
    wait_on(what)
    group = ({"start_new_session": True, "preexec_fn": lambda: signal.pthread_sigmask(signal.SIG_UNBLOCK, STOP_SIGNALS)}
             if hasattr(os, "killpg") else {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)})
    # the child must not inherit the block below, or it would ignore a reaper's TERM
    mask = hasattr(signal, "pthread_sigmask")
    if mask:  # no stop signal between the child starting and its being recorded, so none escapes the bound
        signal.pthread_sigmask(signal.SIG_BLOCK, STOP_SIGNALS)
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace", **group)  # UTF-8 whatever the locale
        waiting["child"] = proc
    finally:
        if mask:
            signal.pthread_sigmask(signal.SIG_UNBLOCK, STOP_SIGNALS)
    try:
        out, err = proc.communicate(timeout=CHILD_SECONDS)
        return proc.returncode, err
    except subprocess.TimeoutExpired:
        kill_group(proc)
        try:  # a detached grandchild may still hold the pipes: do not wait on it
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            for pipe in (proc.stdout, proc.stderr):
                pipe.close()
            proc.wait(timeout=5)
        return None, ""
    finally:
        waiting["child"] = None


PRIVATE = []  # (k, compiled pattern), loaded once by load_private before any check
WITHHELD = "(withheld: it held a %s match%s; find it locally with the lists in dev/package.py and your leak_prefixes, fix it, then rerun; see --help)"


def groups():
    return (("secret", SECRETS), ("obfuscation or encoded text", OBFUSCATION), ("instruction aimed at the agent", AGENT_AIMED + INJECTION),
            ("dangerous command", DANGEROUS))


def hit(text):
    """The kind of the first Safety match in text (the private list first), else None."""
    for k, rx in PRIVATE:
        if rx.search(text):
            return "private prefix #%d" % k
    for group, patterns in groups():
        if any(re.search(p, text) for p in patterns):
            return group
    return None


def where(rel):
    """The path, or its kind when the path itself holds a match: no path, hash or other locator (a hash of a tracked
    path can be reversed over the tracked paths). A line number stays: in a hidden file it narrows nothing to open."""
    kind = hit(rel)
    return "a path matching " + kind if kind else rel


def line_of(text, match):
    return text.count("\n", 0, match.start()) + 1


def fail(rule, text, derived="", after="", source=None, origin=""):
    """Every failure line goes through here. The derived part (read from a shipped file or a child) is withheld whole
    when it, or the uncut source it was cut from, holds a match: masking part of it would leak through length and
    context. The rule text stays, so a line keeps its form."""
    kind = hit(derived) or (hit(source) if source else None)
    if kind:
        derived = WITHHELD % (kind, " from " + origin if origin else "")
    kind = hit(text + after)
    if kind:
        text, derived, after = "", WITHHELD % (kind, ""), ""
    failures.append((rule, text + derived + after))
    print("FAIL %s: %s%s%s" % (rule, text, derived, after), flush=True)  # flushed, so a stopped run keeps the failures it found


def tracked(root):
    """The files git tracks under SHIPPED when root is the top of a git checkout, else None (a loose folder)."""
    try:
        top = subprocess.run(["git", "-C", root, "rev-parse", "--show-prefix"], capture_output=True, timeout=60)
        names = subprocess.run(["git", "-C", root, "ls-files", "-z", "--"] + SHIPPED, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if top.returncode or top.stdout.strip() or names.returncode:
        return None
    return [n for n in names.stdout.decode("utf-8", "replace").split("\0") if n and os.path.lexists(os.path.join(root, n))]


def walk(root):
    """The shipped files: the tracked ones in a git checkout (not __pycache__, lane output or any other loose file), else the folder's."""
    out, listed = [], tracked(root)
    if listed is not None:
        for rel in listed:
            parts = rel.split("/")
            bad = [i for i, name in enumerate(parts[:-1]) if name in BAD_DIRS]
            out += ["/".join(parts[:bad[0] + 1]) + "/"] if bad else []  # a tracked forbidden folder still fails the package
            out.append(rel)
        return sorted(set(out))
    for base in SHIPPED:
        path = os.path.join(root, base)
        wait_on("the walk of " + path)
        if os.path.isfile(path):
            out.append(base)
        for here, dirs, names in os.walk(path):
            for name in names:
                out.append(os.path.relpath(os.path.join(here, name), root).replace(os.sep, "/"))
            for name in dirs:
                if name in BAD_DIRS:
                    out.append(os.path.relpath(os.path.join(here, name), root).replace(os.sep, "/") + "/")
    return sorted(out)


def read(root, rel):
    """The file's bytes as git stores them: a text file checked out with CRLF (core.autocrlf on Windows) reads as LF."""
    with open(os.path.join(root, rel), "rb") as handle:
        data = handle.read()
    try:
        return data.replace(b"\r\n", b"\n") if b"\r\n" in data and b"\0" not in data and data.decode("utf-8") else data
    except ValueError:
        return data


def frontmatter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_frontmatter(root, files):
    skills = [f for f in files if re.fullmatch(r"skills/[^/]+/SKILL\.md", f)]
    if not skills:
        fail("Frontmatter", "no skills/<name>/SKILL.md found")
    for rel in skills:
        fields = frontmatter(read(root, rel).decode("utf-8", "replace"))
        folder = rel.split("/")[1]
        if not fields.get("name"):
            fail("Frontmatter", "%s has no name" % where(rel))
        elif fields["name"] != folder:
            fail("Frontmatter", "%s name " % where(rel), "%r does not match folder %r" % (fields["name"], folder))
        if not fields.get("description"):
            fail("Frontmatter", "%s has no description" % where(rel))
    return skills


def load_listing(root):
    try:
        return json.loads(read(root, "listing.json"))
    except (OSError, ValueError) as error:
        fail("Listing fields", "listing.json unreadable: ", str(error))
        return {}


def check_listing(listing):
    if not listing.get("license"):
        fail("Listing fields", "no license")
    summary = listing.get("summary", "")
    if not summary:
        fail("Listing fields", "no summary")
    if len(summary) > 300:
        fail("Listing fields", "summary is %d characters, 300 at most" % len(summary))
    for key, limit in LIMITS.items():
        if len(listing.get(key, [])) > limit:
            fail("Listing fields", "%s has %d entries, %d at most" % (key, len(listing[key]), limit))


def check_files(root, files):
    total = 0
    for rel in files:
        if rel.endswith("/"):
            fail("Files", "forbidden folder " + where(rel))
            continue
        path = os.path.join(root, rel)
        data = read(root, rel)
        total += len(data)
        if os.stat(path).st_mode & 0o111:
            fail("Files", "%s is executable" % where(rel))
        if rel.endswith((".pyc", ".pyo", ".so", ".dylib", ".exe", ".class", ".jar", ".whl")):
            fail("Files", "%s is a compiled or bundled file" % where(rel))
        try:
            text = data.decode("utf-8")
            if "\0" in text:
                raise ValueError
        except ValueError:
            fail("Files", "%s is not text" % where(rel))
    if len(files) > MAX_FILES:
        fail("Size", "%d files, at most %d allowed" % (len(files), MAX_FILES))
    if total >= MAX_BYTES:
        fail("Size", "%d bytes, under 5,000,000 allowed" % total)


def check_scripts(root, files):
    for rel in [f for f in files if f.endswith(".py")]:
        data = read(root, rel)
        text = data.decode("utf-8", "replace")
        size = len(data.replace(b"\r\n", b"\n"))  # committed (LF) bytes: a Windows CRLF checkout reads the same
        if size >= MAX_SCRIPT:
            fail("Scripts", "%s is %d bytes, under 20 KB allowed" % (where(rel), size))
        modules = set()
        siblings = {n[:-3] for n in os.listdir(os.path.dirname(os.path.join(root, rel))) if n.endswith(".py")}
        try:
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Import):
                    modules |= {item.name.split(".")[0] for item in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                    modules.add(node.module.split(".")[0])
        except SyntaxError as error:
            fail("Scripts", "%s does not parse: " % where(rel), str(error))
        for name in sorted(modules - set(sys.stdlib_module_names) - siblings):
            fail("Scripts", "%s imports " % where(rel), name, ", which is not in the standard library")
        if re.search(r"skills/|\.\./", text.replace("../loop-files.md", "")) and re.search(r"open\([^)]*(skills/|\.\./)", text):
            fail("Scripts", "%s opens another package file" % where(rel))
        if STATIC:
            continue
        with tempfile.TemporaryDirectory() as lone:  # a copy of its own scripts folder only: siblings, nothing else
            waiting["lone"] = lone
            wait_on("the copy of %s's folder" % rel)
            shutil.copytree(os.path.dirname(os.path.join(root, rel)), os.path.join(lone, "scripts"), symlinks=True)
            rc, err = run_alone([sys.executable, "-E", "-s", "-X", "utf8", os.path.join(lone, "scripts", os.path.basename(rel)), "--help"],
                                lone, "%s --help" % rel)
            if rc is None:
                fail("Scripts", "%s --help did not finish in %d seconds with no stdin (it waits on input or a child)" % (where(rel), CHILD_SECONDS))
            elif rc:
                fail("Scripts", "%s does not run alone: " % where(rel), err.strip()[-200:], source=err)
            waiting["lone"] = None


def load_private():
    """The private leak_prefixes setting (flow file, outside the repo): case-insensitive regexes the local leak hook
    blocks, compiled once; k is the 1-based raw position. The path is never printed."""
    path = os.environ.get("LOOP_FLOW") or os.path.expanduser("~/.workflow-loop/flow.json")
    try:
        with open(path, encoding="utf-8") as handle:
            raw = json.load(handle).get("leak_prefixes", [])
    except (OSError, ValueError, AttributeError):
        print("NOTE: no leak_prefixes loaded (the flow file is missing or unreadable); only the built-in scans ran")
        return
    for k, pattern in enumerate(raw if isinstance(raw, list) else [], 1):
        try:
            PRIVATE.append((k, re.compile(pattern, re.I)))
            continue
        except (re.error, TypeError):
            pass
        print("NOTE: leak_prefixes entry #%d is not a valid pattern; skipped" % k)


def check_safety(root, files):
    for rel in files:
        named = [k for k, rx in PRIVATE if rx.search(rel)]
        if named:
            fail("Safety", "private prefix #%d in a path" % named[0])
        if rel.endswith("/"):
            continue
        text = read(root, rel).decode("utf-8", "replace")
        found = [("private prefix #%d" % k, rx.search(text)) for k, rx in PRIVATE]
        found += [(group, re.search(p, text)) for group, patterns in groups() for p in patterns]
        for kind, match in found:
            if match:
                fail("Safety", "%s in %s, line %d" % (kind, where(rel), line_of(text, match)))


def note_shell(root, files):
    """Agensi's scan fails shell=True. Check commands are the repo's own strings, so it stays, and the listing says so."""
    hits = [rel for rel in files if rel.endswith(".py") and "shell=True" in read(root, rel).decode("utf-8", "replace")]
    if hits:
        print("NOTE: Agensi's scan will flag shell=True in: " + ", ".join(where(h) for h in hits))


def check_pack(root):
    with open(os.path.join(root, "README.md"), encoding="utf-8") as handle:
        if not re.match(r"# \S", handle.readline()):
            fail("Files", "README.md must open with a # title: it names the pack")
    if not os.path.isfile(os.path.join(root, "LICENSE")):
        fail("Files", "no LICENSE file")


def check_disclosure(root, files, listing):
    said = " ".join(listing.get("commands", [])).split()
    wanted, hosts, texts = {}, {}, {}
    for rel in files:
        if rel.endswith("/"):
            continue
        texts[rel] = text = read(root, rel).decode("utf-8", "replace")
        if rel.endswith(".py"):
            for name in re.findall(r"add_parser\(\"([a-z-]+)\"", text):
                wanted.setdefault(name, []).append(rel)
        if re.fullmatch(r"skills/[^/]+/SKILL\.md", rel):
            for name in re.findall(r"^## `([a-z-]+)", text, re.M):
                wanted.setdefault(name, []).append(rel)
        if rel != "listing.json":
            for host in re.findall(r"https?://([A-Za-z0-9.-]+)", text):
                hosts.setdefault(host, []).append(rel)
    for kind, values, after in (("command", wanted, " is not in listing.commands"), ("host", hosts, " is not in listing.network")):
        for value in sorted(values):
            if (value in said if kind == "command" else value in {"example.com", "example.test"} or value in " ".join(listing.get("network", []))):
                continue
            bad = [r for r in values[value] if hit(texts[r])]  # withheld when a file it came from holds a match; that file is named
            fail("Disclosure", kind + " ", repr(value) if kind == "command" else value, after, source=texts[bad[0]] if bad else None,
                 origin=where(bad[0]) if bad else "")
    if not listing.get("writes"):
        fail("Disclosure", "listing.writes is empty")
    if not listing.get("network"):
        fail("Disclosure", "listing.network is empty (state \"none\" or each host)")


def version_of(root):
    try:
        text = read(root, "VERSION").decode().strip()
    except OSError:
        text = ""
    if not re.fullmatch(r"\d+\.\d+\.\d+", text):
        fail("Version", "VERSION must hold one number like 1.2.3, not ", repr(text[:20]), source=text)
    return text


def check_inventory(root, files):
    """Every skill folder in the tree ships a SKILL.md, so none is left out of the package."""
    for name in sorted(os.listdir(os.path.join(root, "skills"))):
        if os.path.isdir(os.path.join(root, "skills", name)) and "skills/%s/SKILL.md" % name not in files:
            fail("Frontmatter", "%s has no SKILL.md, so it would not ship as a skill" % where("skills/" + name))


def manifest(root, files, version):
    """The skills-tree files with their hashes, and the newest changelog entries."""
    hashes = {}
    for rel in files:
        if rel.startswith("skills/") and not rel.endswith("/"):
            hashes[SHARED.get(rel, rel)[len("shared/" if rel in SHARED else "skills/"):]] = hashlib.sha256(read(root, rel)).hexdigest()
    try:
        log = read(root, "CHANGELOG.md").decode()
        log = "\n".join(part.rstrip() for part in re.split(r"(?m)^(?=## v)", log)[1:4])
    except OSError:
        log = ""
    wait_on("git remote get-url origin")
    try:
        url = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                             stdin=subprocess.DEVNULL, timeout=CHILD_SECONDS).stdout.strip()
    except subprocess.TimeoutExpired:
        url = ""
    found = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)  # update.py reads releases from this repo
    return {"version": version, "files": dict(sorted(hashes.items())), "changelog": log[:6000], "repo": found.group(1) if found else ""}


def build(root, files, out, version):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    handle, part = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(out)), suffix=".part")  # whole, then renamed
    os.close(handle)
    waiting["part"] = part
    with zipfile.ZipFile(part, "w", zipfile.ZIP_DEFLATED) as bundle:
        for rel in files:
            info = zipfile.ZipInfo(SHARED.get(rel, rel), (2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            bundle.writestr(info, read(root, rel))
        stamp = json.dumps(manifest(root, files, version), indent=1) + "\n"
        for name in ("PACKAGE.json", "shared/workflow-package.json"):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            bundle.writestr(info, stamp)
    umask = os.umask(0)
    os.umask(umask)
    os.chmod(part, 0o666 & ~umask)  # mkstemp makes 0600; the ZIP keeps the mode a plain open() would give
    os.replace(part, out)
    waiting["part"] = None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    parser.add_argument("--out", default=None)
    parser.add_argument("--timeout", type=int, default=None, help="hard bound in seconds (default PACKAGE_TIMEOUT, else 300)")
    parser.add_argument("--static", action="store_true", help="the static rules only (no --help pass, no ZIP): what a pull request check runs")
    args = parser.parse_args()
    global STATIC
    STATIC = args.static
    sys.stdout.reconfigure(errors="backslashreplace")  # a FAIL line quoting text the console code page lacks still prints
    try:
        seconds = args.timeout if args.timeout is not None else int(os.environ.get("PACKAGE_TIMEOUT") or 300)
    except ValueError:
        seconds = 300
    if not 0 < seconds <= 86400:
        print("REFUSED: the time bound must be 1 to 86400 seconds, not %d" % seconds)
        return 2
    arm(seconds)
    load_private()
    root = os.path.abspath(args.root)
    files = walk(root)
    wait_on('the frontmatter checks')
    check_frontmatter(root, files)
    check_inventory(root, files)
    version = version_of(root)
    listing = load_listing(root)
    check_listing(listing)
    wait_on('reading the shipped files')
    check_files(root, files)
    wait_on('the safety scans')
    check_safety(root, files)  # before the scripts run, so a hanging or failing script can't hide a match
    wait_on('the script checks')
    check_scripts(root, files)
    wait_on('the disclosure checks')
    check_disclosure(root, files, listing)
    check_pack(root)
    if failures:
        print("REFUSED: %d rule failure(s); no ZIP built" % len(failures))
        return 1
    if STATIC:
        print("PASS: %d files, the static rules hold" % len(files))
        return 0
    out = args.out or "dist/agent-workflow-template-v%s.zip" % version
    wait_on("writing the ZIP " + out)
    build(root, files, out, version)
    note_shell(root, files)
    print("PASS: %d files, ZIP at %s (%d bytes), version %s" % (len(files), os.path.abspath(out), os.path.getsize(out), version))
    return 0


def unexpected(error):
    """An uncaught error's one stderr line: its type, and its message only when that holds no match and no absolute
    path (a traceback carries local paths and file text, so none is ever printed)."""
    try:
        text = str(error)
        shown = text if text and not hit(text) and not re.search(r"(^|[\s'\"(=])(/|~/|[A-Za-z]:[\\/])", text) else "details withheld"
        return "ERROR (unexpected): %s: %s" % (type(error).__name__, shown)
    except Exception:  # the scan itself failed: a constant line
        return "ERROR (unexpected): details withheld"


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # not BaseException: SystemExit (argparse) and os._exit in stop() pass through
        print(unexpected(error), file=sys.stderr, flush=True)
        sys.exit(4)
