# Copyright 2020-2022 Mark Dickinson. All rights reserved.
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

This module provides two functions: ``simplest_in_interval`` finds the
simplest fraction in a given interval, while ``simplest_from_float`` finds
the simplest fraction that converts to the given float.
"""

import decimal
import fractions
import math
import numbers
import re
import struct
import typing

from simplefractions._simplest_in_interval import _simplest_in_interval

#: Names to be exported when doing 'from simplefractions import *'.
__all__ = ["simplest_from_float", "simplest_in_interval"]


#: Type that roughly matches "number acceptable by the fractions.Fraction
#: constructor"
FractionCompatible = typing.Union[int, float, decimal.Decimal, numbers.Rational]


def simplest_in_interval(
    left: typing.Optional[FractionCompatible] = None,
    right: typing.Optional[FractionCompatible] = None,
    *,
    include_left: bool = False,
    include_right: bool = False,
) -> fractions.Fraction:
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
        is False. If the left endpoint is missing, include_left must be False.
    include_right : bool, optional
        If True, the right endpoint is included in the interval. The default
        is False. If the right endpoint is missing, include_right must be
        False.

    Returns
    -------
    fractions.Fraction
        The simplest fraction in the interval.

    Raises
    ------
    ValueError
        If the interval is empty.
    """
    # Backwards compatibility
    if left == -math.inf:
        left = None
    if right == math.inf:
        right = None

    # Convert floats, Decimal instances, integers, etc. to the
    # corresponding Fraction.
    if left is not None:
        left = fractions.Fraction(left)
    if right is not None:
        right = fractions.Fraction(right)

    return _simplest_in_interval(
        left, right, include_left=include_left, include_right=include_right
    )


def _interval_rounding_to(
    x: float,
) -> typing.Tuple[fractions.Fraction, fractions.Fraction, bool]:
    """
    Return the interval of numbers that round to a given float.

    Returns
    -------
    left, right : fractions.Fraction
        Endpoints of the interval of all numbers that round to x
        under the standard round-ties-to-even rounding mode.
    closed : bool
        True if the interval is closed at both ends, else False.
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


def _interval_rounding_to_str(
    x: str,
) -> typing.Tuple[fractions.Fraction, fractions.Fraction]:
    """
    Return the interval of numbers that round to a given number
    expressed as a string.  It is not specified whether the interval
    includes the endpoints, which is left to the user and the rounding
    convention to be employed.

    Returns
    -------
    left, right : fractions.Fraction
        Endpoints of the interval of all numbers that round to x

    Raises
    ------
    ValueError
        If the input str is not recognized as representing a number.
    """

    # If supplied string is malformed, this will throw an exception
    x_fraction = fractions.Fraction(x)

    # If `x` is positive then we can figure the right end of the rounding interval by
    # attaching a "5" suffix to the mantissa.  If the mantissa does not include a
    # decimal point then append a decimal point before appending the "5".
    right = re.sub(
        r"^([+-]?[0-9_]*)(\.([0-9_]*))?([eE][+-]?[0-9_]+)?$", r"\g<1>.\g<3>5\g<4>", x
    )
    if right == x:
        raise ValueError(f"x ({x}) not recognized as a decimal number")
    right_fraction = fractions.Fraction(right)

    # The left side of the rounding interval is equidistant from the x, but on the other
    # side.
    left_fraction = 2 * x_fraction - right_fraction

    # If `x` is negative, we have left and right swapped
    if left_fraction > right_fraction:
        (left_fraction, right_fraction) = (right_fraction, left_fraction)
    return left_fraction, right_fraction


def _interval_truncating_to_str(
    x: str,
) -> typing.Tuple[fractions.Fraction, fractions.Fraction]:
    """
    Return the interval of numbers that truncate to a given number
    expressed as a string.  It is not specified whether the interval
    includes the endpoints, which is left to the user and the
    truncation convention to be employed.

    Returns
    -------
    left, right : fractions.Fraction
        Endpoints of the interval of all numbers that truncate to x

    Raises
    ------
    ValueError
        If the input str is not recognized as representing a number.
    """

    # If supplied string is malformed, this will throw an exception
    left_fraction = fractions.Fraction(x)

    # If `x` is positive then we can figure the midpoint of the truncation interval by
    # attaching a "5" suffix to the mantissa.  If the mantissa does not include a
    # decimal point then append a decimal point before appending the "5".
    midpoint = re.sub(
        r"^([+-]?[0-9_]*)(\.([0-9_]*))?([eE][+-]?[0-9_]+)?$", r"\g<1>.\g<3>5\g<4>", x
    )
    if midpoint == x:
        raise ValueError(f"x ({x}) not recognized as a decimal number")
    midpoint_fraction = fractions.Fraction(midpoint)

    # The far side of the truncation interval is equidistant from the x, but on the
    # other side.
    right_fraction = 2 * midpoint_fraction - left_fraction

    # If `x` is negative, we have left and right swapped
    if left_fraction > right_fraction:
        (left_fraction, right_fraction) = (right_fraction, left_fraction)
    return left_fraction, right_fraction


def simplest_from_float(x: float) -> fractions.Fraction:
    """
    Return the simplest fraction that converts to the given float.
    """
    if not math.isfinite(x):
        raise ValueError("x should be finite")

    left, right, closed = _interval_rounding_to(x)
    return _simplest_in_interval(left, right, include_left=closed, include_right=closed)
