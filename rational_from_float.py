"""
Problem: given smallish, relatively prime integers a and b,
is it possible to reconstruct a and b from the value a/b?

Alternatively: given a finite float x, what's the "simplest" fraction
a/b such that a/b evaluates to x?

Theory
------

The problem reduces to that of finding the simplest fraction in a given
interval. We can always do this by means of the extended Stern-Brocot tree.

Note: the "extended" terminology here is my own; I don't know whether there's
an official name for this beast. The original Stern Brocot tree is an
infinite binary tree whose nodes comprise all *positive* rational numbers.
The extended Stern Brocot tree is a simple extension whose nodes comprise
all rational numbers: positive, negative and zero.

The extended Stern-Brocot tree provides a bijection between, on the one hand:

- The set S of all finite strings in the alphabet {'L', 'R'}
- The set Q of all rational numbers

Notation: write '' for the empty string, and Ls for the concatenation of
the string 'L' with the string s.

Moreover, we can define a total ordering inductively on the set S.
For general elements s and t of S, we have:

- If s < t then Ls < Lt and Rs < Rt
- Ls < '' < Rt

Applying the first property repeatedly, it follows that if s < t then rs < rt
for any r.

On the other hand, the set Q already has a natural total ordering, and the
structure of the extended Stern-Brocot tree then guarantees that the bijection
between S and Q is order-preserving.

We also have a notion of simplicity: given fractions x and y, we say that x is
"simpler" than y if, when written in lowest terms, |numerator(x)| <=
|numerator(y)| and denominator(x) <= denominator(y). (Note that the word
"simpler" isn't ideal here, because by definition x is simpler than itself.)
Note that this is not a total order: neither of 2/5 or 3/4 is simpler than the
other. But the only way for both x and y to be simpler than the other is for
their absolute values to be equal. Note also that 0/1 is simpler than any
other fraction.

We define "prefix" in the usual way; it does not imply "strict" prefix, so any
string s in S is considered a prefix of itself. Similarly, "longest common
prefix" has the obvious meaning.

The Stern-Brocot tree, by construction, has the following property:

Lemma: suppose x and y are fractions corresponding to strings s and t. If
s is a prefix of t then x is simpler than y.

Moreover, this is strict: if s is a *strict* prefix of t then x is strictly
simpler than y.

We can use this to find the simplest fraction in an interval:

Lemma: suppose that s and t are in S. Let r be the longest commmon prefix
of s and t. Then s <= r <= t.

Proof: write s = ru and t = rv. We know that u <= v. It's enough to show
that u <= '' <= v. We proceed by cases:

- if u and v are both nonempty and start with the same letter, then r was
  not the longest common prefix of s and t and we have a contradiction
- if u and v are both nonempty and start with different letter, then u
  must start with L and v with R (from u <= v), and the result follows
- if u is empty, then '' <= v follows from u <= v.
- if v is empty, then u <= '' follows from u <= v.

Lemma: suppose that s and t are in S, and that r is the longest common prefix
of s and t. Then r is also a prefix of any u in the closed interval [s, t].

Proof: from the definition of the ordering, if s and t both start with L,
anything between them must also start with L. Similarly for R. So working by
induction on the length of r, we can strip the common prefix completely to
reduce to the case where s and t have empty longest common prefix. But then
the statement is trivial.

Corollary: suppose x and y are rationals with x <= y, that s and t are the
corresponding strings, and that r is the longest common prefix of s and t.
Let w be the rational corresponding to r. Then w is the (unique) simplest
fraction in [x, y].

Dealing with non-closed intervals is slightly messier. Fix a string s in S.

Proposition: s < t if and only if there's a nonnegative integer n such that
  sRL^n <= t.
Proof: One way is easy: if sRL^n <= t then s < sRL^n <= t. Now suppose that
s < t. Let r be the longest common prefix of s and t, so s = ru, t = rv.
Then ru < rv, so u < v. Now either:

- u is nonempty, in which case it must start with an L, and n = 0 works.
- u is empty and v starts with an R. Either v = RL^n'' for some n >= 0, or
  v = RL^nR<tail> for some n >= 0. Either way, we've found our n.

In effect, to find the simplest rational in (s, t], s < t, we want to take the
longest common prefix of sRL^infinity with t.

Similarly, to find the simplest rational in (s, t), s < t, we take the longest
common prefix of sRL^infinity with tLR^infinity.

"""

import fractions
import math
import random
import struct
import unittest
import sys


def _compressed_path_unsided(x):
    """
    Compute the path to a positive rational in the Stern-Brocot tree.

    Returns the path in a compressed form that's much more efficient for
    fractions with large numerator or denominator.

    Parameters
    ----------
    x : fractions.Fraction
    """
    if not 0 < x < math.inf:
        raise ValueError("Input must be positive")

    tt = 0

    a, b = x.as_integer_ratio()

    # loop invariant: 0 < a, 0 < b and gcd(a, b) == 1
    # on first iteration, b <= a is possible
    # for subsequent iterations, a < b

    while a != b:
        q, r = divmod(b - (0 <= tt), a)
        yield q
        a, b = r + (0 <= tt), a
        tt = -tt

    if tt:
        yield math.inf


def _compressed_path_sided(x, ss):
    """
    Variant of compressed_path suitable for use with an endpoint
    of an open interval.

    Result always starts with an "L", and then alternates.
    It always ends with an "inf".

    The first number may be a 0; all subsequent numbers will
    be nonzero.

    Parameters
    ----------
    x : number or infinity
        Must be in [0, inf) if ss is True, else in (0, inf]
    ss : bool
    """
    if ss:
        if not 0 <= x < math.inf:
            raise ValueError("Input must be nonnegative")
    else:
        if not 0 < x <= math.inf:
            raise ValueError("Input must be positive or infinity")

    tt = 1 if ss else -1

    a, b = (1, 0) if x == math.inf else x.as_integer_ratio()

    while a:
        q, r = divmod(b - (0 <= tt), a)
        yield q
        a, b = r + (0 <= tt), a
        tt = -tt

    if tt:
        yield math.inf


def compressed_path(x, side):
    """
    Parameters
    ----------
    x : number
        The number to give that path to.
    side : int
        Either -1, 0, or 1
    """

    if side == 1:
        return _compressed_path_sided(x, True)
    elif side == -1:
        return _compressed_path_sided(x, False)
    else:
        return _compressed_path_unsided(x)


def from_compressed_path(path):
    """
    Reconstruct a fraction from a compressed path.
    """
    a, b, c, d = 0, 1, 1, 0
    for count in path:
        if count == math.inf:
            a, b, c, d = a, a, c, c
        else:
            a, b, c, d = b + count * a, a, d + count * c, c
    return fractions.Fraction(a + b, c + d)


def common_prefix(path1, path2):
    """
    Longest common prefix of two paths.
    """
    for count1, count2 in zip(path1, path2):
        if count1 == count2:
            yield count1
        else:
            yield min(count1, count2)
            break


def simplest_in_interval(left, left_included, right, right_included):
    """
    Return simplest fraction in a given nonempty subinterval.
    """
    nonempty = (
        left <= right if left_included and right_included else left < right
    )
    if not nonempty:
        raise ValueError("interval is empty")

    interval_contains_zero = (left <= 0 if left_included else left < 0) and (
        0 <= right if right_included else 0 < right
    )
    if interval_contains_zero:
        return fractions.Fraction(0, 1)

    if right <= 0:
        return -simplest_in_interval(
            -right, right_included, -left, left_included
        )

    left_sequence = compressed_path(left, 0 if left_included else 1)
    right_sequence = compressed_path(right, 0 if right_included else -1)

    return from_compressed_path(common_prefix(left_sequence, right_sequence))


def simplest_in_closed_interval(x, y):
    """
    Return simplest fraction in the given closed interval [x, y].
    """
    return simplest_in_interval(x, True, y, True)


def simplest_in_open_interval(x, y):
    """
    Return simplest fraction in the given open interval (x, y).
    """
    return simplest_in_interval(x, False, y, False)


def interval_rounding_to(x):
    """
    Return the interval of numbers that round to a given float.

    Returns
    -------
    left, right : fractions.Fraction
    closed : bool
    """
    if not math.isfinite(x):
        raise ValueError("x should be finite")

    if x < 0:
        left, right, closed = interval_rounding_to(-x)
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


def float_to_fraction(x):
    """
    Return the simplest fraction that converts to the given float.
    """
    left, right, closed = interval_rounding_to(x)
    if closed:
        return simplest_in_closed_interval(left, right)
    else:
        return simplest_in_open_interval(left, right)


def float_or_inf(frac):
    """
    Test helper: convert a fraction to a float, converting out-of-range
    fractions to an appropriate signed infinity.
    """
    try:
        return float(frac)
    except OverflowError:
        return math.inf if frac > 0 else -math.inf


class SternBrocotTests(unittest.TestCase):
    def test_interval_rounding_to(self):
        test_values = [
            0.1,
            1.0,
            2.7,
            -0.3,
            0.0,
            -0.0,
            sys.float_info.max,
            -sys.float_info.max,
            sys.float_info.min,
            -sys.float_info.min,
            sys.float_info.min * sys.float_info.epsilon,
            -sys.float_info.min * sys.float_info.epsilon,
        ]
        for value in test_values:
            with self.subTest(value=value):
                left, right, closed = interval_rounding_to(value)
                self.assertIsInstance(left, fractions.Fraction)
                self.assertIsInstance(right, fractions.Fraction)
                self.assertLess(left, value)
                self.assertLess(value, right)

                width = right - left
                if closed:
                    self.assertLess(
                        float_or_inf(left - width / 1000),
                        value,
                    )
                    self.assertEqual(float(left), value)
                    self.assertEqual(value, float(right))
                    self.assertLess(
                        value,
                        float_or_inf(right + width / 1000),
                    )
                else:
                    self.assertLess(float_or_inf(left), value)
                    self.assertEqual(
                        float(left + width / 1000),
                        value,
                    )
                    self.assertEqual(
                        value,
                        float(right - width / 1000),
                    )
                    self.assertLess(value, float_or_inf(right))

    def test_roundtrip_through_compressed_path(self):
        test_fractions = [
            fractions.Fraction(n, d)
            for n in range(1, 100)
            for d in range(1, 100)
            if math.gcd(n, d) == 1
        ]

        for x in test_fractions:
            with self.subTest(x=x):
                y = from_compressed_path(compressed_path(x, -1))
                self.assertEqual(y, x)

        for x in test_fractions:
            with self.subTest(x=x):
                y = from_compressed_path(compressed_path(x, 1))
                self.assertEqual(y, x)

        for x in test_fractions:
            with self.subTest(x=x):
                y = from_compressed_path(compressed_path(x, 0))
                self.assertEqual(y, x)

    def test_simplest_in_closed_interval(self):
        # Round fractions to nearest 1000, see if we can recover them

        test_fractions = [
            fractions.Fraction(n, d)
            for n in range(1, 100)
            for d in range(1, 100)
            if math.gcd(n, d) == 1
        ]

        for c in test_fractions:
            z = fractions.Fraction(round(c * 1000), 1000)
            x = z - fractions.Fraction(1, 2000)
            y = z + fractions.Fraction(1, 2000)

            # c is in the closed interval [x, y], so the simplest fraction
            # in [x, y] must be at least as simple as c.
            self.assertTrue(x <= c <= y)

            d = simplest_in_closed_interval(x, y)

            self.assertTrue(x <= d <= y)

            self.assertSimpler(d, c)

        F = fractions.Fraction

        # Corner case where left == right
        self.assertEqual(
            simplest_in_closed_interval(F(1, 2), F(1, 2)),
            F(1, 2),
        )
        self.assertEqual(simplest_in_closed_interval(0, 0), 0)

    def test_simplest_in_open_interval(self):
        F = fractions.Fraction

        self.assertEqual(
            simplest_in_open_interval(F(7, 10), F(5, 7)),
            F(12, 17),
        )
        self.assertEqual(
            simplest_in_open_interval(F(10, 11), F(12, 13)),
            F(11, 12),
        )
        self.assertEqual(
            simplest_in_open_interval(F(6, 11), F(17, 31)),
            F(23, 42),
        )
        self.assertEqual(
            simplest_in_open_interval(F(0, 1), F(3, 5)),
            F(1, 2),
        )
        self.assertEqual(
            simplest_in_open_interval(F(-3, 1), F(-1, 1)),
            F(-2, 1),
        )
        self.assertEqual(
            simplest_in_open_interval(-F(1, 1), F(0, 1)),
            -F(1, 2),
        )
        self.assertEqual(
            simplest_in_open_interval(-F(2, 1), F(2, 1)),
            F(0, 1),
        )
        self.assertEqual(
            simplest_in_open_interval(F(5, 2), math.inf),
            F(3, 1),
        )
        self.assertEqual(
            simplest_in_open_interval(-math.inf, math.inf),
            F(0, 1),
        )
        self.assertEqual(
            simplest_in_open_interval(-math.inf, F(5, 2)),
            F(0, 1),
        )

        with self.assertRaises(ValueError):
            simplest_in_open_interval(F(1, 2), F(1, 2))
        with self.assertRaises(ValueError):
            simplest_in_open_interval(0, 0)

    def test_simplest_in_interval(self):
        self.assertEqual(simplest_in_interval(3, False, 4, False), 3.5)
        self.assertEqual(simplest_in_interval(3, True, 4, True), 3)

        self.assertEqual(simplest_in_interval(3, True, 4, False), 3)
        self.assertEqual(simplest_in_interval(3, False, 4, True), 4)

    def check_float_to_fraction(self, f):
        """
        Check that float_to_fraction accurately recovers the given fraction.

        Given a fraction f, convert it to the nearest representable float,
        then convert that float back to the simplest fraction that represents
        it. The new fraction should be simpler than, or equal to, the
        original fraction.

        Parameters
        ----------
        f : fractions.Fraction
        """
        x = float(f)
        g = float_to_fraction(x)
        self.assertEqual(float(g), x)
        self.assertSimpler(g, f)

    def test_float_to_fraction_roundtrip(self):
        test_values = [0.0, 0.3, -0.3, 1e-100, sys.float_info.max]

        for value in test_values:
            with self.subTest(value=value):
                self.assertEqual(float(float_to_fraction(value)), value)

    def test_float_to_fraction(self):
        # Given a fraction n/d (n and d positive),
        # float_to_fraction(n/d) should give another fraction

        random_test_pairs = [
            (random.randrange(1, 100000), random.randrange(1, 100000))
            for _ in range(10)
        ]

        for n, d in random_test_pairs:
            f = fractions.Fraction(n, d)
            with self.subTest(f=f):
                self.check_float_to_fraction(f)

        # Particular test pairs
        test_pairs = [
            0.3 .as_integer_ratio(),
            1.4 .as_integer_ratio(),
        ]

        for n, d in test_pairs:
            f = fractions.Fraction(n, d)
            with self.subTest(f=f):
                self.check_float_to_fraction(f)

    def assertSimpler(self, x, y):
        """
        Assert that x is at least as simple as y.
        """
        self.assertLessEqual(abs(x.numerator), abs(y.numerator))
        self.assertLessEqual(x.denominator, y.denominator)


if __name__ == "__main__":
    unittest.main()
