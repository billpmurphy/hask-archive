import functools

from ..lang.type_system import arity
from ..lang.typeclasses import Functor


def _apply(wrapper, f, *args, **kwargs):
    f_arity, arglen = arity(f), len(args)
    #print f, type(f), "arglen: %s, arity: %s" % (arglen, f_arity)
    if f_arity == arglen:
        result = f(*args, **kwargs)
        return wrapper(result) if hasattr(result, "__call__") else result
    elif f_arity == 0:
        raise TypeError("Too many arguments")
    elif f_arity < arglen:
        return _apply(wrapper, f(*args[:f_arity], **kwargs), *args[f_arity:])
    return wrapper(f, *args, **kwargs)


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


def F(func, *args, **kwargs):
    if isinstance(func, Func):
        func = func.f
    return _apply(Func, func, *args, **kwargs)


class Func(object):
    """
    Haskell-ified wrapper around function objects that is always curried, an
    instance of functor, and composable with `*`
    """
    def __init__(self, func=lambda x: x, *a, **kw):
        if isinstance(func, self.__class__):
            func = func.f
        self.f = _apply(functools.partial, func, *a, **kw) \
                 if a or kw else func

    def __call__(self, *args, **kwargs):
        return _apply(self.__class__, self.f, *args, **kwargs)

    def fmap(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__class__(lambda x, *a, **kw: self.f(other.f(x, *a, **kw)))

    def __mod__(self, *args):
        """
        `%` is apply operator, equivalent to `$` in Haskell.
        """
        return self.f(*args)


Functor(Func, Func.fmap)

id = Func()


@F
def flip(f, x, y, *a):
    return f(y, x, *a)

@F
def const(a, b):
    return a
