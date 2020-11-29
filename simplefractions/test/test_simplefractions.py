import fractions
import math
import random
import unittest
import sys

from simplefractions import simplest_from_float, simplest_in_interval


def float_or_inf(frac):
    """
    Test helper: convert a fraction to a float, converting out-of-range
    fractions to an appropriate signed infinity.
    """
    try:
        return float(frac)
    except OverflowError:
        return math.inf if frac > 0 else -math.inf


class SimpleFractionsTests(unittest.TestCase):
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

            d = simplest_in_interval(x, True, y, True)

            self.assertTrue(x <= d <= y)

            self.assertSimpler(d, c)

        F = fractions.Fraction

        # Corner case where left == right
        self.assertEqual(
            simplest_in_interval(F(1, 2), True, F(1, 2), True),
            F(1, 2),
        )
        self.assertEqual(simplest_in_interval(0, True, 0, True), 0)

    def test_simplest_in_open_interval(self):
        F = fractions.Fraction

        self.assertEqual(
            simplest_in_interval(F(7, 10), False, F(5, 7), False),
            F(12, 17),
        )
        self.assertEqual(
            simplest_in_interval(F(10, 11), False, F(12, 13), False),
            F(11, 12),
        )
        self.assertEqual(
            simplest_in_interval(F(6, 11), False, F(17, 31), False),
            F(23, 42),
        )
        self.assertEqual(
            simplest_in_interval(F(0, 1), False, F(3, 5), False),
            F(1, 2),
        )
        self.assertEqual(
            simplest_in_interval(F(-3, 1), False, F(-1, 1), False),
            F(-2, 1),
        )
        self.assertEqual(
            simplest_in_interval(-F(1, 1), False, F(0, 1), False),
            -F(1, 2),
        )
        self.assertEqual(
            simplest_in_interval(-F(2, 1), False, F(2, 1), False),
            F(0, 1),
        )
        self.assertEqual(
            simplest_in_interval(F(5, 2), False, math.inf, False),
            F(3, 1),
        )
        self.assertEqual(
            simplest_in_interval(-math.inf, False, math.inf, False),
            F(0, 1),
        )
        self.assertEqual(
            simplest_in_interval(-math.inf, False, F(5, 2), False),
            F(0, 1),
        )

        with self.assertRaises(ValueError):
            simplest_in_interval(F(1, 2), False, F(1, 2), False)
        with self.assertRaises(ValueError):
            simplest_in_interval(0, False, 0, False)

    def test_simplest_in_interval(self):
        self.assertEqual(simplest_in_interval(3, False, 4, False), 3.5)
        self.assertEqual(simplest_in_interval(3, True, 4, True), 3)

        self.assertEqual(simplest_in_interval(3, True, 4, False), 3)
        self.assertEqual(simplest_in_interval(3, False, 4, True), 4)

        self.assertEqual(simplest_in_interval(0, True, math.inf, False), 0)
        self.assertEqual(simplest_in_interval(0, False, math.inf, False), 1)
        self.assertEqual(simplest_in_interval(-1, False, math.inf, False), 0)
        self.assertEqual(simplest_in_interval(-1, True, math.inf, False), 0)

    def test_simplest_from_float_roundtrip(self):
        test_values = [0.0, 0.3, -0.3, 1e-100, sys.float_info.max]

        for value in test_values:
            with self.subTest(value=value):
                self.assertEqual(float(simplest_from_float(value)), value)

    def test_simplest_from_float(self):
        # Given a fraction n/d (n and d positive),
        # simplest_from_float(n/d) should give another fraction

        random_test_pairs = [
            (random.randrange(1, 100000), random.randrange(1, 100000))
            for _ in range(10)
        ]

        for n, d in random_test_pairs:
            f = fractions.Fraction(n, d)
            with self.subTest(f=f):
                self.check_simplest_from_float(f)

        # Particular test pairs
        test_pairs = [
            0.3 .as_integer_ratio(),
            1.4 .as_integer_ratio(),
        ]

        for n, d in test_pairs:
            f = fractions.Fraction(n, d)
            with self.subTest(f=f):
                self.check_simplest_from_float(f)

    def test_simplest_from_float_special_values(self):
        with self.assertRaises(ValueError):
            simplest_from_float(math.inf)
        with self.assertRaises(ValueError):
            simplest_from_float(-math.inf)
        with self.assertRaises(ValueError):
            simplest_from_float(math.nan)

    def check_simplest_from_float(self, f):
        """
        Check that simplest_from_float accurately recovers the given fraction.

        Given a fraction f, convert it to the nearest representable float,
        then convert that float back to the simplest fraction that represents
        it. The new fraction should be simpler than, or equal to, the
        original fraction.

        Parameters
        ----------
        f : fractions.Fraction
        """
        x = float(f)
        g = simplest_from_float(x)
        self.assertEqual(float(g), x)
        self.assertSimpler(g, f)

    def assertSimpler(self, x, y):
        """
        Assert that x is at least as simple as y.
        """
        self.assertLessEqual(abs(x.numerator), abs(y.numerator))
        self.assertLessEqual(x.denominator, y.denominator)


if __name__ == "__main__":
    unittest.main()
