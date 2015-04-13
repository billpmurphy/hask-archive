import functools
import inspect

from ..lang.typeclasses import Functor


def curry(func):
    """
    Curry decorator from fn.py. Needs some upgrades.
    """
    #@wraps(func) # need to do something about this
    def _curried(*args, **kwargs):
        f = func
        count = 0
        while isinstance(f, functools.partial):
            if f.args:
                count += len(f.args)
            f = f.func
        spec = inspect.getargspec(f)
        if count == len(spec.args) - len(args):
            return func(*args, **kwargs)
        return curry(functools.partial(func, *args, **kwargs))
    return _curried


class F(object):
    """
    Haskell-ified wrapper around function objects that is always curried, an
    instance of functor, and composable with `*`
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func.__call__(*args, **kwargs)

    def fmap(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        def _composed(*args, **kwargs):
            return other.func(self.func(*args, **kwargs))

        return self.__class__(_composed)


Functor(F, F.fmap)


@F
def flip(f):
    """
    flip(f) takes its (first) two arguments in the reverse order of f.
    """
    def _flipped(x1, x2, *args, **kwargs):
        return f(x2, x1, *args, **kwargs)
    return _flipped


@F
def const(a, b):
    return a

@F
def id(a):
    return a
