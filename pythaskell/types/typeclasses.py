import abc
from types import *


## Some typeclass utilies

builtins = (NoneType, TypeType, BooleanType, IntType, LongType, FloatType,
            ComplexType, StringType, UnicodeType, TupleType, ListType,
            DictType, DictionaryType, FunctionType, LambdaType, GeneratorType,
            CodeType, ClassType, InstanceType, MethodType, UnboundMethodType,
            BuiltinFunctionType, BuiltinMethodType, ModuleType, FileType,
            XRangeType, EllipsisType, TracebackType, FrameType, BufferType,
            DictProxyType, NotImplementedType, GetSetDescriptorType,
            MemberDescriptorType)


def in_typeclass(cls, typeclass):
    """
    Return True if cls is a member of typeclass, and False otherwise.
    """
    if typeclass in builtins:
        return False
    elif cls in builtins:
        try:
            return issubclass(cls, typeclass)
        except TypeError:
            return False
    elif hasattr(cls, "__typeclasses__"):
        return typeclass in cls.__typeclasses__
    return False


def add_typeclass_flag(cls, typeclass):
    """
    Add a typeclass membership flag to a class, signifying that the class
    belongs to the specified typeclass.
    """
    if hasattr(cls, "__typeclasses__"):
        cls.__typeclasses__.append(typeclass)
    else:
        cls.__typeclasses__ = [typeclass]
    return cls


## Main Haskell typeclasses

class Typeclass(object):
    __metaclass__ = abc.ABCMeta


class Show(Typeclass):

    def __init__(self, cls, __repr__):
        def _repr(self):
            return __repr__(self)

        cls.__repr__ = _repr
        cls.show = _repr
        cls = add_typeclass_flag(cls, self.__class__)
        return


class Eq(Typeclass):

    def __init__(self, cls, __eq__):
        def _eq(self, other):
            return __eq__(self, other)

        cls.__eq__ = _eq
        cls = add_typeclass_flag(cls, self.__class__)
        return


class Num(Typeclass):

    def __init__(self, cls):
        # todo: add checks for magic methods an object should have to be
        # considered an instance of num
        cls = add_typeclass_flag(cls, self.__class__)
        return


class Functor(Typeclass):

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

        cls = add_typeclass_flag(cls, self.__class__)
        cls.fmap = fmap
        cls.__mul__ = mul
        return


class Applicative(Typeclass):

    def __init__(self, cls, __pure__):
        """
        Transform a class into a member of Applicative. The pure function must be
        supplied when making the class a member of Applicative.
        """
        if not in_typeclass(cls, Functor):
            raise TypeError("Class must be a member of Functor")

        def pure(self, value):
            # later, will do some typechecking here
            return __pure__(self, value)

        cls = add_typeclass_flag(cls, self.__class__)
        cls.pure = pure
        return


class Monad(Typeclass):

    def __init__(self, cls, __bind__):
        """
        Transform a class into a member of Monad. The bind function must be
        supplied when making the class a member of Monad.
        """
        if not in_typeclass(cls, Applicative):
            raise TypeError("Class must be a member of Applicative")

        # wrapper around monadic bind
        def bind(self, fn):
            # later, will do some typechecking here
            return __bind__(self, fn)

        # `>>` syntax for monadic bind
        def rshift(self, fn):
            return self.bind(fn)

        cls = add_typeclass_flag(cls, self.__class__)
        cls.bind = bind
        cls.__rshift__ = rshift
        return


## Maybe monad

class Maybe(object):

    def __init__(self, value):
        self._is_nothing = False
        self._value = value

    @staticmethod
    def _make_nothing():
        """
        Build the standard Nothing value.
        """
        nothing = Just(None)
        nothing._is_nothing = True
        return nothing


class Just(Maybe):
    def __init__(self, value):
        super(self.__class__, self).__init__(value)
        self._is_nothing = False


Nothing = Maybe._make_nothing()


class Either(object):
    def __init__(self, value):
        self._value = value


class Left(Either):
    def __init__(self, value, is_left=True):
        super(self.__class__, self).__init__(value)
        self._is_left = True


class Right(Either):
    def __init__(self, value, is_left=False):
        super(self.__class__, self).__init__(value)
        self._is_left = False


# Builtin type typeclass instances

Show.register(int)
Show.register(float)
Show.register(complex)

Num.register(int)
Num.register(float)
Num.register(complex)


## Maybe instances

def _maybe_eq(self, other):
    if self._is_nothing and other._is_nothing:
        return True
    elif not self._is_nothing and not other._is_nothing:
        return self._value == other._value
    else:
        return False

def _maybe_repr(self):
    if self._is_nothing:
        return "Nothing"
    return "Just(%s)" % self._value


def _maybe_fmap(self, fn):
    return Nothing if self._is_nothing else Just(fn(self._value))


def _maybe_pure(self, value):
    return Just(value)


def _maybe_bind(self, fn):
    return Nothing if self._is_nothing else fn(self._value)


Show(Maybe, _maybe_repr)
Eq(Maybe, _maybe_eq)
Functor(Maybe, _maybe_fmap)
Applicative(Maybe, _maybe_pure)
Monad(Maybe, _maybe_bind)


## Either instances

def _either_eq(self, other):
    if self._is_left == other._is_left:
        return self._value == other._value
    return False


def _either_repr(self):
    if self._is_left:
        return "Left(%s)" % self._value
    return "Right(%s)" % self._value


def _either_fmap(self, fn):
    return self if self._is_left else Right(fn(self._value))


def _either_pure(self, value):
    return Right(value)


def _either_bind(self, fn):
    return self if self._is_left else fn(self._value)


Show(Either, _either_repr)
Eq(Either, _either_eq)
Functor(Either, _either_fmap)
Applicative(Either, _either_pure)
Monad(Either, _either_bind)


## Decorators - need a clever way of making these into a typeclass or something

def in_maybe(fn, *args, **kwargs):
    """
    Apply arguments to a function. If the function call raises an exception,
    return Nothing. Otherwise, take the result and wrap it in a Just.
    """
    def _closure_in_maybe(*args, **kwargs):
        try:
            return Just(fn(*args, **kwargs))
        except:
            return Nothing
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_maybe(*args, **kwargs)
    return _closure_in_maybe


def in_either(fn, *args, **kwargs):
    """
    Apply arguments to a function. If the function call raises an exception,
    return the exception inside Left. Otherwise, take the result and wrap it in
    a Right.
    """
    def _closure_in_either(*args, **kwargs):
        try:
            return Right(fn(*args, **kwargs))
        except Exception as e:
            return Left(e)
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_either(*args, **kwargs)
    return _closure_in_either
