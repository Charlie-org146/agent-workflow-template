#!/usr/bin/env python3
"""GRD-20 script size: warn at 19,000 bytes, fail at 20,480, counted as git stores them (line ends as LF).
usage: size-check.py [--control] GLOB...   prints a WARN line for each script over 19,000 and a FAIL line for each over 20,480
(exit 1); --control first proves a 20,481-byte fixture fails and 20,480- and 19,500-byte ones only warn."""
import glob
import os
import sys
import tempfile

WARN, FAIL = 19000, 20480


def verdict(path):
    with open(path, "rb") as handle:
        size = len(handle.read().replace(b"\r\n", b"\n"))
    return size, "FAIL" if size > FAIL else "WARN" if size > WARN else "PASS"


def main(args):
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
