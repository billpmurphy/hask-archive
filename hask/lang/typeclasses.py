import operator
import sys

from type_system import Typeclass
from type_system import is_builtin
from type_system import has_instance
from type_system import nt_to_tuple


#=============================================================================#
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
        if type(a) == str:
            return "'%s'" % a
        return str(a)

    @staticmethod
    def derive_instance(type_constructor):
        def __str__(self):
            if len(self.__class__._fields) == 0:
                return self.__class__.__name__

            nt_tup = nt_to_tuple(self)
            tuple_str = "(%s)" % nt_tup[0] if len(nt_tup) == 1 else str(nt_tup)
            return "{0}{1}".format(self.__class__.__name__, tuple_str)
        Show(type_constructor, __str__ = __str__)
        return



class Eq(Typeclass):
    """
    The Eq class defines equality (==) and inequality (!=).

    Dependencies:
        n/a

    Attributes:
        __eq__
        __ne__

    Minimal complete definition:
        __eq__
    """
    def __init__(self, cls, __eq__, __ne__=None):
        def default_not_eq(self, other):
            return not self.__eq__(other)

        __ne__ = default_not_eq if __ne__ is None else __ne__

        super(Eq, self).__init__(cls, attrs={"__eq__":__eq__, "__ne__":__ne__})
        return

    @staticmethod
    def derive_instance(type_constructor):
        def __eq__(self, other):
            return self.__class__ == other.__class__ and \
                nt_to_tuple(self) == nt_to_tuple(other)

        def __ne__(self, other):
            return self.__class__ != other.__class__ or  \
                nt_to_tuple(self) != nt_to_tuple(other)

        Eq(type_constructor, __eq__ = __eq__, __ne__ = __ne__)
        return



class Ord(Typeclass):

    def __init__(self, cls, __lt__, __le__=None, __gt__=None, __ge__=None):
        __le = lambda s, o: s.__lt__(o) or s.__eq__(o)
        __gt = lambda s, o: not s.__lt__(o) and not s.__eq__(o)
        __ge = lambda s, o: not s.__lt__(o) or not s.__eq__(o)

        __le__ = __le if __le__ is None else __le__
        __gt__ = __gt if __gt__ is None else __gt__
        __ge__ = __ge if __ge__ is None else __ge__

        attrs = {"__lt__":__lt__, "__le__":__le__,
                 "__gt__":__gt__, "__ge__":__ge__}
        super(Ord, self).__init__(cls, dependencies=[Eq], attrs=attrs)
        return

    @staticmethod
    def derive_instance(type_constructor):
        def zip_cmp(self, other, fn):
            """
            Compare the data constructor and all of the fields of two ADTs.
            """
            find_index = lambda x: type_constructor.__constructors__.index(x)

            self_cls = self if nt_to_tuple(self) == () else self.__class__
            other_cls = other if nt_to_tuple(other) == () else other.__class__
            self_i, other_i = find_index(self_cls), find_index(other_cls)

            if self_i == other_i:
                zipped_fields = zip(nt_to_tuple(self), nt_to_tuple(other))
                return all((fn(a, b) for a, b in zipped_fields))
            return fn(self_i, other_i)

        lt = lambda s, o: zip_cmp(s, o, operator.lt)
        le = lambda s, o: zip_cmp(s, o, operator.le)
        gt = lambda s, o: zip_cmp(s, o, operator.gt)
        ge = lambda s, o: zip_cmp(s, o, operator.ge)
        Ord(type_constructor, __lt__=lt, __le__=le, __gt__=gt, __ge__=ge)
        return


class Bounded(Typeclass):

    def __init__(self, cls, minBound, maxBound):
        attrs = {"minBound":minBound, "maxBound":maxBound}
        super(Bounded, self).__init__(cls, attrs=attrs)
        return

    @staticmethod
    def derive_instance(type_constructor):
        # All data constructors must be enums
        for data_con in type_constructor.__constructors__:
            if not isinstance(data_con, type_constructor):
                raise TypeError("Cannot derive Bounded; %s is not an enum" %
                                 data_con.__name__)

        maxBound = lambda s: type_constructor.__constructors__[0]
        minBound = lambda s: type_constructor.__constructors__[-1]
        Bounded(type_constructor, minBound=minBound, maxBound=maxBound)
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


class Enum(Typeclass):

    def __init__(self, cls, toEnum, fromEnum):
        attrs = {"toEnum":toEnum, "fromEnum":fromEnum}
        super(Enum, self).__init__(cls, attrs=attrs)
        return

    @staticmethod
    def toEnum(a):
        if is_builtin(type(a)):
            if has_instance(type(a), Num):
                return int(a)
            elif type(a) == str:
                return ord(a)
        return a.toEnum()

    @staticmethod
    def fromEnum(a, _return=None):
        if is_builtin(type(a)):
            if has_instance(_return, Num):
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


class Num(Typeclass):

    def __init__(self, cls, add, mul, abs, signum, fromInteger, negate, sub=None):
        def default_sub(a, b):
            return a.__add__(b.__neg__())

        sub = default_sub if sub is None else sub

        attrs = {"__add__":add,
                 "__mul__":mul,
                 "__abs__":abs,
                 "signum":signum,
                 "fromInteger":fromInteger,
                 "__neg__":negate,
                 "__sub__":sub}

        super(Num, self).__init__(cls, dependencies=[Show, Eq], attrs=attrs)
        return


class Fractional(Typeclass):

    def __init__(self, cls):
        super(Fractional, self).__init__(cls, dependencies=[Num])


class Floating(Typeclass):

    def __init__(self, cls):
        super(Floating, self).__init__(cls, dependencies=[Fractional])


class Real(Typeclass):

    def __init__(self, cls):
        super(Real, self).__init__(cls, dependencies=[Num, Ord])


class Integral(Typeclass):

    def __init__(self, cls):
        super(Integral, self).__init__(cls, dependencies=[Real, Enum])


class RealFrac(Typeclass):

    def __init__(self, cls):
        super(RealFrac, self).__init__(cls, dependencies=[Real, Fractional])


class RealFloat(Typeclass):

    def __init__(self, cls):
        super(RealFloat, self).__init__(cls, dependencies=[Floating, RealFrac])
        return


class Functor(Typeclass):

    def __init__(self, cls, fmap):
        """
        Transform a class into a member of Functor. The fmap function must be
        supplied when making the class a member of Functor.
        """
        def _fmap(self, fn):
            return fmap(self, fn)

        # `*` syntax for fmap
        def mul(self, fn):
            return self.fmap(fn)

        super(Functor, self).__init__(cls, attrs={"fmap":_fmap, "__mul__":mul})
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

    def __init__(self, cls, __iter__, __getitem__=None, __len__=None):
        def default_len(self):
            count = 0
            for _ in iter(self):
                count += 1
            return count

        def default_getitem(self, i):
            return list(iter(self))[i]

        __len__ = default_len if __len__ is None else __len__
        __getitem__ = default_getitem if __getitem__ is None else __getitem__

        deps = [Foldable, Functor]
        attrs = {"__iter__":__iter__, "__getitem__":__getitem__,
                 "__len__":__len__}
        super(Traversable, self).__init__(cls, dependencies=deps, attrs=attrs)
        return

    @staticmethod
    def length(a):
        return len(a)


class Monoid(Typeclass):

    def __init__(self, cls, mempty, mappend):
        #TODO: mconcat

        attrs = {"mempty":mempty, "mappend":mappend}
        super(Monoid, self).__init__(cls, attrs=attrs)

    @staticmethod
    def mempty(_return):
        return _return.mempty

    @staticmethod
    def mappend(a, b):
        return a.mappend(b)


class Iterator(Typeclass):
    """
    Special typeclass for Python iterators, i.e. classes with a next or
    __next__ attribute.

    Minimal complete definition:
        __next__
    """
    def __init__(self, cls, __next__):
        def _next(self):
            return __next__(self)

        attrs = {"__next__": _next, "next":_next}
        super(Iterator, self).__init__(cls, dependencies=[Traversable],
                                       attrs=attrs)
        return


#=============================================================================#
## Exported typeclass functions

# Enum
succ = Enum.succ
pred = Enum.pred
toEnum = Enum.toEnum
fromEnum = Enum.fromEnum
enumFrom = Enum.enumFrom
enumFromThen = Enum.enumFromThen
enumFromTo = Enum.enumFromTo
enumFromThenTo = Enum.enumFromThenTo

# Functor
fmap = Functor.fmap

# Foldable
foldr = Foldable.foldr

# Traversable
length = Traversable.length

# Monoid
mempty = Monoid.mempty
mappend = Monoid.mappend
