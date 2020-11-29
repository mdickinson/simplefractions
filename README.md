Given fractions *x* and *y*, say that *x* is **simpler** than *y* if, when both
*x* and *y* are written in lowest terms:

- the numerator of *x* is no larger in absolute value than the numerator of
  *y*, and
- the denominator of *x* is no larger than the denominator of *y*, and
- *x* and *y* are not equal to each other in absolute value

The **simplefractions** package provides two functions:

- `simplest_from_float` returns, for a given float ``x``, the unique simplest
  fraction with the property that ``float(simplest_from_float(x)) == x``.
- `simplest_in_interval` returns the unique simplest fraction in a given
  (open or closed, bounded or unbounded) nonempty interval.

Example usage
-------------

```python
>>> from simplefractions import *
>>> x = 231 / 199
>>> x
1.1608040201005025
>>> simplest_from_float(x)
Fraction(231, 199)
>>> float(simplest_from_float(x)) == x
True
>>> simplest_in_interval(3.14, 3.15)
Fraction(22, 7)
>>> simplest_in_interval(3, 4)
Fraction(7, 2)
>>> simplest_in_interval(3, 4, include_left=True, include_right=True)
Fraction(3, 1)
>>> simplest_in_interval(right=4)
Fraction(0, 1)
>>> simplest_in_interval(left=4)
Fraction(5, 1)
```
