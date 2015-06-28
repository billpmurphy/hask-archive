from ..lang import sig
from ..lang import H
from ..lang import instance
from ..lang import build_instance
from ..lang import Show
from ..lang import Eq


class Num(Show, Eq):
    @classmethod
    def make_instance(typeclass, cls, add, mul, abs, signum, fromInteger,
            negate, sub=None):

        @sig(H[(Num, "a")]/ "a" >> "a" >> "a")
        def default_sub(a, b):
            return a.__add__(b.__neg__())

        sub = default_sub if sub is None else sub
        attrs = {"add":add, "mul":mul, "abs":abs, "signum":signum,
                 "fromInteger":fromInteger, "neg":negate, "sub":sub}

        build_instance(Num, cls, attrs)
        return


@sig(H[(Num, "a")]/ "a" >> "a")
def negate(a):
    """
    signum :: Num a => a -> a

    Unary negation.
    """
    return Num[a].negate(a)


@sig(H[(Num, "a")]/ "a" >> "a")
def signum(a):
    """
    signum :: Num a => a -> a

    Sign of a number. The functions abs and signum should satisfy the law:
    abs x * signum x == x
    For real numbers, the signum is either -1 (negative), 0 (zero) or 1
    (positive).
    """
    return Num[a].signum(a)


@sig(H[(Num, "a")]/ "a" >> "a")
def abs_(a):
    """
    abs :: Num a => a -> a

    Absolute value.
    """
    return Num[a].abs(a)



instance(Num, int).where(
    add = int.__add__,
    mul = int.__mul__,
    abs = abs,
    signum = lambda x: -1 if x < 0 else (1 if x > 0 else 0),
    fromInteger = int,
    negate = int.__neg__,
    sub = int.__sub__
)

instance(Num, long).where(
    add = long.__add__,
    mul = long.__mul__,
    abs = abs,
    signum = lambda x: -1 if x < 0 else (1 if x > 0 else 0),
    fromInteger = long,
    negate = long.__neg__,
    sub = long.__sub__
)

instance(Num, float).where(
    add = float.__add__,
    mul = float.__mul__,
    abs = abs,
    signum = lambda x: -1 if x < 0 else (1 if x > 0 else 0),
    fromInteger = float,
    negate = float.__neg__,
    sub = float.__sub__
)

instance(Num, complex).where(
    add = complex.__add__,
    mul = complex.__mul__,
    abs = abs,
    signum = lambda x: -1 if x < 0 else (1 if x > 0 else 0),
    fromInteger = complex,
    negate = complex.__neg__,
    sub = complex.__sub__
)
