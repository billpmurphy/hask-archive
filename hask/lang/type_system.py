import abc
import inspect
import functools
import re
import string
import types

import syntax


## Typeclass infrastructure

class Typeclass(object):
    __metaclass__ = abc.ABCMeta
    __instances__ = []


class Typeable(Typeclass):
    """
    Typeclass for objects that have a type within Hask. This allows the type
    checker to understand higher-kinded types.
    """
    def __init__(self, cls, _type):
        add_attr(cls, "_type", _type)
        add_typeclass_flag(cls, self.__class__)
        return


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


def _t(obj):
    """
    Returns the type of an object. Similar to `:t` in Haskell.
    """
    if hasattr(obj, "_type"):
        return obj._type()
    return type(obj)


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


def add_attr(cls, attr_name, attr):
    """
    Modify an existing class to add an attribute. If the class is a builtin, do
    nothing.
    """
    if not is_builtin(cls):
        setattr(cls, attr_name, attr)
    return


## Type system

class Constraint(object):
    pass


class Poly(object):
    """
    Class that represents a polymorphic type, identified by a word.
    """
    def __init__(self, name):
        for letter in name:
            if letter not in string.lowercase:
                raise SyntaxError("Illegal name for polymorphic variable")
        self.name = name
        self.derived_type = None
        self.__name__ = self.name

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "Poly(%s)" % self.name


class TypeObject(syntax.Syntax):
    """
    Wrapper for tuple that represents types, including higher-kinded types.
    """
    def __init__(self, *args):
        if not args:
            raise TypeError("Cannot have empty typ()")

        args = list(args)
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                args[i] = Poly(arg)
            elif not isinstance(arg, type):
                raise TypeError("%s is not a type or a type variable" % arg)

        self.kind = len(args)
        self.hkt = args if self.kind > 1 else args[0]

        syntax_err_msg = "Syntax error in `typ`"
        super(self.__class__, self).__init__(syntax_err_msg)

    def __eq__(self, other):
        if other.__class__ == typ:
            return self.hkt == other.hkt
        return self.hkt == other

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        if self.kind == 1:
            return str(self.hkt)
        return " ".join(map(lambda x: x.__name__, self.hkt))


typ = TypeObject
con = Constraint


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


## type checking

def arity(f):
    """
    Find the arity of a function, including functools.partial objects.
    """
    if not hasattr(f, "__call__"):
        return 0

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


def sig(ty_args):
    """
    Typechecking without currying.
    """
    def decorate(func):
        if not len(ty_args) == arity(func) + 1:
            raise TypeError("Signature and function have different arity")

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            # typecheck arguments
            assertions = zip(ty_args, args)
            for t, v in assertions:
                if not isinstance(v, t):
                    raise TypeError("Typecheck failed: {v} :: {t}"
                                    .format(v=v, t=t))

            # typecheck return value
            result = func(*args, **kwargs)
            if not isinstance(result, ty_args[-1]):
                raise TypeError("Typecheck failed: {v} :: {t}".format(v=v,t=t))
            else:
                return result
        return _wrapper
    return decorate
