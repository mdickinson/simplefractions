import fractions
import itertools
import typing


#: Type alias: a path is an iterable of positive integers describing a
#: run-length-encoded path in the extended Stern-Brocot tree.
Path = typing.Iterable[int]


def _esb_path(n, d, right_side) -> Path:
    """
    Infinite extended Stern-Brocot tree path for a nonnegative sided fraction.
    """
    n, d, high = n + d, d, not right_side
    while d:
        q, r = divmod(n - high, d)
        yield q
        n, d, high = d, r + high, not high


def _longest_common_prefix(left_path: Path, right_path: Path) -> Path:
    """
    Longest common prefix of two paths.
    """
    left_small = True
    for count1, count2 in itertools.zip_longest(left_path, right_path):
        yield count1 if left_small else count2
        if count1 != count2:
            break
        left_small = not left_small


def _from_esb_path(path: Path) -> fractions.Fraction:
    """
    Reconstruct a fraction from a finite Extended Stern-Brocot tree path.
    """
    a, b, c, d = -1, 1, 1, 0
    for q in path:
        a, b, c, d = c, d, a + q * c, b + q * d
    return fractions.Fraction(a + c, b + d)


def _simplest_in_interval(
    left_endpoint: typing.Optional[fractions.Fraction] = None,
    right_endpoint: typing.Optional[fractions.Fraction] = None,
    *,
    include_left: bool = False,
    include_right: bool = False,
) -> fractions.Fraction:
    """
    Simplest fraction in a subinterval of the real line.
    """
    if left_endpoint is None and include_left:
        raise ValueError("interval may not contain -infinity")

    if right_endpoint is None and include_right:
        raise ValueError("interval may not contain infinity")

    # Is the interval nonempty?
    nonempty_interval = (
        left_endpoint is None
        or right_endpoint is None
        or left_endpoint < right_endpoint
        or (left_endpoint == right_endpoint and include_left and include_right)
    )
    if not nonempty_interval:
        raise ValueError("empty interval")

    # Does the interval contain zero?
    left_negative = (
        left_endpoint is None
        or left_endpoint < 0
        or (left_endpoint == 0 and include_left)
    )
    contains_zero = left_negative and (
        right_endpoint is None
        or 0 < right_endpoint
        or (0 == right_endpoint and include_right)
    )
    if contains_zero:
        return fractions.Fraction(0, 1)

    if left_negative:
        # left could be None; right cannot be
        assert right_endpoint is not None
        left_endpoint, right_endpoint = (
            -right_endpoint,
            None if left_endpoint is None else -left_endpoint,
        )
        include_left, include_right = include_right, include_left

    if left_endpoint is None:
        left_numerator = -1
        left_denominator = 0
    else:
        left_numerator = left_endpoint.numerator
        left_denominator = left_endpoint.denominator

    if right_endpoint is None:
        right_numerator = 1
        right_denominator = 0
    else:
        right_numerator = right_endpoint.numerator
        right_denominator = right_endpoint.denominator

    simplest = _from_esb_path(
        _longest_common_prefix(
            _esb_path(left_numerator, left_denominator, not include_left),
            _esb_path(right_numerator, right_denominator, include_right),
        )
    )
    return -simplest if left_negative else simplest
