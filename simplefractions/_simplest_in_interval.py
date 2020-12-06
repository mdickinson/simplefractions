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

    This is the core algorithm. Given a nonempty, possibly infinite,
    subinterval of the positive real line whose endpoints are rational numbers,
    it finds the unique simplest rational number in that subinterval.

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
    left: typing.Optional[fractions.Fraction] = None,
    right: typing.Optional[fractions.Fraction] = None,
    *,
    include_left: bool = False,
    include_right: bool = False,
) -> fractions.Fraction:
    """
    Simplest fraction in a subinterval of the real line.

    Parameters
    ----------
    left : fractions.Fraction, optional
        Left endpoint of the interval. If not given, the left
        endpoint is -infinity.
    right : fractions.Fraction, optional
        Right endpoint of the interval. If not given, the right
        end point is infinity.
    include_left : bool, optional
        True if the left endpoint should be included in the interval.
        The default is False. Must be False if the left endpoint is -infinity.
    include_right : bool, optional
        True if the right endpoint should be included in the interval.
        The default is False. Must be False if the right endpoint is infinity.

    Returns
    -------
    simplest : fractions.Fraction
        The simplest fraction in the interval described.

    Raises
    ------
    ValueError
        If the interval is empty, or contains infinity or -infinity.
    """
    # Raise on inclusion of infinite endpoints.
    if left is None and include_left:
        raise ValueError("interval may not contain -infinity")

    if right is None and include_right:
        raise ValueError("interval may not contain infinity")

    # Raise on an empty interval.
    nonempty_interval = (
        left is None
        or right is None
        or left < right
        or (left == right and include_left and include_right)
    )
    if not nonempty_interval:
        raise ValueError("empty interval")

    # Reduce to the case of a positive interval.
    left_negative = left is None or left < 0 or (left == 0 and include_left)
    if left_negative:
        right_positive = (
            right is None or 0 < right or (0 == right and include_right)
        )
        if right_positive:
            return fractions.Fraction(0, 1)

        # Now both left and right are negative; negate and swap.
        assert right is not None
        left, right = (
            -right,
            None if left is None else -left,
        )
        include_left, include_right = include_right, include_left

    assert left is not None

    n, d = _simplest_in_interval_pos(
        left.numerator,
        left.denominator,
        not include_left,
        1 if right is None else right.numerator,
        0 if right is None else right.denominator,
        include_right,
    )
    return fractions.Fraction(-n if left_negative else n, d)
