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
Given fractions x = a/b and y = c/d, written in lowest terms in the
normal way, say that x is *simpler* than y if:

- abs(a) <= abs(c), and
- b <= d, and
- abs(x) != abs(y)

Then it can be proved that any subinterval of the real line that contains at
least one fraction contains a unique simplest fraction - that is, there's a
fraction x contained in the given interval, such that x is simpler than all
other fractions in that interval.

It follows that given a finite Python float ``f``, there's a unique simplest
fraction ``x`` such that ``float(x)`` recovers ``f``.

This module provides two functions: ``simplest_in_subinterval`` finds the
simplest fraction in a given interval, while ``simplest_from_float`` finds
the simplest fraction that converts to the given float.

"""

import fractions
import math
import struct


#: Names to be exported when doing 'from simplefractions import *'.
__all__ = ["simplest_from_float", "simplest_in_interval"]


def _to_integer_ratio(x):
    """
    Convert a finite number or an infinity to an integer ratio.
    """
    if x == math.inf:
        return 1, 0
    if x == -math.inf:
        return -1, 0

    # Best effort to get a numerator and denominator from x.
    fx = fractions.Fraction(x)
    return fx.numerator, fx.denominator


def _esb_path(x, neg):
    """
    Extended Stern-Brocot tree path for a given number x.

    Parameters
    ----------
    x : number
        Integer, fraction or float. Can also be math.inf
        or -math.inf
    neg : bool
        Controls which of the two equivalent sequences is produced.

    Yields
    ------
    coeff : int or math.inf
        Sequence of coefficients in the tree path, with each coefficient giving
        the number of times to go left or right. The first coefficient gives
        the number of steps right, and subsequent coefficients alternate in
        direction, so a sequence [0, 3, 5, 2] means: 'take 0 steps right, then
        3 steps left, then 5 steps right, then 2 steps left'.

        The first coefficient generated may be 0, and the last coefficient
        generated may be math.inf; other than that, all coefficients are
        positive integers.

    """
    n, d = _to_integer_ratio(x)
    if n < 0 or n == 0 and neg:
        yield 0
        n, neg = -n, not neg

    n += d
    while d:
        q, r = divmod(n - neg, d)
        yield q
        n, d, neg = d, r + neg, not neg
    yield math.inf


def _from_esb_path(path):
    """
    Reconstruct a fraction from a finite Extended Stern-Brocot tree path.
    """
    a, b, c, d = -1, 1, 1, 0
    for q in path:
        if q == 0:
            a, c = -a, -c
        else:
            a, b, c, d = c, d, a + q * c, b + q * d

    return fractions.Fraction(a + c, b + d)


def _common_prefix(path1, path2):
    """
    Longest common prefix of two paths.
    """
    for count1, count2 in zip(path1, path2):
        if count1 != count2:
            yield min(count1, count2)
            break
        yield count1


def _interval_rounding_to(x):
    """
    Return the interval of numbers that round to a given float.

    Returns
    -------
    left, right : fractions.Fraction
    closed : bool
    """
    if x < 0:
        left, right, closed = _interval_rounding_to(-x)
        return -right, -left, closed

    if x == 0:
        n = struct.unpack("<Q", struct.pack("<d", 0.0))[0]
        x_plus = struct.unpack("<d", struct.pack("<Q", n + 1))[0]
        right = (fractions.Fraction(x) + fractions.Fraction(x_plus)) / 2
        return -right, right, True

    n = struct.unpack("<Q", struct.pack("<d", x))[0]
    x_plus = struct.unpack("<d", struct.pack("<Q", n + 1))[0]
    x_minus = struct.unpack("<d", struct.pack("<Q", n - 1))[0]

    closed = n % 2 == 0
    left = (fractions.Fraction(x) + fractions.Fraction(x_minus)) / 2
    if math.isinf(x_plus):
        # Corner case where x was the largest representable finite float
        right = 2 * fractions.Fraction(x) - left
    else:
        right = (fractions.Fraction(x) + fractions.Fraction(x_plus)) / 2

    return left, right, closed


def simplest_in_interval(
    left=-math.inf,
    right=math.inf,
    *,
    include_left: bool = False,
    include_right: bool = False
):
    """
    Return the simplest fraction in a given interval.

    Given a subinterval of the real line with rational endpoints, return a
    fraction which is contained in the given interval, and which is simpler
    than any other fraction contained in the interval.

    Parameters
    ----------
    left : int, float or Fraction, optional
        Left endpoint of the interval. If not provided, the interval is
        assumed unbounded to the left.
    right : int, float or Fraction, optional
        Right endpoint of the interval. If not provided, the interval is
        assumed unbounded to the right.
    include_left : bool, optional
        If True, the left endpoint is included in the interval. The default
        is False.
    include_right : bool, optional
        If True, the right endpoint is included in the interval. The default
        is False.

    Returns
    -------
    fraction.Fraction
        The simplest fraction in the interval.

    Raises
    ------
    ValueError
        If the interval is empty.
    """
    if left < right or left == right and include_left and include_right:
        return _from_esb_path(
            _common_prefix(
                _esb_path(left, include_left),
                _esb_path(right, not include_right),
            )
        )

    raise ValueError("empty interval")


def simplest_from_float(x: float) -> fractions.Fraction:
    """
    Return the simplest fraction that converts to the given float.
    """
    if not math.isfinite(x):
        raise ValueError("x should be finite")

    left, right, closed = _interval_rounding_to(x)
    return simplest_in_interval(
        left=left, include_left=closed, right=right, include_right=closed
    )
