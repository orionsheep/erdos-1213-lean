import JSP1213.Statement
import Mathlib.Algebra.BigOperators.Ring.Finset

/-!
# Integer-valued finite-sequence bridge

This module transfers a proof of the natural-number presentation to the
integer-valued original statement. At creation it has not been compiled.
It imports only the statement module and does not depend on a main proof.
-/

namespace JSP1213

/-- Positive integer-valued finite inputs are represented exactly by natural
values on their finite domain. No positivity is required outside that domain. -/
theorem integerProblem_of_originalProblem
    (hnat : OriginalProblem) : IntegerProblem := by
  intro A K hA hK
  have hAnat : 0 < A.toNat := by omega
  have hKnat : 0 < K.toNat := by omega
  obtain ⟨F, hF⟩ := hnat A.toNat K.toNat hAnat hKnat
  refine ⟨(F : ℤ), ?_⟩
  intro n z hz hlarge
  let a : ℕ → ℕ := fun i => (z i).toNat
  have hn : 0 < n := hz.length_pos
  have hzpos : ∀ i : ℕ, i < n → 0 < z i := by
    intro i hi
    by_cases hi0 : i = 0
    · subst i
      rw [hz.first]
      exact hA
    · have h0i : 0 < i := by omega
      have hinc : z 0 < z i := hz.strict h0i hi
      rw [hz.first] at hinc
      omega
  have hcast : ∀ i : ℕ, i < n → (a i : ℤ) = z i := by
    intro i hi
    have hnonneg : 0 ≤ z i := le_of_lt (hzpos i hi)
    dsimp only [a]
    omega
  have hKcast : (K.toNat : ℤ) = K := by omega
  have hgood : GoodPrefix A.toNat K.toNat n a := by
    refine ⟨hn, ?_, ?_, ?_⟩
    · change (z 0).toNat = A.toNat
      rw [hz.first]
    · intro i j hij hjn
      have hin : i < n := lt_trans hij hjn
      have hinc : z i < z j := hz.strict hij hjn
      have hincCast : (a i : ℤ) < (a j : ℤ) := by
        simpa only [hcast i hin, hcast j hjn] using hinc
      exact_mod_cast hincCast
    · intro i hnext
      have hin : i < n := by omega
      have hgap : z (i + 1) ≤ z i + K := hz.gaps i hnext
      have hgapCast : (a (i + 1) : ℤ) ≤ (a i : ℤ) + (K.toNat : ℤ) := by
        simpa only [hcast (i + 1) hnext, hcast i hin, hKcast] using hgap
      exact_mod_cast hgapCast
  have hlast : n - 1 < n := by omega
  have hterminalCast : (F : ℤ) < (a (n - 1) : ℤ) := by
    simpa only [hcast (n - 1) hlast] using hlarge
  have hterminal : F < a (n - 1) := by
    exact_mod_cast hterminalCast
  obtain ⟨l, r, l', r', hlr, hrn, hlr', hrn', hdistinct, hequal⟩ :=
    hF n a hgood hterminal
  have hsum : ∀ u v : ℕ, v ≤ n →
      integerBlockSum z u v = (blockSum a u v : ℤ) := by
    intro u v hvn
    unfold integerBlockSum blockSum
    rw [Nat.cast_sum]
    apply Finset.sum_congr rfl
    intro i hi
    have hiv : i < v := (Finset.mem_Ico.mp hi).2
    have hin : i < n := lt_of_lt_of_le hiv hvn
    exact (hcast i hin).symm
  refine ⟨l, r, l', r', hlr, hrn, hlr', hrn', hdistinct, ?_⟩
  calc
    integerBlockSum z l r = (blockSum a l r : ℤ) := hsum l r hrn
    _ = (blockSum a l' r' : ℤ) := congrArg (fun t : ℕ => (t : ℤ)) hequal
    _ = integerBlockSum z l' r' := (hsum l' r' hrn').symm

end JSP1213
