import inspect
import functools
import string
import types

from hindley_milner import *

#==================================================================#
# User interface


# should be syntax
class H2(object):
    """
    Usage:

    @H() >> int >> int >> t.Maybe . int
    def safe_div(x, y):
        if y == 0:
            return Nothing
        return Just(x / y)

    @H(t.Show("a")) >> "a" >> str
    def to_str(x):
        return str(x)
    """
    def __new__(self, *constraints):
        return __signature__(constraints=constraints)


class __signature__(object):
    def __init__(self, constraints=(), *args):
        self.args = args
        self.constraints = constraints
        self.constraints_set = False

    def __getitem__(self, constraints):
        if self.constraints_set:
            raise SyntaxError("Error")
        self.constraints = constraints
        self.constraints_set = True
        return self

    def __rshift__(self, next_arg):
        self.args += (next_arg,)
        return self

    def __call__(self, fn):
        # do all the type checking in here
        return fn


class TypeSignatureError(Exception):
    pass


def fromExistingType(t, *params):
    """Makes a type operator from an existing type.

    Args:
        t: the unknown type
    """
    return TypeOperator(t.__name__, params)


def parse_sig_item(item):
    if isinstance(item, TypeVariable) or isinstance(item, TypeOperator):
        return item

    elif hasattr(item, "type"):
        return TypeOperator(item.type().hkt,
                            map(parse_sig_item, item.type().params))

    # ("a", "b"), (int, ("a", float)), etc.
    elif isinstance(item, tuple):
        return Tuple(map(parse_sig_item, item))

    # ["a"], [int], etc
    elif isinstance(item, list) and len(item) == 1:
        return ListType(parse_sig_item(item[0]))

    # any other type
    elif isinstance(item, type):
        return TypeOperator(item, [])

    raise TypeSignatureError("Invalid item in type signature: %s" % item)



def parse_type_sig(items):
    parsed_items = parse_sig_item(items)
    return



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
