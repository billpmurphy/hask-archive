import math
import fractions

from .lang import build_instance
from .lang import H
from .lang import sig
from .lang import L
from .lang import instance


#=============================================================================#
# Standard types, classes, and related functions
## Basic data types


from Data.Maybe import Maybe
from Data.Maybe import Just
from Data.Maybe import Nothing
from Data.Maybe import in_maybe
from Data.Maybe import maybe

from Data.Either import Either
from Data.Either import Left
from Data.Either import Right
from Data.Either import in_either
from Data.Either import either

from Data.Ord import Ordering
from Data.Ord import LT
from Data.Ord import EQ
from Data.Ord import GT


#=============================================================================#
### Tuples


from Data.Tuple import fst
from Data.Tuple import snd
from Data.Tuple import curry
from Data.Tuple import uncurry


#=============================================================================#
## Basic type classes


from .lang.typeclasses import Read
from .lang.typeclasses import Show


@sig(H/ "a" >> str)
def show(obj):
    return Show.show(obj)


from Data.Eq import Eq
from Data.Ord import Ord
from Data.Ord import max
from Data.Ord import min
from Data.Ord import compare


# builtin instances for Show
for _type in (str, int, long, float, complex, bool, list, tuple):
    instance(Show, _type).where(show=_type.__str__)
    instance(Eq, _type).where(eq=_type.__eq__, ne=_type.__ne__)
    instance(Ord, _type).where(
            lt=_type.__lt__, le=_type.__le__, gt=_type.__gt__, ge=_type.__ge__)


from .lang.typeclasses import Enum
from .lang.typeclasses import fromEnum
from .lang.typeclasses import toEnum
from .lang.typeclasses import succ
from .lang.typeclasses import pred
from .lang.typeclasses import enumFromThen
from .lang.typeclasses import enumFrom
from .lang.typeclasses import enumFromThenTo
from .lang.typeclasses import enumFromTo


instance(Enum, int).where(
        toEnum=int,
        fromEnum=int
)

instance(Enum, long).where(
        toEnum=int,
        fromEnum=long
)

instance(Enum, bool).where(
        toEnum=int,
        fromEnum=bool
)

instance(Enum, str).where(
        toEnum=ord,
        fromEnum=chr
)

from .lang.typeclasses import Bounded
from Data.Functor import Functor
from Data.Functor import fmap

from Control.Applicative import Applicative
from Control.Monad import Monad
from Data.Foldable import Foldable
from Data.Traversable import Traversable


#=============================================================================#
# Numbers
### Numeric type classes


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
def abs(a):
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


class Real(Num, Ord):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(Real, cls, {})
        return


instance(Real, int).where()
instance(Real, long).where()
instance(Real, float).where()


class Integral(Real, Enum):
    @classmethod
    def make_instance(typeclass, cls, quotRem, toInteger, quot=None, rem=None,
            div=None, mod=None, divMod=None):
        attrs = {"quotRem":quotRem, "toInteger":toInteger, "quot":quot,
                 "rem":rem, "div":div, "mod":mod, "divMod":divMod}
        build_instance(Integral, cls, attrs)
        return


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


#=============================================================================#
# Numeric functions


@sig(H[(Num, "a")]/ "a" >> "a" >> "a")
def subtract(x, y):
    """
    subtract :: Num a => a -> a -> a

    the same as lambda x, y: y - x
    """
    return y - x


@sig(H[(Integral, "a")]/ "a" >> bool)
def even(x):
    """
    even :: Integral a => a -> Bool

    Returns True if the integral value is even, and False otherwise.
    """
    return x % 2 == 0


@sig(H[(Integral, "a")]/ "a" >> bool)
def odd(x):
    """
    odd :: Integral a => a -> Bool

    Returns True if the integral value is odd, and False otherwise.
    """
    return x % 2 == 1


@sig(H[(Integral, "a")]/ "a" >> "a" >> "a")
def gcd(x, y):
    """
    gcd :: Integral a => a -> a -> a

    gcd(x,y) is the non-negative factor of both x and y of which every common
    factor of x and y is also a factor; for example gcd(4,2) = 2, gcd(-4,6) =
    2, gcd(0,4) = 4. gcd(0,0) = 0. (That is, the common divisor that is
    "greatest" in the divisibility preordering.)
    """
    return fractions.gcd(x, y)


@sig(H[(Integral, "a")]/ "a" >> "a" >> "a")
def lcm(x, y):
    """
    lcm :: Integral a => a -> a -> a

    lcm(x,y) is the smallest positive integer that both x and y divide.
    """
    return div(x * y, gcd(a, b))


#=============================================================================#
# Monads and functors


from Data.Functor import Functor
from Control.Applicative import Applicative
from Control.Monad import Monad


def mapM(fm, xs):
    return sequence(map(fm, xs))

def mapM_(fm, xs):
    return sequence_(map(fm, xs))

def sequence(xs):
    return

def sequence_(xs):
    return



#=============================================================================#
# Miscellaneous functions


@sig(H/ "a" >> "a")
def id(a):
    """
    id :: a -> a

    Identity function.
    """
    return a


@sig(H/ "a" >> "b" >> "a")
def const(a, b):
    """
    const :: a -> b -> a

    Constant function.
    """
    return a


@sig(H/ (H/ "a" >> "b" >> "c") >> "b" >> "a" >> "c")
def flip(f, b, a):
    """
    flip :: (a -> b -> c) -> b -> a -> c

    flip(f) takes its (first) two arguments in the reverse order of f.
    """
    return f(a, b)


@sig(H/ (H/ "a" >> bool) >> (H/ "a" >> "a") >> "a" >> "a")
def until(p, f, a):
    """
    until :: (a -> Bool) -> (a -> a) -> a -> a

    until(p, f, a) yields the result of applying f until p(a) holds.
    """
    while not p(a):
        a = f(a)
    return a


@sig(H/ "a" >> "a" >> "a")
def asTypeOf(a, b):
    """
    asTypeOf :: a -> a -> a

    asTypeOf is a type-restricted version of const. It is usually used as an
    infix operator, and its typing forces its first argument (which is usually
    overloaded) to have the same type as the second.
    """
    return a


@sig(H/ str >> "a")
def error(msg):
    """
    error :: str -> a

    error(msg) stops execution and displays an error message.
    """
    raise Exception(msg)


from .lang import undefined


#=============================================================================#
# List operations


from Data.List import map
from Data.List import filter
from Data.List import head
from Data.List import last
from Data.List import tail
from Data.List import init
from Data.List import reverse


#=============================================================================#
## Special folds


from Data.List import and_
from Data.List import or_
from Data.List import any_
from Data.List import all_
from Data.List import concat
from Data.List import concatMap


#=============================================================================#
## Building lists
### Scans


from Data.List import and_
from Data.List import and_
from Data.List import and_
from Data.List import and_


#=============================================================================#
### Infinite lists


from Data.List import iterate
from Data.List import repeat
from Data.List import replicate
from Data.List import cycle


#=============================================================================#
## Sublists


from Data.List import take
from Data.List import drop
from Data.List import splitAt
from Data.List import takeWhile
from Data.List import dropWhile
from Data.List import span
from Data.List import break_


#=============================================================================#
## Searching lists


from Data.List import notElem
from Data.List import lookup


#=============================================================================#
## Zipping and unzipping lists


from Data.List import lookup
from Data.List import lookup
from Data.List import lookup
from Data.List import lookup
from Data.List import lookup
from Data.List import lookup


#=============================================================================#
## Functions on strings


from Data.List import lines
from Data.List import words
from Data.List import unlines
from Data.List import unwords
