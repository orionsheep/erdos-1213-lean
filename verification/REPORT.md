# Pre-submission verification — complete original theorem

Repository: https://github.com/orionsheep/erdos-1213-lean
Branch: main
Selected proof commit A: `91c2904b0012ed1f0690fd0ed54b12646ab25ed1`
Actual run: `20261002T065449Z-0894198d119e418eb520c02508cd0f24`
Verification date: 2026-10-02T06:55:26.295192+00:00
Verdict: **passed all eleven required gates**, with no recorded errors.

This report and the raw outputs are stored in an evidence-only descendant
commit B. They describe proof commit A; adding this report does not represent
an unexecuted check of B. All recorded proof/configuration inputs match Git
blobs at A and remained unchanged between capture and completion.

The actual check ran in the generic temporary workspace
`/private/tmp/jsp-001018-public-check`. Existing fixed-version runtime and
external dependency artifacts were reused through local links excluded from publication. Setup
actually verified the official archive SHA-256, all nine real Git HEADs and
tracked dependency source, the upstream frozen lock and selected cache closure.
Its exit was0. No private local paths or account usage records are published.
The raw logs and run record are unedited actual outputs; no hashed record was
redacted and advertised as original.

## Actual commands and results

```bash
bash scripts/prepare-toolchain.sh  # exit0
bash scripts/verify.sh             # exit0; all11 gates
```

The eleven successful gates are actual Lean version, actual Lake version,
all dependency pins, static source admission scan, clean project build,
Statement, Basic, Dyadic, IntegerBridge, Main, and final target/type/axiom checks.
The clean step removed this project's `.lake/build` and actually rebuilt all
six own modules. The independent module checks each executed
`lake env lean JSP1213/<module>.lean` with exit0.

The final entry executed `lake env lean Verification.lean`, including both
exact-type example assignments and expanded prefix, interval and sum definitions.
It checked `JSP1213.erdos_1213 : JSP1213.IntegerProblem` and
`JSP1213.erdos_1213_nat : JSP1213.OriginalProblem`.

```text
'JSP1213.erdos_1213_nat' depends on axioms: [propext, Classical.choice, Quot.sound]
'JSP1213.erdos_1213' depends on axioms: [propext, Classical.choice, Quot.sound]
```

No custom unproved axiom or `sorryAx` occurs in either reported closure.
The static scan separately found no active sorry/admit/sorryAx/axiom token
in the seven-file proof/check tree. Exact versions: Lean4.34.1, commit
5045d0056413266e57c625dcd7c365b10e377c52; Lake5.0.0-src+5045d00;
Mathlibd13f23b723b8a846827a245b89c10fc7d3f11612, with all eight upstream
dependencies fixed in lake-manifest.json and verified against real Git HEADs.

## Scope and limits

[Statement correspondence](../docs/STATEMENT_AUDIT.md) covers the complete
original qualitative finite-sequence existence problem: arbitrary positive
integer parameters, threshold before the sequence, all nonempty finite lengths,
strict increase, bounded adjacent gaps, distinct nonempty contiguous intervals
and actual equal sums, with overlap permitted. No extra mathematical assumption
was introduced. The numerical threshold is coarser than Hegyvári's; his sharper
estimate and a canonical least-threshold equality are not claimed.

Fixed external dependency binaries were retained. A from-source rebuild of all
Mathlib and an independent kernel replay of dependency binaries were **not
executed**. This is a project clean build and standard Lean checking under its
explicit dependency/toolchain trust. Self-checking and Codex agent scope review
do not establish independent human review, organizer acceptance, priority or
award entitlement. Maintainer verification remains pending.

## Raw evidence

- [Source-bound run record](runs/20261002T065449Z-0894198d119e418eb520c02508cd0f24/record.json)
- [Clean project build](runs/20261002T065449Z-0894198d119e418eb520c02508cd0f24/clean-project-build.log)
- [Complete types, definitions and transitive axioms](runs/20261002T065449Z-0894198d119e418eb520c02508cd0f24/final-targets-and-axioms.log)
- [Actual dependency-pin checks](runs/20261002T065449Z-0894198d119e418eb520c02508cd0f24/pins.log)
- [Actual Lean version](runs/20261002T065449Z-0894198d119e418eb520c02508cd0f24/lean-version.log)
- [Setup output](setup.log) and [setup exit](setup.exit)
- [Full verification output](verification.log) and [exit](verification.exit)
