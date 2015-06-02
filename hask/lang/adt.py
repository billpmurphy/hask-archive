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
# User-facing syntax


class __new_tcon__(Syntax):
    """
    """
    def __init__(self, tcon_name, type_args=()):
        self.__name = tcon_name
        self.__args = type_args
        super(__new_tcon__, self).__init__("Syntax error in `data`")
        return

    def __call__(self, *typeargs):
        # make sure all type params are strings
        if not all((type(arg) == str for arg in typeargs)):
            self.raise_invalid("Type parameters must be strings")

        # all type parameters must have unique names
        if len(typeargs) != len(set(typeargs)):
            self.raise_invalid("Type parameters are not unique")

        return __new_tcon__(self.__name, typeargs)

    def __eq__(self, d):
        # one data constructor, no derived typedclasses
        if isinstance(d, __new_dcon__):
            return build_ADT(self.__name, self.__args, [(d.name, d.args)], ())

        # one data constructor, derived typeclasses
        elif isinstance(d, __new_dcon_deriving__):
            return build_ADT(self.__name, self.__args, [(d.name, d.args)],
                             d.classes)

        # one or more data constructors, no derived typeclasses
        elif isinstance(d, __new_dcons__):
            return build_ADT(self.__name, self.__args, d.dcons, ())

        # one or more data constructors, one or more derived typeclasses
        elif isinstance(d, __new_dcons_deriving__):
            return build_ADT(self.__name, self.__args, d.dcons, d.classes)

        self.raise_invalid()
        return


class __new_dcon__(Syntax):

    def __init__(self, dcon_name, args=()):
        self.name = dcon_name
        self.args = ()
        super(__new_dcon__, self).__init__("Syntax error in `d`")
        return

    def __call__(self, *typeargs):
        return __new_dcon__(self.name, typeargs)

    def __or__(self, dcon):
        if isinstance(dcon, __new_dcon__):
            return __new_dcons__(((self.name, self.args),
                                  (dcon.name, dcon.args),))
        elif isinstance(dcon, __new_dcon_deriving__):
            return __new_dcons__(((self.name, self.args),
                                  (dcon.name, dcon.args),),
                                 dcon.classes)
        self.raise_invalid()
        return

    def __and__(self, derive):
        if not isinstance(derive, deriving):
            self.raise_invalid()
        return __new_dcon_deriving__(self.name, self.args, derive.classes)


class __new_dcon_deriving__(Syntax):

    def __init__(self, dcon_name, args, classes):
        self.name = dcon_name
        self.args = args
        self.classes = classes


class __new_dcons__(Syntax):

    def __init__(self, data_consts, deriving=()):
        self.dcons = data_consts
        super(__new_dcons__, self).__init__("Syntax error in `d`")
        return

    def __or__(self, new_dcon):
        if isinstance(new_dcon, __new_dcon__):
            return __new_dcons__(self.dcons + \
                                 ((new_dcon.name, new_dcon.args),))
        elif isinstance(new_dcon, __new_dcon_deriving__):
            return __new_dcons_deriving__(self.dcons + \
                                          ((new_dcon.name, new_dcon.args),),
                                          new_dcon.classes)
        self.raise_invalid()


class __new_dcons_deriving__(Syntax):

    def __init__(self, data_consts, classes):
        self.dcons = data_consts
        self.classes = classes
        super(__new_dcons_deriving__, self).__init__("Syntax error in `d`")
        return


class __data__(Syntax):
    """
    Examples:

    Maybe, Nothing, Just =\
    data.Maybe("a") == d.Nothing | d.Just("a") deriving(Read, Show, Eq, Ord)

    """
    def __getattr__(self, value):
        return __new_tcon__(value)


class __d__(Syntax):
    """
    `d` is part of hask's special syntax for defining algebraic data types.

    See help(data) for more information.
    """
    def __getattr__(self, value):
        return __new_dcon__(value)


data = __data__()
d = __d__()


class deriving(Syntax):
    """
    `deriving` is part of hask's special syntax for defining algebraic data
    types.

    See help(data) for more information.
    """
    def __init__(self, *tclasses):
        for tclass in tclasses:
            if not issubclass(tclass, Typeclass):
                raise TypeError("Cannot derive non-typeclass %s" % tclass)
        self.classes = tclasses
        return
