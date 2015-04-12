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
    instance of functor, and composable with `.`
    """
    def __init__(self, func, *args, **kwargs):
        self.func = curry(func)(*args, **kwargs)

    def __ensure_callable(self, f):
        return self.__class__(*f) if isinstance(f, tuple) else f

    def __call__(self, *args, **kwargs):
        return self.func.__call__(*args, **kwargs)

    def __getattr__(self, other):
        return _func_fmap(self, other)


def _func_fmap(self, other):
    if type(other) != _f:
        other = _f(other)

    def _apply(*args, **kwargs):
        return other(self(*args, **kwargs))

    return self.__class__(_apply)


Functor(F, _func_fmap)

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
