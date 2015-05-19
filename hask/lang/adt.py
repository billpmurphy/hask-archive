import operator
import re
import string
import types
from collections import namedtuple

from ..lang import syntax
from ..lang import type_system
from ..lang import typeclasses


## ADT internals

def _dc_items(dc):
    return tuple((dc.__getattribute__(i) for i in dc.__class__._fields))


def make_type_const(name, typeargs):
    """
    Build a new type constructor given a name and the type parameters.
    This is simply a new class with a field `_params` that contains the list of
    type parameter names.
    """
    def raise_fn(err):
        raise err()

    cls = type(name, (object,), {"__params__":tuple(typeargs),
                                 "__constructors__":(),
                                 "__typeclasses__":[]})

    # TODO
    cls._type = lambda self: self.typeargs

    cls.__iter__ = lambda self, other: raise_fn(TypeError)
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
    cls = type(name, (type_constructor, base), {})

    # TODO: make sure __init__ or __new__ is typechecked

    return cls


def derive_eq(type_constructor):
    """
    Add a default __eq__ method to a type constructor.
    """
    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               all((s == o for s, o in zip(_dc_items(self), _dc_items(other))))
    type_constructor.__eq__ = __eq__
    type_constructor.__ne__ = lambda self, other: not __eq__(self, other)
    return type_constructor


def derive_show(type_constructor):
    """
    Add a default __repr__ method to a data constructor.
    """
    def __repr__(self):
        if len(self.__class__._fields) == 0:
            return self.__class__.__name__
        return "%s(%s)" % (self.__class__.__name__,
                           ", ".join(map(repr, _dc_items(self))))
    type_constructor.__repr__ = __repr__
    return type_constructor


def derive_read(type_constructor):
    """
    Add a default __read__ method to a data constructor.
    """
    pass


def derive_ord(type_constructor):
    """
    Add default comparison operators to a data constructor.
    """
    # compare all of the _fields of two objects
    def zip_cmp(self, other, fn):
        return all((fn(a, b) for a, b in zip(_dc_items(self), _dc_items(other))))

    type_constructor.__lt__ = lambda s, o: zip_cmp(s, o, operator.lt)
    return type_constructor


## User-facing syntax


class __dotwrapper__(object):

    def __init__(self, cls):
        self.cls = cls

    def __getattr__(self, value):
        return getattr(self, "cls")(value)


class __new_tcon__(syntax.Syntax):

    def __init__(self, tcon_name):
        self.tcon_name = tcon_name
        self.type_args = ()

        syntax_err_msg = "Syntax error in `data`"
        super(self.__class__, self).__init__(syntax_err_msg)
        return

    def __call__(self, *typeargs):
        self.type_args = typeargs
        return self

    def __eq__(self, ds):
        newtype = make_type_const(self.tcon_name, self.type_args)
        dcons = [make_data_const(d[0], d[1], newtype) for d in ds.donstructors]

        for add_tclass in ds.derived_classes:
            newtype = add_tclass(newtype)

        # make the type constructor and data constructors available globally
        globals()[self.tcon_name] = newtype
        for dcon in dcons:
            globals()[dcon.__name__] = dcon
        return


class __new_dcon__(syntax.Syntax):

    def __init__(self, dcon_name):
        self.dcon_name = dcon_name
        self.dconstructors = [(dcon_name, type_args)]
        self.type_args = ()

        syntax_err_msg = "Syntax error in `d`"
        super(self.__class__, self).__init__(syntax_err_msg)
        return

    def __call__(self, *typeargs):
        self.type_args = typeargs
        self.dconstructors = [(self.dcon_name, self.type_args)]
        return self

    def __or__(self, other):
        self.derives = other.derives
        self.dconstructors += other.dconstructors

        # Check for duplicate data constructors
        dconst_names = set(zip(*self.dconstructors)[0])
        if len(dconst_names) < len(self.dconstructors):
            raise SyntaxError("Illegal duplicate data constructors")
        return self

    def __and__(self, derives):
        self.derives = derives.derived_classes
        return self


data = __dotwrapper__(__new_tcon__)
d = __dotwrapper__(__new_dcon__)


class deriving(syntax.Syntax):
    __supported__ = {typeclasses.Show:derive_show,
                     typeclasses.Eq:derive_eq,
                     typeclasses.Ord:derive_ord,
                     typeclasses.Read:derive_read}

    def __init__(self, *tclasses):
        for tclass in set(tclasses):
            if tclass not in self.__class__.__supported__:
                raise TypeError("Cannot derive typeclass %s" % tclass)
        self.derived_classes = [__supported__[t] for t in tclasses]
        return
