#!/usr/bin/env python3
"""Get the fixed libraries' cache only for the project's explicit imports."""
from pathlib import Path
import json
import re
import subprocess

root = Path(__file__).resolve().parent.parent
modules = set()
for path in sorted((root / "JSP1213").glob("*.lean")):
    for line in path.read_text().splitlines():
        match = re.fullmatch(r"import (Mathlib(?:\.[A-Za-z0-9_]+)*)", line.strip())
        if match:
            modules.add(match.group(1))
if "Mathlib" in modules:
    raise SystemExit("A broad Mathlib import remains; review imports before selective setup")
if not modules:
    raise SystemExit("No explicit Mathlib dependency imports found")
selection = {"modules": sorted(modules),
             "mathlib_commit": "d13f23b723b8a846827a245b89c10fc7d3f11612",
             "mode": "content-addressed cache of listed modules and all imports"}
(root / "verification/cache-selection.json").write_text(json.dumps(selection, indent=2) + "\n")
print(json.dumps(selection, indent=2), flush=True)
raise SystemExit(subprocess.run(["lake", "exe", "cache", "get", *sorted(modules)], cwd=root).returncode)
