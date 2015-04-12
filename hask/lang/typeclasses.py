import type_system


class Show(type_system.Typeclass):

    def __init__(self, cls, __repr__):
        type_system.add_attr(cls, "__repr__", __repr__)
        type_system.add_typeclass_flag(cls, self.__class__)
        return


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
    def __init__(self, cls, __cmp__):
        if not type_system.in_typeclass(cls, Eq):
            raise TypeError("Class must be a member of Eq")

        type_system.add_attr(cls, "__cmp__", __eq__)
        type_system.add_typeclass_flag(cls, self.__class__)
        return


class Enum(type_system.Typeclass):
    pass


class Bounded(type_system.Typeclass):
    def __init__(self, cls, minBound, maxBound):
        type_system.add_attr(cls, "minBound", minBound)
        type_system.add_attr(cls, "maxBound", maxBound)
        type_system.add_typeclass_flag(cls, self.__class__)
        return


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

        type_system.add_attr(cls, "pure", _pure)
        type_system.add_typeclass_flag(cls, self.__class__)
        return


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


class Foldable(type_system.Typeclass):
    def __init__(self, cls, _foldr):
        type_system.add_typeclass_flag(cls, self.__class__)
        return


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
