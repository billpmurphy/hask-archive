import abc
import inspect
import functools
import string
import types


class ArityError(TypeError):
    pass


## Typeclass infrastructure

class Typeclass(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls, dependencies=(), attrs=None):
        for dep in dependencies:
            if not in_typeclass(cls, dep):
                raise TypeError("%s is not a member of %s" %
                                (cls.__name__, dep.__name__))

        if attrs is not None:
            for attr_name, attr in attrs.iteritems():
                add_attr(cls, attr_name, attr)

        add_typeclass_flag(cls, self.__class__)
        return


def is_builtin(cls):
    """
    Return True if a type is a Python builtin type, and False otherwise.
    """
    b = set((types.NoneType, types.TypeType, types.BooleanType, types.IntType,
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
             types.GetSetDescriptorType, types.MemberDescriptorType))
    return cls in b


def in_typeclass(cls, typeclass):
    """
    Return True if cls is a member of typeclass, and False otherwise.
    Python builtins cannot be typeclasses.
    """
    if is_builtin(typeclass):
       return False
    elif is_builtin(cls):
        try:
            return issubclass(cls, typeclass)
        except TypeError:
            return False
    elif hasattr(cls, "__typeclasses__"):
        return typeclass in cls.__typeclasses__
    return False


def add_attr(cls, attr_name, attr):
    """
    Modify an existing class to add an attribute. If the class is a builtin, do
    nothing.
    """
    if not is_builtin(cls):
        setattr(cls, attr_name, attr)
    return


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
    return


def _t(obj):
    """
    Returns the type of an object. Similar to `:t` in Haskell.
    """
    if hasattr(obj, "_type"):
        return obj._type()
    return type(obj)


## Type system

class H(object):
    """
    Wrapper for list that represents a chain of types in a type signature,
    e.g. "a -> b -> c". Used for cosmetic purposes, so that we can write e.g.
    "typ(a) >> str"
    """
    def __init__(self):
        self.ty_args = []

    def __rshift__(self, other):
        self.ty_args.append(other)
        return self

    def __iter__(self):
        return iter(self.ty_args)

    def __len__(self):
        return len(self.ty_args)

    def __getitem__(self, ix):
        return self.ty_args[ix]


def arity(f):
    """
    Find the arity of a function or method, including functools.partial
    objects.
    """
    if not hasattr(f, "__call__"):
        return 0

    if isinstance(f, types.MethodType):
        f = f.__func__

    count = 0
    while isinstance(f, functools.partial):
        if f.args:
            count += len(f.args)
        f = f.func
    spec = inspect.getargspec(f)
    args = spec.args

    var = 0
    if not args and (spec.varargs is not None or spec.keywords is not None):
        var = 1

    argcount = len(spec.args) + var
    return argcount - count


###############################################################################
# Type checking
###############################################################################

def typecheck_arg(type_a, value):
    if not isinstance(value, type_a):
        err = "Typecheck failed: {v} :: {t}"
        raise TypeError(err.format(v=repr(value), t=type_a))
    return


def sig(ty_args):
    """
    Typechecking without currying.
    """
    def decorate(func):
        if not len(ty_args) == arity(func) + 1:
            raise ArityError("Signature and function have different arity")

        def _wrapper(*args, **kwargs):
            # typecheck arguments
            for t, v in zip(ty_args[:-1], args):
                typecheck_arg(t, v)

            # typecheck return value
            result = func(*args, **kwargs)
            typecheck_arg(ty_args[-1], result)
            return result
        return _wrapper
    return decorate


def sig2(ty_args):
    """
    Typechecking with currying.
    """
    def decorate(func):
        def _wrapper(*args, **kwargs):
            # typecheck arguments
            for t, v in zip(ty_args[:-1], args):
                typecheck_arg(t, v)

            # typecheck return value
            result = func(*args, **kwargs)
            typecheck_arg(ty_args[-1], result)
            return result

        return _wrapper
    return decorate
