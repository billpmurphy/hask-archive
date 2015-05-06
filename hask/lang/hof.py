import functools

from .type_system import arity
from .type_system import ArityError
from .typeclasses import Functor


def _apply(wrapper, f, *args, **kwargs):
    """
    Apply a callable `f` to a set of arguments. If the result is a callable,
    wrap it in `wrapper`. Otherwise, return the result.
    If not enough arguments are supplied, partially apply the given arguments
    and wrap the resulting curried function in `wrapper`.
    If too many arguments are supplied, apply the correct number, and if the
    result is a callable, continue to apply the rest of the arguments
    (recursively).
    """
    if not hasattr(f, "__call__") and (args or kwargs):
        raise ArityError("Too many arguments supplied")
    elif not hasattr(f, "__call__"):
        return f

    while isinstance(f, Func):
        f = f.func

    f_arity, arglen = arity(f), len(args)

    if f_arity == arglen == 0:
        return _apply(wrapper, f(), *args, **kwargs)
    elif f_arity == arglen:
        result = f(*args, **kwargs)
        return wrapper(result) if hasattr(result, "__call__") else result
    elif f_arity == 0:
        raise ArityError("Too many arguments supplied")
    elif f_arity < arglen:
        applied = f(*args[:f_arity], **kwargs)
        return _apply(wrapper, applied, *args[f_arity:])
    return wrapper(f, *args, **kwargs)


class Func(object):
    """
    Haskell-ified wrapper around function objects that is always curried, an
    instance of functor, and composable with `*`
    """
    def __init__(self, func=lambda x: x, *a, **kw):
        self.func = _apply(functools.partial, func, *a, **kw) \
                 if a or kw else func

    def __call__(self, *args, **kwargs):
        return _apply(self.__class__, self.func, *args, **kwargs)

    def fmap(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__class__(lambda x, *a, **kw: \
                              self.func(other.func(x, *a, **kw)))

    def __rmul__(self, other):
        # override __rmul__ so that we can say `f * g` and compose correctly
        # even if `f` is not a Func object
        return F(other).fmap(self)

    def __mod__(self, *args):
        """
        `%` is apply operator, equivalent to `$` in Haskell.
        """
        return self.func(*args)


def F(fn=Func(), *args, **kwargs):
    return _apply(Func, fn, *args, **kwargs)


Functor(Func, Func.fmap)
id = Func()


@F
def flip(f, x, y, *a):
    return F(f)(y, x, *a)

@F
def const(a, b):
    return a
