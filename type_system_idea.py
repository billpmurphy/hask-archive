from hask import in_typeclass
from hask import F


class TypeArg(object):

    def __init__(self, typ=None, constraints=None):
        if typ is not None:
            self.unify(typ)
        elif constraints is not None:
            self.fn = lambda x: all([in_typeclass(type(x), c)
                                     for c in constraints])
        return

    def __unify__(self, newtype):
        self.fn = lambda x: isinstance(x, newtype)
        return

    def check(self, arg):
        if self.fn(arg):
            self.unify(type(arg))
            return
        raise TypeError("%s does not match" % arg)


class TypedFunc(object):

    def __init__(self, typeargs, func):
        self.func = F(func)
        varargs = {t:TypeArg() for t in set((t for t in typeargs if type(t) is str))}

        self.typeargs = [TypeArg(x) if type(x) is not str else varargs[x]
                         for x in typeargs]

        return

    def __call__(self, *args, **kwargs):
        for t, a in zip(self.typeargs, args):
            t.check(a)
        return self.func(*args, **kwargs)


f = lambda x, y
