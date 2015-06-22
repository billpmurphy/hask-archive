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


Show.derive_instance(str)
Show.derive_instance(int)
Show(long, long.__str__)
Show(float, float.__str__)
Show(complex, complex.__str__)
Show(bool, bool.__str__)
Show(list, list.__str__)
Show(tuple, tuple.__str__)

from Data.Eq import Eq

Eq(str, str.__eq__)
Eq(int, int.__eq__)
Eq(long, long.__eq__)
Eq(float, float.__eq__)
Eq(complex, complex.__eq__)
Eq(bool, bool.__eq__)
Eq(list, list.__eq__)
Eq(tuple, tuple.__eq__)

from Data.Ord import Ord
from Data.Ord import max
from Data.Ord import min
from Data.Ord import compare

Ord(str, str.__lt__, str.__le__, str.__gt__, str.__ge__)
Ord(int, int.__lt__, int.__le__, int.__gt__, int.__ge__)
Ord(long, long.__lt__, long.__le__, long.__gt__, long.__ge__)
Ord(float, float.__lt__, float.__le__, float.__gt__, float.__ge__)
Ord(complex, complex.__lt__, complex.__le__, complex.__gt__, complex.__ge__)
Ord(bool, bool.__lt__, bool.__le__, bool.__gt__, bool.__ge__)
Ord(list, list.__lt__, list.__le__, list.__gt__, list.__ge__)
Ord(tuple, tuple.__lt__, tuple.__le__, tuple.__gt__, tuple.__ge__)


from .lang.typeclasses import Enum

Enum(int,  toEnum=lambda a: a,      fromEnum=lambda a: a)
Enum(long, toEnum=lambda a: a,      fromEnum=lambda a: a)
Enum(bool, toEnum=lambda a: int(a), fromEnum=lambda a: bool(a))


from .lang.typeclasses import Functor
from .lang.typeclasses import fmap

from .lang.typeclasses import Applicative
from .lang.typeclasses import Monad
from .lang.typeclasses import Traversable
from .lang.typeclasses import Iterator
from .lang.typeclasses import Foldable


#=============================================================================#
## Numbers
### Numeric types


from .lang.typeclasses import Num
from .lang.typeclasses import Real
from .lang.typeclasses import Integral
from .lang.typeclasses import Floating
from .lang.typeclasses import Fractional
from .lang.typeclasses import RealFrac
from .lang.typeclasses import RealFloat
from .lang.typeclasses import Read

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


Real(int)
Real(long)
Real(float)

Integral(int)
Integral(long)

Fractional(float)

Floating(float)

RealFrac(float)

RealFloat(float)


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


from .lang.typeclasses import Functor
from .lang.typeclasses import Applicative
from .lang.typeclasses import Monad


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
