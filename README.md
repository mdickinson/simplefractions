Given fractions *x* and *y*, say that *x* is **simpler** than *y* if when both
*x* and *y* are written in lowest terms:

- the numerator of *x* is no larger in absolute value than the numerator of
  *y*, and
- the denominator of *x* is no larger than the denominator of *y*, and
- *x* and *y* are not equal (disregarding sign)

The **simplefractions** package provides two functions:

- `simplest_in_interval` returns the unique simplest fraction in a given
  (open or closed, infinite or bounded) nonempty interval.
- `simplest_from_float` returns the unique simplest fraction that rounds to
  the given finite floating-point number.

Example usage
-------------
