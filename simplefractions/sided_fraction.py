"""
Core algorithms for computing the simplest fraction in an interval.
"""

import fractions
import typing


def _simplest_in_interval_pos(
    ln: int, ld: int, lh: bool, rn: int, rd: int, rh: bool
) -> typing.Tuple[int, int]:
    """
    Simplest fraction between two other fractions in the positive real line.

    This is the core algorithm. Given a nonempty subinterval of the positive
    real line whose endpoints are rational numbers, it finds the unique
    simplest rational number in that subinterval.

    Parameters
    ----------
    ln, ld : int
        Numerator and denominator of the left endpoint of the interval.
        Can be 0 and 1 (respectively) to represent zero.
    lh : bool
        True if left endpoint is *not* included in the interval, else False.
        Must be True if the left endpoint is zero.
    rn, rd : int
        Numerator and denominator of the right endpoint of the interval.
        Can be 1 and 0 (respectively) to represent infinity.
    rh : bool
        True if the right endpoint *is* included in the interval, else False.
        Must be False if the right endpoint is infinity.

    Returns
    -------
    n, d : int
        Numerator and denominator of the simplest fraction in the interval.
    """
    ln, ld, lh, rn, rd, rh = ln + ld, ld, not lh, rn + rd, rd, not rh
    a, b, c, d = -1, 1, 1, 0

    while ld <= ln - lh:
        q = (ln - lh) // ld
        ln, ld, lh, rn, rd, rh = (
            rd,
            rn - q * rd,
            not rh,
            ld,
            ln - q * ld,
            not lh,
        )
        a, b, c, d = c, d, a + q * c, b + q * d
    return a + c, b + d


def _simplest_in_interval(
    left_endpoint: typing.Optional[fractions.Fraction] = None,
    right_endpoint: typing.Optional[fractions.Fraction] = None,
    *,
    include_left: bool = False,
    include_right: bool = False,
) -> fractions.Fraction:
    """
    Simplest fraction in a subinterval of the real line.
    """
    if left_endpoint is None and include_left:
        raise ValueError("interval may not contain -infinity")

    if right_endpoint is None and include_right:
        raise ValueError("interval may not contain infinity")

    # Is the interval nonempty?
    nonempty_interval = (
        left_endpoint is None
        or right_endpoint is None
        or left_endpoint < right_endpoint
        or (left_endpoint == right_endpoint and include_left and include_right)
    )
    if not nonempty_interval:
        raise ValueError("empty interval")

    # Does the interval contain zero?
    left_negative = (
        left_endpoint is None
        or left_endpoint < 0
        or (left_endpoint == 0 and include_left)
    )
    contains_zero = left_negative and (
        right_endpoint is None
        or 0 < right_endpoint
        or (0 == right_endpoint and include_right)
    )
    if contains_zero:
        return fractions.Fraction(0, 1)

    if left_negative:
        # left could be None; right cannot be
        assert right_endpoint is not None
        left_endpoint, right_endpoint = (
            -right_endpoint,
            None if left_endpoint is None else -left_endpoint,
        )
        include_left, include_right = include_right, include_left

    if left_endpoint is None:
        left_numerator = -1
        left_denominator = 0
    else:
        left_numerator = left_endpoint.numerator
        left_denominator = left_endpoint.denominator

    if right_endpoint is None:
        right_numerator = 1
        right_denominator = 0
    else:
        right_numerator = right_endpoint.numerator
        right_denominator = right_endpoint.denominator

    n, d = _simplest_in_interval_pos(
        left_numerator,
        left_denominator,
        not include_left,
        right_numerator,
        right_denominator,
        include_right,
    )
    return fractions.Fraction(-n if left_negative else n, d)
