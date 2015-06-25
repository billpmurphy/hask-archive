from ..lang import Show
from ..lang import sig
from ..lang import H
from ..lang import t
from ..lang import d
from ..lang import data
from ..lang import deriving
from ..lang import instance
from ..lang import L
from ..lang import typify

from Eq import Eq
from Ord import Ord
from Functor import Functor
from ..Control.Applicative import Applicative
from ..Control.Monad import Monad


# data Either a b = Left b | Right a deriving(Show, Eq, Ord)
Either, Left, Right =\
        data.Either("a", "b") == d.Left("a") | d.Right("b") &\
                                 deriving(Show, Eq, Ord)

instance(Functor, Either).where(
    fmap = lambda v, f: v if Left(v[0]) == v else Right(f(v[0]))
)

instance(Applicative, Either).where(
    pure = Right
)

instance(Monad, Either).where(
    bind = lambda v, f: v if Left(v[0]) == v else f(v[0])
)


def in_either(fn, *args, **kwargs):
    """
    Decorator for monadic error handling.
    If the decorated function raises an exception, return the exception inside
    Left. Otherwise, take the result and wrap it in Right.
    """
    def closure_in_either(*args, **kwargs):
        try:
            return Right(fn(*args, **kwargs))
        except Exception as e:
            return Left(e)
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_either(*args, **kwargs)

    return typify(fn, hkt=lambda x: t(Either, "z", x))(closure_in_either)


@sig(H/ (H/ "a" >> "c") >> (H/ "b" >> "c") >> t(Either, "a", "b") >> "c")
def either(f_a, f_b, either_a_b):
    """
    either :: (a -> c) -> (b -> c) -> Either a b -> c

    Case analysis for the Either type. If the value is Left(a), apply the first
    function to a; if it is Right(b), apply the second function to b.
    """
    pass


@sig(H/ [t(Either, "a", "b")] >> ["a"])
def lefts(xs):
    """
    lefts :: [Either a b] -> [a]

    Extracts from a List of Either all the Left elements. All the Left elements
    are extracted in order.
    """
    pass


@sig(H/ [t(Either, "a", "b")] >> ["b"])
def rights(xs):
    """
    rights :: [Either a b] -> [b]

    Extracts from a list of Either all the Right elements. All the Right
    elements are extracted in order.
    """
    pass


@sig(H/ t(Either, "a", "b") >> bool)
def isLeft(x):
    """
    isLeft :: Either a b -> bool

    Return True if the given value is a Left-value, False otherwise.
    """
    pass


@sig(H/ t(Either, "a", "b") >> bool)
def isRight(x):
    """
    isRight :: Either a b -> bool

    Return True if the given value is a Right-value, False otherwise.
    """
    pass


@sig(H/ [t(Either, "a", "b")] >> (["a"], ["b"]))
def partitionEithers(xs):
    """
    partitionEithers :: [Either a b] -> ([a], [b])

    Partitions a List of Either into two lists. All the Left elements are
    extracted, in order, to the first component of the output. Similarly the
    Right elements are extracted to the second component of the output.
    """
    pass
