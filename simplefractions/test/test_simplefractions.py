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

import fractions
import math
import random
import unittest
import sys

from simplefractions import simplest_from_float, simplest_in_interval


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

            d = simplest_in_interval(
                x, y, include_left=True, include_right=True
            )

            self.assertTrue(x <= d <= y)

            self.assertSimplerOrEqual(d, c)

        F = fractions.Fraction

        # Corner case where left == right
        self.assertEqual(
            simplest_in_interval(
                F(1, 2),
                F(1, 2),
                include_left=True,
                include_right=True,
            ),
            F(1, 2),
        )
        self.assertEqual(
            simplest_in_interval(0, 0, include_left=True, include_right=True),
            0,
        )

    def test_simplest_in_open_interval(self):
        F = fractions.Fraction

        self.assertEqual(
            simplest_in_interval(
                F(7, 10),
                F(5, 7),
                include_left=False,
                include_right=False,
            ),
            F(12, 17),
        )
        self.assertEqual(
            simplest_in_interval(
                F(10, 11),
                F(12, 13),
                include_left=False,
                include_right=False,
            ),
            F(11, 12),
        )
        self.assertEqual(
            simplest_in_interval(
                F(6, 11),
                F(17, 31),
                include_left=False,
                include_right=False,
            ),
            F(23, 42),
        )
        self.assertEqual(
            simplest_in_interval(
                F(0, 1),
                F(3, 5),
                include_left=False,
                include_right=False,
            ),
            F(1, 2),
        )
        self.assertEqual(
            simplest_in_interval(
                F(-3, 1),
                F(-1, 1),
                include_left=False,
                include_right=False,
            ),
            F(-2, 1),
        )
        self.assertEqual(
            simplest_in_interval(
                -F(1, 1),
                F(0, 1),
                include_left=False,
                include_right=False,
            ),
            -F(1, 2),
        )
        self.assertEqual(
            simplest_in_interval(
                -F(2, 1),
                F(2, 1),
                include_left=False,
                include_right=False,
            ),
            F(0, 1),
        )
        self.assertEqual(
            simplest_in_interval(
                F(5, 2),
                math.inf,
                include_left=False,
                include_right=False,
            ),
            F(3, 1),
        )
        self.assertEqual(
            simplest_in_interval(
                -math.inf,
                math.inf,
                include_left=False,
                include_right=False,
            ),
            F(0, 1),
        )
        self.assertEqual(
            simplest_in_interval(
                -math.inf,
                F(5, 2),
                include_left=False,
                include_right=False,
            ),
            F(0, 1),
        )

        with self.assertRaises(ValueError):
            simplest_in_interval(
                F(1, 2),
                F(1, 2),
                include_left=False,
                include_right=False,
            )
        with self.assertRaises(ValueError):
            simplest_in_interval(0, 0, include_left=False, include_right=False)

    def test_simplest_in_interval(self):
        self.assertEqual(
            simplest_in_interval(
                3, 4, include_left=False, include_right=False
            ),
            3.5,
        )
        self.assertEqual(
            simplest_in_interval(3, 4, include_left=True, include_right=True),
            3,
        )

        self.assertEqual(
            simplest_in_interval(3, 4, include_left=True, include_right=False),
            3,
        )
        self.assertEqual(
            simplest_in_interval(3, 4, include_left=False, include_right=True),
            4,
        )
        self.assertEqual(
            simplest_in_interval(
                0, math.inf, include_left=True, include_right=False
            ),
            0,
        )
        self.assertEqual(
            simplest_in_interval(
                0, math.inf, include_left=False, include_right=False
            ),
            1,
        )
        self.assertEqual(
            simplest_in_interval(
                -1,
                math.inf,
                include_left=False,
                include_right=False,
            ),
            0,
        )
        self.assertEqual(
            simplest_in_interval(
                -1, math.inf, include_left=True, include_right=False
            ),
            0,
        )

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

    def test_simplest_in_interval_defaults(self):
        # By default, assumes an open interval.
        self.assertEqual(simplest_in_interval(3, 5), 4)
        self.assertEqual(simplest_in_interval(3, 5, include_left=True), 3)
        self.assertEqual(simplest_in_interval(-5, -3), -4)
        self.assertEqual(simplest_in_interval(-5, -3, include_right=True), -3)
        with self.assertRaises(ValueError):
            simplest_in_interval(2, 2)

        # semi-infinite interval
        self.assertEqual(simplest_in_interval(left=3.5), 4)
        self.assertEqual(simplest_in_interval(right=3.5), 0)
        self.assertEqual(simplest_in_interval(), 0)

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
        self.assertSimplerOrEqual(g, f)

    def assertSimplerOrEqual(self, x, y):
        """
        Assert that x is either simpler than, or equal to, y.
        """
        if x == y:
            return

        self.assertLessEqual(abs(x.numerator), abs(y.numerator))
        self.assertLessEqual(x.denominator, y.denominator)
        self.assertNotEqual(abs(x), abs(y))
