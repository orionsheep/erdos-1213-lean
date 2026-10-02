#!/usr/bin/env python3
"""Record fresh verification runs. Synthetic self-tests never verify Lean."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid


ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
DEFAULT_GATES = [
    "lean-version", "lake-version", "pins", "source-audit", "clean-project-build",
    "module-Statement", "module-Basic", "module-Dyadic", "module-IntegerBridge",
    "module-Main", "final-targets-and-axioms",
]
DEFAULT_TARGETS = ["JSP1213.erdos_1213_nat", "JSP1213.erdos_1213"]
EXCLUDED = {".git", ".lake", ".tools", ".downloads", "verification", "evidence"}
CONFIG_FILES = [
    "lean-toolchain", "lakefile.toml", "lakefile.lean", "lake-manifest.json",
    "scripts/verify.sh", "scripts/source-audit.py", "scripts/verification-record.py",
    "scripts/check-pins.py", "scripts/clean-build.py",
    "scripts/prepare-toolchain.sh", "scripts/prepare-dependencies.py",
    "scripts/download-lean.py", "scripts/get-mathlib-cache.py",
    "evidence/mathlib-upstream-lake-manifest.json",
]


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def snapshot(project):
    files = {p.relative_to(project).as_posix(): digest(p)
             for p in project.rglob("*.lean")
             if p.is_file() and not (set(p.relative_to(project).parts) & EXCLUDED)}
    for name in CONFIG_FILES:
        path = project / name
        files[name] = digest(path) if path.is_file() else None
    git = {}
    for name, args in [("head", ["rev-parse", "HEAD"]),
                       ("status", ["status", "--porcelain=v1", "--untracked-files=all"])]:
        result = subprocess.run(["git", "-C", str(project), *args],
                                capture_output=True, text=True)
        git[name] = {"exit_code": result.returncode, "stdout": result.stdout,
                     "stderr": result.stderr}
    return {"files": files, "git": git, "captured_utc": utc()}


@contextmanager
def locked(run_dir):
    with (run_dir / ".record.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def read_record(run_dir):
    record = json.loads((run_dir / "record.json").read_text())
    if record["run_id"] != run_dir.name:
        raise ValueError("Run directory does not match its recorded identity")
    return record


def save_record(run_dir, record):
    write_json(run_dir / "record.json", record)
    latest_path = run_dir.parent.parent / "latest.json"
    if latest_path.is_file():
        latest = json.loads(latest_path.read_text())
        if latest.get("run_id") != record["run_id"]:
            return  # An older run must not supersede a newer run's status.
    write_json(latest_path, {"run_id": record["run_id"], "kind": record["kind"],
                            "status": record["status"],
                            "record_file": str(run_dir / "record.json")})


def start(args):
    project = args.project.resolve()
    gates = args.gate or DEFAULT_GATES
    targets = args.target or DEFAULT_TARGETS
    if len(set(gates)) != len(gates) or len(set(targets)) != len(targets):
        raise ValueError("Gate and target names must be unique")
    if args.axiom_gate not in gates:
        raise ValueError("The axiom gate must be a required gate")
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+", g) for g in gates):
        raise ValueError("Gate names must be simple filename-safe identifiers")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex
    run_dir = project / "verification" / "runs" / run_id
    run_dir.mkdir(parents=True)
    record = {"schema": 1, "run_id": run_id, "kind": args.kind,
              "created_utc": utc(), "project": str(project), "status": "running",
              "required_gates": gates, "axiom_gate": args.axiom_gate,
              "targets": targets, "allowed_axioms": sorted(ALLOWED_AXIOMS),
              "initial": None, "gates": {}, "protocol_errors": []}
    write_json(run_dir / "record.json", record)
    write_json(project / "verification/latest.json",
               {"run_id": run_id, "kind": args.kind, "status": "running",
                "record_file": str(run_dir / "record.json")})
    try:
        record["initial"] = snapshot(project)
    except OSError as error:
        record.update({"status": "failed", "finished_utc": utc(),
                       "errors": ["Initial evidence capture failed: " + str(error)]})
        save_record(run_dir, record)
        print("Evidence recorder start failed; recorded at " + str(run_dir), file=sys.stderr)
        return 2
    save_record(run_dir, record)
    print(run_dir)
    return 0


def run_gate(args):
    run_dir = args.run_dir.resolve()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    with locked(run_dir):
        record = read_record(run_dir)
        if record["status"] != "running":
            raise ValueError("Run is finished; start a fresh run")
        error = None
        if args.gate not in record["required_gates"]:
            error = "Unrequested gate: " + args.gate
        elif args.gate in record["gates"]:
            error = "Gate already attempted; start a fresh run to retry: " + args.gate
        elif not command:
            error = "Gate has no command"
        log_path = run_dir / (args.gate + ".log")
        if log_path.exists():
            error = "Unexpected pre-existing gate log: " + str(log_path)
        if error:
            record["protocol_errors"].append(error)
            save_record(run_dir, record)
            raise ValueError(error)
        gate = {"argv": command, "started_utc": utc(), "status": "running",
                "log_file": log_path.name, "executed": False}
        record["gates"][args.gate] = gate
        save_record(run_dir, record)
        with log_path.open("xb") as log:
            try:
                result = subprocess.run(command, cwd=record["project"],
                                        stdout=log, stderr=subprocess.STDOUT)
                code = result.returncode
                gate["executed"] = True
            except OSError as error:
                code = 127
                gate["execution_error"] = str(error)
                log.write((str(error) + "\n").encode())
            except KeyboardInterrupt:
                code = 130
                gate["interrupted"] = True
                log.write(b"Evidence recorder interrupted during command.\n")
        gate.update({"exit_code": code, "ended_utc": utc(), "log_digest": digest(log_path),
                     "status": "passed" if code == 0 else "failed"})
        save_record(run_dir, record)
        sys.stdout.write(log_path.read_text(errors="replace"))
    return code if code >= 0 else 128 - code


def parse_axioms(output, targets):
    pattern = re.compile(
        r"^'([^'\n]+)' (?:depends on axioms:\s*\[([^\]]*)\]|"
        r"does not depend on any axioms)\s*$", re.MULTILINE)
    reports = {}
    errors = []
    for match in pattern.finditer(output):
        name = match.group(1)
        axioms = {v.strip() for v in (match.group(2) or "").split(",") if v.strip()}
        if name in reports:
            errors.append("Duplicate axiom report for " + name)
        reports[name] = sorted(axioms)
        if axioms - ALLOWED_AXIOMS:
            errors.append("Forbidden axioms for " + name + ": " + str(sorted(axioms - ALLOWED_AXIOMS)))
    if set(reports) != set(targets):
        errors.append("Axiom report names differ from exact required targets: " + str(sorted(reports)))
    return reports, errors


def finish(args):
    run_dir = args.run_dir.resolve()
    with locked(run_dir):
        record = read_record(run_dir)
        if record["status"] != "running":
            raise ValueError("Run is already finished; its historical result is immutable")
        errors = list(record["protocol_errors"])
        for name in record["required_gates"]:
            gate = record["gates"].get(name)
            if not gate or not gate.get("executed") or gate.get("exit_code") != 0:
                errors.append("Required gate did not execute successfully: " + name)
                continue
            path = run_dir / gate["log_file"]
            if not path.is_file() or digest(path) != gate.get("log_digest"):
                errors.append("Gate log missing or changed: " + name)
        final = snapshot(Path(record["project"]))
        record["final"] = final
        if final["files"] != record["initial"]["files"]:
            errors.append("Proof/configuration/lock source inventory changed during run")
        if record["initial"]["git"]["head"]["exit_code"] != 0 or final["git"]["head"]["exit_code"] != 0:
            errors.append("Exact Git HEAD unavailable")
        elif final["git"]["head"]["stdout"] != record["initial"]["git"]["head"]["stdout"]:
            errors.append("Git HEAD changed during run")
        if any(s["git"]["status"]["exit_code"] != 0 for s in [record["initial"], final]):
            errors.append("Exact Git dirty status unavailable")
        files = record["initial"]["files"]
        for name in ["lean-toolchain", "lake-manifest.json", "Verification.lean"]:
            if files.get(name) is None:
                errors.append("Required pinned input missing at start: " + name)
        if files.get("lakefile.toml") is None and files.get("lakefile.lean") is None:
            errors.append("Lake configuration missing at start")
        reports = {}
        gate = record["gates"].get(record["axiom_gate"])
        if gate and gate.get("executed") and gate.get("exit_code") == 0:
            log = run_dir / gate["log_file"]
            if log.is_file() and digest(log) == gate.get("log_digest"):
                reports, axiom_errors = parse_axioms(log.read_text(errors="replace"), record["targets"])
                errors.extend(axiom_errors)
        else:
            errors.append("Target axiom gate did not execute successfully")
        record.update({"finished_utc": utc(), "errors": errors, "target_axioms": reports,
                       "status": "failed" if errors else
                       ("verified" if record["kind"] == "actual" else "recorder-test-passed")})
        save_record(run_dir, record)
        print(json.dumps({"run_id": record["run_id"], "kind": record["kind"],
                          "status": record["status"], "errors": errors}, indent=2))
    return 1 if errors else 0


def self_test(_args):
    """Exercise recorder failure isolation using explicitly synthetic fixtures."""
    script = str(Path(__file__).resolve())

    def cli(*arguments, expected=0):
        result = subprocess.run([sys.executable, script, *map(str, arguments)],
                                capture_output=True, text=True)
        if result.returncode != expected:
            raise AssertionError((arguments, result.returncode, result.stdout, result.stderr))
        return result.stdout.strip()

    with tempfile.TemporaryDirectory(prefix="evidence-recorder-test-") as directory:
        project = Path(directory)
        for name in ["Fixture.lean", "Verification.lean", "lean-toolchain", "lakefile.toml", "lake-manifest.json"]:
            (project / name).write_text("synthetic evidence-recorder fixture; not Lean input\n")
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "add", "."], check=True)
        subprocess.run(["git", "-C", str(project), "-c", "user.name=Recorder Fixture",
                        "-c", "user.email=recorder@example.invalid", "commit", "-qm", "synthetic fixture"], check=True)

        def fresh():
            return Path(cli("start", "--project", project, "--kind", "evidence-recorder-test",
                            "--gate", "build", "--gate", "axioms", "--axiom-gate", "axioms",
                            "--target", "Fixture.target"))

        def gate(run, name, code, expected=0):
            cli("run", "--run-dir", run, "--gate", name, "--", sys.executable, "-c", code, expected=expected)

        valid = "print(\"'Fixture.target' depends on axioms: [propext]\")"

        def successful_gates(run, output=valid):
            gate(run, "build", "print('synthetic build gate; no Lean execution')")
            gate(run, "axioms", output)

        run = fresh()
        successful_gates(run)
        cli("finish", "--run-dir", run)
        assert json.loads((run / "record.json").read_text())["status"] == "recorder-test-passed"
        cases = ["synthetic success cannot claim Lean verified"]
        unavailable = subprocess.run(
            [sys.executable, script, "start", "--project", str(project),
             "--kind", "evidence-recorder-test"],
            env={"PATH": str(project / "no-git-executable")}, capture_output=True, text=True)
        assert unavailable.returncode == 2
        assert json.loads((project / "verification/latest.json").read_text())["status"] == "failed"
        cases.append("failed initial capture supersedes prior success")
        run = fresh()  # The previous complete run must supply no status/log to this one.
        cli("finish", "--run-dir", run, expected=1)
        assert not json.loads((run / "record.json").read_text())["gates"]
        cases.append("stale prior success is not inherited")
        run = fresh()
        gate(run, "build", "raise SystemExit(7)", expected=7)
        gate(run, "axioms", valid)
        cli("finish", "--run-dir", run, expected=1)
        cases.append("failed build cannot verify")
        for label, output in [
            ("forbidden axiom rejected", "print(\"'Fixture.target' depends on axioms: [propext, sorryAx]\")"),
            ("wrong target rejected", "print(\"'Fixture.other' does not depend on any axioms\")"),
        ]:
            run = fresh()
            successful_gates(run, output)
            cli("finish", "--run-dir", run, expected=1)
            cases.append(label)
        run = fresh()
        successful_gates(run)
        (project / "Fixture.lean").write_text("changed synthetic source\n")
        cli("finish", "--run-dir", run, expected=1)
        cases.append("changing source rejected")
        run = fresh()
        successful_gates(run)
        (run / "axioms.log").write_text("changed log\n")
        cli("finish", "--run-dir", run, expected=1)
        cases.append("changed gate log rejected")
        latest = json.loads((project / "verification/latest.json").read_text())
        assert latest["run_id"] == run.name and latest["status"] == "failed"
        print(json.dumps({"test_kind": "synthetic evidence-recorder behavior tests; not Lean checks",
                          "passed": len(cases), "cases": cases}, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    p = commands.add_parser("start")
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--gate", action="append")
    p.add_argument("--target", action="append")
    p.add_argument("--axiom-gate", default="final-targets-and-axioms")
    p.add_argument("--kind", choices=["actual", "evidence-recorder-test"], default="actual")
    p.set_defaults(function=start)
    p = commands.add_parser("run")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--gate", required=True)
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(function=run_gate)
    p = commands.add_parser("finish")
    p.add_argument("--run-dir", type=Path, required=True)
    p.set_defaults(function=finish)
    p = commands.add_parser("self-test")
    p.set_defaults(function=self_test)
    args = parser.parse_args()
    try:
        return args.function(args)
    except (OSError, ValueError, KeyError) as error:
        print("Evidence recorder: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
