"""A small levelled repository for the level checks: its own git folder and HOME, and a stand-in issue reader (no
network). Imported by test-lvl-table.py and test-lvl-relevel.py."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REG = os.path.join(ROOT, "skills", "workflow-regression", "scripts")
DELIVERY = os.path.join(ROOT, "skills", "workflow-delivery", "scripts")
FIELDS = ("id", "level", "command", "goal", "seen_red", "description", "category", "link")
COLS = ("id", "old", "level", "risk", "covers", "seconds", "cmdhash", "reason")
RISKS = ["requirement\tDEL-9\tprivate\tfixture requirement", "requirement\tGRD-6\tsecurity\tfixture requirement",
         "row\tlisted-guard\tsecurity\tfixture listed row", "label\tsecurity\tsecurity\tfixture label",
         "label\tprivate\tprivate\tfixture label"]
# gh api repos/O/R/issues/N: the labels, or the error text, that the file LVL_GH gives for it
STAND_IN = """#!/usr/bin/env python3
import json, os, sys
with open(os.environ["LVL_GH"]) as handle:
    said = json.load(handle)
with open(os.environ["LVL_GH"] + ".calls", "a") as out:
    out.write(sys.argv[2] + "\\n")
got = said.get(sys.argv[2], {"error": "HTTP 404: Not Found"})
if isinstance(got, dict):
    sys.stderr.write(got["error"] + "\\n")
    sys.exit(1)
print("\\n".join(got))
"""

failed = []


def check(ok, said, detail=""):
    print(("PASS: " if ok else "FAIL: ") + said)
    if not ok:
        failed.append(said)
        if detail:
            print("  " + str(detail)[:600].replace("\n", "\n  "))
    return ok


def done():
    print("%d failed" % len(failed) if failed else "ALL PASS")
    return 1 if failed else 0


def sha(text):
    import hashlib
    return hashlib.sha1(text.encode()).hexdigest()


def row(key, level="land", command="true", goal="", category="criterion", link="", seen="2026-01-01"):
    return dict(zip(FIELDS, (key, level, command, goal, seen, "checks " + key, category, link)))


def entry(key, old="land", level="L1", risk="none", covers="", seconds="", cmdhash="", reason="default"):
    return dict(zip(COLS, (key, old, level, risk, covers, seconds, cmdhash, reason)))


class Repo:
    def __init__(self, rows=(), entries=None, risks=RISKS):
        self.top = tempfile.mkdtemp(prefix="lvl-fixture-")
        self.path, self.home = os.path.join(self.top, "repo"), os.path.join(self.top, "home")
        bin_dir = os.path.join(self.top, "bin")
        for folder in (self.path, self.home, bin_dir, os.path.join(self.path, ".loop")):
            os.makedirs(folder, exist_ok=True)
        with open(os.path.join(bin_dir, "gh"), "w") as out:
            out.write(STAND_IN)
        os.chmod(os.path.join(bin_dir, "gh"), 0o755)
        self.answers = os.path.join(self.top, "gh.json")
        self.labels({})
        self.env = dict(os.environ, HOME=self.home, PATH=bin_dir + os.pathsep + os.environ["PATH"], LVL_GH=self.answers,
                        PYTHONDONTWRITEBYTECODE="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.test",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.test", LOOP_PRIVATE_NAMES=os.devnull,
                        LOOP_LANES_DIR=os.path.join(self.top, "lanes"))
        for name in ("LOOP_ROLE", "LOOP_ROW_TIMES", "LOOP_PR_SHARD", "GH_TOKEN", "GITHUB_TOKEN"):
            self.env.pop(name, None)
        self.git("init", "-q", "-b", "main")
        if rows:
            self.table(rows)
        if risks is not None:
            self.write(".loop/regression-risk.tsv", "".join(x + "\n" for x in risks))
        if entries is not None:
            self.record(entries)

    def close(self):
        shutil.rmtree(self.top, ignore_errors=True)

    def labels(self, answers):
        with open(self.answers, "w") as out:
            json.dump(answers, out)

    def calls(self):
        try:
            with open(self.answers + ".calls") as handle:
                return handle.read().split()
        except OSError:
            return []

    def git(self, *args, check_it=True):
        got = subprocess.run(["git"] + list(args), cwd=self.path, env=self.env, capture_output=True, text=True)
        if check_it and got.returncode:
            raise RuntimeError("git %s: %s" % (" ".join(args), got.stderr))
        return got

    def write(self, rel, text):
        path = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as out:
            out.write(text)

    def read(self, rel):
        try:
            with open(os.path.join(self.path, rel), newline="") as handle:
                return handle.read()
        except OSError:
            return None

    def table(self, rows):
        self.write(".loop/regression.tsv", "".join("\t".join(r[n] for n in FIELDS) + "\n" for r in rows))

    def record(self, entries):
        self.write(".loop/regression-relevel.tsv", "".join("\t".join(e[n] for n in COLS) + "\n" for e in entries))

    def entries(self):
        lines = (self.read(".loop/regression-relevel.tsv") or "").split("\n")
        return {x.split("\t")[0]: dict(zip(COLS, x.split("\t"))) for x in lines if x and x[0] != "#"}

    def rows(self):
        lines = (self.read(".loop/regression.tsv") or "").split("\n")
        return {x.split("\t")[0]: dict(zip(FIELDS, x.split("\t"))) for x in lines if x and x[0] != "#"}

    def commit(self, message="fixture"):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)

    def run(self, *args, **env):
        got = subprocess.run([sys.executable, os.path.join(REG, "regression.py")] + list(args), cwd=self.path,
                             env=dict(self.env, **env), capture_output=True, text=True, timeout=300)
        return got.returncode, got.stdout + got.stderr

    def snapshot(self):
        return tuple(self.read(".loop/" + n) for n in ("regression.tsv", "regression-relevel.tsv",
                                                       "regression-risk.tsv"))
