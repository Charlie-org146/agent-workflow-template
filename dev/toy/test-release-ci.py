#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/autorelease.py .github/workflows/release.yml .github/workflows/regression.yml
# reads: .github/workflows/regression-pr.yml skills/workflow-setup/scripts/update.py dev/skills-scan.py dev/package.py
# reads: skills/workflow-regression/scripts/lanes_cli.py
"""REL-15: with merge_queue on, the release is made in CI on push to main, so finish() pushes no commit and opens no pull request.

A toy origin and a fake gh that logs every call. finish() with merge_queue must leave the base commit where it was, call
gh for no pull request or release, and label_part must put release:minor or release:major (not patch) on the merged
pull request. release.yml must trigger on push to main, run no lane, and regression.yml must not run on a tag.
SET-10 (the loop ships only as the template): no workflow builds, attaches or uploads a package (a line scan with the standard library,
so a failure prints the file and line, the rule and a fix, with a code REL-CI-001 to 003), and the release is a tag on a release commit whose
tree has VERSION set (the job's own steps run in a temp clone with a fake gh), so a no-zip adopter reads the true latest version from the
tag's source archive. The negative controls run the same checks on temp copies: a zip step, a package step, a release made at the merge
commit (VERSION left stale, which the adopter check must refuse).
AUTORELEASE=PATH tests another copy of autorelease.py (a red run uses the one before this goal)."""
import contextlib
import glob
import io
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.normpath(os.path.join(here, "..", ".."))
scripts = os.path.join(root, "skills", "workflow-release", "scripts")
sys.path.insert(0, scripts)
sys.path.insert(1, os.path.join(root, "skills", "workflow-delivery", "scripts"))
if os.environ.get("AUTORELEASE"):  # a copy of autorelease.py: the other scripts still come from this tree
    import importlib.util
    spec = importlib.util.spec_from_file_location("autorelease", os.environ["AUTORELEASE"])
    ar = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ar)
else:
    import autorelease as ar  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


# ---------------------------------------------------------------------------------------------------------------------
# The no-package scan. A workflow file is read line by line: the lines of a `run:` value (inline, or the indented lines of
# a `|`, `|-`, `>` or `>-` block) are shell, comment lines are dropped, a trailing backslash joins the next line.
BANNED = ("zip", "tar", "gzip", "7z", "zipfile", "--attach", "gh release upload", "uploads.github.com", "actions/upload-artifact",
          "actions/create-release", "softprops/action-gh-release", "ncipollo/release-action")
ALLOWED_FLAGS = {"--verify-tag": 0, "--generate-notes": 0, "--title": 1, "--target": 1}
SPLITTERS = {"||", "&&", ";", "|", ")", "(", "&"}
FIX = {
    "REL-CI-001": "remove the step: the loop ships only as the template, no package is built (SET-10); the static scan is dev/skills-scan.py",
    "REL-CI-002": "remove it: a release builds, attaches and uploads nothing (SET-10); call no local script or action from release.yml",
    "REL-CI-003": "pass gh release create only the tag, --title, --target, --verify-tag and --generate-notes",
}


def shell_lines(text):
    """[(lineno, logical shell line)] of every run: value, comments dropped, backslash continuations joined."""
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        m = re.match(r"^(\s*)(?:- )?run:\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        indent, value, start = len(m.group(1)), m.group(2).strip(), i
        body = []
        if value in ("|", "|-", ">", ">-", "|+", ">+"):
            i += 1
            while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent + 1):
                body.append((i + 1, lines[i].strip()))
                i += 1
        else:
            body.append((start + 1, value))
            i += 1
        joined = ""
        for no, line in body:
            if line.startswith("#") or not line:
                continue
            if joined:
                joined += " " + line
            else:
                first = no
                joined = line
            if joined.endswith("\\"):
                joined = joined[:-1].rstrip()
                continue
            out.append((first, joined))
            joined = ""
        if joined:
            out.append((first, joined))
    return out


def words(line):
    try:
        return shlex.split(line, comments=True)
    except ValueError:
        return line.split()


def scan(path, release):
    """The messages of every rule a workflow file breaks: 'REL-CI-00N path:line: what (rule) -> fix: ...'. [] when it holds."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        return ["REL-CI-000 %s: cannot read the workflow (%s) -> fix: pass an existing workflow file" % (path, error.strerror)]
    found = []

    def add(code, no, what, rule):
        found.append("%s %s:%d: %s (%s) -> fix: %s" % (code, path, no, what, rule, FIX[code]))
    for no, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        if line.startswith("#"):
            continue
        if re.search(r"dev/package\b|package\.py|\bname:.*\bpackage\b", line, re.I):
            add("REL-CI-001", no, "a package step: %r" % line[:70], "no-package-step")
        if release and re.match(r"^(-\s*)?uses:", line):
            for token in BANNED:
                if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(token), line):
                    add("REL-CI-002", no, "uses a package action: %r" % line[:70], "banned-token")
            if re.search(r"uses:\s*\./", line):
                add("REL-CI-002", no, "calls a local action: %r" % line[:70], "banned-token")
    if release:
        for no, line in shell_lines(text):
            for token in BANNED:
                if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(token), line):
                    add("REL-CI-002", no, "the token %r: %r" % (token, line[:70]), "banned-token")
            tokens = words(line)
            if re.search(r"(^|\s)(bash|sh|python3?|source|\.)\s+[\w./-]+(\.sh|\.py)\b", line) or re.search(r"(^|[\s;&|(])\./[\w.-]+", line):
                add("REL-CI-002", no, "calls a local script: %r" % line[:70], "banned-token")
            for i in range(len(tokens) - 2):
                if tokens[i:i + 3] != ["gh", "release", "create"]:
                    continue
                args, j, positional = [], i + 3, 0
                while j < len(tokens) and tokens[j] not in SPLITTERS:
                    tok = tokens[j]
                    if tok in ALLOWED_FLAGS:
                        j += ALLOWED_FLAGS[tok]
                    elif not tok.startswith("-") and positional == 0:
                        positional = 1
                    else:
                        args.append(tok)
                    j += 1
                if args:
                    add("REL-CI-003", no, "gh release create takes %s" % " ".join(repr(a) for a in args), "file-argument")
    return found


def release_scan_ok(path):
    return scan(path, True) == []


def run_blocks(text):
    """The run: values of a workflow as whole text blocks, in order."""
    blocks, current = [], None
    for no, line in shell_lines(text):
        blocks.append((no, line))
    grouped, last = [], None
    for no, line in blocks:
        if last is not None and no == last + 1 or (grouped and no == grouped[-1][0] + grouped[-1][1].count("\n") + 1):
            pass
        grouped.append((no, line))
        last = no
    return grouped


def step_scripts(path):
    """(version step script, release step script): the run: blocks of release.yml whose text holds version= or gh release create."""
    text = open(path, encoding="utf-8").read()
    lines, blocks, i = text.split("\n"), [], 0
    while i < len(lines):
        m = re.match(r"^(\s*)(?:- )?run:\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        indent, value, body = len(m.group(1)), m.group(2).strip(), []
        if value in ("|", "|-", ">", ">-"):
            i += 1
            while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent + 1):
                body.append(lines[i][indent + 2:] if lines[i].strip() else "")
                i += 1
        else:
            body.append(value)
            i += 1
        blocks.append("\n".join(body))
    version = next(b for b in blocks if 'echo "version=' in b)
    release = next(b for b in blocks if 'gh release create "v$v"' in b and 'echo "version=' not in b)
    return version, release


FAKE_GH = """#!/bin/sh
echo "$@" >> "$FAKE_DIR/gh.log"
case "$1 $2" in
  "release view") [ -f "$FAKE_DIR/rel-$3" ] && { echo 0; exit 0; }; exit 1 ;;
  "release create") tag=$3; target=""; prev=""
    for a in "$@"; do [ "$prev" = "--target" ] && target=$a; prev=$a; done
    : > "$FAKE_DIR/rel-$tag"
    git --git-dir="$FAKE_ORIGIN" rev-parse -q --verify "refs/tags/$tag" > /dev/null 2>&1 || git --git-dir="$FAKE_ORIGIN" update-ref "refs/tags/$tag" "${target:-$(git --git-dir="$FAKE_ORIGIN" rev-parse main)}"
    exit 0 ;;
esac
exit 0
"""


def release_job(workflow, temp):
    """Runs release.yml's version and release steps in a temp clone of a template at merge commit M (VERSION 1.0.112, newest tag
    v1.0.157) with a fake gh. Returns the origin, the merge commit and the tools to run the job again."""
    origin, clone, bindir, fake = (os.path.join(temp, n) for n in ("origin.git", "clone", "bin", "fake"))
    os.makedirs(bindir)
    os.makedirs(fake)
    git("init", "-q", "--bare", "-b", "main", origin, cwd=temp)
    git("clone", "-q", origin, clone, cwd=temp)
    git("config", "user.email", "t@example.com", cwd=clone)
    git("config", "user.name", "t", cwd=clone)
    os.makedirs(os.path.join(clone, "skills", "workflow-x"))
    open(os.path.join(clone, "skills", "workflow-x", "SKILL.md"), "w").write("# x\n")
    open(os.path.join(clone, "VERSION"), "w").write("1.0.112\n")
    open(os.path.join(clone, "CHANGELOG.md"), "w").write("## v1.0.112\n- first\n")
    git("add", "-A", cwd=clone)
    git("commit", "-q", "-m", "first", cwd=clone)
    git("tag", "v1.0.157", cwd=clone)
    open(os.path.join(clone, "later.txt"), "w").write("a merged change\n")
    git("add", "-A", cwd=clone)
    git("commit", "-q", "-m", "a merged change", cwd=clone)
    git("push", "-q", "origin", "main", "--tags", cwd=clone)
    merge = git("rev-parse", "HEAD", cwd=clone)
    with open(os.path.join(bindir, "gh"), "w") as handle:
        handle.write(FAKE_GH)
    os.chmod(os.path.join(bindir, "gh"), 0o755)
    version_step, release_step = step_scripts(workflow)

    def run(script, version=""):
        out = os.path.join(temp, "out")
        env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"], GITHUB_SHA=merge, GITHUB_OUTPUT=out, FAKE_DIR=fake,
                   FAKE_ORIGIN=origin, GITHUB_REPOSITORY="owner/template", GH_TOKEN="toy-token", GIT_TERMINAL_PROMPT="0")
        done = subprocess.run(["bash", "-c", script.replace("${{ steps.version.outputs.version }}", version)], cwd=clone, env=env,
                              capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    def job():
        """One run of the job: the version step, then the release step unless it says skip."""
        if os.path.exists(os.path.join(temp, "out")):
            os.remove(os.path.join(temp, "out"))
        code, said = run(version_step)
        outputs = dict(line.split("=", 1) for line in open(os.path.join(temp, "out")).read().split("\n") if "=" in line) if os.path.exists(os.path.join(temp, "out")) else {}
        if code or outputs.get("skip") == "1":
            return code, outputs, said
        code, said = run(release_step, outputs.get("version", ""))
        return code, outputs, said
    return origin, merge, job, fake


def adopter_sees_latest(workflow):
    """True when an adopter who installed 1.0.157 reads a newer version from the source archive of the tag the job made."""
    sys.path.insert(0, os.path.join(root, "skills", "workflow-setup", "scripts"))
    import update
    temp = tempfile.mkdtemp(prefix="rel-adopter-")
    try:
        origin, merge, job, fake = release_job(workflow, temp)
        code, outputs, said = job()
        tag = "v" + outputs.get("version", "?")
        archive = os.path.join(temp, "tag.zip")
        done = subprocess.run(["git", "--git-dir=" + origin, "archive", "--format=zip", "--prefix=template/", "-o", archive, tag],
                              capture_output=True, text=True)
        if code or done.returncode:
            return False, "the job or the archive failed: %s %s" % (said[-120:], done.stderr[-120:])
        manifest, _ = update.load(archive)
        got = manifest["version"]
        return update.version_key(got) > update.version_key("1.0.157") and got == outputs["version"], "archive VERSION %s, tag %s" % (got, tag)
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def skills_scan_checks():
    """ENG-2: the static scan of the skills files keeps its per-PR and merge-group enforcement under a name that says no package."""
    pr = open(os.path.join(root, ".github", "workflows", "regression-pr.yml"), encoding="utf-8").read()
    step = "python3 dev/skills-scan.py"

    def holding(text):
        parts = re.split(r"(?m)^  (?=[a-z]+:$)", text.split("jobs:", 1)[1])
        return {part.split(":", 1)[0]: step in part for part in parts if part.strip()}
    holds = holding(pr)
    check(holds.get("affected") and holds.get("small"), "the generated regression-pr.yml runs dev/skills-scan.py in the affected job and in the merge-group job (%s)" % holds)
    gen = open(os.path.join(root, "skills", "workflow-regression", "scripts", "lanes_cli.py"), encoding="utf-8").read()
    check(gen.count(step) == 2, "the generator in lanes_cli.py emits the scan step in both jobs, so regenerating keeps it")
    without = pr.replace("      - run: test ! -f dev/skills-scan.py || python3 dev/skills-scan.py\n", "")
    seen = holding(without)
    check(without != pr and not seen.get("affected") and not seen.get("small"), "the control: a workflow without the step is seen as missing it in both jobs")
    temp = tempfile.mkdtemp(prefix="skills-scan-")
    try:
        for name in ("skills", "dev"):
            shutil.copytree(os.path.join(root, name), os.path.join(temp, name), ignore=shutil.ignore_patterns("__pycache__", "toy"))
        for name in ("README.md", "listing.json", "VERSION", "CHANGELOG.md", "LICENSE"):
            if os.path.exists(os.path.join(root, name)):
                shutil.copy(os.path.join(root, name), temp)
        scan_cmd = [sys.executable, os.path.join(temp, "dev", "skills-scan.py"), "--root", temp]
        clean = subprocess.run(scan_cmd, capture_output=True, text=True, cwd=temp)
        check(clean.returncode == 0 and "the static rules hold" in clean.stdout, "dev/skills-scan.py passes on this tree (%s)" % clean.stdout.strip()[-60:])
        with open(os.path.join(temp, "skills", "workflow-docs", "SKILL.md"), "a", encoding="utf-8") as handle:
            handle.write("\n" + "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ejAxMjM0NTY3ODlBQkNERUZHSElKS0xNTk9QUVJTVFVWWFla" + "\n")
        dirty = subprocess.run(scan_cmd, capture_output=True, text=True, cwd=temp)
        check(dirty.returncode != 0 and "obfuscation or encoded text in skills/workflow-docs/SKILL.md" in dirty.stdout,
              "the control: an encoded blob in a Markdown skills file fails the entry point (%s)" % dirty.stdout.strip()[:80])
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def release_checks():
    workflow = os.path.join(root, ".github", "workflows", "release.yml")
    # the scan on this repo: every workflow has no package step; release.yml builds, attaches and uploads nothing
    flows = sorted(glob.glob(os.path.join(root, ".github", "workflows", "*.yml")))
    found = [m for f in flows for m in scan(f, os.path.basename(f) == "release.yml")]
    for message in found:
        print(message, file=sys.stderr)
    check(found == [] and len(flows) >= 3, "SET-10: no workflow runs a package step, and release.yml builds, attaches and uploads nothing (%d workflows scanned)" % len(flows))
    # negative controls on temp copies: each breaks exactly the rule it names, and its message carries the file, the line, the rule, a fix and a code
    base = open(workflow, encoding="utf-8").read()
    pr = open(os.path.join(root, ".github", "workflows", "regression-pr.yml"), encoding="utf-8").read()
    temp = tempfile.mkdtemp(prefix="rel-scan-")
    try:
        def variant(name, text, release, code, rule):
            path = os.path.join(temp, name)
            open(path, "w", encoding="utf-8").write(text)
            msgs = scan(path, release)
            ok = any(m.startswith(code + " " + path + ":") and "(%s)" % rule in m and " -> fix: " in m for m in msgs)
            check(ok, "the control: %s is refused as %s %s with its file, line and a fix (%s)" % (name, code, rule, (msgs or ["no message"])[0][:90]))
        tail = '      - run: |\n          set -eu\n'
        variant("zip-step.yml", base + tail + '          zip -r dist.zip skills\n', True, "REL-CI-002", "banned-token")
        variant("tar-step.yml", base + tail + '          tar czf dist.tgz skills\n', True, "REL-CI-002", "banned-token")
        variant("upload-action.yml", base + '      - uses: softprops/action-gh-release@v2\n', True, "REL-CI-002", "banned-token")
        variant("local-script.yml", base + tail + '          bash dev/release.sh\n', True, "REL-CI-002", "banned-token")
        variant("local-action.yml", base + '      - uses: ./.github/actions/release\n', True, "REL-CI-002", "banned-token")
        variant("file-arg.yml", base + tail + '          gh release create v9 dist/x.tgz --title v9\n', True, "REL-CI-003", "file-argument")
        variant("variable-arg.yml", base + tail + '          gh release create "v9" $FILES --generate-notes\n', True, "REL-CI-003", "file-argument")
        variant("continued.yml", base + tail + '          gh release create v9 \\\n            --generate-notes \\\n            dist.bin\n', True, "REL-CI-003", "file-argument")
        variant("folded.yml", base + '      - run: >\n          gh release create v9 packed.bin\n', True, "REL-CI-003", "file-argument")
        variant("strip-block.yml", base + '      - run: |-\n          gh release upload v9 x\n', True, "REL-CI-002", "banned-token")
        variant("package-step.yml", pr + '      - run: python3 dev/package.py --static\n', False, "REL-CI-001", "no-package-step")
        variant("package-name.yml", pr + '      - name: package the skills\n        run: echo x\n', False, "REL-CI-001", "no-package-step")
        # regression-pr.yml keeps its shard-log upload-artifact: the asset tokens apply to the release only
        path = os.path.join(temp, "pr-copy.yml")
        open(path, "w", encoding="utf-8").write(pr)
        check(scan(path, False) == [] and "upload-artifact" in pr, "regression-pr.yml keeps its shard-log upload-artifact and holds no package step")
        gone = scan(os.path.join(temp, "missing.yml"), True)
        check(len(gone) == 1 and gone[0].startswith("REL-CI-000 ") and " -> fix: " in gone[0], "an unreadable path is a usage error with a code and a fix, not a traceback")
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    skills_scan_checks()
    # the job's own steps, run in a temp clone: the release is a tag on a release commit whose tree has VERSION set
    temp = tempfile.mkdtemp(prefix="rel-job-")
    try:
        origin, merge, job, fake = release_job(workflow, temp)
        code, outputs, said = job()
        v = outputs.get("version", "?")
        tag = "v" + v
        show = lambda *a: subprocess.run(["git", "--git-dir=" + origin, *a], capture_output=True, text=True).stdout.strip()
        check(code == 0 and v == "1.0.158", "the job makes v1.0.158 from the newest tag v1.0.157 (%s)" % v)
        check(show("show", tag + ":VERSION") == v, "VERSION at the tag is the version, not the merge's stale 1.0.112 (%s)" % show("show", tag + ":VERSION"))
        check(show("diff", "--name-only", tag + "^", tag).split() == ["VERSION"] and show("rev-parse", tag + "^") == merge,
              "the tag's commit differs from the merge commit only in VERSION and has the merge as its parent")
        check(show("rev-parse", "main") == merge, "main is where the merge left it: only the tag was pushed")
        calls = open(os.path.join(fake, "gh.log")).read()
        check("release create %s --verify-tag --title %s --generate-notes" % (tag, tag) in calls and ".zip" not in calls and "--target" not in calls,
              "the release is made on the existing tag with --verify-tag and --generate-notes, no file and no --target")
        tags_before = show("tag", "--list", "v*")
        code, outputs, said = job()
        check(code == 0 and outputs.get("skip") == "1" and show("tag", "--list", "v*") == tags_before,
              "a rerun makes no second tag (the tag whose parent is this commit is found)")
        os.remove(os.path.join(fake, "rel-" + tag))
        code, outputs, said = job()
        again = open(os.path.join(fake, "gh.log")).read()
        check(code == 0 and again.count("release create " + tag) == 2 and show("tag", "--list", "v*") == tags_before,
              "a rerun after a failed release creates only the missing release on the existing tag")
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    # the adopter: a no-zip adopter on 1.0.157 reads the true latest version from the tag's source archive
    ok, detail = adopter_sees_latest(workflow)
    check(ok, "a no-zip adopter on 1.0.157 sees the newer version in the tag's source archive (%s)" % detail)
    reverted = base.replace(
        base[base.index('          # The tag is a release commit'):base.index("      - if: always()")],
        '          gh release create "v$v" --target "$GITHUB_SHA" --title "v$v" --generate-notes\n')
    temp = tempfile.mkdtemp(prefix="rel-revert-")
    try:
        path = os.path.join(temp, "release.yml")
        open(path, "w", encoding="utf-8").write(reverted)
        stale, detail = adopter_sees_latest(path)
        check(not stale and "VERSION 1.0.112" in detail, "the control: with the release made at the merge commit (ENG-1 reverted) the adopter reads the stale VERSION (%s)" % detail)
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def main():
    temp = tempfile.mkdtemp(prefix="rel15-")
    origin, clone, bindir, log = (os.path.join(temp, n) for n in ("origin.git", "clone", "bin", "gh.log"))
    os.makedirs(bindir)
    git("init", "-q", "--bare", "-b", "main", origin, cwd=temp)
    git("clone", "-q", origin, clone, cwd=temp)
    git("config", "user.email", "t@example.com", cwd=clone)
    git("config", "user.name", "t", cwd=clone)
    open(os.path.join(clone, "VERSION"), "w").write("1.0.0\n")
    git("add", "VERSION", cwd=clone)
    git("commit", "-q", "-m", "first", cwd=clone)
    git("push", "-q", "origin", "main", cwd=clone)
    with open(os.path.join(bindir, "gh"), "w") as fake:
        fake.write('#!/bin/sh\necho "$@" >> "%s"\nexit 0\n' % log)
    os.chmod(os.path.join(bindir, "gh"), 0o755)
    os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
    base_before = git("rev-parse", "origin/main", cwd=clone)

    def gh_calls():
        return open(log).read() if os.path.exists(log) else ""

    state = {"slug": "toy", "pr": "https://example.com/pull/7", "release_part": "minor", "release_reason": "a goal"}
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        ar.label_part(clone, {"merge_queue": True}, state)
        got = ar.finish(clone, {"merge_queue": True, "base": "main"}, state)
    calls = gh_calls()
    git("fetch", "-q", "origin", cwd=clone)
    check(got is True and "RELEASE from CI" in out.getvalue(), "finish() with merge_queue on says the release comes from CI")
    check(git("rev-parse", "origin/main", cwd=clone) == base_before and not git("branch", "-r", cwd=clone).count("release/"),
          "finish() pushes no commit to the base and no release branch")
    check("pr create" not in calls and "release create" not in calls, "finish() opens no pull request and creates no release")
    check("label create release:minor" in calls and "pr edit https://example.com/pull/7 --add-label release:minor" in calls,
          "a minor part is labelled release:minor on the merged pull request")
    open(log, "w").close()
    state["release_part"] = "patch"
    with contextlib.redirect_stdout(io.StringIO()):
        ar.label_part(clone, {"merge_queue": True}, state)
        state["release_part"] = "major"
        ar.label_part(clone, {}, state)  # the setting off labels nothing
    check(gh_calls() == "", "a patch part and a repo without merge_queue add no label")

    release = open(os.path.join(root, ".github", "workflows", "release.yml")).read()
    check("branches: [main]" in release and "regression.py" not in release and "pull_request" not in release.split("jobs:")[0],
          "release.yml runs on push to main and runs no lane")
    check("gh release create" in release and "--generate-notes" in release and "git push" not in release,
          "release.yml makes the release with gh release create --generate-notes and pushes nothing")
    flow = open(os.path.join(root, ".github", "workflows", "regression.yml")).read()
    check("tags:" not in flow, "regression.yml does not run on a release tag")

    # a negative control: a push to the base is seen by the same detector
    open(os.path.join(clone, "VERSION"), "w").write("1.0.1\n")
    git("commit", "-q", "-am", "Release v1.0.1", cwd=clone)
    git("push", "-q", "origin", "main", cwd=clone)
    git("fetch", "-q", "origin", cwd=clone)
    check(git("rev-parse", "origin/main", cwd=clone) != base_before, "the control: a release commit on the base is detected")
    release_checks()
    if failed:
        sys.exit(1)
    print("PASS: REL-15: with merge_queue on, the release is made in CI and finish() pushes nothing and opens no pull request")


main()
