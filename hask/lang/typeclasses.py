import operator

from type_system import Typeclass
from type_system import ADT
from type_system import is_builtin
from type_system import has_instance
from type_system import nt_to_tuple
from type_system import build_instance

from syntax import instance
from syntax import sig
from syntax import H


#=============================================================================#
# Basic typeclasses


class Read(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, read):
        build_instance(Read, cls, {"read":read})
        return

    @classmethod
    def derive_instance(typeclass, cls):
        Read.make_instance(cls, read=eval)
        return


class Show(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, show):
        __show__ = show ** (H/ "a" >> str)
        show = lambda self: __show__(self)

        build_instance(Show, cls, {"show":show})
        if not is_builtin(cls):
            cls.__repr__ = show
            cls.__str__ = show
        return

    @classmethod
    def derive_instance(typeclass, cls):
        def show(self):
            if len(self.__class__._fields) == 0:
                return self.__class__.__name__

            nt_tup = nt_to_tuple(self)
            if len(nt_tup) == 1:
                tuple_str = "(%s)" % Show[nt_tup[0]].show(nt_tup[0])
            else:
                tuple_str = Show[nt_tup].show(nt_tup)

            return "{0}{1}".format(self.__class__.__name__, tuple_str)
        Show.make_instance(cls, show=show)
        return


@sig(H/ "a" >> str)
def show(obj):
    return Show[obj].show(obj)


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
        def default_ne(self, other):
            return not eq(self, other)

        __eq__ = eq ** (H/ "a" >> "a" >> bool)
        __ne__ = (default_ne if ne is None else ne) ** (H/ "a" >> "a" >> bool)
        eq = lambda self, other: __eq__(self, other)
        ne = lambda self, other: __ne__(self, other)

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
        def_le = lambda s, o: s.__lt__(o) or s.__eq__(o)
        def_gt = lambda s, o: not s.__lt__(o) and not s.__eq__(o)
        def_ge = lambda s, o: not s.__lt__(o) or s.__eq__(o)

        __lt__ = lt ** (H/ "a" >> "a" >> bool)
        __le__ = (def_le if le is None else le) ** (H/ "a" >> "a" >> bool)
        __gt__ = (def_gt if gt is None else gt) ** (H/ "a" >> "a" >> bool)
        __ge__ = (def_ge if ge is None else ge) ** (H/ "a" >> "a" >> bool)

        lt = lambda self, other: __lt__(self, other)
        le = lambda self, other: __le__(self, other)
        gt = lambda self, other: __gt__(self, other)
        ge = lambda self, other: __ge__(self, other)

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
            if self.__ADT_slot__ == other.__ADT_slot__:
                if len(nt_to_tuple(self)) == 0:
                    return fn((), ())
                zipped_fields = zip(nt_to_tuple(self), nt_to_tuple(other))
                return all((fn(a, b) for a, b in zipped_fields))
            return fn(self.__ADT_slot__, other.__ADT_slot__)

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


instance(Show, str).where(show=str.__repr__)
instance(Show, int).where(show=int.__str__)
instance(Show, long).where(show=long.__str__)
instance(Show, float).where(show=tuple.__str__)
instance(Show, complex).where(show=complex.__str__)
instance(Show, bool).where(show=bool.__str__)
instance(Show, list).where(show=list.__str__)
instance(Show, tuple).where(show=tuple.__str__)

instance(Eq, str).where(eq=str.__eq__, ne=str.__ne__)
instance(Eq, int).where(eq=int.__eq__, ne=int.__ne__)
instance(Eq, long).where(eq=long.__eq__, ne=long.__ne__)
instance(Eq, float).where(eq=float.__eq__, ne=float.__ne__)
instance(Eq, complex).where(eq=complex.__eq__, ne=complex.__ne__)
instance(Eq, bool).where(eq=bool.__eq__, ne=bool.__ne__)
instance(Eq, list).where(eq=list.__eq__, ne=list.__ne__)
instance(Eq, tuple).where(eq=tuple.__eq__, ne=tuple.__ne__)

instance(Ord, str).where(lt=str.__lt__, le=str.__le__,
                         gt=str.__gt__, ge=str.__ge__)
instance(Ord, int).where(lt=int.__lt__, le=int.__le__,
                         gt=int.__gt__, ge=int.__ge__)
instance(Ord, long).where(lt=long.__lt__, le=long.__le__,
                          gt=long.__gt__, ge=long.__ge__)
instance(Ord, float).where(lt=float.__lt__, le=float.__le__,
                           gt=float.__gt__, ge=float.__ge__)
instance(Ord, complex).where(lt=complex.__lt__, le=complex.__le__,
                             gt=complex.__gt__, ge=complex.__ge__)
instance(Ord, bool).where(lt=bool.__lt__, le=bool.__le__,
                          gt=bool.__gt__, ge=bool.__ge__)
instance(Ord, list).where(lt=list.__lt__, le=list.__le__,
                          gt=list.__gt__, ge=list.__ge__)
instance(Ord, tuple).where(lt=tuple.__lt__, le=tuple.__le__,
                           gt=tuple.__gt__, ge=tuple.__ge__)

instance(Enum, int).where(toEnum=int, fromEnum=int)
instance(Enum, long).where(toEnum=int, fromEnum=long)
instance(Enum, bool).where(toEnum=int, fromEnum=bool)
instance(Enum, str).where(toEnum=ord, fromEnum=chr)


