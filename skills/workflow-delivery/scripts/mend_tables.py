"""The automatic repair of a conflicted merge (moved whole out of lanekit.py): the row tables are unioned by row id,
the levels record with them, and the Tests page is taken from the base and rendered again. A conflict in the risk data,
or one id with two different record lines, is left to the person merging."""
import os
import subprocess
import sys
import tempfile

# A prompt from git or gh must fail, not block (DEL-10).
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = ".loop/regression-relevel.tsv"
REGRESSION = os.path.join(HERE, "..", "..", "workflow-regression", "scripts", "regression.py")


def fill(top, git):
    """Add the entries of rows the merge brought without one; False stops the repair, None had nothing to do."""
    if not os.path.exists(os.path.join(top, RECORD)):
        return None
    done = subprocess.run([sys.executable, "-B", REGRESSION, "levels", "--fill"], cwd=top, capture_output=True, text=True)
    if done.returncode not in (0, 2):  # 2: filled what it could; a defect or covered row is left, and named
        print("LEVELS the record could not be filled, so the merge is left to you:")
        print(((done.stdout or "") + (done.stderr or "")).strip()[-2000:])
        return False
    for line in done.stdout.splitlines():
        if line.startswith(("FILLED", "NOT FILLED", "  ")):
            print("LEVELS " + line)
    if done.returncode == 2:
        print("LEVELS entries are still missing after the merge: every run refuses them until the named fix is made")
    return not git("add", "--", RECORD).returncode


def mend(git, files, base):
    top = git("rev-parse", "--show-toplevel").stdout.strip()
    tsv = (".loop/regression.tsv", ".loop/regression-runs.tsv", RECORD)
    page = lambda f: os.path.basename(f) == "Tests.md" and os.path.dirname(f).endswith("wiki")
    criteria = os.path.join(HERE, "..", "..", "workflow-docs", "scripts", "criteria.py")
    if not files or not all(f in tsv or page(f) for f in files):
        return False
    if any(page(f) for f in files) and not (os.path.exists(top + "/.loop/docs.tsv") and os.path.exists(criteria)):
        return False
    for f in files:
        s = [git("show", ":%d:%s" % (n, f)) for n in (1, 2, 3)]
        if s[1].returncode or s[2].returncode:
            return False
        if f not in tsv:
            git("checkout", "--theirs", "--", f)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            for n, r in zip("abc", (s[1], s[0], s[2])):
                open(tmp + "/" + n, "w").write(r.stdout if not r.returncode else "")
            union = subprocess.run(["git", "merge-file", "-p", "--union"] + [tmp + "/" + n for n in "abc"],
                                   capture_output=True, text=True).stdout
        rows = lambda t: {l.split("\t")[0]: l for l in t.splitlines() if l and l[0] != "#"}
        b, o, t = rows(s[0].stdout if not s[0].returncode else ""), rows(s[1].stdout), rows(s[2].stdout)
        if any(k not in o or k not in t for k in b):
            return False
        out, at = [], {}
        for line in union.splitlines():
            k = line.split("\t")[0]
            if line[0:1] == "#" or not line or k not in at:
                at[k] = len(out)
                out.append(line)
            elif line != out[at[k]]:
                a, b = line.split("\t"), out[at[k]].split("\t")
                same = a[:8] == b[:8] and (len(a) < 9 or len(b) < 9 or a[8] == b[8])  # two different state cells are a real conflict
                if f == tsv[2] and same:  # one record entry with and without the ninth (state) cell: keep the longer
                    out[at[k]] = max(line, out[at[k]], key=len)
                    continue
                if f != tsv[1] or line.split("\t")[2:3] == out[at[k]].split("\t")[2:3]:
                    return False
                out[at[k]] = max(line, out[at[k]], key=lambda l: l.split("\t")[2:3])
        open(top + "/" + f, "w").write("\n".join(out) + "\n")
    if any(page(f) for f in files):
        if subprocess.run([sys.executable, criteria, "render", "--tables"], cwd=top, capture_output=True).returncode:
            return False
        git("add", "-u")
    added = fill(top, git)  # the record follows the merged rows: missing entries join the same merge commit
    if git("add", "--", *files).returncode or added is False or git("commit", "--no-edit", "-q").returncode:
        return False
    print("MENDED %s: rows unioned, Tests.md taken from %s and re-rendered" % (", ".join(files), base))
    return True
