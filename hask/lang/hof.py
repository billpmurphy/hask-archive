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
        if isinstance(func, self.__class__):
            func = func.f
        self.f = functools.partial(func, *a, **kw) if any([a, kw]) else func

    def __call__(self, *args, **kwargs):
        f_arity, arglen = arity(self.f), len(args)
        if f_arity == arglen:
            return self.f(*args, **kwargs)
        elif f_arity < arglen:
            app = self.f(*args[:f_arity], **kwargs)
            if arity(app) == 0:
                return TypeError("Number of arguments ({a}) > arity ({f})"
                                 .format(f=f_arity, a=arglen))
            elif arity(app) == len(args[f_arity:]):
                return app(*args[f_arity:])
            else:
                return self.__class__(app, *args[f_arity:])
        else:
            return self.__class__(self.f, *args, **kwargs)

    def fmap(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__class__(lambda x, *a, **kw: self.f(other.f(x, *a, **kw)))

    def __mod__(self, *args):
        """
        `%` is apply operator, equivalent to `$` in Haskell.
        """
        return self.f(*args)


Functor(F, F.fmap)


@F
def id(a):
    return a


@F
def flip(f, x1, x2):
    """
    flip(f) takes its (first) two arguments in the reverse order of f.
    """
    return F(f)(x2, x1)


@F
def const(a, b):
    return a
