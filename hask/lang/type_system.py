import abc
import types

from hindley_milner import TypeVariable
from hindley_milner import TypeOperator
from hindley_milner import Tuple


#=============================================================================#
# Static typing and type signatures


def HM_typeof(obj):
    """
    Returns the type of an object within the internal type system.
    """
    if hasattr(obj, "type"):
        return obj.type()

    elif isinstance(obj, tuple):
        return Tuple(map(HM_typeof, obj))

    return TypeOperator(type(obj), [])


#=============================================================================#
# Typeclasses

__typeclass_flag__ = "__typeclasses__"

__python_builtins__ = set((
    types.NoneType, types.TypeType, types.BooleanType, types.IntType,
    types.LongType, types.FloatType, types.ComplexType, types.StringType,
    types.UnicodeType, types.TupleType, types.ListType, types.DictType,
    types.DictionaryType, types.FunctionType, types.LambdaType,
    types.GeneratorType, types.CodeType, types.ClassType, types.InstanceType,
    types.MethodType, types.UnboundMethodType, types.BuiltinFunctionType,
    types.BuiltinMethodType, types.ModuleType, types.FileType,
    types.XRangeType, types.EllipsisType, types.TracebackType, types.FrameType,
    types.BufferType, types.DictProxyType, types.NotImplementedType,
    types.GetSetDescriptorType, types.MemberDescriptorType))


def is_builtin(cls):
    """
    Return True if a type is a Python builtin type, and False otherwise.
    """
    return cls in __python_builtins__


def in_typeclass(cls, typeclass):
    """
    Return True if cls is a member of typeclass, and False otherwise.
    """
    if is_builtin(typeclass):
       return False
    elif is_builtin(cls):
        try:
            return issubclass(cls, typeclass)
        except TypeError:
            return False
    elif hasattr(cls, __typeclass_flag__):
        return typeclass in getattr(cls, __typeclass_flag__)
    return False


def nt_to_tuple(nt):
    """
    Convert an instance of namedtuple (or an instance of a subclass of
    namedtuple) to a tuple, even if the instance's __iter__
    method has been changed. Useful for writing derived instances of
    typeclasses.
    """
    return tuple((getattr(nt, f) for f in nt.__class__._fields))



class Typeclass(object):
    """
    Base metaclass for Typeclasses.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls, dependencies=(), attrs=None):
        """
        Create an instance of a typeclass.

        1) Check whether the instance type is a member of parent typeclasses of
           the typeclass being instantiated
        2) Modify the instance type, adding the appropriate attributes
        3) Add a typeclass flag to the instance type, signifying that it is now
           a member of the typeclass
        """
        # 1) Check dependencies
        for dep in dependencies:
            if not in_typeclass(cls, dep):
                msg = "%s is not a member of %s" % (cls.__name__, dep.__name__)
                raise TypeError(msg)

        if is_builtin(cls):
            # 2a) If the class is a builtin, make it a subclass
            self.__class__.register(cls)
        else:
            # 2b) Otherwise, add attributes to the class
            if attrs is not None:
                for attr_name, attr in attrs.iteritems():
                    Typeclass.add_attr(cls, attr_name, attr)

            # 3b) Add flag to the class
            Typeclass.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def derive_instance(cls, type_constructor):
        """
        Derive a typeclass instance for the given type constructor.

        Derivable typeclasses should override this method and provide their own
        implementation. Note that this method should be decorated with
        @staticmethod.
        """
        raise TypeError("Cannot derive instance for class %s" % cls.__name__)

    @staticmethod
    def add_attr(cls, attr_name, attr):
        """
        Modify an existing class, adding an attribute. If the class is a
        Python builtin, do nothing.
        """
        if not is_builtin(cls):
            setattr(cls, attr_name, attr)
        return

    @staticmethod
    def add_typeclass_flag(cls, typeclass):
        """
        Add a typeclass membership flag to a class, signifying that the class
        belongs to the specified typeclass.

        If the class is a Python builtin (and therefore immutable), make it a
        subclass of the specified typeclass.
        """
        if is_builtin(cls):
            typeclass.register(cls)
        elif hasattr(cls, __typeclass_flag__):
            setattr(cls, __typeclass_flag__,
                    getattr(cls, __typeclass_flag__) + (typeclass,))
        else:
            setattr(cls, __typeclass_flag__, (typeclass,))
        return


#=============================================================================#
# ADT creation


#=============================================================================#
# Pattern matching
