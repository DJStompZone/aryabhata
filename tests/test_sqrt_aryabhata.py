# tests/test_sqrt_aryabhata.py
import math
import itertools

from aryabhata.sqrt import sqrt_aryabhata


def expected_scaled_root_and_remainder(n: int, digits: int):
    """
    Reference: floor(sqrt(n) * 10**digits) computed via integer arithmetic,
    and the exact integer remainder relation remainder = N - r**2, where
    N = n * 10**(2*digits), r = floor(sqrt(N)).
    """
    N = n * (10 ** (2 * digits))
    r = math.isqrt(N)
    remainder = N - r * r
    return r, remainder


def assert_matches_reference(n: int, digits: int):
    r, rem = sqrt_aryabhata(n, digits=digits)
    r_ref, rem_ref = expected_scaled_root_and_remainder(n, digits)
    assert r == r_ref, f"root mismatch for n={n}, digits={digits}"
    assert rem == rem_ref, f"remainder mismatch for n={n}, digits={digits}"
    # sanity: the approximation should be within one ulp at the requested scale
    approx = r / (10 ** digits)
    assert approx <= math.sqrt(n) + 10 ** (-digits), "approx overshot tolerance"


def test_zero_and_one_trivial_cases():
    # n=0 with several digit counts (exercise early-return path & loop body)
    for d in (0, 1, 7):
        assert_matches_reference(0, d)
    # n=1 with and without fractional digits
    for d in (0, 3, 10):
        assert_matches_reference(1, d)


def test_perfect_squares():
    squares = [k * k for k in range(1, 40)]
    for n, d in itertools.product(squares, (0, 1, 2, 6)):
        assert_matches_reference(n, d)


def test_non_squares_small_and_medium():
    nums = [2, 3, 5, 6, 7, 8, 10, 42, 99, 123, 999, 2025, 2026, 65535, 10**6 - 1]
    for n, d in itertools.product(nums, (0, 1, 3, 8)):
        assert_matches_reference(n, d)


def test_large_values_and_many_digits():
    # large n with multiple pairs; also encourages steps where next digit is 0
    nums = [
        12345678901234567890,
        10**24 + 123456,
        999999999999999999,  # 18 digits
    ]
    for n, d in itertools.product(nums, (0, 2, 9, 12)):
        assert_matches_reference(n, d)


def test_string_input_and_odd_digit_padding():
    # odd count ("7" -> "07" pairing); should equal the integer behavior
    r1, rem1 = sqrt_aryabhata("7", digits=5)
    r2, rem2 = sqrt_aryabhata(7, digits=5)
    assert (r1, rem1) == (r2, rem2)

    # leading zeros in string should be irrelevant
    r3, rem3 = sqrt_aryabhata("000123", digits=4)
    r4, rem4 = sqrt_aryabhata(123, digits=4)
    assert (r3, rem3) == (r4, rem4)


def test_float_is_truncated_to_integer_part():
    # float -> integer part only
    r_float, rem_float = sqrt_aryabhata(123.999, digits=6)
    r_int, rem_int = sqrt_aryabhata(123, digits=6)
    assert (r_float, rem_float) == (r_int, rem_int)


def test_invariant_remainder_relation():
    # For several cases, remainder must equal N - r^2 by definition
    cases = [(2, 0), (2, 7), (999, 4), (10**10 + 7, 6)]
    for n, d in cases:
        r, rem = sqrt_aryabhata(n, digits=d)
        N = n * (10 ** (2 * d))
        assert rem == N - r * r
        assert 0 <= rem < 2 * r + 1 if d == 0 else rem >= 0  # quick sanity; exact bound varies with scaling
