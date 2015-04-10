import abc
import types


## Some typeclass utilies

def is_builtin(cls):
    """
    Return True if a type is a Python builtin type, and False otherwise.
    """
    b = (types.NoneType, types.TypeType, types.BooleanType, types.IntType,
         types.LongType, types.FloatType, types.ComplexType,
         types.StringType, types.UnicodeType, types.TupleType,
         types.ListType, types.DictType, types.DictionaryType,
         types.FunctionType, types.LambdaType, types.GeneratorType,
         types.CodeType, types.ClassType, types.InstanceType,
         types.MethodType, types.UnboundMethodType,
         types.BuiltinFunctionType, types.BuiltinMethodType,
         types.ModuleType, types.FileType, types.XRangeType,
         types.EllipsisType, types.TracebackType, types.FrameType,
         types.BufferType, types.DictProxyType, types.NotImplementedType,
         types.GetSetDescriptorType, types.MemberDescriptorType)
    return cls in b


def in_typeclass(cls, typeclass):
    """
    Return True if cls is a member of typeclass, and False otherwise.
    """
    if is_builtin(typeclass):
        # builtins are never typeclasses, even if they are subclasses of
        # Typeclass. This is because builtins inherit typeclasses to signify
        # their membership
        return False
    elif is_builtin(cls):
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
    if is_builtin(cls):
        typeclass.register(cls)
    elif hasattr(cls, "__typeclasses__"):
        cls.__typeclasses__.append(typeclass)
    else:
        cls.__typeclasses__ = [typeclass]
    return cls


## Main Haskell typeclasses

class Typeclass(object):
    __metaclass__ = abc.ABCMeta


class Show(Typeclass):

    def __init__(self, cls, __repr__):
        cls.__repr__ = __repr__
        cls = add_typeclass_flag(cls, self.__class__)
        return


class Eq(Typeclass):

    def __init__(self, cls, __eq__):
        def __ne__(self, other):
            return not self.__eq__(other)

        cls.__eq__ = __eq__
        cls.__ne__ = __ne__
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

