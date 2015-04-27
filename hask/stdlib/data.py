import re
import string
from collections import namedtuple

from ..lang import syntax
from ..lang import type_system
from ..lang import typeclasses


def make_adt(name, typeargs, type_constructor):
    base = namedtuple(name, ["i%s" % i for i, _ in enumerate(typeargs)])

    def raise_fn(err):
        raise err()

    cls = type(name, (base, type_constructor), {})

    # init
    con = type_system.H() >> cls
    for arg in typeargs:
        con = con >> arg
    init_sig = type_system.sig(con >> type(None))

    cls.__init__ = init_sig(cls.__init__)
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


def derive_eq(cls):
    pass


def derive_show(cls):
    pass


def derive_read(cls):
    pass


def derive_ord(cls):
    pass



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
    __supported__ = (typeclasses.Show, typeclasses.Eq, typeclasses.Ord)

    def __init__(self, *tclasses):
        for tclass in tclasses:
            if tclass not in self.__class__.__supported__:
                raise TypeError("Cannot derive typeclass %s" % tclass)
        self.tclasses = tclasses
        return

    def derived_classes(self):
        return self.tclasses
