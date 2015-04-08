import abc
from types import *

builtins = (NoneType, TypeType, BooleanType, IntType, LongType, FloatType,
            ComplexType, StringType, UnicodeType, TupleType, ListType,
            DictType, DictionaryType, FunctionType, LambdaType, GeneratorType,
            CodeType, ClassType, InstanceType, MethodType, UnboundMethodType,
            BuiltinFunctionType, BuiltinMethodType, ModuleType, FileType,
            XRangeType, EllipsisType, TracebackType, FrameType, BufferType,
            DictProxyType, NotImplementedType, GetSetDescriptorType,
            MemberDescriptorType)


def is_typeclass_member(cls, typeclass):
    """
    Return true if cls is a mmeber of typeclass_name, and False otherwise.
    """
    if cls in builtins:
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


class Show(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls):
        if not hasattr(cls, "__repr__"):
            raise TypeError("Class must implement `__repr__`")

        cls = add_typeclass_flag(cls, self.__class__)
        return


class Num(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls):
        # todo: add checks for magic methods an object should have to be
        # considered an instance of num
        cls = add_typeclass_flag(cls, self.__class__)
        pass



class Functor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls):
        """
        Transform a class into a member of Functor. The class must implement
        __fmap__() as appropriate.
        """
        if not hasattr(cls, "__fmap__"):
            raise TypeError("Class must implement `__fmap__`")

        # wrapper around fmap
        def fmap(self, fn):
            # later, will do some typechecking here
            return self.__fmap__(fn)

        # `*` syntax for fmap
        def mul(self, fn):
            return self.fmap(fn)

        cls = add_typeclass_flag(cls, self.__class__)
        cls.fmap = fmap
        cls.__mul__ = mul
        return


class Applicative(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls):
        """
        Transform a class into a member of Applicative. The class must implement
        __pure__() as appropriate, and must be a member of Functor.
        """
        if not is_typeclass_member(cls, Functor):
            raise TypeError("Class must be a member of Functor")

        if not hasattr(cls, "__pure__"):
            raise TypeError("Class must implement `__pure__`")

        def pure(self, value):
            # later, will do some typechecking here
            return self.__pure__(value)

        cls = add_typeclass_flag(cls, self.__class__)
        cls.pure = pure
        return


class Monad(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls):
        """
        Transform a class into a member of Monad. The class must implement
        __bind__() as appropriate, and must be a member of Applicative.
        """
        if not is_typeclass_member(cls, Applicative):
            raise TypeError("Class must be a member of Applicative")

        if not hasattr(cls, "__bind__"):
            raise TypeError("Class must implement `__bind__`")

        # wrapper around monadic bind
        def bind(self, fn):
            # later, will do some typechecking here
            return self.__bind__(fn)

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

    def __fmap__(self, fn):
        return Nothing if self._is_nothing else Just(fn(self._value))

    def __pure__(self, value):
        return Just(value)

    def __bind__(self, fn):
        return Nothing if self._is_nothing else fn(self._value)

    def __eq__(self, other):
        if self._is_nothing and other._is_nothing:
            return True
        elif not self._is_nothing and not other._is_nothing:
            return self._value == other._value
        else:
            return False

    def __type__(self):
        return (Maybe, type(self._value))

    def __repr__(self):
        if self._is_nothing:
            return "Nothing"
        else:
            return "Just(%s)" % self._value

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


# todo: @maybe decorator: Your function will act as if it is always inside
# in_maybe


class Either(object):
    def __init__(self, value):
        self._value = value

    def __fmap__(self, fn):
        return self if self._is_left else Right(fn(self._value))

    def __pure__(self, value):
        return Right(value)

    def __bind__(self, fn):
        return self if self._is_left else fn(self._value)

    def __eq__(self, other):
        if self._is_left == other._is_left:
            return self._value == other._value
        return False

    def __repr__(self):
        if self._is_left:
            return "Left(%s)" % self._value
        return "Right(%s)" % self._value


class Left(Either):
    def __init__(self, value, is_left=True):
        super(self.__class__, self).__init__(value)
        self._is_left = True


class Right(Either):
    def __init__(self, value, is_left=False):
        super(self.__class__, self).__init__(value)
        self._is_left = False


def in_either(fn, *args, **kwargs):
    def _closure_in_either(*args, **kwargs):
        try:
            return Right(fn(*args, **kwargs))
        except Exception as e:
            return Left(e)
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_either(*args, **kwargs)
    return _closure_in_either


# todo: @either decorator: Your function will act as if it is always inside
# in_either


# Typeclass instances

Show.register(int)
Show.register(float)
Show.register(complex)
Show(Maybe)
Show(Either)

Num.register(int)
Num.register(float)
Num.register(complex)

Functor(Maybe)
Functor(Either)

Applicative(Maybe)
Applicative(Either)

Monad(Maybe)
Monad(Either)
