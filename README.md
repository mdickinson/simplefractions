The **simplefractions** package finds the simplest fraction that converts
to a given float, or more generally, the simplest fraction that lies within
a given interval.

**Definition.** Given fractions *x = a/b* and *y = c/d* (written in lowest
terms with positive denominators), say that *x* is **simpler** than *y* if
*abs(a) <= abs(c)*, *b <= d*, and at least one of these two inequalities
is strict.

For example, 22/7 is simpler than 23/8, but neither of 3/8 and 4/7 is
simpler than the other.

Then it's a theorem that given any subinterval *I* of the real line that
contains at least one fraction, that interval contains a unique simplest
fraction. That is, there's a fraction *a/b* in *I* such that *a/b* is
simpler (in the above sense) than all other fractions in *I*. As a
consequence, for any given finite Python float *x*, there's a unique
simplest fraction that rounds to that float.

The **simplefractions** package provides two functions:

- `simplest_from_float` returns, for a given float ``x``, the unique simplest
  fraction with the property that ``float(simplest_from_float(x)) == x``.
- `simplest_in_interval` returns the unique simplest fraction in a given
  (open or closed, bounded or unbounded) nonempty interval.

## Example usage

Start by importing the functions from the module:

```python
>>> from simplefractions import *
```

The `simplest_from_float` function takes a single finite float `x` and
produces a `Fraction` object that recovers that float:

```python
>>> simplest_from_float(0.25)
Fraction(1, 4)
>>> simplest_from_float(0.33)
Fraction(33, 100)
```

No matter what `x` is given, the invariant `float(simplest_from_float(x)) == x`
will always be true.

```python
>>> x = 0.7429667872099244
>>> simplest_from_float(x)
Fraction(88650459, 119319545)
>>> float(simplest_from_float(x))
0.7429667872099244
>>> float(simplest_from_float(x)) == x
True
```

If the float `x` was constructed by dividing two small integers, then
more often than not, `simplest_from_float` will recover those integers:

```python
>>> x = 231 / 199
>>> x
1.1608040201005025
>>> simplest_from_float(x)
Fraction(231, 199)
```

More precisely, if `x` was constructed by dividing two relatively prime
integers smaller than or equal to `67114657` in absolute value,
`simplest_from_float` will recover those integers.

```python
>>> simplest_from_float(64841043 / 66055498)
Fraction(64841043, 66055498)
```

But `67114657` is the best we can do here:

```python
>>> simplest_from_float(67114658 / 67114657)
Fraction(67114657, 67114656)
```

In larger cases, `simplest_from_float` might discover a simpler fraction
that gives the same float:

```python
>>> x = 818421477165 / 1580973145504
>>> simplest_from_float(x)
Fraction(5171, 9989)
>>> 818421477165 / 1580973145504 == 5171 / 9989
True
```

Note that `simplest_from_float` does not magically fix floating-point
inaccuracies. For example:

```python
>>> x = 1.1 + 2.2
>>> simplest_from_float(x)
Fraction(675539944105597, 204709073971393)
```

You might have expected `Fraction(33, 10)` here, but when converted to float,
that gives a value very close to, but not exactly equal to, `x`. In contrast,
the return value of `simplest_from_float(x)` will always produce exactly `x`
when converted to `float`.

To fix this, you might want to ask for the simplest float that lies within
some small error bound of `x` - for example, within 5 ulps (units in the
last place) in either direction. `simplest_from_float` can't do that, but
`simplest_in_interval` can! For example

```python
>>> from math import ulp
>>> x = 1.1 + 2.2
>>> simplest_in_interval(x - 5*ulp(x), x + 5*ulp(x))
Fraction(33, 10)
```

Alternatively, you might ask for the simplest fraction approximating `x`
with a relative error of at most 0.000001:

```python
>>> relerr = 1e-6
>>> simplest_in_interval(x - relerr*x, x + relerr*x)
Fraction(33, 10)
```

Here are some more examples of `simplest_in_interval` at work. The inputs
to `simplest_in_interval` can be floats, integers, or `Fraction` objects.

```python
>>> simplest_in_interval(3.14, 3.15)
Fraction(22, 7)
```

By default, `simplest_in_interval` assumes that you're specifying an
open interval:

```python
>>> simplest_in_interval(3, 4)
Fraction(7, 2)
```

Keyword arguments `include_left` and `include_right` allow you to specify
that one or both endpoints should be included in the interval:

```python
>>> simplest_in_interval(3, 4, include_left=True, include_right=True)
Fraction(3, 1)
```

The left and right endpoints of the interval are also both optional, alowing
a semi-infinite or infinite interval to be specified:

```python
>>> simplest_in_interval(right=4)  # simplest in (-inf, 4)
Fraction(0, 1)
>>> simplest_in_interval(left=4, include_left=True)  # simplest in [4, inf)
Fraction(4, 1)
>>> simplest_in_interval()  # simplest in (-inf, inf)
Fraction(0, 1)
```
