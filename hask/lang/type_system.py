import inspect
import functools
import string
import types

from hindley_milner import *

##############################################################################


class ArityError(TypeError):
    pass


def _t(obj):
    """
    Returns the type of an object. Similar to `:t` in Haskell.
    """
    if hasattr(obj, "type"):
        return str(obj._type())
    return str(HM_typeof(obj))


def HM_typeof(obj):
    """
    Returns the type of an object within the internal type system.
    """
    if hasattr(obj, "type"):
        return obj.type()
    #TODO: add TypedFunc
    elif isinstance(obj, tuple):
        return Tuple(map(HM_typeof, obj))
    return TypeOperator(type(obj), [])


## Type system

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
