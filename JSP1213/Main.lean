import JSP1213.Basic
import JSP1213.Dyadic
import JSP1213.IntegerBridge

/-!
# A uniform finite threshold for Erdős problem 1213

The source implements the dyadic counting proof in the project's mathematical
exposition. Hegyvári is the original mathematical solver. This additional
implementation claims no first-formalization priority.

Executed checking evidence, including the exact endpoint types and transitive
axiom reports, is recorded separately under `verification/`.
-/

namespace JSP1213

def threshold (A K : ℕ) : ℕ := A + K * N A K

theorem window_sum_le_D {A K n : ℕ} {a : ℕ → ℕ}
    (h : GoodPrefix A K n a) (hn : N A K ≤ n) (w : Window A K) :
    blockSum a (start w) (start w + len w) ≤ D A K := by
  have hfit : start w + len w ≤ n := (start_add_len_le_N w).trans hn
  have hb := block_bound h (start w) (len w) hfit
  have hj := len_le_M w
  have hij := start_mul_len_le w
  have hj2 : len w ^ 2 ≤ M K ^ 2 := by
    simpa only [pow_two] using Nat.mul_le_mul hj hj
  have h1 : len w * A ≤ M K * A := Nat.mul_le_mul_right A hj
  have h2 : K * (start w * len w) ≤ K * (2 * L A K * M K) :=
    Nat.mul_le_mul_left K hij
  have h3 : K * len w ^ 2 ≤ K * M K ^ 2 := Nat.mul_le_mul_left K hj2
  calc
    blockSum a (start w) (start w + len w) ≤
        len w * A + K * (start w * len w) + K * len w ^ 2 := hb
    _ ≤ M K * A + K * (2 * L A K * M K) + K * M K ^ 2 :=
      Nat.add_le_add (Nat.add_le_add h1 h2) h3
    _ = D A K := by unfold D B; ring

/-- Every admissible prefix of length at least `N` already has repeated sums. -/
theorem repeatedSums_of_length_ge {A K n : ℕ} {a : ℕ → ℕ}
    (h : GoodPrefix A K n a) (hn : N A K ≤ n) : RepeatedSums a n := by
  classical
  let value : Window A K → Fin (D A K + 1) := fun w =>
    ⟨blockSum a (start w) (start w + len w),
      Nat.lt_succ_of_le (window_sum_le_D h hn w)⟩
  by_contra hnone
  have hinj : Function.Injective value := by
    intro x y heq
    apply window_endpoints_injective
    by_contra hend
    have hsum : blockSum a (start x) (start x + len x) =
        blockSum a (start y) (start y + len y) := congrArg Fin.val heq
    have hxpos : start x < start x + len x := by
      have hp := len_pos x
      omega
    have hypos : start y < start y + len y := by
      have hp := len_pos y
      omega
    have hxend : start x + len x ≤ n := (start_add_len_le_N x).trans hn
    have hyend : start y + len y ≤ n := (start_add_len_le_N y).trans hn
    exact hnone ⟨start x, start x + len x, start y, start y + len y,
      hxpos, hxend, hypos, hyend, hend, hsum⟩
  have hc := Fintype.card_le_of_injective value hinj
  simp only [Fintype.card_fin] at hc
  have htoo := card_window_gt_D_succ (A := A) (K := K)
  omega

/-- Complete natural presentation, with the threshold chosen uniformly before
the finite length and sequence. -/
theorem erdos_1213_nat : OriginalProblem := by
  intro A K hA hK
  refine ⟨threshold A K, ?_⟩
  intro n a h hend
  have hn : N A K < n := length_gt_of_endpoint_gt h (N A K) hend
  exact repeatedSums_of_length_ge h (Nat.le_of_lt hn)

/-- Complete signed-integer presentation of the original finite problem. -/
theorem erdos_1213 : IntegerProblem :=
  integerProblem_of_originalProblem erdos_1213_nat

end JSP1213
