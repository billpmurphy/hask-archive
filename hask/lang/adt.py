from collections import namedtuple

from syntax import Syntax
from type_system import Typeclass
from type_system import __typeclass_flag__

#=============================================================================#
# ADT internals

class ADT(object):
    """Base class for Hask algebraic data types."""
    pass


def make_type_const(name, typeargs):
    """
    Build a new type constructor given a name and the type parameters.
    A new type constructor is a new class with a field __params__ that
    contains a tuple of type parameter names, and a field __constructors__ with
    a list of data constructors for that type.
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


#=============================================================================#
# User-facing syntax


class __new_tcon__(Syntax):

    def __init__(self, tcon_name):
        self.tcon_name = tcon_name
        self.type_args = ()

        super(__new_tcon__, self).__init__("Syntax error in `data`")
        return

    def __call__(self, *typeargs):
        self.type_args = typeargs
        return self

    def __eq__(self, ds):
        # create the new type constructor and data constructors
        newtype = make_type_const(self.tcon_name, self.type_args)
        dcons = [make_data_const(d[0], d[1], newtype) for d in ds.dconstructors]

        # derive typeclass instances for the new type constructore
        for tclass in ds.derives:
            tclass.derive_instance(newtype)

        # make the type constructor and data constructors available globally
        return tuple([newtype,] + dcons)


class __new_dcon__(Syntax):

    def __init__(self, dcon_name):
        self.dcon_name = dcon_name
        self.dconstructors = [(self.dcon_name, ())]
        self.derives = ()
        super(__new_dcon__, self).__init__("Syntax error in `d`")
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


class __data__(Syntax):
    def __getattr__(self, value):
        return __new_tcon__(value)


class __d__(Syntax):
    def __getattr__(self, value):
        return __new_dcon__(value)


data = __data__()
d = __d__()


class deriving(Syntax):

    def __init__(self, *tclasses):
        for tclass in tclasses:
            if not issubclass(tclass, Typeclass):
                raise TypeError("Cannot derive non-typeclass %s" % tclass)
        self.derived_classes = tclasses
        return
