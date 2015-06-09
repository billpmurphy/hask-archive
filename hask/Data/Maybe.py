from ..lang.builtins import Maybe
from ..lang.builtins import Just
from ..lang.builtins import Nothing
from ..lang.syntax import L


def maybe(default, f, maybe_a):
    """
    maybe :: b -> (a -> b) -> Maybe a -> b

    The maybe function takes a default value, a function, and a Maybe value. If
    the Maybe value is Nothing, the function returns the default value.
    Otherwise, it applies the function to the value inside the Just and returns
    the result.
    """
    pass


def isJust(maybe_a):
    return not maybe_a is Nothing


def isNothing(maybe_a):
    return not isJust(maybe_a)


def fromJust(maybe_a):
    if isJust(maybe_a):
        return maybe_a._value
    raise ValueError("Cannot call fromJust on Nothing.")


def listToMaybe(list_a):
    if list_a:
        return Just(list_a)
    return Nothing


def maybeToList(maybe_a):
    if isJust(maybe_a):
        return [fromJust(maybe_a)]
    return []


def catMaybes(list_maybes):
    return [maybe_item for maybe_item in list_maybes if isJust(maybe_item)]


def mapMaybe(fn, list_a):
    maybe_bs = (fn(a) for a in list(a))
    return (fromJust(b) for b in maybe_bs if isJust(b))


