import math
import fractions

from ..lang import data
from ..lang import d
from ..lang import deriving
from ..lang import H
from ..lang import sig
from ..lang import t
from ..lang import instance
from ..lang import build_instance
from ..lang import Enum
from ..lang import Show
from Eq import Eq
from Ord import Ord


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


class Fractional(Num):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(Fractional, cls, {})
        return

instance(Fractional, float).where()


class Floating(Fractional):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(Floating, cls, {})
        return

instance(Floating, float).where()


Ratio, R =\
        data.Ratio("a") == d.R("a", "a") & deriving(Eq)

Rational = t(Ratio, int)


class Real(Num, Ord):
    @classmethod
    def make_instance(typeclass, cls, toRational):
        build_instance(Real, cls, {})
        return


@sig(H[(Real, "a")]/ "a" >> Rational)
def toRational(x):
    return Real[x].toRational(x)


class Integral(Real, Enum):
    @classmethod
    def make_instance(typeclass, cls, quotRem, toInteger, quot=None, rem=None,
            div=None, mod=None, divMod=None):
        attrs = {"quotRem":quotRem, "toInteger":toInteger, "quot":quot,
                 "rem":rem, "div":div, "mod":mod, "divMod":divMod}
        build_instance(Integral, cls, attrs)
        return


@sig(H[(Integral, "a")]/ "a" >> "a" >> t(Ratio, "a"))
def toRatio(num, denom):
    frac = fractions.Fraction(num, denom)
    return R(frac.numerator, frac.deominator)



instance(Real, int).where(
    toRational = lambda x: toRatio(x, 1)
)

instance(Real, long).where(
    toRational = lambda x: toRatio(x, 1)
)

instance(Real, float).where(
    toRational = lambda x: toRatio(round(x), 1)
)

instance(Integral, int).where(
    quotRem = lambda x, y: (x / y, x % y),
    toInteger = int
)

instance(Integral, long).where(
    quotRem = lambda x, y: (x / y, x % y),
    toInteger = int
)


class RealFrac(Real, Fractional):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(RealFrac, cls, {})
        return


instance(RealFrac, float).where()


class RealFloat(Floating, RealFrac):
    @classmethod
    def make_instance(typeclass, cls, floatRadix, floatDigits, floatRange,
            decodeFloat, encodeFloat, exponent, significant, scaleFloat, isNan,
            isInfinite, isDenormalized, isNegativeZero, isIEEE, atan2):
        build_instance(RealFloat, cls, {})
        return


instance(RealFloat, float).where(
    floatRadix=None,
    floatDigits=None,
    floatRange=None,
    decodeFloat=None,
    encodeFloat=None,
    exponent=None,
    significant=None,
    scaleFloat=None,
    isNan=None,
    isInfinite=lambda x: x == float('inf') or x == -float('inf'),
    isDenormalized=None,
    isNegativeZero=None,
    isIEEE=None,
    atan2=math.atan2
)
