import Mathlib.Algebra.BigOperators.Group.Finset.Defs
import Mathlib.Algebra.Group.Int.Defs
import Mathlib.Order.Interval.Finset.Nat

/-!
# JSP-001018 / Erdős problem 1213: statement specification

This file defines the finite problem. It does not prove it. The specification
is written from the original problem and Hegyvári's finite-sequence scope.
At creation, no Lean compiler has checked this file.

Intervals are nonempty half-open intervals of indices. Two intervals may
overlap. A function on natural indices represents only its initial segment;
the predicates impose no condition on its values outside that segment.
-/

open scoped BigOperators

namespace JSP1213

/-- The sum on the half-open index interval `[l,r)`. -/
def blockSum (a : ℕ → ℕ) (l r : ℕ) : ℕ :=
  ∑ i ∈ Finset.Ico l r, a i

/-- The original hypotheses on a finite nonempty initial segment of length `n`.
The upper gap bound uses addition, avoiding truncated natural subtraction. -/
structure GoodPrefix (A K n : ℕ) (a : ℕ → ℕ) : Prop where
  length_pos : 0 < n
  first : a 0 = A
  strict : ∀ {i j : ℕ}, i < j → j < n → a i < a j
  gaps : ∀ i : ℕ, i + 1 < n → a (i + 1) ≤ a i + K

/-- Two distinct nonempty intervals, both contained in the finite domain, have
equal sums. Distinctness concerns their indices; disjointness is not required. -/
def RepeatedSums (a : ℕ → ℕ) (n : ℕ) : Prop :=
  ∃ l r l' r' : ℕ,
    l < r ∧ r ≤ n ∧
    l' < r' ∧ r' ≤ n ∧
    (l, r) ≠ (l', r') ∧
    blockSum a l r = blockSum a l' r'

/-- The complete natural-number presentation of the finite original problem.
The single threshold may depend on `A,K`, and is chosen before every length
and every admissible finite sequence. -/
def OriginalProblem : Prop :=
  ∀ A K : ℕ, 0 < A → 0 < K →
    ∃ F : ℕ, ∀ n : ℕ, ∀ a : ℕ → ℕ,
      GoodPrefix A K n a →
      F < a (n - 1) →
      RepeatedSums a n

/-- Integer-valued block sums for the signed-integer statement bridge. -/
def integerBlockSum (z : ℕ → ℤ) (l r : ℕ) : ℤ :=
  ∑ i ∈ Finset.Ico l r, z i

/-- Integer version of the same finite hypotheses. Positivity of the first
value will imply positivity of all values inside the finite domain. -/
structure GoodIntegerPrefix (A K : ℤ) (n : ℕ) (z : ℕ → ℤ) : Prop where
  length_pos : 0 < n
  first : z 0 = A
  strict : ∀ {i j : ℕ}, i < j → j < n → z i < z j
  gaps : ∀ i : ℕ, i + 1 < n → z (i + 1) ≤ z i + K

/-- The same interval conclusion with signed-integer values and sums. -/
def RepeatedIntegerSums (z : ℕ → ℤ) (n : ℕ) : Prop :=
  ∃ l r l' r' : ℕ,
    l < r ∧ r ≤ n ∧
    l' < r' ∧ r' ≤ n ∧
    (l, r) ≠ (l', r') ∧
    integerBlockSum z l r = integerBlockSum z l' r'

/-- The original integer-valued problem, with arbitrary positive integer
parameters. The intended final submission must cover this presentation too. -/
def IntegerProblem : Prop :=
  ∀ A K : ℤ, 0 < A → 0 < K →
    ∃ F : ℤ, ∀ n : ℕ, ∀ z : ℕ → ℤ,
      GoodIntegerPrefix A K n z →
      F < z (n - 1) →
      RepeatedIntegerSums z n

end JSP1213
