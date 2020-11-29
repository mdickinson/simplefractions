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
import struct


def _to_integer_ratio(x):
    """
    Convert a finite number or an infinity to an integer ratio.
    """
    if x == math.inf:
        return 1, 0
    elif x == -math.inf:
        return -1, 0
    else:
        return x.as_integer_ratio()


def _esb_path(x, side):
    """
    Extended Stern-Brocot tree path for a given number x.

    Parameters
    ----------
    x : number
        Integer, fraction or float. Can also be math.inf
        or -math.inf
    side : int
        Either -1, 0 or 1; controls which of the three
        equivalent paths for a given x is produced.

    Yields
    ------
    coeff : int
        Sequence of coefficients in the tree path, with
        each coefficient giving the number of times to
        go left or right. The first coefficient gives
        the number of steps left, and subsequent coefficients
        alternative with respect to the direction, so a
        sequence [0, 3, 5, 2] means: 'take 0 steps left,
        then 3 steps right, then 5 steps left, then 2 steps
        right'.

        The first coefficient generated may be 0,
        and the last coefficient generated may be math.inf; other
        than that, all coefficients are positive integers.
        Additionally, an initial zero is always followed
        by something nonzero, so `[0]` is not a possible
        output sequence.
    """
    n, d = _to_integer_ratio(x)

    if (n, side) < (0, 0):
        yield 0
        n, side = -n, -side

    n += d
    while d < n or side:
        if not d:
            yield math.inf
            return
        q, r = divmod(n - (side <= 0), d)
        yield q
        n, d, side = d, r + (side <= 0), -side


def _from_esb_path(path):
    """
    Reconstruct a number x from its Extended Stern-Brocot tree path.
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


def simplest_in_interval(left, include_left, right, include_right):
    """
    Return simplest fraction in a given nonempty subinterval.
    """
    left_side = 0 if include_left else 1
    right_side = 0 if include_right else -1
    if (left, left_side) > (right, right_side):
        raise ValueError("empty interval")

    left_sequence = _esb_path(left, left_side)
    right_sequence = _esb_path(right, right_side)
    return _from_esb_path(_common_prefix(left_sequence, right_sequence))


def simplest_from_float(x: float) -> fractions.Fraction:
    """
    Return the simplest fraction that converts to the given float.
    """
    if not math.isfinite(x):
        raise ValueError("x should be finite")

    left, right, closed = _interval_rounding_to(x)
    return simplest_in_interval(left, closed, right, closed)
