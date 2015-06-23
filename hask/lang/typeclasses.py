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
    @classmethod
    def make_instance(typeclass, cls, minBound, maxBound):
        attrs = {"minBound":minBound, "maxBound":maxBound}
        build_instance(Bounded, cls, attrs)
        return

    @classmethod
    def derive_instance(typeclass, cls):
        # All data constructors must be enums
        for data_con in cls.__constructors__:
            if not isinstance(data_con, cls):
                raise TypeError("Cannot derive Bounded; %s is not an enum" %
                                 data_con.__name__)

        maxBound = lambda s: cls.__constructors__[0]
        minBound = lambda s: cls.__constructors__[-1]
        Bounded.make_instance(cls, minBound=minBound, maxBound=maxBound)
        return


class Enum(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, toEnum, fromEnum):
        def succ(a):
            return fromEnum(toEnum(a) + 1)

        def pred(a):
            return fromEnum(toEnum(a) - 1)

        def enumFromThen(start, second):
            pointer = toEnum(start)
            step = toEnum(second) - pointer
            while True:
                yield fromEnum(pointer)
                pointer += step
            return

        def enumFrom(start):
            return enumFromThen(start, succ(start))

        def enumFromThenTo(start, second, end):
            pointer, stop = toEnum(start), toEnum(end)
            step = toEnum(second) - pointer
            while pointer <= stop:
                yield fromEnum(pointer)
                pointer += step
            return

        def enumFromTo(start, end):
            return enumFromThenTo(start, succ(start), end)

        attrs = {"toEnum":toEnum, "fromEnum":fromEnum, "succ":succ,
                 "pred":pred, "enumFromThen":enumFromThen, "enumFrom":enumFrom,
                 "enumFromThenTo":enumFromThenTo, "enumFromTo":enumFromTo}
        build_instance(Enum, cls, attrs)
        return


def toEnum(a):
    return Enum[a].toEnum(a)

def fromEnum(a):
    return Enum[a].fromEnum(a)

def succ(a):
    return Enum[a].succ(a)

def pred(a):
    return Enum[a].pred(a)

def enumFromThen(start, second):
    return Enum[start].enumFromThen(start, second)

def enumFrom(start):
    return Enum[start].enumFrom(start)

def enumFromThenTo(start, second, end):
    return Enum[start].enumFromThenTo(start, second, end)

def enumFromTo(start, end):
    return Enum[start].enumFromTo(start, end)
