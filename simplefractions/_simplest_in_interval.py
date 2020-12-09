# Copyright 2020 Mark Dickinson. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Core algorithms for computing the simplest fraction in an interval.

Proof of correctness
====================

Here's a sketch of a proof of correctness for _simplest_in_interval_pos.


Loop invariants
---------------

The following invariants hold at the beginning and end of every while loop
iteration::

    0 <= a, 0 <= b, 0 <= c, 0 <= d
    t <= r, 0 < s, 0 < u, w <= v
    r * v < u * s + t * w

(for example, in the case of an open interval we have 0 <= r/s < u/v <= inf at
all times, while for a closed interval we have 0 < r/s <= u/v < inf at all
times).

We can always recover the original values of r, s, t, u, v and w from the
current values. Writing r0 through w0 for the original values, on every *even*
iteration (considering the first iteration to be even) we have:

    (a * r + b * s, c * r + d * s, t) == (r0, s0, t0)
    (a * u + b * v, c * u + d * v, w) == (u0, v0, w0)
    a * d - b * c == 1

while on every *odd* iteration:

    (a * u + b * v, c * u + d * v, w) == (r0, s0, t0)
    (a * r + b * s, c * r + d * s, t) == (u0, v0, w0)
    a * d - b * c == -1

Reinterpreting this:

- write I for the subinterval of the positive real line represented by the
  original inputs to _simplest_in_interval_pos.
- at each step, write J for the subinterval of the positive real line
  with endpoints r / s and u / v, closed on the left if t is True, and
  on the right if w is True.
- at each step, write T for the linear fractional transformation
  defined by T(z) = (az + b) / (cz + d).

Then at the beginning and end of each iteration of the while loop:

- J is a subinterval of the positive real line
- T(J) = I, and T establishes a bijection between the rationals in J
  and the rationals in I


Termination
-----------

On every iteration except possibly the first, q is positive. Since the sum r +
s + u + v decreases by q*(v+s) at each step, and s is positive, it follows that
the sum r + s + u + v strictly decreases on every iteration except possibly the
first. Since all of r, s, u and v are nonnegative, the loop must eventually
terminate.

When the loop terminates, the exit condition r - t < s implies that the
interval J contains the value 1. As a consequence, the image under T of that
value, (a + b) / (c + d), is in I.

Furthermore, (a + b) / (c + d) must be the simplest fraction in I: if x / y is
*any* fraction in the interval I (written in lowest terms), we'll show that (a
+ b) / (c + d) is either simpler than or equal to x / y. Let p / q be the
preimage of x / y under T; p / q is in J, so both p and q are positive. Then by
definition of T,

    x / y = (ap + bq) / (cp + dq)

Since gcd(p, q) = 1 and |ad - bc| = 1, it follows that gcd(ap + bq, cp + dq) =
1, so both sides above are in lowest terms and we must have

   x = ap + bq
   y = cp + dq

But a, b, c and d are all nonnegative, and 1 <= p, 1 <= q, so it follows
that

    x >= a + b
    y >= c + d

So (a + b) / (c + d) is either equal to, or simpler than, x / y. Since this is
true for all fractions x / y in I, we've successfully found the simplest
fraction in the interval.
"""

import fractions
import typing


def _simplest_in_interval_pos(
    r: int, s: int, t: bool, u: int, v: int, w: bool
) -> typing.Tuple[int, int]:
    """
    Simplest fraction in a subinterval of the positive reals.

    Given a nonempty, possibly infinite, subinterval of the positive real line
    whose endpoints are rational numbers, find the unique simplest rational
    number in that subinterval.

    Parameters
    ----------
    r, s : int
        r / s is the left endpoint of the interval.
    t : bool
        True if left endpoint is included in the interval, else False.
        Must be False if the left endpoint is 0.
    u, v : int
        u / v is the right endpoint of the interval. u and v can be 1
        and 0 (respectively) to represent an infinite endpoint.
    w : bool
        True if the right endpoint is included in the interval, else False.
        Must be False if the right endpoint is infinity.

    Returns
    -------
    x, y : int
        Numerator and denominator of the simplest fraction in the interval.
    """
    a, b, c, d = 1, 0, 0, 1
    while True:
        q = (r - t) // s
        r, s, t, u, v, w = v, u - q * v, w, s, r - q * s, t
        a, b, c, d = b + q * a, a, d + q * c, c
        if r - t < s:
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

    # Convert inputs to the form expected by _simplest_in_interval_pos.
    if left is None:
        r, s, t = (-1, 0, False)
    else:
        r, s, t = (left.numerator, left.denominator, include_left)
    if right is None:
        u, v, w = (1, 0, False)
    else:
        u, v, w = (right.numerator, right.denominator, include_right)

    # Raise on an empty interval.
    if s and v and u * s + t * w <= r * v:
        raise ValueError("empty interval")

    if u + w <= 0:
        # Subinterval of negative real line.
        return -fractions.Fraction(*_simplest_in_interval_pos(-u, v, w, -r, s, t))
    elif r - t < 0:
        # Interval contains zero.
        return fractions.Fraction(0, 1)
    else:
        # Subinterval of positive real line.
        return fractions.Fraction(*_simplest_in_interval_pos(r, s, t, u, v, w))
