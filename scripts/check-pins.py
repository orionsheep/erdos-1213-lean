#!/usr/bin/env python3
"""Check installed version and every library revision against fixed inputs."""
import argparse
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--version-log", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
assert (root / "lean-toolchain").read_text().strip() == "leanprover/lean4:v4.34.1"
version = args.version_log.read_text()
version_match = re.search(r"\bversion ([^,\s)]+)", version)
assert version_match and version_match.group(1) == "4.34.1", version
actual = json.loads((root / "lake-manifest.json").read_text())
upstream = json.loads((root / "evidence/mathlib-upstream-lake-manifest.json").read_text())
expected = {p["name"]: p["rev"] for p in upstream["packages"]}
expected["mathlib"] = "d13f23b723b8a846827a245b89c10fc7d3f11612"
found = {p["name"]: p["rev"] for p in actual["packages"]}
assert found == expected, (found, expected)
for name, revision in expected.items():
    package_dir = root / actual.get("packagesDir", ".lake/packages") / name
    head = subprocess.check_output(["git", "-C", str(package_dir), "rev-parse", "HEAD"], text=True).strip()
    assert head == revision, (name, head, revision)
    subprocess.run(["git", "-C", str(package_dir), "diff", "--exit-code", "HEAD"], check=True)
print("Lean and all library repository versions match the fixed pins.")
print(json.dumps(found, indent=2, sort_keys=True))
