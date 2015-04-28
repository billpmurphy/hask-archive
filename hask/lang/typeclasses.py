import type_system
from type_system import Typeable


class Read(type_system.Typeclass):

    def __init__(self, cls, read=None):
        if read is None:
            read = lambda string: eval(string)
        type_system.add_attr(cls, "read", classmethod(read))
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def read(string, _return):
        if _return is not None:
            return _return.__class_.read(string)
        else:
            return eval(string)


class Show(type_system.Typeclass):

    def __init__(self, cls, __repr__):
        type_system.add_attr(cls, "__repr__", __repr__)
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def show(a):
        return str(a)


class Eq(type_system.Typeclass):
    """
    The Eq class defines equality (==) and inequality (!=). Minimal complete
    definition: __eq__
    """

    def __init__(self, cls, __eq__):
        def __ne__(self, other):
            return not self.__eq__(other)

        type_system.add_attr(cls, "__eq__", __eq__)
        type_system.add_attr(cls, "__ne__", __ne__)
        type_system.add_typeclass_flag(cls, self.__class__)
        return


class Ord(type_system.Typeclass):
    def __init__(self, cls, __lt__):
        if not type_system.in_typeclass(cls, Eq):
            raise TypeError("Class must be a member of Eq")

        __le__ = lambda s, o: s.__lt__(o) or s.__eq__(o)
        __gt__ = lambda s, o: not s.__lt__(o) and not s.__eq__(o)
        __ge__ = lambda s, o: not s.__lt__(o) or not s.__eq__(o)

        type_system.add_attr(cls, "__lt__", __lt__)
        type_system.add_attr(cls, "__le__", __le__)
        type_system.add_attr(cls, "__gt__", __gt__)
        type_system.add_attr(cls, "__ge__", __ge__)
        type_system.add_typeclass_flag(cls, self.__class__)
        return


class Bounded(type_system.Typeclass):
    def __init__(self, cls, minBound, maxBound):
        type_system.add_attr(cls, "minBound", minBound)
        type_system.add_attr(cls, "maxBound", maxBound)
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def maxBound(a):
        # handle builtins
        if type_system.is_builtin(type(a)):
            return NotImplemented
        return a.maxBound()

    @staticmethod
    def minBound(a):
        # handle builtins
        if type_system.is_builtin(type(a)):
            return NotImplemented
        return a.minBound()


class Num(type_system.Typeclass):

    def __init__(self, cls):
        # todo: add checks for magic methods an object should have to be
        # considered an instance of num
        if not type_system.in_typeclass(cls, Show):
            raise TypeError("Class must be a member of Show")

        if not type_system.in_typeclass(cls, Eq):
            raise TypeError("Class must be a member of Eq")

        type_system.add_typeclass_flag(cls, self.__class__)
        return


class RealFloat(type_system.Typeclass):

    def __init__(self, cls):
        if not type_system.in_typeclass(cls, Num):
            raise TypeError("Class must be a member of Num")

        type_system.add_typeclass_flag(cls, self.__class__)
        return


class Enum(type_system.Typeclass):
    def __init__(self, cls, toEnum, fromEnum):
        type_system.add_attr(cls, "toEnum", toEnum)
        type_system.add_attr(cls, "fromEnum", fromEnum)
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def toEnum(a):
        # handle builtins
        if type_system.is_builtin(type(a)):
            if type_system.in_typeclass(type(a), Num):
                return a
            elif type(a) == str:
                return ord(a)

        # handle everything else
        return a.toEnum()

    @staticmethod
    def fromEnum(a, _return=None):
        # handle builtins
        if type_system.is_builtin(type(a)):
            if type_system.in_typeclass(_return, Num):
                return a
            elif _return == str:
                return chr(a)

        # handle everything else
        elif _return is not None:
            return _return.from_Enum(a)
        return a.fromEnum()

    @staticmethod
    def succ(a):
        return Enum.fromEnum(Enum.toEnum(a) + 1, type(a))

    @staticmethod
    def pred(a):
        return Enum.fromEnum(Enum.toEnum(a) - 1, type(a))

    @staticmethod
    def enumFromThen(start, second):
        pointer = Enum.toEnum(start)
        step = Enum.toEnum(second) - pointer
        while True:
            yield Enum.fromEnum(pointer, type(start))
            pointer += step
        return

    @staticmethod
    def enumFrom(start):
        return Enum.enumFromThen(start, Enum.succ(start))

    @staticmethod
    def enumFromThenTo(start, second, end):
        pointer, stop = Enum.toEnum(start), Enum.toEnum(end)
        step = Enum.toEnum(second) - pointer
        while pointer <= stop:
            yield Enum.fromEnum(pointer, type(start))
            pointer += step
        return

    @staticmethod
    def enumFromTo(start, end):
        return Enum.enumFromThenTo(start, Enum.succ(start), end)


class Functor(type_system.Typeclass):

    def __init__(self, cls, __fmap__):
        """
        Transform a class into a member of Functor. The fmap function must be
        supplied when making the class a member of Functor.
        """
        # wrapper around fmap
        def _fmap(self, fn):
            # later, will do some typechecking here
            return __fmap__(self, fn)

        # `*` syntax for fmap
        def _mul(self, fn):
            return self.fmap(fn)

        type_system.add_attr(cls, "fmap", _fmap)
        type_system.add_attr(cls, "__mul__", _mul)
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def fmap(fn, functor):
        return functor.fmap(fn)


class Applicative(type_system.Typeclass):

    def __init__(self, cls, __pure__):
        """
        Transform a class into a member of Applicative. The pure function must be
        supplied when making the class a member of Applicative.
        """
        if not type_system.in_typeclass(cls, Functor):
            raise TypeError("Class must be a member of Functor")

        def _pure(self, value):
            # later, will do some typechecking here
            return __pure__(self, value)

        type_system.add_attr(cls, "pure", classmethod(_pure))
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def pure(value, app):
        return app.__class__.pure(value)


class Monad(type_system.Typeclass):

    def __init__(self, cls, __bind__):
        """
        Transform a class into a member of Monad. The bind function must be
        supplied when making the class a member of Monad.
        """
        if not type_system.in_typeclass(cls, Applicative):
            raise TypeError("Class must be a member of Applicative")

        # wrapper around monadic bind
        def _bind(self, fn):
            # later, will do some typechecking here
            return __bind__(self, fn)

        # `>>` syntax for monadic bind
        def _rshift(self, fn):
            return self.bind(fn)

        type_system.add_attr(cls, "bind", _bind)
        type_system.add_attr(cls, "__rshift__", _rshift)
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def bind(m, fn):
        return m.bind(fn)


class Foldable(type_system.Typeclass):
    def __init__(self, cls, _foldr):
        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def foldr(fn, a, lb):
        return lb.foldr(fn, a)


class Traversable(type_system.Typeclass):

    def __init__(self, cls, __iter__):
        if not type_system.in_typeclass(cls, Foldable):
            raise TypeError("Class must be a member of Foldable")

        if not type_system.in_typeclass(cls, Functor):
            raise TypeError("Class must be a member of Functor")

        def _iter(self):
            return __iter__(self)

        type_system.add_attr(cls, "__iter__", _iter)
        type_system.add_typeclass_flag(cls, self.__class__)
        return


class Ix(type_system.Typeclass):

    def __init__(self, cls, __getitem__, __len__=None):
        if not type_system.in_typeclass(cls, Traversable):
            raise TypeError("Class must be a member of Traversable")

        def _getitem(self, i):
            return __getitem__(self, i)

        type_system.add_attr(cls, "__getitem__", _getitem)

        if __len__ is None:
            def _default_len(self):
                """
                Default length function: Iterate through elements and count
                them up.
                """
                count = 0
                for _ in iter(self):
                    count += 1
                return count
            type_system.add_attr(cls, "__len__", _default_len)
        else:
            type_system.add_attr(cls, "__len__", __len__)

        type_system.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def length(a):
        return a.__len__()


class Iterator(type_system.Typeclass):
    def __init__(self, cls, __next__):
        if not type_system.in_typeclass(cls, Traversable):
            raise TypeError("Class must be a member of Traversable")

        def _next(self):
            return __next__(self)

        type_system.add_attr(cls, "__next__", _next)
        type_system.add_attr(cls, "next", _next)
        type_system.add_typeclass_flag(cls, self.__class__)
        return
