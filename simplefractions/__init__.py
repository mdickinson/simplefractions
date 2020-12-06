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

# Theory: the Stern-Brocot tree contains every positive rational exactly once.
# By creating a second copy of the tree for negative numbers and adding
# an extra node labelled "0" at the top (and connected to the root nodes
# of the negative and positive trees) we get a infinite full binary tree with
# nodes labelled by rational numbers, and with every rational number appearing
# on exactly one node.
#
#                                 0
#                                / \
#                               /   \
#                              /     \
#                             /       \
#                            /         \
#                           /           \
#                          /             \
#                        -1               1
#                        / \             / \
#                       /   \           /   \
#                      /     \         /     \
#                    -2     -1/2     1/2      2
#                    / \     / \     / \     / \
#                 -3 -3/2 -2/3 -1/3 1/3 2/3 3/2 3
#                  / \ / \ / \ / \ / \ / \ / \ / \
#                 .................................
#
# Note that each rational in the tree is simpler than all rationals that
# descend from it.
#
# Any infinite string of "L" and "R" characters maps to a path in the tree, by
# starting from the root node and taking the left or right branch at each node
# as dictated by successive characters in the string. As the path passes
# through the nodes it generates a sequence of rationals, and that sequence
# converges to a limit in ℝ ∪ {-∞, ∞}. So we get a mapping from those infinite
# strings to ℝ ∪ {-∞, ∞}. That mapping is order-preserving with respect to the
# lexicographic order on the strings, and it's surjective but not injective:
# irrationals and infinites each arise from a single infinite string, but each
# rational is the image of two infinite strings, of the form <p>LRRR... and
# <p>RLLL..., where <p> is the finite path to the position of that rational in
# the tree.
#
# Call the two infinite string representations of a rational number the *left*
# and *right* representations respectively (the left one ending in LRRR..., and
# the right one ending in RLLL...).
#
# Example: the fraction 2/3 has representations RLRLRRR... and RLRRLLL...
# as an infinite string.
#
# The task of finding the (unique) simplest rational in an interval reduces to
# the task of finding the longest common prefix of the corresponding paths. In
# more detail, to find the unique simplest rational in a closed interval [x, y]
# with x <= y rational numbers, find the left representation of x and the right
# representation of y, take the longest common prefix (which will be a finite
# string of Ls and Rs), and take the rational corresponding to that path. For
# an open interval (x, y) with x < y, do the same but start instead with the
# right representation of x and the left representation of y. Extend in the
# obvious way for infinite endpoints or half-open intervals.
#
# Practical computation requires an efficient representation of the paths. We
# use run-length encoding: each path is represented by a sequence of positive
# integers giving the numbers of Ls and Rs, augmented by a math.inf marker
# indicating an infinite tail of Ls or Rs. We also need to indicate whether
# each sequence starts with a run of Ls or a run or Rs.
#
# Example: the fraction 2/3 is represented by the sequences [1, 1, 1, 1, inf]
# and [1, 1, 2, inf] of path lengths, starting with a sequence of "R" steps
# in each case.

import fractions
import math
import struct
import typing

from simplefractions._simplest_in_interval import _simplest_in_interval


#: Names to be exported when doing 'from simplefractions import *'.
__all__ = ["simplest_from_float", "simplest_in_interval"]


def simplest_in_interval(
    left=None,
    right=None,
    *,
    include_left: bool = False,
    include_right: bool = False,
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
        is False. If the left endpoint is missing, include_left must be False.
    include_right : bool, optional
        If True, the right endpoint is included in the interval. The default
        is False. If the right endpoint is missing, include_right must be
        False.

    Returns
    -------
    fraction.Fraction
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


def simplest_from_float(x: float) -> fractions.Fraction:
    """
    Return the simplest fraction that converts to the given float.
    """
    if not math.isfinite(x):
        raise ValueError("x should be finite")

    left, right, closed = _interval_rounding_to(x)
    return _simplest_in_interval(
        left, right, include_left=closed, include_right=closed
    )
