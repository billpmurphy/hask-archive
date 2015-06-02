import abc
import types
from collections import namedtuple

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


class ADT(object):
    """Base class for Hask algebraic data types."""
    pass


def make_type_const(name, typeargs):
    """
    Build a new type constructor given a name and the type parameters.

    Args:
        name: the name of the new type constructor to be created
        typeargs: the type parameters to the constructor

    Returns:
        A new class that acts as a type constructor
    """
    def raise_fn(err):
        raise err()

    default_attrs = {"__params__":tuple(typeargs), "__constructors__":(),
             __typeclass_flag__:()}
    cls = type(name, (ADT,), default_attrs)

    # TODO
    cls.type = lambda self: self.typeargs

    cls.__iter__ = lambda self: raise_fn(TypeError)
    cls.__contains__ = lambda self, other: raise_fn(TypeError)
    cls.__add__ = lambda self, other: raise_fn(TypeError)
    cls.__rmul__ = lambda self, other: raise_fn(TypeError)
    cls.__mul__ = lambda self, other: raise_fn(TypeError)
    cls.__lt__ = lambda self, other: raise_fn(TypeError)
    cls.__gt__ = lambda self, other: raise_fn(TypeError)
    cls.__le__ = lambda self, other: raise_fn(TypeError)
    cls.__ge__ = lambda self, other: raise_fn(TypeError)
    cls.__eq__ = lambda self, other: raise_fn(TypeError)
    cls.__ne__ = lambda self, other: raise_fn(TypeError)
    cls.__repr__ = object.__repr__
    cls.__str__ = object.__str__
    return cls


def make_data_const(name, fields, type_constructor):
    """
    Build a data constructor given the name, the list of field types, and the
    corresponding type constructor.

    The general approach is to create a subclass of the type constructor and a
    new class created with `namedtuple`, with some of the features from
    `namedtuple` such as equality and comparison operators stripped out.
    """
    base = namedtuple(name, ["i%s" % i for i, _ in enumerate(fields)])

    # create the data constructor
    cls = type(name, (type_constructor, base), {})

    # TODO: make sure __init__ or __new__ is typechecked

    # If the data constructor takes no arguments, create an instance of the
    # data constructor class and return that instance rather than returning the
    # class
    if len(fields) == 0:
        cls = cls()

    type_constructor.__constructors__ += (cls,)
    return cls


def build_ADT(typename, type_args, data_constructors, to_derive):
    # create the new type constructor and data constructors
    newtype = make_type_const(typename, type_args)
    dcons = [make_data_const(d[0], d[1], newtype) for d in data_constructors]

    # derive typeclass instances for the new type constructors
    for tclass in to_derive:
        tclass.derive_instance(newtype)

    # return everything
    return tuple([newtype,] + dcons)


#=============================================================================#
# Pattern matching
