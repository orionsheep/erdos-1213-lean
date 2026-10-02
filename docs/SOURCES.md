# Sources and scope

The original question is [Erdős Problem 1213](https://www.erdosproblems.com/1213), recorded as **JSP-001018** in the Justin Sun Prize catalog. These two numbering systems must not be confused with Erdős Problem 1018.

The established affirmative mathematical result is due to **Norbert Hegyvári**, *On consecutive sums in sequences*, Acta Mathematica Hungarica **48** (1986), **193–200**, [DOI 10.1007/BF01949064](https://doi.org/10.1007/BF01949064). Section **3**, printed **p.197**, states the question, attributed to Erdős by personal communication, and **Theorem 3**. The complete proof is on printed **pp.197–198**. Equation **(3.1)** explicitly uses a positive integer gap parameter.

The [MTA journal archive](https://real-j.mtak.hu/7472/1/MTA_ActaMathHung_48.pdf) contains the complete article on one-based PDF pages **199–206**; the question, theorem and proof are on PDF pages **203–204**. The research reading used this historical journal version. No article scan is redistributed in this repository, and no license for the historical article is asserted.

This project proves the complete original qualitative existence statement, with a deliberately coarser explicit threshold. It does not formalize Hegyvári's sharper exponential bound or identify the canonical least sufficient threshold. The mathematical argument followed by this implementation is written in [MATHEMATICAL_PROOF.md](MATHEMATICAL_PROOF.md); definition correspondence is in [STATEMENT_AUDIT.md](STATEMENT_AUDIT.md).

The official submission rules were read at awards commit `5125fd797a5a5e63588406feceb8f08ca72c491a`:

- [Contribution guide](https://github.com/TheJustinSunPrize/awards/blob/5125fd797a5a5e63588406feceb8f08ca72c491a/CONTRIBUTING.md)
- [PR template](https://github.com/TheJustinSunPrize/awards/blob/5125fd797a5a5e63588406feceb8f08ca72c491a/.github/PULL_REQUEST_TEMPLATE.md)
- [Award process](https://github.com/TheJustinSunPrize/awards/blob/5125fd797a5a5e63588406feceb8f08ca72c491a/docs/award-process.md)
- [Verification requirements](https://github.com/TheJustinSunPrize/awards/blob/5125fd797a5a5e63588406feceb8f08ca72c491a/docs/verification.md)

An official catalog state such as `Unclaimed` or `Lean proof: No` does not show that nobody has previously completed the problem. Existing contributions are acknowledged in [PRIOR_ART.md](PRIOR_ART.md). Mathematical solver credit, formalizer credit, accepted verification and award priority remain distinct.
