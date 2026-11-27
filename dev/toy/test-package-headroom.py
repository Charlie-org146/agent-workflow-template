#!/usr/bin/env python3
# windows: ok
# reads: dev/package.py
"""Headroom under dev/package.py's file cap: no more than its MAX_FILES shipped files (the marketplace's rule; principle 5
retired our own 19,000-byte script target, o988).

The files are counted the way package.py counts them: the ones git tracks, never __pycache__ or other loose files."""
import importlib.util
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
spec = importlib.util.spec_from_file_location("package", os.path.join(root, "dev", "package.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)
files = len(package.walk(root))
print("%s: the package holds %d files (at most %d)" % ("PASS" if files <= package.MAX_FILES else "FAIL", files, package.MAX_FILES))
raise SystemExit(1 if files > package.MAX_FILES else 0)
