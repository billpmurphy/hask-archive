from .lang.type_system import build_instance
from .lang.syntax import H
from .lang.syntax import sig
from .lang.syntax import L
from .lang.syntax import instance


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


from .lang.typeclasses import Bounded
from Data.Functor import Functor
from Data.Functor import fmap

from Control.Applicative import Applicative
from Control.Monad import Monad
from Data.Foldable import Foldable
from Data.Traversable import Traversable


#=============================================================================#
## Numbers
### Numeric types


class Num(Show, Eq):
    @classmethod
    def make_instance(typeclass, cls, add, mul, abs, signum, fromInteger,
            negate, sub=None):
        def default_sub(a, b):
            return a.__add__(b.__neg__())

        sub = default_sub if sub is None else sub
        attrs = {"add":add, "mul":mul, "abs":abs, "signum":signum,
                 "fromInteger":fromInteger, "neg":negate, "sub":sub}

        build_instance(Num, cls, attrs)
        return


def __signum(a):
    """
    Signum function for python builtin numeric types.
    """
    if a < 0:   return -1
    elif a > 0: return 1
    else:       return 0


instance(Num, int).where(
    add = int.__add__,
    mul = int.__mul__,
    abs = abs,
    signum = __signum,
    fromInteger = int,
    negate = int.__neg__,
    sub = int.__sub__
)

instance(Num, long).where(
    add = long.__add__,
    mul = long.__mul__,
    abs = abs,
    signum = __signum,
    fromInteger = long,
    negate = long.__neg__,
    sub = long.__sub__
)

instance(Num, float).where(
    add = float.__add__,
    mul = float.__mul__,
    abs = abs,
    signum = __signum,
    fromInteger = float,
    negate = float.__neg__,
    sub = float.__sub__
)

instance(Num, complex).where(
    add = complex.__add__,
    mul = complex.__mul__,
    abs = abs,
    signum = __signum,
    fromInteger = complex,
    negate = complex.__neg__,
    sub = complex.__sub__
)


class Fractional(Num):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(Fractional, cls, {})
        return


class Floating(Fractional):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(Floating, cls, {})
        return


class Real(Num, Ord):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(Real, cls, {})
        return


class Integral(Real, Enum):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(Integral, cls, {})
        return


class RealFrac(Real, Fractional):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(RealFrac, cls, {})
        return


class RealFloat(Floating, RealFrac):
    @classmethod
    def make_instance(typeclass, cls):
        build_instance(RealFloat, cls, {})
        return


instance(Real, int).where()
instance(Real, long).where()
instance(Real, float).where()

instance(Integral, int).where()
instance(Integral, long).where()

instance(Fractional, float).where()
instance(Floating, float).where()
instance(RealFrac, float).where()
instance(RealFloat, float).where()


#=============================================================================#
# Numeric type classes



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
    pass


@sig(H[(Integral, "a")]/ "a" >> "a" >> "a")
def lcm(x, y):
    """
    lcm :: Integral a => a -> a -> a

    lcm(x,y) is the smallest positive integer that both x and y divide.
    """
    pass


#=============================================================================#
# Monads and functors


from Data.Functor import Functor
from Control.Applicative import Applicative
from Control.Monad import Monad


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


#=============================================================================#
## Building lists


#=============================================================================#
### Scans


#=============================================================================#
### Infinite lists


from Data.List import iterate
from Data.List import repeat
from Data.List import replicate
from Data.List import cycle


#=============================================================================#
## Sublists


#=============================================================================#
## Searching lists


#=============================================================================#
## Zipping and unzipping lists


#=============================================================================#
## Functions on strings


from Data.List import lines
from Data.List import words
from Data.List import unlines
from Data.List import unwords
