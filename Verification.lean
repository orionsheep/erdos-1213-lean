import JSP1213

set_option format.width 200

-- These commands become evidence only after this file is actually checked.
#check JSP1213.erdos_1213_nat
#check JSP1213.erdos_1213
#print JSP1213.OriginalProblem
#print JSP1213.IntegerProblem
#print JSP1213.GoodPrefix
#print JSP1213.GoodIntegerPrefix
#print JSP1213.RepeatedSums
#print JSP1213.RepeatedIntegerSums
#print JSP1213.blockSum
#print JSP1213.integerBlockSum
#print axioms JSP1213.erdos_1213_nat
#print axioms JSP1213.erdos_1213

-- Reject a final theorem with the wrong type, even if a similarly named
-- auxiliary statement happens to have a proof.
example : JSP1213.OriginalProblem := JSP1213.erdos_1213_nat
example : JSP1213.IntegerProblem := JSP1213.erdos_1213
