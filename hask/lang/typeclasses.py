import abc
import sys
import types


# Typeclass infrastructure

__typeclass_flag__ = "__typeclasses__"


def is_builtin(cls):
    """
    Return True if a type is a Python builtin type, and False otherwise.
    """
    b = set((types.NoneType, types.TypeType, types.BooleanType, types.IntType,
             types.LongType, types.FloatType, types.ComplexType,
             types.StringType, types.UnicodeType, types.TupleType,
             types.ListType, types.DictType, types.DictionaryType,
             types.FunctionType, types.LambdaType, types.GeneratorType,
             types.CodeType, types.ClassType, types.InstanceType,
             types.MethodType, types.UnboundMethodType,
             types.BuiltinFunctionType, types.BuiltinMethodType,
             types.ModuleType, types.FileType, types.XRangeType,
             types.EllipsisType, types.TracebackType, types.FrameType,
             types.BufferType, types.DictProxyType, types.NotImplementedType,
             types.GetSetDescriptorType, types.MemberDescriptorType))
    return cls in b


def in_typeclass(cls, typeclass):
    """
    Return True if cls is a member of typeclass, and False otherwise.
    Python builtins cannot be typeclasses.
    """
    if is_builtin(typeclass):
       return False
    elif is_builtin(cls):
        try:
            return issubclass(cls, typeclass)
        except TypeError:
            return False
    elif hasattr(cls, __typeclass_flag__):
        return typeclass in cls.__typeclasses__
    return False


class Typeclass(object):
    """
    Base metaclass for Typeclasses.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls, dependencies=(), attrs=None):
        for dep in dependencies:
            if not in_typeclass(cls, dep):
                raise TypeError("%s is not a member of %s" %
                                (cls.__name__, dep.__name__))

        if attrs is not None:
            for attr_name, attr in attrs.iteritems():
                Typeclass.add_attr(cls, attr_name, attr)

        Typeclass.add_typeclass_flag(cls, self.__class__)
        return

    @staticmethod
    def add_attr(cls, attr_name, attr):
        """
        Modify an existing class to add an attribute. If the class is a
        builtin, do nothing.
        """
        if not is_builtin(cls):
            setattr(cls, attr_name, attr)
        return

    @staticmethod
    def add_typeclass_flag(cls, typeclass):
        """
        Add a typeclass membership flag to a class, signifying that the class
        belongs to the specified typeclass.
        """
        if is_builtin(cls):
            typeclass.register(cls)
        elif hasattr(cls, __typeclass_flag__):
            cls.__typeclasses__.append(typeclass)
        else:
            cls.__typeclasses__ = [typeclass]
        return


# Basic typeclasses

class Read(Typeclass):

    def __init__(self, cls, read=None):
        read = classmethod(lambda s: eval(s) if read is None else read)
        super(Read, self).__init__(cls, attrs={"read":read})
        return

    @staticmethod
    def read(string, _return):
        if _return is not None:
            return _return.__class_.read(string)
        return eval(string)


class Show(Typeclass):

    def __init__(self, cls, __str__):
        super(Show, self).__init__(cls, attrs={"__str__":__str__})
        return

    @staticmethod
    def show(a):
        return str(a)


class Eq(Typeclass):
    """
    The Eq class defines equality (==) and inequality (!=). Minimal complete
    definition: __eq__
    """

    def __init__(self, cls, __eq__):
        def __ne__(self, other):
            return not self.__eq__(other)

        super(Eq, self).__init__(cls, attrs={"__eq__":__eq__, "__ne__":__ne__})
        return


class Ord(Typeclass):

    def __init__(self, cls, __lt__):
        __le__ = lambda s, o: s.__lt__(o) or s.__eq__(o)
        __gt__ = lambda s, o: not s.__lt__(o) and not s.__eq__(o)
        __ge__ = lambda s, o: not s.__lt__(o) or not s.__eq__(o)

        attrs = {"__lt__":__lt__, "__le__":__le__,
                 "__gt__":__gt__, "__ge__":__ge__}
        super(Ord, self).__init__(cls, dependencies=[Eq], attrs=attrs)
        return


class Bounded(Typeclass):

    def __init__(self, cls, minBound, maxBound):
        attrs = {"minBound":minBound, "maxBound":maxBound}
        super(Bounded, self).__init__(cls, attrs=attrs)
        return

    @staticmethod
    def maxBound(a):
        if is_builtin(type(a)):
            if type(a) == int:
                return sys.maxint
            elif type(a) == float:
                return sys.float_info.max
        return a.maxBound()

    @staticmethod
    def minBound(a):
        if is_builtin(type(a)):
            if type(a) == int:
                return -sys.maxint - 1
            elif type(a) == float:
                return sys.float_info.min
        return a.minBound()


class Num(Typeclass):

    def __init__(self, cls):
        super(Num, self).__init__(cls, dependencies=[Show, Eq])
        return


class RealFloat(Typeclass):

    def __init__(self, cls):
        super(RealFloat, self).__init__(cls, dependencies=[Num])
        return


class Enum(Typeclass):
    def __init__(self, cls, toEnum, fromEnum):
        attrs = {"toEnum":toEnum, "fromEnum":fromEnum}
        super(Enum, self).__init__(cls, attrs=attrs)
        return

    @staticmethod
    def toEnum(a):
        if is_builtin(type(a)):
            if in_typeclass(type(a), Num):
                return a
            elif type(a) == str:
                return ord(a)
        return a.toEnum()

    @staticmethod
    def fromEnum(a, _return=None):
        if is_builtin(type(a)):
            if in_typeclass(_return, Num):
                return a
            elif _return == str:
                return chr(a)
        elif _return is not None:
            return _return.from_Enum(a)
        return a.fromEnum()

    @staticmethod
    def succ(a):
        return Enum.fromEnum(Enum.toEnum(a) + 1, type(a))

    @staticmethod
    def pred(a):
        return Enum.fromEnum(Enum.toEnum(a) - 1, type(a))

    @staticmethod
    def enumFromThen(start, second):
        pointer = Enum.toEnum(start)
        step = Enum.toEnum(second) - pointer
        while True:
            yield Enum.fromEnum(pointer, type(start))
            pointer += step
        return

    @staticmethod
    def enumFrom(start):
        return Enum.enumFromThen(start, Enum.succ(start))

    @staticmethod
    def enumFromThenTo(start, second, end):
        pointer, stop = Enum.toEnum(start), Enum.toEnum(end)
        step = Enum.toEnum(second) - pointer
        while pointer <= stop:
            yield Enum.fromEnum(pointer, type(start))
            pointer += step
        return

    @staticmethod
    def enumFromTo(start, end):
        return Enum.enumFromThenTo(start, Enum.succ(start), end)


class Functor(Typeclass):

    def __init__(self, cls, __fmap__):
        """
        Transform a class into a member of Functor. The fmap function must be
        supplied when making the class a member of Functor.
        """
        def fmap(self, fn):
            return __fmap__(self, fn)

        # `*` syntax for fmap
        def mul(self, fn):
            return self.fmap(fn)

        super(Functor, self).__init__(cls, attrs={"fmap":fmap, "__mul__":mul})
        return

    @staticmethod
    def fmap(fn, functor):
        return functor.fmap(fn)


class Applicative(Typeclass):

    def __init__(self, cls, __pure__):
        """
        Transform a class into a member of Applicative. The pure function must be
        supplied when making the class a member of Applicative.
        """
        @classmethod
        def pure(cls, value):
            return __pure__(cls, value)

        super(Applicative, self).__init__(cls, dependencies=[Functor],
                                          attrs={"pure":pure})
        return

    @staticmethod
    def pure(value, app):
        return app.__class__.pure(value)


class Monad(Typeclass):

    def __init__(self, cls, __bind__):
        """
        Transform a class into a member of Monad. The bind function must be
        supplied when making the class a member of Monad.
        """
        def bind(self, fn):
            return __bind__(self, fn)

        # `>>` syntax for monadic bind
        def rshift(self, fn):
            return self.bind(fn)

        attrs = {"bind":bind, "__rshift__":rshift}
        super(Monad, self).__init__(cls, dependencies=[Applicative],
                                    attrs=attrs)
        return

    @staticmethod
    def bind(m, fn):
        return m.bind(fn)


class Foldable(Typeclass):
    def __init__(self, cls, foldr):
        super(Foldable, self).__init__(cls, attrs={"foldr":foldr})
        return

    @staticmethod
    def foldr(fn, a, lb):
        return lb.foldr(fn, a)


class Traversable(Typeclass):

    def __init__(self, cls, __iter__):
        def _iter(self):
            return __iter__(self)

        deps = [Foldable, Functor]
        super(Traversable, self).__init__(cls, dependencies=deps,
                                          attrs={"__iter__":_iter})
        return


class Ix(Typeclass):

    def __init__(self, cls, __getitem__, __len__=None):
        def getitem(self, i):
            return __getitem__(self, i)

        def default_len(self):
            count = 0
            for _ in iter(self):
                count += 1
            return count

        __len__ = default_len if __len__ is None else __len__

        attrs = {"__len__":__len__, "__getitem__":getitem}
        super(Ix, self).__init__(cls, dependencies=[Traversable], attrs=attrs)
        return

    @staticmethod
    def length(a):
        return a.__len__()


class Iterator(Typeclass):
    def __init__(self, cls, __next__):
        def _next(self):
            return __next__(self)

        attrs = {"__next__": _next, "next":_next}
        super(Iterator, self).__init__(cls, dependencies=[Traversable],
                                       attrs=attrs)
        return


## Typeclass functions

read = Read.read
show = Show.show
succ = Enum.succ
pred = Enum.pred
toEnum = Enum.toEnum
fromEnum = Enum.fromEnum
enumFrom = Enum.enumFrom
enumFromThen = Enum.enumFromThen
enumFromTo = Enum.enumFromTo
enumFromThenTo = Enum.enumFromThenTo
fmap = Functor.fmap
foldr = Foldable.foldr
length = Ix.length


