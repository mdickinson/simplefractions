from math import gcd


def find_cd(a: int, b: int) -> list[tuple[int, int]]:
    """
    Given a positive fraction a/b (expressed in lowest terms), find both
    fractions c/d which are simpler than a/b and which satisfy |ad - bc| = 1.
    """
    p, q, r, s = 0, 1, 1, 0
    while b:
        x = a // b
        a, b, p, q, r, s = b, a - x * b, r, s, p + x * r, q + x * s
    return [(p, q), (r - p, s - q)]


for a in range(2**26, 2**27):
    for b in range(2**26, a):
        if gcd(a, b) > 1:
            continue
        for c, d in find_cd(a, b):
            if a / b == c / d:
                print(f"{a}/{b} == {c}/{d}")
