import JSP1213.Statement
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Lean.Elab.Tactic.Omega
import Mathlib.Tactic.Ring.RingNF

/-!
Elementary estimates for a bounded-gap finite sequence.
Freshly authored in this project. Actual checking evidence is saved separately
under `verification/` for the fixed toolchain and source hashes.
-/

open scoped BigOperators

namespace JSP1213

theorem prefix_bound {A K n : ℕ} {a : ℕ → ℕ}
    (h : GoodPrefix A K n a) :
    ∀ q : ℕ, q < n → a q ≤ A + K * q := by
  intro q
  induction q with
  | zero =>
      intro hq
      simp [h.first]
  | succ q ih =>
      intro hq
      have hq' : q < n := by omega
      have hg := h.gaps q hq
      have hb := ih hq'
      calc
        a (q + 1) ≤ a q + K := hg
        _ ≤ (A + K * q) + K := Nat.add_le_add_right hb K
        _ = A + K * (q + 1) := by ring

/-- A deliberately coarse estimate: every term of a block of length `j`
is at most `A + K * (i+j)`. It avoids divisions and floor functions. -/
theorem block_bound {A K n : ℕ} {a : ℕ → ℕ}
    (h : GoodPrefix A K n a) (i j : ℕ) (hij : i + j ≤ n) :
    blockSum a i (i + j) ≤ j * A + K * (i * j) + K * j ^ 2 := by
  have hterm : ∀ q ∈ Finset.Ico i (i + j), a q ≤ A + K * (i + j) := by
    intro q hq
    have hqi := Finset.mem_Ico.mp hq
    have hqn : q < n := lt_of_lt_of_le hqi.2 hij
    calc
      a q ≤ A + K * q := prefix_bound h q hqn
      _ ≤ A + K * (i + j) :=
        Nat.add_le_add_left (Nat.mul_le_mul_left K (Nat.le_of_lt hqi.2)) A
  calc
    blockSum a i (i + j) ≤
        ∑ q ∈ Finset.Ico i (i + j), (A + K * (i + j)) :=
      Finset.sum_le_sum hterm
    _ = j * (A + K * (i + j)) := by
      simp [Nat.card_Ico]
    _ = j * A + K * (i * j) + K * j ^ 2 := by ring

/-- An endpoint beyond `A + K*N` forces a prefix longer than `N`. -/
theorem length_gt_of_endpoint_gt {A K n : ℕ} {a : ℕ → ℕ}
    (h : GoodPrefix A K n a) (N : ℕ)
    (hend : A + K * N < a (n - 1)) : N < n := by
  have hnonempty : 0 < n := h.length_pos
  have hlast : n - 1 < n := by omega
  have hb := prefix_bound h (n - 1) hlast
  by_contra hn
  have hnN : n - 1 ≤ N := by omega
  have hmul : K * (n - 1) ≤ K * N := Nat.mul_le_mul_left K hnN
  omega

end JSP1213
