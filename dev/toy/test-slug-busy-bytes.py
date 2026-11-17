#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/board_status.py skills/workflow-monitoring/scripts/checkin.py
"""#4810: a process list with bytes that are not UTF-8 (a zh-CN PC's GBK command line) does not kill the check-in: slug_busy
decodes it as text. Negative controls: the same bytes fail a strict UTF-8 decode, and another goal's slug is still not busy."""
import datetime
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import board_status  # noqa: E402
import checkin  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


GBK = b"python goal.py pr quietone D:\\xc4\xe3\xba\xc3\xa1\xa1\r\npython flow.py other qa\r\n"  # 0xa1 and 0xc4 are not valid UTF-8 here
os.environ.pop("LOOP_PROCS", None)  # the real read path, with the process list faked at subprocess.run
real_run = subprocess.run
TOOLS = ("powershell", "ps", "tasklist", "vm_stat")  # the process-list tools answer in code-page bytes; git and the rest are real
subprocess.run = lambda argv, *a, **k: (subprocess.CompletedProcess(argv, 0, stdout=GBK, stderr=b"") if argv[0] in TOOLS
                                        else real_run(argv, *a, **k))
try:
    try:
        GBK.decode("utf-8")
        strict = False
    except UnicodeDecodeError:
        strict = True
    check(strict, "#4810 negative control: the process list is not valid UTF-8 (a strict decode raises)")
    try:
        check(board_status.slug_busy("quietone") is True, "#4810: slug_busy finds a goal's process in a list with non-UTF-8 bytes")
        check(board_status.slug_busy("absent") is False, "#4810 negative control: a goal with no process line is not busy")
    except UnicodeDecodeError:
        check(False, "#4810: slug_busy raised UnicodeDecodeError on a non-UTF-8 process list")

    NOW = datetime.datetime(2026, 11, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
    stamp = (NOW - datetime.timedelta(minutes=40)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
        for key in ("HOME", "USERPROFILE"):
            os.environ[key] = home
        for args in (("init", "-q", "-b", "main", tmp), ("-C", tmp, "config", "user.email", "t@example.test"), ("-C", tmp, "config", "user.name", "t")):
            real_run(("git",) + args, check=True, capture_output=True)
        os.makedirs(os.path.join(tmp, ".loop"))
        with open(os.path.join(tmp, ".loop", "config.json"), "w") as f:
            json.dump({"base": "main"}, f)
        runs = os.path.join(tmp, ".git", "loop", "runs")
        os.makedirs(runs)
        with open(os.path.join(runs, "quietone.json"), "w") as f:
            json.dump({"slug": "quietone", "goal": "Goal quietone", "status": "running", "step": "build", "worker": "session",
                       "branch": "loop/quietone", "pid": os.getpid(), "updated": stamp, "report": {"at": stamp, "text": "working"}}, f)
        try:
            out = checkin.render(tmp, NOW)
            check("Needs you" in out and "STALLED quietone" not in out,
                  "#4810: the check-in prints with a non-UTF-8 process list, and a goal with a process is not STALLED")
        except UnicodeDecodeError:
            check(False, "#4810: the check-in raised UnicodeDecodeError on a non-UTF-8 process list")
finally:
    subprocess.run = real_run
sys.exit(1 if failed else 0)
