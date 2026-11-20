#!/usr/bin/env python3
"""Rebuilds docs/wiki/system-design.svg from the README's principle tables: python3 dev/system-design.py [--check].
A dot means a principle has a requirement on a feature (the Feature column). Not shipped: the package holds skills/ only."""
import re, sys
SVG = "docs/wiki/system-design.svg"
NAMES = ["Docs-driven", "Enforced", "Fast, cheap", "Private", "Reproducible", "Autonomous", "Standard", "Honest"]
AREAS = [("Build loop", ["Delivery", "Operation", "Check in and board"]), ("Quality", ["Regression", "Health", "Guardrails"]),
         ("Docs", ["Documentation"]), ("Operations", ["Automation", "Machines", "Setup"]), ("Other", ["Release", "Integrations"])]
SHORT = {"Check in and board": "Check-in and board"}
LIGHT = ["#3b6fd6", "#d9822b", "#2f8f4a", "#c5483f", "#8a5cd6", "#0f8f9c", "#a8791a", "#cc3f7c"]
DARK = ["#6d9bf0", "#f0a050", "#4fb56c", "#e0736a", "#b08cf0", "#3fc4d2", "#e0b84a", "#f07aa8"]
F = "system-ui,-apple-system,Segoe UI,sans-serif"

def pairs(readme):
    got = set()
    for sec in re.split(r"\n(?=## )", readme):
        m = re.match(r"## (\d)\. ", sec)
        if not m:
            continue
        rows = sec.split("\n")
        head = next(i for i, r in enumerate(rows) if r.startswith("| Requirement"))
        col = [c.strip() for c in rows[head].strip("|").split("|")].index("Feature")
        for r in rows[head + 2:]:
            if not r.startswith("|"):
                break
            for name in re.findall(r"([^,()]+?) \([^)]+\)", re.split(r"(?<!\\)\|", r.strip()[1:-1])[col]):
                got.add((int(m[1]), name.strip()))
    return got

def build(readme):
    dots, o = pairs(readme), []
    css = "".join(".c%d{fill:%s}" % (i + 1, c) for i, c in enumerate(LIGHT))
    dk = "".join(".c%d{fill:%s}" % (i + 1, c) for i, c in enumerate(DARK))
    o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 612" width="640" role="img" aria-label="System design: a grid of the eight principles by the features, a dot where the principle has a requirement on the feature">')
    o.append("<title>System design: the principles and the features they have requirements on</title>")
    o.append("<style>.t{font:600 15px %s;fill:#1b2430}.h{font:600 9px %s;fill:#566173;letter-spacing:.04em}.s{font:400 12px %s;fill:#27303c}.x{font:400 10.5px %s;fill:#566173}.n{font:400 9px %s;fill:#27303c}.k{font:700 9.5px %s;fill:#fff}"
             ".bg{fill:#fff}.you{fill:#e4eeff;stroke:#3b6fd6}.box{fill:#f3f5f8;stroke:#8a94a3}.stripe{fill:#f3f5f8}.rule{stroke:#8a94a3;stroke-width:1}.a{stroke:#6b7686;stroke-width:1.5;fill:none}.ah{fill:#6b7686}%s"
             "@media (prefers-color-scheme: dark){.t{fill:#eef2f6}.h,.x{fill:#a3afbf}.s,.n{fill:#e1e7ee}.k{fill:#12171d}.bg{fill:#12171d}.you{fill:#162a4f;stroke:#6d9bf0}.box{fill:#222b36;stroke:#5c6b7d}.stripe{fill:#181e26}.rule{stroke:#5c6b7d}.a{stroke:#9aa7b8}.ah{fill:#9aa7b8}%s}</style>" % (F, F, F, F, F, F, css, dk))
    o.append('<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8 z" class="ah"/></marker></defs>')
    o.append('<rect width="640" height="612" class="bg"/>')
    o.append('<text x="12" y="22" class="t">System design: how the principles and the features connect</text>')
    o.append('<text x="12" y="38" class="x">C4 model, level 1 (system context): the owner, the loop, and the outside systems it uses.</text>')
    o.append('<rect x="240" y="48" width="160" height="38" rx="8" class="you" stroke-width="1.2"/><text x="320" y="65" text-anchor="middle" class="s">The owner</text><text x="320" y="79" text-anchor="middle" class="x">any machine</text>')
    o.append('<path d="M320 86 L320 104" class="a" marker-end="url(#ah)"/><text x="326" y="98" class="x">says a goal, answers what is theirs</text>')
    cx = [198 + i * 56 for i in range(8)]
    for i, n in enumerate(NAMES):
        extra = ' textLength="50" lengthAdjust="spacingAndGlyphs"' if len(n) > 10 else ""
        o.append('<circle cx="%d" cy="120" r="8" class="c%d"/><text x="%d" y="123.5" text-anchor="middle" class="k">%d</text><text x="%d" y="146" text-anchor="middle" class="n"%s>%s</text>' % (cx[i], i + 1, cx[i], i + 1, cx[i], extra, n))
    y, rows = 160, 0
    for area, feats in AREAS:
        top = y
        for f in feats:
            if rows % 2 == 0:
                o.append('<rect x="12" y="%d" width="616" height="26" class="stripe"/>' % y)
            o.append('<text x="86" y="%d" class="s" style="font-size:11px">%s</text>' % (y + 17, SHORT.get(f, f)))
            for n in range(1, 9):
                if (n, f) in dots:
                    o.append('<circle cx="%d" cy="%d" r="7" class="c%d"><title>Principle %d has a requirement on %s</title></circle>' % (cx[n - 1], y + 13, n, n, f))
            y += 26; rows += 1
        o.append('<text x="16" y="%d" class="h">%s</text>' % ((top + y) // 2 + 3, area.upper()))
        o.append('<path d="M12 %d L628 %d" class="rule"/>' % (y, y))
        y += 5
    o.append('<text x="12" y="%d" class="h">OUTSIDE SYSTEMS</text>' % (y + 16))
    for i, (t, sub) in enumerate([("GitHub", "repos, wiki, Actions"), ("Agent tools", "Claude Code, Codex"), ("The PC and the Mac", "the hardware it runs on")]):
        x = 28 + i * 204
        o.append('<rect x="%d" y="%d" width="176" height="42" rx="8" class="box" stroke-width="1.2"/><text x="%d" y="%d" text-anchor="middle" class="s">%s</text><text x="%d" y="%d" text-anchor="middle" class="x">%s</text>' % (x, y + 24, x + 88, y + 42, t, x + 88, y + 57, sub))
    o.append('<text x="12" y="%d" class="x">Each dot means: this principle has a requirement on this feature. One figure for all principles.</text></svg>' % (y + 88))
    return "\n".join(o) + "\n", len(dots)

if __name__ == "__main__":
    text, count = build(open("README.md").read())
    if "--check" in sys.argv:
        same = open(SVG).read() == text
        print("system-design.svg %s (%d dots)" % ("is current" if same else "is stale: run python3 dev/system-design.py", count))
        sys.exit(0 if same else 1)
    open(SVG, "w").write(text)
    print("WROTE %s (%d dots)" % (SVG, count))
