from ..lang.builtins import Maybe
from ..lang.builtins import Just
from ..lang.builtins import Nothing
from ..lang.syntax import L
from ..lang.syntax import H
from ..lang.syntax import sig
from ..lang.syntax import t


@sig(H/ "b" >> (H/ "a" >> "b") >> t(Maybe, "a") >> "b")
def maybe(default, f, maybe_a):
    """
    maybe :: b -> (a -> b) -> Maybe a -> b

    The maybe function takes a default value, a function, and a Maybe value. If
    the Maybe value is Nothing, the function returns the default value.
    Otherwise, it applies the function to the value inside the Just and returns
    the result.
    """
    pass


@sig(H/ t(Maybe, "a") >> bool)
def isJust(maybe_a):
    return not maybe_a == Nothing


@sig(H/ t(Maybe, "a")  >> bool)
def isNothing(maybe_a):
    return not isJust(maybe_a)


@sig(H/ t(Maybe, "a") >> "a")
def fromJust(x):
    if isJust(x):
        return x[0]
    raise ValueError("Cannot call fromJust on Nothing.")


@sig(H/ ["a"] >> t(Maybe, "a"))
def listToMaybe(list_a):
    if list_a:
        return Just(list_a)
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
