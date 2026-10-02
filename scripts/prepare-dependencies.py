#!/usr/bin/env python3
"""Materialize exact official Git commits without fetching unrelated history.

The frozen Lake manifest is assembled from Mathlib's checked-in upstream lock
and the root's exact Git requirement. Lake subsequently reads this manifest;
it is not represented as output of a successful `lake update` command.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import copy
import json
import subprocess
import tomllib

root = Path(__file__).resolve().parent.parent
revision = "d13f23b723b8a846827a245b89c10fc7d3f11612"
url = "https://github.com/leanprover-community/mathlib4.git"
config = tomllib.loads((root / "lakefile.toml").read_text())
assert config["require"] == [{"name": "mathlib", "git": url, "rev": revision}]
packages_dir = root / ".lake/packages"
packages_dir.mkdir(parents=True, exist_ok=True)


def materialize(package):
    directory = packages_dir / package["name"]
    if not directory.exists():
        directory.mkdir()
        subprocess.run(["git", "init", "-q", str(directory)], check=True)
        subprocess.run(["git", "-C", str(directory), "remote", "add", "origin",
                        package["url"]], check=True)
    assert (directory / ".git").exists(), f"Not a Git checkout: {directory}"
    remote = subprocess.check_output(["git", "-C", str(directory), "remote", "get-url",
                                      "origin"], text=True).strip()
    assert remote == package["url"], (package["name"], remote)
    head = subprocess.run(["git", "-C", str(directory), "rev-parse", "--verify", "HEAD"],
                          capture_output=True, text=True)
    if head.returncode:
        subprocess.run(["git", "-C", str(directory), "fetch", "--depth=1", "--no-tags",
                        "origin", package["rev"]], check=True)
        subprocess.run(["git", "-C", str(directory), "checkout", "--detach",
                        package["rev"]], check=True)
    actual = subprocess.check_output(["git", "-C", str(directory), "rev-parse", "HEAD"],
                                     text=True).strip()
    assert actual == package["rev"], (package["name"], actual, package["rev"])
    subprocess.run(["git", "-C", str(directory), "diff", "--exit-code", "HEAD"], check=True)
    print(json.dumps({"package": package["name"], "actual_git_head": actual,
                      "verified": True}), flush=True)
    return actual


mathlib = {"url": url, "type": "git", "subDir": None, "scope": "",
           "rev": revision, "name": "mathlib", "manifestFile": "lake-manifest.json",
           "inputRev": revision, "inherited": False, "configFile": "lakefile.lean"}
materialize(mathlib)
upstream = json.loads((packages_dir / "mathlib/lake-manifest.json").read_text())
saved = json.loads((root / "evidence/mathlib-upstream-lake-manifest.json").read_text())
assert upstream == saved, "Pinned Mathlib manifest differs from saved upstream evidence"
dependencies = copy.deepcopy(upstream["packages"])
with ThreadPoolExecutor(max_workers=4) as executor:
    list(executor.map(materialize, dependencies))
for dependency in dependencies:
    dependency["inherited"] = True
manifest = {"version": upstream["version"], "packagesDir": ".lake/packages",
            "packages": dependencies + [mathlib], "name": config["name"],
            "lakeDir": ".lake", "fixedToolchain": True}
manifest_path = root / "lake-manifest.json"
if manifest_path.exists():
    assert json.loads(manifest_path.read_text()) == manifest, "Existing lock differs; refusing overwrite"
else:
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
print("Frozen Lake manifest written from verified actual Git checkouts and upstream pins.", flush=True)
