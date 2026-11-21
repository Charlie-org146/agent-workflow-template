#!/usr/bin/env python3
"""GRD-20 script size: warn at 19,000 bytes, fail at 20,480, counted as git stores them (line ends as LF).
usage: size-check.py [--control] GLOB...   prints a WARN line for each script over 19,000 and a FAIL line for each over 20,480
(exit 1); --control first proves a 20,481-byte fixture fails and 20,480- and 19,500-byte ones only warn.
       size-check.py --unread [--control]   REG-4: an UNREAD line for each assert in dev/toy that no row of .loop/regression.tsv reads,
then the count of scripts with some (a row reads an assert by naming its text; a row that runs the script with no grep, or greps
ALL PASS, reads all of them); --control proves a script with an unread assert is named and a fully read one is not."""
import glob
import os
import re
import sys
import tempfile

WARN, FAIL = 19000, 20480


def verdict(path):
    with open(path, "rb") as handle:
        size = len(handle.read().replace(b"\r\n", b"\n"))
    return size, "FAIL" if size > FAIL else "WARN" if size > WARN else "PASS"


ASSERT = re.compile(r"""(?:\b(?:ok|bad|no|check)\s+|\bcheck\()[^"'\n]*?(?:"(\w[^"]{5,})"|'(\w[^']{5,})')""")


def unread(toys, tsv):
    """(lines, scripts with an unread assert, scripts with asserts): the asserts of each toy script that no row reads."""
    with open(tsv, encoding="utf-8") as handle:
        rows = [line.split("\t")[2] for line in handle if line[:1] != "#" and line.count("\t") > 2]
    out, bad, seen = [], 0, 0
    for path in sorted(glob.glob(os.path.join(toys, "*.sh")) + glob.glob(os.path.join(toys, "*.py"))):
        with open(path, encoding="utf-8", errors="replace") as handle:
            asserts = [[t for m in ASSERT.finditer(line) for t in m.groups() if t] for line in handle.read().splitlines()]
        asserts = [t for t in asserts if t]
        mine = [r for r in rows if re.search(r"(?<![\w.-])%s(?![\w.-])" % re.escape(os.path.basename(path)), r)]
        if not asserts:
            continue
        seen += 1
        if any("grep" not in r or "ALL PASS" in r for r in mine):
            continue
        lost = [t[-1] for t in asserts if not any(x.strip("$: ") in r for x in t for r in mine)]
        out += ["UNREAD %s: %s" % (os.path.relpath(path, os.path.dirname(os.path.dirname(toys))), t) for t in lost]
        bad += bool(lost)
    return out, bad, seen


def unread_main(control):
    here = os.path.dirname(os.path.abspath(__file__))
    if control:
        with tempfile.TemporaryDirectory() as tmp:
            for name, body in (("a.sh", 'ok "alpha works fine" || bad "alpha broke"\nok "beta works fine" || bad "beta broke"\n'), ("b.sh", 'ok "gamma works fine" || bad "gamma broke"\n')):
                with open(os.path.join(tmp, name), "w") as handle:
                    handle.write(body)
            with open(os.path.join(tmp, "rows.tsv"), "w") as handle:
                handle.write('r1\tland\tbash dev/toy/a.sh | grep -qF "PASS: alpha works fine"\tG\nr2\tland\tbash dev/toy/b.sh\tG\n')
            lines, bad, seen = unread(tmp, os.path.join(tmp, "rows.tsv"))
            if not (len(lines) == 1 and lines[0].endswith("a.sh: beta broke") and (bad, seen) == (1, 2)):
                sys.exit("FAIL negative control: %r %d of %d" % (lines, bad, seen))
        print("PASS negative control: a script with an unread assert is named, a fully read one is not")
    lines, bad, seen = unread(os.path.join(here), os.path.join(here, "..", "..", ".loop", "regression.tsv"))
    print("\n".join(lines))
    print("UNREAD SCRIPTS: %d of %d scripts with asserts" % (bad, seen))


def main(args):
    if args[:1] == ["--unread"]:
        return unread_main(args[1:2] == ["--control"])
    control = args[:1] == ["--control"]
    if control:
        with tempfile.TemporaryDirectory() as tmp:
            for count, want in ((FAIL + 1, "FAIL"), (FAIL, "WARN"), (19500, "WARN")):
                fixture = os.path.join(tmp, "f.py")
                with open(fixture, "wb") as handle:
                    handle.write(b"#" * (count - 1) + b"\n")
                if verdict(fixture)[1] != want:
                    sys.exit("FAIL negative control: %d bytes should be %s" % (count, want))
        print("PASS negative control: 20,481 bytes fails, 20,480 and 19,500 only warn")
    bad = 0
    for pattern in args[1 if control else 0:]:
        for path in sorted(glob.glob(pattern)):
            size, state = verdict(path)
            if state != "PASS":
                print("%s %s %d bytes (GRD-20: warn at %d, fail at %d)" % (state, path, size, WARN, FAIL))
            bad += state == "FAIL"
    sys.exit(1 if bad else 0)


main(sys.argv[1:])
