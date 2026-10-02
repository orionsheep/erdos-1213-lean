#!/usr/bin/env python3
"""Finite diagnostics for the window construction; not Lean verification."""

from itertools import product
import json


def constants(a, k):
    m = 2 * k + 1
    big_m = 2**m
    b = a + k * big_m
    ell = b + 1
    return m, big_m, b, ell, big_m * (ell + 1), big_m * (b + 2 * k * ell)


def check_extrema():
    checked = 0
    for a, k in product(range(1, 21), range(1, 11)):
        m, big_m, b, ell, n, d = constants(a, k)
        total = 0
        bands = []
        for r in range(m):
            starts = ell * 2 ** (m - r)
            offsets = 2**r
            length_max = 2 ** (r + 1) - 1
            start_max = starts - 1
            assert length_max > 0
            assert length_max <= big_m
            assert start_max + length_max <= n
            assert start_max * length_max <= 2 * ell * big_m
            sum_bound = length_max * (a + k * (start_max + length_max))
            assert sum_bound <= d
            bands.append((2**r, length_max))
            total += starts * offsets
        assert all(bands[r][1] < bands[r + 1][0] for r in range(m - 1))
        assert total == m * ell * big_m == d + big_m
        assert total > d + 1
        assert a + k * n >= a
        checked += 1
    return checked


def check_actual_sequences():
    # K=1 leaves a unique sequence; K=2 is sampled deterministically because
    # exhaustive length-N binary gaps would be exponentially large.
    # These are sequences of length N, on which the counting argument works
    # directly. The endpoint-to-length implication is a separate proof lemma.
    cases = 0
    for a, k in product(range(1, 4), range(1, 3)):
        m, big_m, b, ell, n, d = constants(a, k)
        patterns = sorted({(1,), (k,), tuple(range(1, k + 1)), (k, 1, k)})
        for gaps in patterns:
            seq = [a]
            for q in range(n - 1):
                seq.append(seq[-1] + gaps[q % len(gaps)])
            assert all(value <= a + k * q for q, value in enumerate(seq))
            prefix = [0]
            for value in seq:
                prefix.append(prefix[-1] + value)
            seen = {}
            found = False
            for r in range(m):
                for i in range(ell * 2 ** (m - r)):
                    for t in range(2**r):
                        length = 2**r + t
                        interval = (i, i + length)
                        value = prefix[i + length] - prefix[i]
                        assert 0 <= value <= d
                        if value in seen:
                            assert seen[value] != interval
                            found = True
                            break
                        seen[value] = interval
                    if found:
                        break
                if found:
                    break
            assert found
            cases += 1
    return cases


if __name__ == "__main__":
    print(json.dumps({
        "extrema_parameter_pairs_checked": check_extrema(),
        "actual_sequences_checked": check_actual_sequences(),
        "status": "passed finite diagnostics only",
        "lean_kernel_verification": "not executed by this script",
    }, indent=2))
