#!/usr/bin/env bash
set -euo pipefail

# Fixed project-local reproduction procedure.
# This downloads free tools into this project, changing no system installation.
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
archive_name=lean-4.34.1-darwin_aarch64.tar.zst
archive_path="$project_dir/.downloads/$archive_name"
archive_digest=65f22a4f047738ec742667b3247e836a86ebf06eabc12655c3dee00637e37866
mkdir -p .downloads .tools verification
if [[ ! -f "$archive_path" ]]; then
  python3 scripts/download-lean.py
fi
printf '%s  %s\n' "$archive_digest" "$archive_path" | shasum -a 256 -c -
if [[ ! -x .tools/lean-4.34.1-darwin_aarch64/bin/lean ]]; then
  zstd -q -d -c "$archive_path" | tar -xf - -C .tools
fi
export PATH="$project_dir/.tools/lean-4.34.1-darwin_aarch64/bin:$PATH"
export MATHLIB_CACHE_DIR="$project_dir/.downloads/mathlib-cache"
lean --version
lake --version
python3 scripts/prepare-dependencies.py
python3 scripts/get-mathlib-cache.py
