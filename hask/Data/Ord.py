from ..lang import Show, Bounded
from ..lang import Ord
from ..lang import sig
from ..lang import H
from ..lang import data
from ..lang import d
from ..lang import deriving

from Eq import Eq


# data Ordering = LT | EQ | GT deriving(Show, Eq, Ord, Bounded)
Ordering, LT, EQ, GT =\
data.Ordering == d.LT | d.EQ | d.GT & deriving(Show, Eq, Ord, Bounded)


#TODO: Down?


@sig(H[(Ord, "a")]/ "a" >> "a" >> "a")
def max_(x, y):
    """
    max :: a -> a -> a

    Maximum function.
    """
    return x if x >= y else y


@sig(H[(Ord, "a")]/ "a" >> "a" >> "a")
def min_(x, y):
    """
    min :: a -> a -> a

    Minumum function.
    """
    return x if x <= y else y


@sig(H[(Ord, "a")]/ "a" >> "a" >> Ordering)
def compare(x, y):
    """
    compare :: a -> a -> Ordering

    Comparison function.
    """
    if x == y:
        return EQ
    elif x < y:
        return LT
    return GT


@sig(H[(Ord, "a")]/ (H/ "a" >> "b") >> "b" >> "b" >> Ordering)
def comparing(p, x, y):
    """
    comparing :: Ord a => (b -> a) -> b -> b -> Ordering

    comparing(p, x, y) = compare(p(x), p(y))

    Useful combinator for use in conjunction with the xxxBy family of functions
    from Data.List, for example:

    ... sortBy (comparing(fst)) ...
    """
    return compare(p(x), p(y))
