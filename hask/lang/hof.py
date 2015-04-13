import functools

from ..lang.type_system import arity
from ..lang.typeclasses import Functor


def curry(func):
    """
    Curry decorator from fn.py. Needs some upgrades.
    """
    #@functools.wraps(func) # need to do something about this
    def _curried(*args, **kwargs):
        if arity(func) == len(args):
            return func(*args, **kwargs)
        return curry(functools.partial(func, *args, **kwargs))
    return _curried


class F(object):
    """
    Haskell-ified wrapper around function objects that is always curried, an
    instance of functor, and composable with `*`
    """
    def __init__(self, func=lambda x: x, *a, **kw):
        self.f = functools.partial(func, *a, **kw) if any([a, kw]) else func

    def __call__(self, *args, **kwargs):
        if arity(self.f) == len(args):
            return self.f(*args, **kwargs)
        else:
            return self.__class__(self.f, *args, **kwargs)

    def fmap(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__class__(lambda x, *a, **kw: self.f(other.f(x, *a, **kw)))


Functor(F, F.fmap)


@F
def id(a):
    return a


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
