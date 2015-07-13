import functools
import operator

from ..lang import sig
from ..lang import H
from ..lang import t
from ..lang import Typeclass
from ..lang import build_instance
from ..lang import List
from ..lang import Ord

from Num import Num


class Foldable(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, foldr):
        build_instance(Foldable, cls, {"foldr":foldr})
        return


def traverse_(s):
    pass

def mapM_(x):
    pass

def sequenceA_(x):
    pass

def sequence_(x):
    pass

def fold(xs):
    pass


def foldl(f, b, xs):
    """
    foldl :: (b -> a -> b) -> b -> t a -> b

    Left-associative fold of a structure.
    """
    raise NotImplementedError()


def foldl_(f, b, xs):
    """
    foldl' :: (b -> a -> b) -> b -> t a -> b

    Left-associative fold of a structure. but with strict application of the
    operator.
    """
    raise NotImplementedError()


@sig(H/ (H/ "a" >> "a" >> "a") >> ["a"] >> "a")
def foldl1(f, b, xs):
    """


    """
    raise NotImplementedError()


@sig(H/ (H/ "a" >> "a" >> "a") >> ["a"] >> "a")
def foldl1_(f, b, xs):
    """
    """
    raise NotImplementedError()


@sig(H/ (H/ "a" >> "b" >> "b") >> "b" >> ["a"] >> "b")
def foldr(f, b, xs):
    """
    """
    raise NotImplementedError()


@sig(H/ (H/ "a" >> "a" >> "a") >> ["a"] >> "a")
def foldr1(f, b, xs):
    """
    """
    raise NotImplementedError()


#=============================================================================#
# Special folds


@sig(H/ [["a"]] >> ["a"] )
def concat(xss):
    """
    concat :: [[a]] -> [a]

    Concatenate a list of lists.
    """
    return L[(x for xs in xss for x in xs)]


@sig(H/ (H/ "a" >> ["b"]) >> ["a"] >> ["b"])
def concatMap(f, xs):
    """
    concatMap :: (a -> [b]) -> [a] -> [b]

    Map a function over a list and concatenate the results.
    """
    return concat(map_(f, xs))


@sig(H/ [bool] >> bool)
def and_(xs):
    """
    and_ :: [Bool] -> Bool

    and returns the conjunction of a Boolean list. For the result to be True,
    the list must be finite; False, however, results from a False value at a
    finite index of a finite or infinite list.
    """
    return False not in xs


@sig(H/ [bool] >> bool)
def or_(xs):
    """
    or_ :: [Bool] -> Bool

    or returns the disjunction of a Boolean list. For the result to be False,
    the list must be finite; True, however, results from a True value at a
    finite index of a finite or infinite list.
    """
    return True in xs


@sig(H/ (H/ "a" >> bool) >> ["a"] >> bool)
def any(xs):
    """
    any :: (a -> Bool) -> [a] -> Bool

    Applied to a predicate and a list, any determines if any element of the
    list satisfies the predicate. For the result to be False, the list must be
    finite; True, however, results from a True value for the predicate applied
    to an element at a finite index of a finite or infinite list.
    """
    return True in ((p(x) for x in xs))


@sig(H/ (H/ "a" >> bool) >> ["a"] >> bool)
def all(p, xs):
    """
    all :: (a -> Bool) -> [a] -> Bool

    Applied to a predicate and a list, all determines if all elements of the
    list satisfy the predicate. For the result to be True, the list must be
    finite; False, however, results from a False value for the predicate
    applied to an element at a finite index of a finite or infinite list.
    """
    return False not in ((p(x) for x in xs))


@sig(H[(Num, "a")]/ ["a"] >> "a")
def sum(xs):
    """
    sum :: Num a => [a] -> a

    The sum function computes the sum of a finite list of numbers.
    """
    return functools.reduce(operator.add, xs, 0)


@sig(H[(Num, "a")]/ ["a"] >> "a")
def product(xs):
    """
    product :: Num a => [a] -> a

    The product function computes the product of a finite list of numbers.
    """
    return functools.reduce(operator.mul, xs, 1)


@sig(H[(Ord, "a")]/ ["a"] >> "a")
def minimum(xs):
    """
    minimum :: Ord a => [a] -> a

    minimum returns the minimum value from a list, which must be non-empty,
    finite, and of an ordered type. It is a special case of minimumBy, which
    allows the programmer to supply their own comparison function.
    """
    return min(xs)


@sig(H[(Ord, "a")]/ ["a"] >> "a")
def maximum(xs):
    """
    maximum :: Ord a => [a] -> a

    maximum returns the maximum value from a list, which must be non-empty,
    finite, and of an ordered type. It is a special case of maximumBy, which
    allows the programmer to supply their own comparison function.
    """
    return max(xs)
