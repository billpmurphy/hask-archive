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
    def __init__(self, func=None):
        self.func = func

    def __call__(self, arg):
        if self.func is not None:
            return self.func(arg)
        else:
            return arg

    def __mul__(self, other):
        if self.func is not None:
            return f(lambda x: other(self.func(x)))
        else:
            return f(lambda x: other(x))


id = f()


class _lambda(object):
    def __init__(self):
        pass

    def __call__(self, arg):
        return

    def __add__(self, other): return f(lambda x: x + other)
    def __radd__(self, other): return f(lambda x: x + other)

__ = _lambda()
