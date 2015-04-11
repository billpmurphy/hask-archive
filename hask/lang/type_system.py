import abc
import functools
import types


class Typeclass(object):
    __metaclass__ = abc.ABCMeta


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


# static type assertion decorator
def sig(signature):
    @functools.wraps
    def _wrapper(*args, **kwargs):
        pass

    return _wrapper
