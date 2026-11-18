#!/usr/bin/env python3
# windows: ok
"""Break one rule of the docs-gate-scope goal in the current checkout, so `regression.py red ID --break "python3 dev/toy/break-docs-gate-scope.py NAME"`
can show its row fails without it. usage: break-docs-gate-scope.py NAME"""
import sys

REL = "skills/workflow-release/scripts/release.py"
MER = "skills/workflow-release/scripts/merge.py"
WIKI = "skills/workflow-release/scripts/wiki.py"
MS = "skills/workflow-docs/scripts/milestones.py"
BREAKS = {
    "gate-all-kept": (REL, "if page and not any(", "if False and not any("),
    "gate-no-filer": (REL, 'filer(top, page, texts) if filer else "left for health"', '"left for health"'),
    "gate-one-line-per-page": (REL, "moved.setdefault(page, []).append(line)", "moved[page] = [line]"),
    "gate-all-docs-kinds": (REL, "DOC-(?:19|4) ", "DOC-"),
    "gate-changed-moved": (REL, "f == page or f.endswith", "f == page and f.endswith"),
    "gate-base-scoped": (REL, ' or run(["git", "merge-base", "--is-ancestor", "HEAD", base], top).returncode == 0', ""),
    "gate-no-dedupe": (MER, "if title in gh(", "if False and title in gh("),
    "gate-feature-milestone": (MER, 'page[11:] if page.startswith("How-to-use-")', 'page if page.startswith("How-to-use-")'),
    "gate-docs-milestone": (MER, '"Documentation" if "/" in page or page == "Home" else page', "page"),
    "gate-gh-fails-raises": (MER, "except (OSError, IndexError):", "except OSError:"),
    "gate-gh-missing-raises": (MER, "except (OSError, IndexError):", "except IndexError:"),
    "gate-pending-unscoped": (WIKI, "release.untouched(tree, base, release.docs_trouble(tree, base, whole=True), filer)", "release.docs_trouble(tree, base, whole=True)"),
    "gate-left-silent": (REL, 'if filer else "left for health"', 'if filer else ""'),
    "gate-split-whitespace": (REL, 'diff.stdout.split("\\0")', "diff.stdout.split()"),
    "gate-feature-page-ignored": (REL, 're.sub("^How-to-use-", "", page) + ".md"', 'page + ".md"'),
    "gate-list-failure-creates": (MER, "held.returncode or title in", "title in"),
    "links-sites-ignored": (MS, "for o in sites)", "for o in ())"),
    "links-sites-default": (MS, 'def stands_alone(page, text, repo="", sites=()):', 'def stands_alone(page, text, repo="", sites=("https://demo.example.org",)):'),
    "links-lookalike-passes": (MS, 'in ("", "/", "?", "#")', 'in ("", "/", "?", "#", ".")'),
    "links-source-passes": (MS, "/blob/[^/]+/README\\.md", "/blob/.*"),
    "links-config-ignored": (MS, 'get("public_origins")', 'get("public_origin")'),
    "links-file-ignored": (MS, '"public-origins.json"', '"public-origin.json"'),
    "links-broken-file-raises": (MS, "except (OSError, ValueError, TypeError, AttributeError):", "except OSError:"),
    "links-alone-ignores-sites": (MS, "out, sites = [], origins(root)", "out, sites = [], ()"),
}

path, old, new = BREAKS[sys.argv[1]]
with open(path, encoding="utf-8", newline="") as handle:
    text = handle.read()
if text.count(old) != 1:
    sys.exit("cannot break %s: %r found %d times in %s" % (sys.argv[1], old, text.count(old), path))
with open(path, "w", encoding="utf-8", newline="") as handle:
    handle.write(text.replace(old, new))
