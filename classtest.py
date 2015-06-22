from collections import namedtuple


class TypeMeta(type):
    """
    Metaclass for Typeclass type. Ensures that all typeclasses are instantiated
    with a dictionary to map instances to their member functions, and a list of
    dependencies.
    """
    def __init__(self, *args):
        super(TypeMeta, self).__init__(*args)
        self.__instances__ = {}
        self.__dependencies__ = self.mro()[1:-2] # excl. self, Typeclass, object

    def __getitem__(self, item):
        return self.__instances__[resolve(item)]


def has_instance(cls, typeclass):
    """
    Test whether a class is a member of a particular typeclass.

    Args:
        cls: The class or type to test for membership
        typeclass: The typeclass to check. Must be a subclass of Typeclass.

    Returns:
        True if cls is a member of typeclass, and False otherwise.
    """
    return cls in typeclass.__instances__


class instance(object):

    def __init__(self, typeclass, cls):
        import inspect
        if len(inspect.getargspec(typeclass.make_instance).args) == 2:
            return typeclass.make_instance(cls)
        self.typeclass = typeclass
        self.cls = cls
        return

    def where(self, **kwargs):
        self.typeclass.make_instance(self.cls, **kwargs)



class Typeclass(object):
    """Base class for typeclasses"""
    __metaclass__ = TypeMeta

    @classmethod
    def make_instance(cls, type_, *args):
        raise NotImplementedError("Typeclasses must implement `make`")

    @classmethod
    def derive_instance(cls, type_):
        raise NotImplementedError("Typeclasses must implement `derive`")


def build_instance(typeclass, _type, attrs):
    # check dependencies
    for dep in typeclass.__dependencies__:
        if _type not in dep.__instances__:
            raise TypeError("Missing dependency: %s" % dep.__name__)

    # add type and its instance method to typeclass's instance dictionary
    __methods__ = namedtuple("__%s__" % _type.__name__, attrs.keys())(**attrs)
    typeclass.__instances__[_type] = __methods__
    return


def resolve(obj):
    """
    This should call HM_typeof and return the type constructor
    """
    return type(obj)


class Parent1(Typeclass):
    @classmethod
    def make_instance(cls, _type):
        build_instance(Parent1, _type, {})
        return


class Parent2(Typeclass):
    @classmethod
    def make_instance(cls, _type):
        build_instance(Parent2, _type, {})
        return


class Addable(Parent1, Parent2):
    @classmethod
    def make_instance(cls, type_, add):
        build_instance(Addable, type_, {"add":add})

    @classmethod
    def derive_instance(cls, type_):
        Addable.make_instance(type_, {"add":lambda x, y: x + y})


def f(x, y):
    return Addable[x].add(x, y)


######


instance(Parent1, int)
instance(Parent2, int)
instance(Addable, int).where(add = lambda x, y: x + y)
print "P1", Parent1.__instances__
print "P2", Parent2.__instances__
print "A", Addable.__instances__
print "T", Typeclass.__instances__
print ""
print "A", Addable.__dependencies__
print "P1", Parent1.__dependencies__
print "T", Typeclass.__dependencies__
print f(1, 2)
