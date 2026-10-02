#!/usr/bin/env python3
"""Retrieve the pinned official Lean asset in checked, resumable HTTP ranges."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import json
import re
import socket
import subprocess
import time

root = Path(__file__).resolve().parent.parent
downloads = root / ".downloads"
downloads.mkdir(exist_ok=True)
parts = downloads / "lean-ranges"
parts.mkdir(exist_ok=True)
size = 562038070
expected_sha = "65f22a4f047738ec742667b3247e836a86ebf06eabc12655c3dee00637e37866"
archive = downloads / "lean-4.34.1-darwin_aarch64.tar.zst"
chunk_size = 4 * 1024 * 1024
asset_api = "https://api.github.com/repos/leanprover/lean4/releases/assets/586761729"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()

if archive.exists() and archive.stat().st_size == size and sha256(archive) == expected_sha:
    print("Existing complete official asset passes SHA-256.", flush=True)
    raise SystemExit(0)

head = downloads / "fresh-asset-api-head.headers"
subprocess.run(["curl", "--fail", "--silent", "--show-error", "--connect-timeout", "10",
                "--max-time", "30", "--head", "-H", "Accept: application/octet-stream",
                asset_api, "--output", str(head)], check=True)
url = next(line.split(":", 1)[1].strip() for line in head.read_text().splitlines()
           if line.lower().startswith("location:"))
host = urlparse(url).hostname
if host != "release-assets.githubusercontent.com":
    raise SystemExit("Unexpected official asset redirect host")
ips = sorted({r[4][0] for r in socket.getaddrinfo(host, 443, family=socket.AF_INET)})
if not ips:
    raise SystemExit("No official CDN IPv4 address resolved")
print("Official CDN checked ranges; source SHA-256 remains the published release digest.", flush=True)

def download(index):
    start = index * chunk_size
    end = min(size - 1, start + chunk_size - 1)
    count = end - start + 1
    path = parts / f"{index:04}.part"
    header = parts / f"{index:04}.headers"
    expected_range = f"bytes {start}-{end}/{size}"
    def valid():
        if not path.exists() or path.stat().st_size != count or not header.exists():
            return False
        ranges = re.findall(r"(?im)^content-range:\s*([^\r\n]+)", header.read_text())
        return bool(ranges and ranges[-1].strip() == expected_range)
    if valid():
        return index, count, "reused"
    errors = []
    for attempt in range(4):
        temporary = path.with_suffix(".partial")
        address = ips[(index + attempt) % len(ips)]
        result = subprocess.run([
            "curl", "--fail", "--silent", "--show-error", "--connect-timeout", "8",
            "--max-time", "120", "--speed-limit", "1024", "--speed-time", "30",
            "--resolve", f"{host}:443:{address}", "--range", f"{start}-{end}",
            "--dump-header", str(header), "--output", str(temporary), url
        ], capture_output=True, text=True)
        if result.returncode == 0:
            temporary.replace(path)
            if valid():
                return index, count, "downloaded"
        errors.append({"attempt": attempt + 1, "exit": result.returncode,
                       "error": result.stderr.strip()})
        time.sleep(min(2 * (attempt + 1), 6))
    raise RuntimeError(f"Range {index} failed: {errors}")

count = (size + chunk_size - 1) // chunk_size
received = 0
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = [pool.submit(download, i) for i in range(count)]
    for completed, future in enumerate(as_completed(futures), 1):
        index, amount, kind = future.result()
        received += amount
        print(json.dumps({"parts_complete": completed, "parts_total": count,
                          "checked_range_bytes": received, "index": index, "kind": kind}),
              flush=True)
merged = archive.with_suffix(".assembling")
with merged.open("wb") as output:
    for i in range(count):
        with (parts / f"{i:04}.part").open("rb") as source:
            for data in iter(lambda: source.read(4 * 1024 * 1024), b""):
                output.write(data)
actual_sha = sha256(merged)
result = {"source": "official GitHub release asset via checked CDN byte ranges",
          "asset_id": 586761729, "bytes": merged.stat().st_size,
          "expected_sha256": expected_sha, "actual_sha256": actual_sha,
          "passed": merged.stat().st_size == size and actual_sha == expected_sha}
(root / "verification/lean-download-integrity.json").write_text(json.dumps(result, indent=2) + "\n")
if not result["passed"]:
    raise SystemExit("Merged asset failed official full SHA-256; not installing it")
merged.replace(archive)
print(json.dumps(result, indent=2), flush=True)
