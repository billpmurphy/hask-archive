import type_system


## Main Haskell typeclasses


class Show(type_system.Typeclass):

    def __init__(self, cls, __repr__):
        cls.__repr__ = __repr__
        cls = type_system.add_typeclass_flag(cls, self.__class__)
        return


class Eq(type_system.Typeclass):

    def __init__(self, cls, __eq__):
        def __ne__(self, other):
            return not self.__eq__(other)

        cls.__eq__ = __eq__
        cls.__ne__ = __ne__
        cls = type_system.add_typeclass_flag(cls, self.__class__)
        return


class Num(type_system.Typeclass):

    def __init__(self, cls):
        # todo: add checks for magic methods an object should have to be
        # considered an instance of num
        if not type_system.in_typeclass(cls, Show):
            raise TypeError("Class must be a member of Show")

        if not type_system.in_typeclass(cls, Eq):
            raise TypeError("Class must be a member of Eq")

        cls = type_system.add_typeclass_flag(cls, self.__class__)
        return


class Functor(type_system.Typeclass):

    def __init__(self, cls, __fmap__):
        """
        Transform a class into a member of Functor. The fmap function must be
        supplied when making the class a member of Functor.
        """
        # wrapper around fmap
        def fmap(self, fn):
            # later, will do some typechecking here
            return __fmap__(self, fn)

        # `*` syntax for fmap
        def mul(self, fn):
            return self.fmap(fn)

        cls.fmap = fmap
        cls.__mul__ = mul
        cls = type_system.add_typeclass_flag(cls, self.__class__)
        return


class Applicative(type_system.Typeclass):

    def __init__(self, cls, __pure__):
        """
        Transform a class into a member of Applicative. The pure function must be
        supplied when making the class a member of Applicative.
        """
        if not type_system.in_typeclass(cls, Functor):
            raise TypeError("Class must be a member of Functor")

        def pure(self, value):
            # later, will do some typechecking here
            return __pure__(self, value)

        cls = type_system.add_typeclass_flag(cls, self.__class__)
        cls.pure = pure
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
        def bind(self, fn):
            # later, will do some typechecking here
            return __bind__(self, fn)

        # `>>` syntax for monadic bind
        def rshift(self, fn):
            return self.bind(fn)

        cls = type_system.add_typeclass_flag(cls, self.__class__)
        cls.bind = bind
        cls.__rshift__ = rshift
        return
