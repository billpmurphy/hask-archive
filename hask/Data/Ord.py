from ..lang.syntax import sig
from ..lang.syntax import H
from ..lang.builtins import Ordering
from ..lang.builtins import LT
from ..lang.builtins import EQ
from ..lang.builtins import GT
from ..lang.typeclasses import Ord


#TODO: Down?


@sig(H[(Ord, "a")]/ "a" >> "a" >> "a")
def max(x, y):
    """
    max :: a -> a -> a

    Maximum function.
    """
    return x if x >= y else y


@sig(H[(Ord, "a")]/ "a" >> "a" >> "a")
def min(x, y):
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
