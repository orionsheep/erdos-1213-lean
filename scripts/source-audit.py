#!/usr/bin/env python3
"""A static admission scan. A pass is not a kernel correctness certificate."""

from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parent.parent
paths = sorted((root / "JSP1213").glob("*.lean"))
paths += [root / "JSP1213.lean", root / "Verification.lean"]


def code_only(source):
    # Strip nested block comments, line comments, and escaped string literals.
    out, i, depth = [], 0, 0
    while i < len(source):
        if depth:
            if source.startswith("/-", i):
                depth += 1
                i += 2
            elif source.startswith("-/", i):
                depth -= 1
                i += 2
            else:
                i += 1
        elif source.startswith("/-", i):
            depth = 1
            out.append(" ")
            i += 2
        elif source.startswith("--", i):
            end = source.find("\n", i)
            i = len(source) if end == -1 else end
        elif source[i] == '"':
            i += 1
            while i < len(source):
                if source[i] == "\\":
                    i += 2
                elif source[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            out.append(" ")
        else:
            out.append(source[i])
            i += 1
    if depth:
        raise ValueError("Unclosed block comment")
    return "".join(out)


records = []
for path in paths:
    data = path.read_bytes()
    tokens = re.findall(r"(?<![\w'])\b(sorry|admit|sorryAx|axiom)\b", code_only(data.decode()))
    records.append({"file": str(path.relative_to(root)), "sha256": hashlib.sha256(data).hexdigest(),
                    "prohibited_tokens": tokens})
result = {"files": records, "status": "failed" if any(r["prohibited_tokens"] for r in records) else "passed",
          "scope": "static source only; dependencies and transitive axioms require actual Lean checks"}
print(json.dumps(result, indent=2))
raise SystemExit(result["status"] != "passed")
