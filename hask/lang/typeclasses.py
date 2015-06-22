import operator
import sys

from type_system import Typeclass
from type_system import is_builtin
from type_system import has_instance
from type_system import nt_to_tuple
from type_system import build_instance


#=============================================================================#
# Basic typeclasses


class Read(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, read):
        build_instance(Read, cls, {"read":read})
        return


class Show(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, show):
        build_instance(Show, cls, {"show":show})
        if not is_builtin(cls):
            cls.__str__ = show
        return

    @classmethod
    def derive_instance(typeclass, cls):
        def show(self):
            if len(self.__class__._fields) == 0:
                return self.__class__.__name__
            nt_tup = nt_to_tuple(self)
            tuple_str = "(%s)" % nt_tup[0] if len(nt_tup) == 1 else str(nt_tup)
            return "{0}{1}".format(self.__class__.__name__, tuple_str)
        Show.make_instance(cls, show=show)
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
        eq
    """
    @classmethod
    def make_instance(typeclass, cls, eq, ne=None):
        def default_not_eq(self, other):
            return not eq(self, other)

        ne = default_not_eq if ne is None else ne
        build_instance(Eq, cls, {"eq":eq, "ne":ne})

        if not is_builtin(cls):
            cls.__eq__ = eq
            cls.__ne__ = ne
        return

    @classmethod
    def derive_instance(typeclass, cls):
        def __eq__(self, other):
            return self.__class__ == other.__class__ and \
                nt_to_tuple(self) == nt_to_tuple(other)

        def __ne__(self, other):
            return self.__class__ != other.__class__ or  \
                nt_to_tuple(self) != nt_to_tuple(other)

        Eq.make_instance(cls, eq=__eq__, ne=__ne__)
        return



class Ord(Eq):
    @classmethod
    def make_instance(typeclass, cls, lt, le=None, gt=None, ge=None):
        __le__ = lambda s, o: s.__lt__(o) or s.__eq__(o)
        __gt__ = lambda s, o: not s.__lt__(o) and not s.__eq__(o)
        __ge__ = lambda s, o: not s.__lt__(o) or not s.__eq__(o)

        le = __le__ if le is None else le
        gt = __gt__ if gt is None else gt
        ge = __ge__ if ge is None else ge

        attrs = {"lt":lt, "le":le, "gt":gt, "ge":ge}
        build_instance(Ord, cls, attrs)
        if not is_builtin(cls):
            cls.__lt__ = lt
            cls.__le__ = le
            cls.__gt__ = gt
            cls.__ge__ = ge
        return

    @classmethod
    def derive_instance(typeclass, cls):
        def zip_cmp(self, other, fn):
            """
            Compare the data constructor and all of the fields of two ADTs.
            """
            find_index = lambda x: cls.__constructors__.index(x)

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
        Ord.make_instance(cls, lt=lt, le=le, gt=gt, ge=ge)
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


class Num(Show, Eq):

    def __init__(self, cls, add, mul, abs, signum, fromInteger, negate, sub=None):
        def default_sub(a, b):
            return a.__add__(b.__neg__())

        sub = default_sub if sub is None else sub
        attrs = {"__add__":add, "__mul__":mul, "__abs__":abs, "signum":signum,
                 "fromInteger":fromInteger, "__neg__":negate, "__sub__":sub}

        super(Num, self).__init__(cls, dependencies=[Show, Eq], attrs=attrs)
        return


class Fractional(Num):

    def __init__(self, cls):
        super(Fractional, self).__init__(cls, dependencies=[Num])


class Floating(Fractional):

    def __init__(self, cls):
        super(Floating, self).__init__(cls, dependencies=[Fractional])


class Real(Num, Ord):

    def __init__(self, cls):
        super(Real, self).__init__(cls, dependencies=[Num, Ord])


class Integral(Real, Enum):

    def __init__(self, cls):
        super(Integral, self).__init__(cls, dependencies=[Real, Enum])


class RealFrac(Real, Fractional):

    def __init__(self, cls):
        super(RealFrac, self).__init__(cls, dependencies=[Real, Fractional])


class RealFloat(Floating, RealFrac):

    def __init__(self, cls):
        super(RealFloat, self).__init__(cls, dependencies=[Floating, RealFrac])
        return


class Functor(Typeclass):

    @classmethod
    def make_instance(typeclass, cls, fmap):
        """
        """
        if not is_builtin(cls):
            cls.__mul__ = fmap
        build_instance(Functor, cls, {"fmap":fmap})
        return


class Applicative(Functor):
    @classmethod
    def make_instance(self, cls, pure):
        build_instance(Applicative, cls, {"pure":pure})
        return


class Monad(Applicative):
    @classmethod
    def make_instance(typeclass, cls, bind):
        build_instance(Monad, cls, {"bind":bind})
        if not is_builtin(cls):
            cls.__rshift__ = bind
        return


class Foldable(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, foldr):
        build_instance(Foldable, cls, {"foldr":foldr})
        return


class Traversable(Foldable, Functor):
    @classmethod
    def make_instance(typeclass, cls, iter, getitem=None, len=None):
        def default_len(self):
            count = 0
            for _ in iter(self):
                count += 1
            return count

        def default_getitem(self, i):
            return list(iter(self))[i]

        len = default_len if len is None else len
        getitem = default_getitem if getitem is None else getitem

        attrs = {"iter":iter, "getitem":getitem, "len":len}
        build_instance(Traversable, cls, attrs)
        return

    @staticmethod
    def length(a):
        return len(a)


class Monoid(Typeclass):

    @classmethod
    def make_instance(typeclass, cls, mempty, mappend, mconcat=None):
        #TODO: mconcat
        attrs = {"mempty":mempty, "mappend":mappend}
        build_instance(Monoid, cls, attrs)
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

# Foldable
foldr = lambda x, f: Foldable[x].foldr(x, f)

# Traversable
length = Traversable.length

# Monoid
mempty = lambda x: Monoid[x].mempty
mappend = lambda x, y: Monoid[x].mappend(x, y)
