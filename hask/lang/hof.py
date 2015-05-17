import functools

from type_system import arity
from type_system import ArityError
from typeclasses import Functor


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
    # unwrap nested instances of Func
    while isinstance(f, Func):
        f = f.func

    f_arity, arglen = arity(f), len(args)

    # if the function is not actually a callable, and no arguments are given,
    # just return it
    if not hasattr(f, "__call__") and arglen == 0:
        return f

    # if the function takes no arguments and some are given, raise error
    elif f_arity == 0 and arglen > 0:
        raise ArityError("Too many arguments supplied")

    # if the function takes no arguments and none are given, call it
    elif f_arity == arglen == 0:
        return _apply(wrapper, f(), *args, **kwargs)

    # if the number of args given matches the arity, call it with the args
    elif f_arity == arglen:
        return _apply(wrapper, f(*args, **kwargs))

    # if the arity is lower than the number of arguments given,
    # call the function with the correct number of arguments, and try
    # to call the result with the remaining arguments
    elif f_arity < arglen:
        applied = f(*args[:f_arity], **kwargs)
        return _apply(wrapper, applied, *args[f_arity:])

    # if the arity is higher than the number of args given, partially apply
    return wrapper(f, *args, **kwargs)


class Func(object):
    """
    Wrapper around function objects that is always curried.

    `*` is the compose operator
    `%` is the apply operator

    Typeclass instances:
    Functor
    """
    def __init__(self, func=lambda x: x, *a, **kw):
        self.func = _apply(functools.partial, func, *a, **kw) \
                 if a or kw else func

    def __call__(self, *args, **kwargs):
        return _apply(self.__class__, self.func, *args, **kwargs)

    def fmap(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__class__(lambda x: self.func(other.func(x)))

    def __rmul__(self, other):
        # override __rmul__ so that we can say `f * g` and compose correctly
        # even if `f` is not a Func object
        return self.__class__(other).fmap(self)

    def __mod__(self, arg):
        """
        `%` is apply operator, equivalent to `$` in Haskell.
        """
        return self.__call__(arg)


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
