#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
export PATH="$project_dir/.tools/lean-4.34.1-darwin_aarch64/bin:$PATH"
export MATHLIB_CACHE_DIR="$project_dir/.downloads/mathlib-cache"
verification_run="$(python3 scripts/verification-record.py start --project "$project_dir")"

finish_run() {
  local command_exit=$?
  trap - EXIT
  local record_exit=0
  python3 scripts/verification-record.py finish --run-dir "$verification_run" || record_exit=$?
  if [[ "$command_exit" -ne 0 ]]; then
    exit "$command_exit"
  fi
  exit "$record_exit"
}
trap finish_run EXIT

run_gate() {
  local gate_name="$1"
  shift
  python3 scripts/verification-record.py run --run-dir "$verification_run" \
    --gate "$gate_name" -- "$@"
}

run_gate lean-version lean --version
run_gate lake-version lake --version
run_gate pins python3 scripts/check-pins.py --version-log "$verification_run/lean-version.log"
run_gate source-audit python3 scripts/source-audit.py
run_gate clean-project-build python3 scripts/clean-build.py
for module in Statement Basic Dyadic IntegerBridge Main; do
  run_gate "module-$module" lake env lean "JSP1213/$module.lean"
done
run_gate final-targets-and-axioms lake env lean Verification.lean
