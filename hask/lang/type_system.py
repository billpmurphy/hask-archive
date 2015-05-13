import inspect
import functools
import string
import types

from hindley_milner import *

#==================================================================#
# User interface


def fromExistingType(t):
    """Makes a nullary type operator from an existing type.

    Args:
        t: the unknown type
    """
    return TypeOperator(t.__name__, [])


class TypedFunc(object):

    def __init__(self, signature, fn):
        self.typeargs = parse_typeargs(signature)
        self.signature = make_fn_type(typeargs)
        self.fn = fn
        return

    def __call__(self, *args, **kwargs):
        ap = self.signature
        for arg in args:
            if isinstance(arg, self.__class__):
                arg_ast = arg.signature
            else:
                arg_ast = Var(arg)
            ap = App(ap, arg_ast)

        # typecheck, raising a TypeError if things don't check
        t = analyze(ap, globals()) #need to supply environment
        fn = self.fn.__call__(*args, **kwargs)
        return self.__class__(t, fn)

    def __str__(self):
        return "%s :: %s" % (self.fn.__name__, self.signature)

    @staticmethod
    def parse_typeargs(signature):
        typeargs = [None] * len(signature)
        typevars = {s:TypeVariable() for s in signature if type(s) == str}

        for i, s in enumerate(signature):
            if isinstance(s, str):
                typeargs[i] = typevars[s]
            elif isinstance(s, self.__class__):
                return s.signature
            else:
                typeargs[i] = fromExistingType(s)
        return typeargs


def sig(signature):
    def decorator(fn):
        return TypedFunc(signature, fn)
    return decorator


##############################################################################


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
