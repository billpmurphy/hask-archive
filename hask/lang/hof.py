import functools


def flip(f):
    """
    flip(f) takes its (first) two arguments in the reverse order of f.
    """
    def _flipped(x1, x2, *args, **kwargs):
        return f(x2, x1, *args, **kwargs)
    return _flipped


def const(a, b):
    return a


class f(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, arg):
        return self.func.__call__(arg)


def _func_fmap(self, other):
    return f(lambda x: other(self.func(x)))


def _identity(a):
    return a


id = f(_identity)


class _lambda(object):
    def __init__(self):
        pass

    def __call__(self, arg):
        return

    def __add__(self, other): return f(lambda x: x + other)
    def __radd__(self, other): return f(lambda x: x + other)

__ = _lambda()
