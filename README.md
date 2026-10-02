# Erdős Problem 1213 / JSP-001018 — Lean formalization

An additional complete, Codex-assisted Lean implementation of the original
finite-sequence existence theorem. This project claims no new mathematical
solution, first-formalization priority or award entitlement.

For every positive integer starting value A and positive integer gap bound K,
a threshold F exists, chosen before the sequence and its length. Every nonempty
finite strictly increasing integer sequence starting at A, with each adjacent
gap at most K and last term greater than F, contains two distinct nonempty
contiguous index intervals with equal actual sums. The intervals may overlap.
The finite prefix imposes no restrictions on values outside its domain.

The established mathematics is **Norbert Hegyvári**, *On consecutive sums in
sequences*, Acta Mathematica Hungarica48 (1986),193–200,
[DOI10.1007/BF01949064](https://doi.org/10.1007/BF01949064), §3, Theorem3,
printed p.197; complete proof pp.197–198. The question is attributed to Erdős.
See [exact sources](docs/SOURCES.md) and
[Erdős1213](https://www.erdosproblems.com/1213).

## Targets and source correspondence

- `JSP1213.erdos_1213 : JSP1213.IntegerProblem` — complete integer presentation.
- `JSP1213.erdos_1213_nat : JSP1213.OriginalProblem` — natural presentation.

The definitions are in [Statement.lean](JSP1213/Statement.lean), the final
proofs in [Main.lean](JSP1213/Main.lean), and the exact-type/axiom checking entry
in [Verification.lean](Verification.lean). The proof has no admissions or
added unproved assumptions. The reported transitive axioms for both targets
are `propext`, `Classical.choice`, and `Quot.sound`.

The construction uses m=2K+1, M=2^m, B=A+KM, L=B+1, N=M(L+1),
D=M(B+2KL), and F=A+KN. More than D+1 distinct finite dyadic windows have sums
at most D, forcing equality of two different interval sums. All windows fit
inside the finite prefix. The explicit integer bridge transports the terms
and finite sums exactly. The threshold is coarser than Hegyvári's numerical
bound, but proves the entire original qualitative existence statement.
It does not claim the sharper estimate or equality with a least threshold.

See the [complete counting proof](docs/MATHEMATICAL_PROOF.md) and
[statement/case audit](docs/STATEMENT_AUDIT.md).

## Fixed-version reproduction

Lean `leanprover/lean4:v4.34.1` (commit
`5045d0056413266e57c625dcd7c365b10e377c52`); Mathlib
`d13f23b723b8a846827a245b89c10fc7d3f11612`.
All eight transitive dependency revisions are fixed in
[lake-manifest.json](lake-manifest.json) and checked against real Git HEADs
and the upstream Mathlib lock.

On macOS arm64 with Bash, curl, tar, zstd, Git and Python3.11 or newer:

```bash
git clone https://github.com/orionsheep/erdos-1213-lean.git
cd erdos-1213-lean
git checkout <selected-full-proof-commit-from-the-verification-report>
bash scripts/prepare-toolchain.sh
bash scripts/verify.sh
```

Setup downloads the free official Lean release into this project, checks its
published whole-archive SHA-256, shallow-fetches the exact dependency commits,
assembles the frozen Lake lock from those checked sources, and retrieves the
official content-addressed cache for the explicit import closure. It changes
no system toolchain. Unexpected existing pins are rejected.

Verification records actual command arguments, exits, raw output and input
hashes. It removes this project's .lake/build, builds every own module, checks
five independent modules, and checks both final types and transitive axioms.
Fixed external dependency binaries are retained; this is a clean project build,
not a rebuild of all Mathlib or an independent replay of dependency binaries.

[verification/REPORT.md](verification/REPORT.md) identifies the selected checked
proof commit A and the evidence-only descendant B. The public raw evidence at B
describes A, not an unexecuted check of B. No report is inferred from source alone.

## Contribution and prior work

Submitting account/project director: [@orionsheep](https://github.com/orionsheep).
OpenAI Codex agents performed substantial statement specification, mathematical
exposition, Lean proof engineering, debugging and checks under that direction.
This is not described as human-only proof authoring or independent human review.
The public authorship record is [ATTRIBUTION.md](docs/ATTRIBUTION.md).

Earlier complete public formalizations are acknowledged in
[PRIOR_ART.md](docs/PRIOR_ART.md). Earlier research inspected some competing
Lean sources; strict clean-room status is not claimed. No prior proof code was
copied, imported or vendored into this proof tree. The historical PDF, toolchains,
dependencies, private local research and account/goal records are not distributed.

No new-source license was specified during development. Publication retains
that status; see [LICENSE-STATUS.md](LICENSE-STATUS.md). Dependencies retain
their respective licenses. Maintainers of The Justin Sun Prize must independently
review mathematics, statement correspondence, proof checking and attribution;
public availability and successful checks do not establish prize priority.
