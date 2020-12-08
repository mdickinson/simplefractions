"""
Core algorithms for computing the simplest fraction in an interval.

Proof of correctness
====================

Here's a sketch of a proof of correctness for _simplest_in_interval_pos.

We assume that on input to _simplest_in_interval_pos:

- right_numerator > 0, or right_numerator == 0 and right_closed is True
- the interval described is nonempty, so left < right (or left == right
  with both endpoints closed)
- the interval doesn't include either -inf or inf

First we deal with a couple of special cases:

1. If left_numerator < 0, then (given our assumptions on the
   right endpoint), the interval contains 0, and 0 is the simplest
   fraction in the interval. But in this case we have
   left_numerator + left_denominator < left_denominator,
   so on entry to the while statement, t > s >= s - left_closed.
   So the while block is not executed, and we immediately return
   the pair (c + a, d + b), which has value (0, 1), the correct result.

2. Similarly, if left_numerator == 0 and left_closed is True, then on entry to
   the while statement, t == s, so the while block is again not executed, and
   we immediately return with the correct result of (0, 1).

If we're not in either of the above special cases, then either
0 < left_numerator and so t < s, or 0 == left_numerator and left_closed
is False. In both cases, the condition at the top of the while loop
is satisfied, so we end up executing the while loop at least once.

From this point on we assume that we're not in either case 1 or case 2
above, so our interval is a subinterval of the positive real line.

Loop invariants
---------------

The following invariants hold at the beginning and end of every while loop
iteration::

    s * v < u * t or (s * v == u * t and st_closed and uv_closed)
    0 < s or (0 == s and not st_closed)

Additionally, on every *even* iteration (assuming that we start with
iteration 0, so the first iteration is even):

    a * s + b * t == left_numerator
    c * s + d * t == left_denominator
    st_closed == left_closed
    a * u + b * v == right_numerator
    c * u + d * v == right_denominator
    uv_closed == right_closed
    a * d - b * c == 1

while on every *odd* iteration:

    a * s + b * t == right_numerator
    c * s + d * t == right_denominator
    st_closed == right_closed
    a * u + b * v == left_numerator
    c * u + d * v == left_denominator
    uv_closed == left_closed
    a * d - b * c == -1

Reinterpreting this:

- write I for the subinterval of the positive real line represented by the
  inputs to _simplest_in_interval_pos. Note that each endpoint of the interval
  may be either open or closed.
- at each step, write J for the subinterval of the positive real line
  represented by the fractions s/t and u/v, together with the closure
  information st_closed and uv_closed.
- at each step, write T for the linear fractional transformation
  defined by T(z) = (az + b) / (cz + d).

Then at the beginning and end of each iteration of the while loop:

- J is a subinterval of the positive real line
- T(J) = I, and T establishes a bijection between the rationals in J
  and the rationals in I

Additionally, when the while loop exits, the while loop condition
ensures that the interval J contains the value 1. As a consequence,
the image of that value, (a + b) / (c + d), is in I.

And in fact, (a + b) / (c + d) must be the simplest fraction in I: if x/y is
*any* fraction in the interval I (written in lowest terms), and p/q is its
preimage (under T) in J, again written in lowest terms, then by definition of
T:

    x/y = (ap + bq) / (cp + dq)

moreover, since gcd(p, q) = 1 and |ad - bc| = 1, it follows that gcd(ap + bq,
cp + dq) = 1, so both sides above are in lowest terms and we must have

   x = ap + bq
   y = cp + dq

But a, b, c and d are all nonnegative, and 1 <= p, 1 <= q, so it follows
that

    x >= a + b
    y >= c + d

So (a+b)/(c+d) is either equal to, or simpler than, x/y. Since this is true
for all fractions x/y in I, we've successfully found the simplest fraction
in the interval.
"""

import fractions
import typing


def _simplest_in_interval_pos(
    left_numerator: int,
    left_denominator: int,
    left_closed: bool,
    right_numerator: int,
    right_denominator: int,
    right_closed: bool,
) -> typing.Tuple[int, int]:
    """
    Simplest fraction between two other fractions in the real line.

    This is the core algorithm. Given a nonempty, possibly infinite,
    subinterval of the real line whose endpoints are rational numbers,
    it finds the unique simplest rational number in that subinterval.

    The algorithm is not quite fully general: it requires the right endpoint
    of the interval to be positive (or zero, with right_closed being True).

    Parameters
    ----------
    left_numerator, left_denominator : int
        Numerator and denominator of the left endpoint of the interval.
        Can be -1 and 0 (respectively) to represent -infinity.
    left_closed : bool
        True if left endpoint is included in the interval, else False.
        Must be False if the left endpoint is -infinity.
    right_numerator, right_denominator : int
        Numerator and denominator of the right endpoint of the interval.
        Can be 1 and 0 (respectively) to represent infinity.
    right_closed : bool
        True if the right endpoint is included in the interval, else False.
        Must be False if the right endpoint is infinity.

    Returns
    -------
    n, d : int
        Numerator and denominator of the simplest fraction in the interval.
    """
    s, t = left_numerator + left_denominator, left_denominator
    u, v = right_numerator + right_denominator, right_denominator
    st_closed, uv_closed = left_closed, right_closed
    a, b, c, d = 1, -1, 0, 1
    while t <= s - st_closed:
        q = (s - st_closed) // t
        s, t, u, v = v, u - q * v, t, s - q * t
        a, b, c, d = b + q * a, a, d + q * c, c
        st_closed, uv_closed = uv_closed, st_closed
    return a + b, c + d


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

    # The core routine works provided that the right endpoint is positive.
    # If not, we negate the interval.
    negate = right is not None and (right < 0 or (right == 0 and not include_right))
    if negate:
        assert right is not None  # help mypy out
        left, right = -right, None if left is None else -left
        include_left, include_right = include_right, include_left

    n, d = _simplest_in_interval_pos(
        -1 if left is None else left.numerator,
        0 if left is None else left.denominator,
        include_left,
        1 if right is None else right.numerator,
        0 if right is None else right.denominator,
        include_right,
    )
    return fractions.Fraction(-n if negate else n, d)
