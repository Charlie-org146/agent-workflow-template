#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/defects.py dev/toy/test-machine.sh
"""Fast controls for the main-reds bundle; fixtures never reach the owner's home."""
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/workflow-health/scripts"))
import defects


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        raise SystemExit(1)


def consistency():
    with tempfile.TemporaryDirectory() as tmp:
        wiki = Path(tmp) / "docs/wiki"
        wiki.mkdir(parents=True)
        feature = "# A\n\n## Requirements\n\n### Functional\n\n- AB-1: **Unreviewed** One.\n"
        (wiki / "A.md").write_text(feature)
        (wiki / "How-to-use-A.md").write_text("# How to use A\n\n## How to reach or run it\n\n- AB-1: Run the tool.\n")
        check(not defects.ids_unique(tmp), "How-to items do not duplicate canonical requirement definitions (#4865)")
        (wiki / "B.md").write_text(feature.replace("# A", "# B"))
        found = defects.ids_unique(tmp)
        check(len(found) == 1 and found[0]["subject"] == "AB-1", "two real requirement definitions still fail")
        (wiki / "B.md").unlink()
        with (wiki / "A.md").open("a") as handle:
            handle.write("- AB-1: **Unreviewed** Repeated on one page.\n")
        check(bool(defects.ids_unique(tmp)), "a repeated definition on the same page still fails")
    check(not defects.ids_unique(str(ROOT)), "the checked-out wiki has no duplicate definitions")


def smtp():
    text = (ROOT / "dev/toy/test-machine.sh").read_text()
    # A literal assignment is scanner-sensitive even though its value is made up.
    pattern = r"SMTP_PASSWORD=([^\s'\"\\]+)"
    check(all(m.group(1) == "%s" for m in re.finditer(pattern, text)) and "SMTP_PASSWORD=%s" in text,
          "the toy SMTP value is assembled at runtime, with no literal credential assignment (#4758)")
    check('grep -qF "$toy_smtp"' in text, "the mailer output check uses the full assembled value")
    check(re.search(pattern, "SMTP_PASSWORD=" + "fixture-value").group(1) != "%s", "the source check rejects a literal assignment")


if __name__ == "__main__":
    {"consistency": consistency, "smtp": smtp}[sys.argv[1]]()
