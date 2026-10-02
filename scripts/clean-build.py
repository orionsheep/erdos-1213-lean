#!/usr/bin/env python3
"""Clean this project's proof outputs, then actually invoke Lake."""
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parent.parent
build_dir = root / ".lake/build"
if build_dir.exists():
    shutil.rmtree(build_dir)
print("Removed generated project proof outputs; fixed dependency binaries retained.", flush=True)
raise SystemExit(subprocess.run(["lake", "build"], cwd=root).returncode)
