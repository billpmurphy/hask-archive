from ..lang.typeclasses import Read, Show
from ..lang.syntax import L
from ..lang.syntax import H
from ..lang.syntax import sig
from ..lang.syntax import t
from ..lang.syntax import data
from ..lang.syntax import d
from ..lang.syntax import deriving
from ..lang.syntax import instance

from Eq import Eq
from Ord import Ord
from Functor import Functor
from ..Control.Applicative import Applicative
from ..Control.Monad import Monad


# data Maybe a = Nothing | Just a deriving(Show, Eq, Ord)
Maybe, Nothing, Just =\
        data.Maybe("a") == d.Nothing | d.Just("a") & deriving(Show, Eq, Ord)

instance(Functor, Maybe).where(
    fmap = lambda x, f: Nothing if x == Nothing else Just(f(x[0]))
)

instance(Applicative, Maybe).where(
    pure = Just
)

instance(Monad, Maybe).where(
    bind = lambda x, f: Nothing if x == Nothing else f(x[0])
)


def in_maybe(fn, *args, **kwargs):
    """
    Decorator for monadic error handling.
    If the decorated function raises an exception, return Nothing. Otherwise,
    take the result and wrap it in a Just.
    """
    def closure_in_maybe(*args, **kwargs):
        try:
            return Just(fn(*args, **kwargs))
        except:
            return Nothing
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_maybe(*args, **kwargs)
    return closure_in_maybe


@sig(H/ "b" >> (H/ "a" >> "b") >> t(Maybe, "a") >> "b")
def maybe(default, f, maybe_a):
    """
    maybe :: b -> (a -> b) -> Maybe a -> b

    The maybe function takes a default value, a function, and a Maybe value. If
    the Maybe value is Nothing, the function returns the default value.
    Otherwise, it applies the function to the value inside the Just and returns
    the result.
    """
    return default if maybe_a == Nothing else f(maybe_a[0])


@sig(H/ t(Maybe, "a") >> bool)
def isJust(a):
    return not isNothing(a)


@sig(H/ t(Maybe, "a")  >> bool)
def isNothing(a):
    return a == Nothing


@sig(H/ t(Maybe, "a") >> "a")
def fromJust(x):
    if isJust(x):
        return x[0]
    raise ValueError("Cannot call fromJust on Nothing.")


@sig(H/ ["a"] >> t(Maybe, "a"))
def listToMaybe(a):
    if len(a) > 0:
        return Just(a[0])
    return Nothing


@sig(H/ t(Maybe, "a") >> ["a"])
def maybeToList(maybe_a):
    """
    maybeToList :: Maybe a -> [a]

    The maybeToList function returns an empty list when given Nothing or a
    singleton list when not given Nothing.
    """
    if isJust(maybe_a):
        return L[[fromJust(maybe_a)]]
    return L[[]]


@sig(H/ [t(Maybe, "a")] >> ["a"])
def catMaybes(a):
    """
    catMaybes :: [Maybe a] -> [a]

    The catMaybes function takes a list of Maybes and returns a list of all the
    Just values.
    """
    return L[(item for item in a if isJust(item))]


@sig(H/ (H/ "a" >> (Maybe, "a")) >> ["a"] >> ["b"])
def mapMaybe(f, la):
    """
    mapMaybe :: (a -> Maybe b) -> [a] -> [b]

    The mapMaybe function is a version of map which can throw out elements. In
    particular, the functional argument returns something of type Maybe b. If
    this is Nothing, no element is added on to the result list. If it is Just
    b, then b is included in the result list.
    """
    return L[(fromJust(b) for b in (f(a) for a in la) if isJust(b))]
