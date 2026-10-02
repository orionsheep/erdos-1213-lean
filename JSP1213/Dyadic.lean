import JSP1213.Statement
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.Positivity.Basic
import Mathlib.Tactic.Ring.RingNF
import Mathlib.Tactic.SimpRw
import Lean.Elab.Tactic.Omega
import Lean.Elab.Tactic.RCases

/-!
# Finite dyadic windows for Erdős problem 1213

This module was independently authored from the mathematical counting proof
in `docs/MATHEMATICAL_PROOF.md`, without reading another implementation.
Its quantitative threshold is deliberately larger than Hegyvári's published
bound. The definitions involve only natural arithmetic and finite types.

Creation status: source written before a compiler was available. Successful
executed checks, if later obtained, must be recorded separately.
-/

open scoped BigOperators

namespace JSP1213

def m (K : ℕ) : ℕ := 2 * K + 1
def M (K : ℕ) : ℕ := 2 ^ m K
def B (A K : ℕ) : ℕ := A + K * M K
def L (A K : ℕ) : ℕ := B A K + 1
def N (A K : ℕ) : ℕ := M K * (L A K + 1)
def D (A K : ℕ) : ℕ := M K * (B A K + 2 * K * L A K)

/-- A band, a start, and a length offset, all intrinsically within range. -/
abbrev Window (A K : ℕ) :=
  Σ r : Fin (m K),
    Fin (L A K * 2 ^ (m K - r.val)) × Fin (2 ^ r.val)

variable {A K : ℕ}

def start (w : Window A K) : ℕ := w.2.1.val
def len (w : Window A K) : ℕ := 2 ^ w.1.val + w.2.2.val

/-- Monotonicity of powers of two, proved directly on the upper exponent. -/
theorem two_pow_mono {a b : ℕ} (h : a ≤ b) : 2 ^ a ≤ 2 ^ b := by
  induction b generalizing a with
  | zero =>
      have ha : a = 0 := by omega
      subst a
      exact le_rfl
  | succ b ih =>
      by_cases hab : a ≤ b
      · calc
          2 ^ a ≤ 2 ^ b := ih hab
          _ ≤ 2 ^ (b + 1) := by rw [pow_succ]; omega
      · have ha : a = b + 1 := by omega
        subst a
        exact le_rfl

/-- The subtraction in the exponent is justified by the stated inequality. -/
theorem power_split {r s : ℕ} (h : r ≤ s) :
    2 ^ (s - r) * 2 ^ r = 2 ^ s := by
  rw [← pow_add, Nat.sub_add_cancel h]

theorem len_lower (w : Window A K) : 2 ^ w.1.val ≤ len w := by
  unfold len
  omega

theorem len_lt_pow_succ (w : Window A K) :
    len w < 2 ^ (w.1.val + 1) := by
  calc
    len w < 2 ^ w.1.val + 2 ^ w.1.val := by
      exact Nat.add_lt_add_left w.2.2.isLt _
    _ = 2 ^ (w.1.val + 1) := by rw [pow_succ]; omega

theorem len_pos (w : Window A K) : 0 < len w := by
  have hpow : 0 < (2 : ℕ) ^ w.1.val := by positivity
  have hl := len_lower w
  omega

theorem len_le_M (w : Window A K) : len w ≤ M K := by
  have hr := w.1.isLt
  have hpow : 2 ^ (w.1.val + 1) ≤ M K := by
    exact two_pow_mono (by omega)
  exact (Nat.le_of_lt (len_lt_pow_succ w)).trans hpow

theorem start_le_LM (w : Window A K) : start w ≤ L A K * M K := by
  calc
    start w ≤ L A K * 2 ^ (m K - w.1.val) :=
      Nat.le_of_lt w.2.1.isLt
    _ ≤ L A K * M K :=
      Nat.mul_le_mul_left _ (two_pow_mono (Nat.sub_le _ _))

theorem start_add_len_le_N (w : Window A K) :
    start w + len w ≤ N A K := by
  calc
    start w + len w ≤ L A K * M K + M K :=
      Nat.add_le_add (start_le_LM w) (len_le_M w)
    _ = N A K := by unfold N; ring

theorem start_mul_len_le (w : Window A K) :
    start w * len w ≤ 2 * L A K * M K := by
  have hr : w.1.val ≤ m K := Nat.le_of_lt w.1.isLt
  calc
    start w * len w ≤
        (L A K * 2 ^ (m K - w.1.val)) * 2 ^ (w.1.val + 1) :=
      Nat.mul_le_mul (Nat.le_of_lt w.2.1.isLt)
        (Nat.le_of_lt (len_lt_pow_succ w))
    _ = 2 * L A K * (2 ^ (m K - w.1.val) * 2 ^ w.1.val) := by
      rw [pow_succ]
      ring
    _ = 2 * L A K * M K := by rw [power_split hr]; rfl

/-- A natural length lies in at most one half-open dyadic band. -/
theorem dyadic_band_unique {r s j : ℕ}
    (hrlo : 2 ^ r ≤ j) (hrhi : j < 2 ^ (r + 1))
    (hslo : 2 ^ s ≤ j) (hshi : j < 2 ^ (s + 1)) : r = s := by
  by_contra hne
  have horder : r < s ∨ s < r := by omega
  rcases horder with hrs | hsr
  · have hpow := two_pow_mono (show r + 1 ≤ s by omega)
    omega
  · have hpow := two_pow_mono (show s + 1 ≤ r by omega)
    omega

/-- Keeping the band in the family does not count the same interval twice. -/
theorem window_pair_injective :
    Function.Injective (fun w : Window A K => (start w, len w)) := by
  intro x y h
  have hs : start x = start y := congrArg Prod.fst h
  have hl : len x = len y := congrArg Prod.snd h
  have hb : x.1.val = y.1.val :=
    dyadic_band_unique (len_lower x) (len_lt_pow_succ x)
      (by rw [hl]; exact len_lower y)
      (by rw [hl]; exact len_lt_pow_succ y)
  have hr : x.1 = y.1 := Fin.ext hb
  rcases x with ⟨r, i, t⟩
  rcases y with ⟨s, j, u⟩
  dsimp only at hr
  subst s
  have hi : i = j := by
    apply Fin.ext
    simpa only [start] using hs
  have ht : t = u := by
    apply Fin.ext
    dsimp only [len] at hl
    omega
  subst j
  subst u
  rfl

theorem window_endpoints_injective :
    Function.Injective
      (fun w : Window A K => (start w, start w + len w)) := by
  intro x y h
  have hs : start x = start y := congrArg Prod.fst h
  have he : start x + len x = start y + len y := congrArg Prod.snd h
  apply window_pair_injective
  apply Prod.ext hs
  change len x = len y
  omega

/-- Each dyadic band supplies exactly `L*M` windows. -/
theorem card_window : Fintype.card (Window A K) = m K * L A K * M K := by
  classical
  change Fintype.card
    (Σ r : Fin (m K),
      Fin (L A K * 2 ^ (m K - r.val)) × Fin (2 ^ r.val)) = _
  rw [Fintype.card_sigma]
  simp only [Fintype.card_prod, Fintype.card_fin]
  have hterm (r : Fin (m K)) :
      (L A K * 2 ^ (m K - r.val)) * 2 ^ r.val = L A K * M K := by
    rw [Nat.mul_assoc, power_split (Nat.le_of_lt r.isLt)]
    rfl
  simp_rw [hterm]
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, Nat.nsmul_eq_mul]
  ring

theorem card_window_eq_D_add_M : Fintype.card (Window A K) = D A K + M K := by
  rw [card_window]
  unfold m D L B
  ring

theorem one_lt_M (K : ℕ) : 1 < M K := by
  have hm : 1 ≤ m K := by unfold m; omega
  have hpow := two_pow_mono hm
  change 2 ≤ M K at hpow
  omega

theorem card_window_gt_D_succ : D A K + 1 < Fintype.card (Window A K) := by
  rw [card_window_eq_D_add_M]
  have hM := one_lt_M K
  omega

end JSP1213
