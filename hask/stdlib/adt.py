import operator
import re
import string
import types
from collections import namedtuple

from ..lang import syntax
from ..lang import type_system
from ..lang import typeclasses


def _dc_items(dc):
    return tuple((dc.__getattribute__(i) for i in dc.__class__._fields))


def make_type_const(name, typeargs):
    """
    Build a new type constructor given a name and the type parameters.
    This is simply a new class with a field `_params` that contains the list of
    type parameter names.
    """
    cls = type(name, (object,), {"_params":tuple(typeargs)})
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
    cls = type(name, (base, type_constructor), {})

    def raise_fn(err):
        raise err()

    # TODO:
    # make sure __init__ or __new__ is typechecked
    cls.__init__ = base.__init__
    cls.__type__ = lambda self: type_constructor

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

    typeclasses.Typeable(cls, cls.__type__)
    return cls


def derive_eq_data(data_constructor):
    """
    Add a default __eq__ method to a data constructor.
    """
    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               all((s == o for s, o in zip(_dc_items(self), _dc_items(other))))
    data_constructor.__eq__ = __eq__
    data_constructor.__ne__ = lambda self, other: not __eq__(self, other)
    return data_constructor


def derive_show_data(data_constructor):
    """
    Add a default __repr__ method to a data constructor.
    """
    def __repr__(self):
        if len(self.__class__._fields) == 0:
            return self.__class__.__name__
        return "%s(%s)" % (self.__class__.__name__,
                           ", ".join(map(repr, _dc_items(self))))
    data_constructor.__repr__ = __repr__
    return data_constructor


def derive_read_data(data_constructor):
    """
    Add a default __read__ method to a data constructor.
    """
    pass


def derive_ord_data(data_constructor):
    """
    Add default comparison operators to a data constructor.
    """
    # compare all of the _fields of two objects
    def zip_cmp(self, other, fn):
        return all((fn(a, b) for a, b in zip(_dc_items(x), _dc_items(x))))

    data_constructor.__lt__ = lambda s, o: zip_cmp(s, o, operator.lt)
    data_constructor.__gt__ = lambda s, o: zip_cmp(s, o, operator.gt)
    data_constructor.__le__ = lambda s, o: zip_cmp(s, o, operator.le)
    data_constructor.__ge__ = lambda s, o: zip_cmp(s, o, operator.ge)
    return data_constructor


class data(syntax.Syntax):

    def __init__(self, dt_name, *type_args):
        if type(dt_name) != str:
            raise SyntaxError("Data type name must be str, not %s"
                              % type(dt_name))

        if not re.match("^[A-Z]\w*$", dt_name):
            raise SyntaxError("Invalid ADT name.")

        for type_arg in type_args:
            if type(type_arg) != str:
                raise SyntaxError("Data type name must be string")

            for letter in type_arg:
                if letter not in string.lowercase:
                    raise SyntaxError("Invalid type variable %s" % type_arg)

        if len(set(type_args)) != len(type_args):
            raise SyntaxError("Conflicting definitions for type variable")

        self.dt_name = dt_name
        self.type_args = type_args

        syntax_err_msg = "Syntax error in `data`"
        super(self.__class__, self).__init__(syntax_err_msg)
        return

    def __eq__(self, constructors):
        return self



class d(syntax.Syntax):

    def __init__(self, dconstructor, *typeargs):
        self.dconstructors = [(dconstructor, typeargs)]
        self.derives = None

    def __or__(self, other):
        if type(other) == str:
            return self.__or__(self.__class__(other))
        elif type(other) == self.__class__:
            self.derives = other.derives
            self.dconstructors += other.dconstructors

            # Check for duplicate data constructors
            dconst_names = set(zip(*self.dconstructors)[0])
            if len(dconst_names) < len(self.dconstructors):
                raise SyntaxError("Illegal duplicate data constructors")
        else:
            raise SyntaxError("Illegal `%s` in data statement" % other)
        return self

    def __and__(self, derives):
        self.derives = derives.derived_classes()
        return self


class deriving(syntax.Syntax):
    __supported__ = (typeclasses.Show, typeclasses.Eq, typeclasses.Ord,
                     typeclasses.Read)

    def __init__(self, *tclasses):
        for tclass in tclasses:
            if tclass not in self.__class__.__supported__:
                raise TypeError("Cannot derive typeclass %s" % tclass)
        self.tclasses = tclasses
        return

    def derived_classes(self):
        return self.tclasses
