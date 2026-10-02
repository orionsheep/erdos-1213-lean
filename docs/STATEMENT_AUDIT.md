# Correspondence to the original problem

The target is [Erdős Problem 1213](https://www.erdosproblems.com/1213), catalog ID JSP-001018. Hegyvári's historical statement appears in *On consecutive sums in sequences*, Section 3, printed p.197, with a complete affirmative proof on pp.197–198. See [SOURCES.md](SOURCES.md) for exact bibliographic and archive coordinates.

For every positive integer initial value and positive integer upper bound on adjacent gaps, one threshold must work for every strictly increasing nonempty finite integer sequence with that initial value and gap bound. If its last term exceeds that threshold, two different nonempty consecutive index intervals must have equal actual sums. Their intervals may overlap.

The exact signed endpoint is `JSP1213.erdos_1213 : JSP1213.IntegerProblem`. The natural endpoint is `JSP1213.erdos_1213_nat : JSP1213.OriginalProblem`. The complete definitions are in [Statement.lean](../JSP1213/Statement.lean).

| Original requirement | Lean representation |
| --- | --- |
| Arbitrary positive integer parameters | `∀ A K : ℤ, 0 < A → 0 < K → ...` in `IntegerProblem`; corresponding natural quantification in `OriginalProblem`. |
| Threshold depends only on parameters | `∃ F` precedes `∀ n` and `∀ z`/`∀ a`. |
| Nonempty finite sequence | A total index function and a finite prefix length `n`, with `length_pos : 0 < n`. |
| Prescribed initial value | `first : z 0 = A` or `a 0 = A`. |
| Strict increase throughout the prefix | `i < j → j < n → z i < z j`, with the natural counterpart. |
| Upper adjacent gap bound | `i + 1 < n → z (i + 1) ≤ z i + K`; this avoids truncated natural subtraction. |
| Last term exceeds threshold | `F < z (n - 1)` or `F < a (n - 1)`. |
| Nonempty consecutive intervals inside the prefix | Half-open intervals `[l,r)` and `[l',r')`, with `l < r ≤ n` and `l' < r' ≤ n`. |
| Distinct intervals | `(l,r) ≠ (l',r')`. |
| Equal actual sums | `integerBlockSum` or `blockSum` uses finite sums over `Finset.Ico`. |
| Permitted overlap | No separation or disjointness requirement is imposed. |
| No conditions on unused values | Order and gap assumptions concern only indices below `n`. |

A finite tuple can be extended arbitrarily to a total function; the proof uses only its initial prefix. Conversely, restricting that function to the prefix recovers the tuple. Distinct endpoint pairs describe distinct nonempty consecutive index intervals.

Length zero is excluded by the original nonempty-sequence hypothesis. Length one is retained, and the chosen threshold is at least the initial value, so the last-term trigger cannot hold there. Length two, all larger lengths and gap bound one remain within the statement; the proof derives any needed lower length from the last-term trigger rather than adding it as an input assumption.

[IntegerBridge.lean](../JSP1213/IntegerBridge.lean) derives positivity of every term inside a signed prefix from its positive first value and strict increase. Conversion through `Int.toNat` is exact only on that finite domain, where it is needed. The natural threshold is selected before the sequence, casts preserve both interval sums termwise, and the same four endpoint witnesses preserve bounds and distinctness. Negative or arbitrary unused tail values require no conversion identity.

The explicit threshold in [Main.lean](../JSP1213/Main.lean) is coarser than Hegyvári's published quantitative bound. It proves the complete original qualitative existence statement; no claim is made about that sharper bound or the canonical least sufficient threshold.

[Verification.lean](../Verification.lean) checks both named endpoints, prints the complete specifications and relevant definitions, checks exact-type assignments, and requests both transitive axiom reports. The reproduction workflow additionally performs a clean project build, separate module checks, dependency-pin checks and a static admission scan. Compiler results and axiom dependencies are established by the fresh executed verification evidence described in the repository README; this correspondence document alone is not a build certificate.
