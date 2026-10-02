# An explicit finite proof of Erdős problem 1213

This document is an independently written mathematical proof for JSP-001018 / Erdős problem 1213. It uses the counting idea in Hegyvári's published solution, replacing the analytic estimates by dyadic length groups. It does not claim a new mathematical discovery, a sharper bound, prize eligibility, or a completed Lean verification. Actual Lean checks belong in the project's verification record.

## Original scope and attribution

The problem asks: for every pair of positive integers `A,K`, does there exist a threshold `F(A,K)` such that every finite strictly increasing integer sequence beginning at `A`, with adjacent gaps at most `K`, and ending above `F(A,K)`, has two different nonempty consecutive blocks of equal sum? The blocks may overlap. They are different when their pairs of index endpoints differ.

The current source is [Erdős problem 1213](https://www.erdosproblems.com/1213). N. Hegyvári, *On consecutive sums in sequences*, Acta Mathematica Hungarica 48 (1986), pp.193–200, [DOI 10.1007/BF01949064](https://doi.org/10.1007/BF01949064), Section 3, printed p.197, states the original question and credits Erdős's personal communication. Theorem 3 is on p.197 and its proof is on pp.197–198. The complete article is available in the [MTA journal archive](https://real-j.mtak.hu/7472/1/MTA_ActaMathHung_48.pdf), one-based archive PDF pages 199–206; printed pages 197–198 correspond to archive PDF pages 203–204. This repository links the historical publication and does not redistribute its PDF.

Hegyvári proves the stronger quantitative estimate involving exponentials. The proof below supplies an elementary, larger threshold sufficient for the original existence question; it does not formalize the sharper quantitative estimate of Theorem 3. No third-party Lean implementation was consulted to derive this proof.

## Precise finite statement

Fix natural numbers `A,K` with `A > 0` and `K > 0`. A sequence of length `n > 0` is a function on indices `0,...,n-1`. For Lean convenience it may be represented by a total function `a : ℕ → ℕ`, imposing assumptions only on that initial segment. Its values outside the segment play no role. Require:

- `a(0) = A`;
- `a(i) < a(j)` whenever `i < j < n`;
- `a(i+1) ≤ a(i)+K` whenever `i+1 < n`.

For `0 ≤ l < r ≤ n`, write

\[
 S_a(l,r)=\sum_{q=l}^{r-1}a(q).
\]

The conclusion is that there exist `l<r≤n` and `l'<r'≤n` with `(l,r)≠(l',r')` and `S_a(l,r)=S_a(l',r')`. These are half-open index intervals. The corresponding inclusive intervals are `[l,r-1]` and `[l',r'-1]`; since each length is positive, the two conventions are equivalent and preserve distinctness.

The final theorem must choose `F` before `n` and `a`. In particular, choosing a threshold after inspecting an individual sequence would not prove this problem.

## Explicit constants

Define, using natural arithmetic only,

\[
\begin{aligned}
 m&=2K+1, & M&=2^m,\\
 B&=A+KM, & L&=B+1,\\
 N&=M(L+1), & D&=M(B+2KL),\\
 F(A,K)&=A+KN.
\end{aligned}
\]

Here `m≥3`, `M≥8`, `L≥1`, and `N>0`. The counting argument only needs `M>1`, which also follows from `m=2K+1≥1` when `K=0`. It likewise permits `A=0`, but the final original theorem retains both `A>0` and `K>0`.

The constants are intentionally large. No optimality is asserted.

## 1. A linear upper bound for the terms

For each `q<n`,

\[
 a(q)\le A+Kq.
\]

Proof is by induction on `q`. For `q=0` it is the first-term condition. For `q+1<n`, induction applies because `q<n`, and the gap condition gives

\[
 a(q+1)\le a(q)+K\le A+Kq+K=A+K(q+1).
\]

Neither strict increase nor positivity is needed for this upper-bound lemma. This stronger helper lemma does not remove those assumptions from the final original theorem.

## 2. An endpoint above the threshold supplies enough indices

Assume `F(A,K)<a(n-1)`. Since `n>0`, the linear bound applies to `n-1`. If `n≤N`, then `n-1≤N` and

\[
 a(n-1)\le A+K(n-1)\le A+KN=F(A,K),
\]

a contradiction. Therefore `N<n`; in particular every index below `N` is inside the finite sequence. This step explicitly justifies the finite supply of blocks; it does not extend a finite sequence to an infinite sequence satisfying the gap condition.

## 3. A finite family of dyadic blocks

For each `r=0,...,m-1`, select all pairs

\[
 0\le i<L2^{m-r},\qquad 0\le t<2^r.
\]

Assign the length `j=2^r+t` and the block `[i,i+j)`. Thus

\[
 2^r\le j<2^{r+1}\le 2^m=M,
\]

so `j≥1` and `j≤M`. Also `2^{m-r}≤M`, because `0≤m-r≤m`. Consequently

\[
 i+j\le LM+M=N.
\]

Every chosen block is nonempty and contained in the first `N` terms. The proof uses weak inequalities for these estimates; the strict bounds on `i` and `j` are retained for counting and for uniqueness of the length band.

The product of its start and its length satisfies

\[
\begin{aligned}
 ij
 &\le (L2^{m-r})2^{r+1}\\
 &=L2^{(m-r)+(r+1)}\\
 &=L2^{m+1}=2LM.
\end{aligned}
\]

The exponent equality uses `r<m`, hence `r≤m` and `(m-r)+r=m`. Natural-number subtraction here is justified, rather than silently treated as integer subtraction.

### Distinct parameters give distinct blocks

Suppose the pairs `(i,j)` from two parameter triples coincide. The common length cannot lie in different dyadic bands. Indeed, if `r<s`, then `r+1≤s`, hence

\[
 j<2^{r+1}\le2^s\le j,
\]

a contradiction. The case `s<r` is symmetric. Thus `r=s`; equality of lengths `2^r+t=2^r+t'` gives `t=t'`, and equality of starts gives `i=i'`. The parameter triples coincide.

Likewise, equality of endpoint pairs `(i,i+j)` forces equality of `(i,j)` by cancellation of the common start. Therefore different parameter triples produce different interval endpoint pairs, even when the intervals overlap.

### Exact cardinality

For each `r`, the number of starts is `L2^{m-r}` and the number of lengths is `2^r`. Their product is

\[
 (L2^{m-r})2^r=L2^m=LM.
\]

There are `m` bands, so the family has exactly `mLM` members. A dependent finite type encodes the family without floors or unions with multiplicities:

\[
 \coprod_{r\in\operatorname{Fin}(m)}
 \operatorname{Fin}(L2^{m-r})\times\operatorname{Fin}(2^r).
\]

Its elements keep the band, start, and length offset. The injectivity just proved shows that its cardinality counts distinct blocks.

## 4. Every selected sum is at most `D`

Let `[i,i+j)` be a selected block. For each of its indices `q`, we have `q<i+j≤N<n`. The linear bound and monotonicity of multiplication by `K` give

\[
 a(q)\le A+Kq\le A+K(i+j).
\]

Summing over the `j` indices gives

\[
\begin{aligned}
 S_a(i,i+j)
 &\le j\bigl(A+K(i+j)\bigr)\\
 &=jA+Kij+Kj^2\\
 &\le MA+2KLM+KM^2\\
 &=M(A+KM+2KL)=D.
\end{aligned}
\]

The three estimates use respectively `j≤M`, `ij≤2LM`, and `j≤M` twice to infer `j²≤M²`. The interval-cardinality identity is `|(Finset.Ico i (i+j))|=j`. No source index beyond `n-1` occurs.

## 5. The pigeonhole contradiction

Using `m=2K+1` and `L=B+1`, the family cardinality is

\[
\begin{aligned}
 mLM
 &=M\bigl((2K+1)L\bigr)\\
 &=M(2KL+B+1)\\
 &=D+M.
\end{aligned}
\]

Since `M>1`, this is strictly larger than `D+1`. Map each family member to its block sum as an element of `Fin(D+1)`; the bound above supplies the proof that the value is less than `D+1`. The codomain has cardinality `D+1`, so this map cannot be injective. Hence two different family members have equal block sums. Injectivity of the parameter-to-endpoint map shows that their endpoint pairs are different. All their blocks are nonempty and end at most at `N<n`.

This proves the complete original existence conclusion with the specified `F(A,K)`.

We use the codomain `{0,...,D}`, which has `D+1` elements. Although the original sums are positive, the proof needs no separate positivity lemma and makes no off-by-one inference about a codomain of size `D`.

## Integer presentation and edge cases

For a positive integer start `A` and a strictly increasing integer-valued finite sequence, all its entries inside the finite domain are positive. In particular, they are nonnegative. Taking natural-number values preserves each such integer exactly. The adjacent integer inequality `z(i+1)≤z(i)+K` becomes the corresponding natural inequality for `K.toNat`, and `A.toNat` is positive. Apply the natural theorem and then cast the two finite block sums back to integers. The cast commutes with the finite sum because every summand in either block is nonnegative. The threshold in the integer theorem is the integer cast of the displayed natural threshold.

This bridge must be proved in Lean to claim the integer presentation; this paragraph is a proof plan until its source has actually compiled.

- `n=0` is excluded solely because the original first and last terms are undefined for an empty sequence.
- For `n=1`, the first and last entries both equal `A`, and `F≥A`; hence the endpoint-above-threshold premise is false. No added lower bound on sequence length is required.
- `K=1` is covered: `m=3`, `M=8`, and the cardinal excess is still at least eight.
- `A=1` is covered without a separate argument.
- Both intervals can overlap. Neither pairwise disjointness nor equal lengths is imposed.
- Values of the total representing function beyond the finite domain are arbitrary and unused.
- Strict increase is retained in the final statement, although the counting helper needs only the first-term and upper-gap assumptions.

## Verification status

This document proves the mathematics with explicit finite indexing and elementary inequalities. It is not a record that Lean has checked the implementation. The Lean project must separately record successful compilation, a clean build on pinned versions, and the transitive axioms of the final theorem. A source file without such executed checks remains unverified.
