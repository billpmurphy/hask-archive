import abc
import types
from collections import namedtuple

import hof
from hindley_milner import TypeVariable
from hindley_milner import TypeOperator
from hindley_milner import Var
from hindley_milner import App
from hindley_milner import unify
from hindley_milner import analyze
from hindley_milner import Function
from hindley_milner import Tuple
from hindley_milner import ListType


#=============================================================================#
# Static typing and type signatures


def HM_typeof(obj):
    """
    Returns the type of an object within the internal type system.

    Args:
        obj: the object to inspect

    Returns:
        An obj
    """
    if hasattr(obj, "type"):
        return obj.type()

    elif isinstance(obj, tuple):
        return Tuple(map(HM_typeof, obj))

    elif obj is None:
        return TypeOperator(None, [])

    return TypeOperator(type(obj), [])


class TypeSignatureHKT(object):

    def __init__(self, tcon, params):
        self.tcon = tcon
        self.params = params


class TypeSignature(object):

    def __init__(self, args, constraints):
        self.args = args
        self.constraints = constraints


class TypeSignatureError(Exception):
    pass


def build_sig_arg(arg, var_dict):
    if isinstance(arg, TypeVariable) or isinstance(arg, TypeOperator):
        return arg

    # string representing type variable
    elif isinstance(arg, str):
        if arg not in var_dict:
            var_dict[arg] = TypeVariable()
        return var_dict[arg]

    # subsignature, e.g. H/ (H/ int >> int) >> int >> int
    elif isinstance(arg, TypeSignature):
        return build_sig(arg.args, var_dict)

    # HKT, e.g. t(Maybe "a") or t("m", "a", "b")
    elif isinstance(arg, TypeSignatureHKT):
        if type(arg.tcon) == str:
            hkt = build_sig_arg(arg.tcon, var_dict)
        else:
            hkt = arg.tcon
        return TypeOperator(hkt,
                            [build_sig_arg(a, var_dict) for a in arg.params])

    # None: The unit type
    elif arg is None:
        return TypeOperator(None, [])

    # Tuples: ("a", "b"), (int, ("a", float)), etc.
    elif isinstance(arg, tuple):
        return Tuple(map(lambda x: build_sig_arg(x, var_dict), arg))

    # Lists: ["a"], [int], etc.
    elif isinstance(arg, list) and len(arg) == 1:
        return TypeOperator(ListType, [build_sig_arg(arg[0], var_dict)])

    # any other type
    elif isinstance(arg, type):
        return TypeOperator(arg, [])

    raise TypeSignatureError("Invalid item in type signature: %s" % arg)


def make_fn_type(params):
    """
    Turn a list of type parameters into the corresponding internal type system
    object that represents the type of a function over the parameters.

    Args:
        params: a list of type paramaters, e.g. from a type signature. These
                should be instances of TypeOperator or TypeVariable

    Returns:
        An instance of TypeOperator representing the function type
    """
    if len(params) == 2:
        last_input, return_type = params
        return Function(last_input, return_type)
    return Function(params[0], make_fn_type(params[1:]))


def build_sig(args, var_dict=None):
    """
    Parse a list of items (representing a type signature) and convert it to the
    internal type system language.
    """
    var_dict = {} if var_dict is None else var_dict
    return make_fn_type([build_sig_arg(i, var_dict) for i in args])


class TypedFunc(object):

    def __init__(self, fn, fn_type):
        self.__doc__ = fn.__doc__
        self.func = fn
        self.fn_type = fn_type
        return

    def type(self):
        return self.fn_type

    def __call__(self, *args, **kwargs):
        # the evironment contains the type of the function and the types
        # of the arguments
        env = {id(self.func):self.fn_type}
        env.update({id(arg):HM_typeof(arg) for arg in args})

        ap = Var(id(self.func))
        for arg in args:
            ap = App(ap, Var(id(arg)))

        result_type = analyze(ap, env)
        result = self.func.__call__(*args, **kwargs)
        unify(result_type, HM_typeof(result))

        if hof.F(result) is result:
            return result
        return hof.F(result)


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

    Args:
        nt: an instance of namedtuple

    Returns:
        A tuple containing each of the items in nt
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
            # 2a) If the class is a builtin make it a subclass of the typeclass
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

    cls.type = lambda self: TypeOperator(cls,
            [TypeVariable() for i in cls.__params__])
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
    # create the data constructor
    base = namedtuple(name, ["i%s" % i for i, _ in enumerate(fields)])
    cls = type(name, (type_constructor, base), {})

    # If the data constructor takes no arguments, create an instance of it
    # and return that instance rather than returning the class
    # The type() method does not need to be modified in this case
    if len(fields) == 0:
        cls = cls()
    # Otherwise, modify type() so that it matches up fields from the data
    # constructor with type params from the type constructor
    else:
        def _type(self):
            args = [HM_typeof(self[fields.index(p)]) \
                    if p in fields else TypeVariable()
                    for p in type_constructor.__params__]
            return TypeOperator(type_constructor, args)
        cls.type = _type

    # TODO: make sure __init__ or __new__ is typechecked

    type_constructor.__constructors__ += (cls,)
    return cls


def build_ADT(typename, typeargs, data_constructors, to_derive):
    """
    """
    # create the new type constructor and data constructors
    newtype = make_type_const(typename, typeargs)
    dcons = [make_data_const(d[0], d[1], newtype) for d in data_constructors]

    # derive typeclass instances for the new type constructors
    for tclass in to_derive:
        tclass.derive_instance(newtype)

    return tuple([newtype,] + dcons)


#=============================================================================#
# Pattern matching
