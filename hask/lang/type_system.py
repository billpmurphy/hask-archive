import inspect
import functools
import string
import types


###############################################################################

class Lambda(object):

    def __init__(self, v, body):
        self.v = v
        self.body = body

    def __str__(self):
        return "\{v} -> {body}".format(v=self.v, body=self.body)


class Ident(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Apply(object):

    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def __str__(self):
        return "({fn} {arg})".format(fn=self.fn, arg=self.arg)

#####

class TypeVariable(object):

    next_variable_id = 0
    next_variable_name = 'a'

    def __init__(self):
        self.id = TypeVariable.next_variable_id
        self.instance = None
        self.__name = None
        TypeVariable.next_variable_id += 1

    def _getName(self):
        return self.name if self.instance is None else str(self.instance)

    def __repr__(self):
        return "TypeVariable(id = {0})".format(self.id)


class TypeOperator(object):

    def __init__(self, name, types):
        self.name = name
        self.types = types

    def __str__(self):
        if num_types == 0:
            return self.name
        return "({0} {1})".format(self.name, " ".join(self.types))


class Function(TypeOperator):

    def __init__(self, from_type, to_type):
        super(Function, self).__init__("->", [from_type, to_type])









###############################################################################


class ArityError(TypeError):
    pass


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
