import collections
import itertools

# not sure about this
from type_system import HM_typeof
from type_system import build_ADT

from typeclasses import Show
from typeclasses import Eq
from typeclasses import Ord
from typeclasses import Enum
from typeclasses import Num
from typeclasses import Real
from typeclasses import Integral
from typeclasses import Floating
from typeclasses import Fractional
from typeclasses import RealFrac
from typeclasses import RealFloat
from typeclasses import Read
from typeclasses import Functor
from typeclasses import Applicative
from typeclasses import Monad
from typeclasses import Traversable
from typeclasses import Iterator
from typeclasses import Foldable

from hof import Func


#=============================================================================#
# Wrappers for Python builtins (for cosmetic purposes only)


Int = int
Integer = long
Float = float
Complex = complex
String = str


#=============================================================================#
# Typeclasses for Python builtins


Show(str, str.__str__)
Show(int, int.__str__)
Show(long, long.__str__)
Show(float, float.__str__)
Show(complex, complex.__str__)
Show(bool, bool.__str__)
Show(list, list.__str__)
Show(tuple, tuple.__str__)

Eq(str, str.__eq__)
Eq(int, int.__eq__)
Eq(long, long.__eq__)
Eq(float, float.__eq__)
Eq(complex, complex.__eq__)
Eq(bool, bool.__eq__)
Show(list, list.__eq__)
Show(tuple, tuple.__eq__)

Ord(str, str.__lt__, str.__le__, str.__gt__, str.__ge__)
Ord(int, int.__lt__, int.__le__, int.__gt__, int.__ge__)
Ord(long, long.__lt__, long.__le__, long.__gt__, long.__ge__)
Ord(float, float.__lt__, float.__le__, float.__gt__, float.__ge__)
Ord(complex, complex.__lt__, complex.__le__, complex.__gt__, complex.__ge__)
Ord(bool, bool.__lt__, bool.__le__, bool.__gt__, bool.__ge__)
Show(list, list.__ord__)
Show(tuple, tuple.__ord__)



Enum(int,  toEnum=lambda a: a,      fromEnum=lambda a: a)
Enum(long, toEnum=lambda a: a,      fromEnum=lambda a: a)
Enum(bool, toEnum=lambda a: int(a), fromEnum=lambda a: bool(a))


def __signum(a):
    """
    Signum function for python builtin numeric types.
    """
    if a < 0:   return -1
    elif a > 0: return 1
    else:       return 0


Num(int, int.__add__, int.__mul__, abs, __signum, lambda a: int(a),
    int.__neg__, int.__sub__)
Num(long, long.__add__, long.__mul__, abs, __signum, lambda a: long(a),
    long.__neg__, long.__sub__)
Num(float, float.__add__, float.__mul__, abs, __signum, lambda a: float(a),
    float.__neg__, float.__sub__)
Num(complex, complex.__add__, complex.__mul__, abs, __signum,
    lambda a: complex(a), complex.__neg__, complex.__sub__)

Real(int)
Real(long)
Real(float)

Integral(int)
Integral(long)

Fractional(float)

Floating(float)

RealFrac(float)

RealFloat(float)


#=============================================================================#
# Maybe

Maybe, Nothing, Just = build_ADT("Maybe", ["a"],
                                 [("Nothing", []), ("Just", ["a"])],
                                 [Show, Eq, Ord])


Functor(Maybe, lambda x, f: Nothing if x == Nothing else Just(f(x[0])))
Applicative(Maybe, Just)
Monad(Maybe, lambda x, f: Nothing if x == Nothing else f(x[0]))


def in_maybe(fn, *args, **kwargs):
    """
    Decorator for monadic error handling.
    If the decorated function raises an exception, return Nothing. Otherwise,
    take the result and wrap it in a Just.
    """
    def _closure_in_maybe(*args, **kwargs):
        try:
            return Just(fn(*args, **kwargs))
        except:
            return Nothing
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_maybe(*args, **kwargs)
    return _closure_in_maybe


#=============================================================================#
# Either


Either, Left, Right = build_ADT("Either", ["a", "b"],
                                 [("Left", ["b"]), ("Right", ["a"])],
                                 [Show, Eq, Ord])


Functor(Either, lambda v, f: v if Left(v[0]) == v else Right(f(v[0])))
Applicative(Either, Right)
Monad(Either, lambda v, f: v if Left(v[0]) == v else f(v[0]))


def in_either(fn, *args, **kwargs):
    """
    Decorator for monadic error handling.
    If the decorated function raises an exception, return the exception inside
    Left. Otherwise, take the result and wrap it in Right.
    """
    def _closure_in_either(*args, **kwargs):
        try:
            return Right(fn(*args, **kwargs))
        except Exception as e:
            return Left(e)
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_either(*args, **kwargs)
    return _closure_in_either


#=============================================================================#
# List


class List(collections.Sequence):
    """
    Efficient lazy sequence datatype.
    """
    def __init__(self, iterable=None):
        self.evaluated = collections.deque()
        self.unevaluated = itertools.chain([])

        if iterable is None:
            return
        elif hasattr(iterable, "next") or hasattr(iterable, "__next__"):
            self.unevaluated = itertools.chain(self.unevaluated, iterable)
        else:
            self.evaluated.extend(iterable)
        return

    def eval_all(self):
        """
        Evaluate the entire List.
        """
        self.evaluated.extend(self.unevaluated)
        return

    def __rpow__(self, item):
        """
        ** is the cons operator (equivalent to : in Haskell)
        """
        raise NotImplementedError("hmm")

    def __add__(self, iterable):
        """
        + is the list concatenation operator (equivalent to ++ in Haskell and +
        for Python lists
        """
        self.unevaluated = itertools.chain(self.unevaluated, iterable)
        return self

    def __str__(self):
        # this needs to be better
        return str(list(self.evaluated))[:-1] + "...]"

    def __eq__(self, other):
        # this is horrifically inefficient
        return list(self) == list(other)

    def __len__(self):
        self.eval_all()
        return len(self.evaluated)

    def fmap(self, fn):
        return List(itertools.imap(fn, iter(self)))

    def pure(self, x):
        return List([x])

    def bind(self, fn):
        return List(itertools.chain.from_iterable(self.fmap(fn)))

    def foldr(self, fn, a):
        # note that this is not lazy
        for i in reversed(self):
            a = fn(i, a)
        return a

    def __next__(self):
        try:
            next_iter = next(self.unevaluated)
        except StopIteration as si:
            raise si
        self.evaluated.append(next_iter)
        return next_iter

    def __iter__(self):
        count = 0
        for item in itertools.chain(self.evaluated, self.unevaluated):
            if count >= len(self.evaluated):
                self.evaluated.append(item)
            count += 1
            yield item

    def __contains__(self, item):
        for i in self:
            if i == item:
                return True
        return False

    def __getitem__(self, ix):
        is_slice = isinstance(ix, slice)
        i = ix.stop if is_slice else ix

        # make sure that the list is evaluated enough to do the indexing, but
        # not any more than necessary
        if i >= 0:
            while (i+1) > len(self.evaluated):
                try:
                    next(self)
                except (StopIteration, IndexError):
                    raise IndexError("List index out of range: %s" % i)
        else:
            # if index is negative, evaluate the entire list
            self.eval_all()

        if is_slice:
            istart, istop, istep = ix.indices(len(self.evaluated))
            indices = Enum.enumFromThenTo(istart, istart+istep, istop-istep)
            return [self.evaluated[idx] for idx in indices]

        return self.evaluated[ix]



## Typeclass instances for list

Read(List)
Show(List, List.__repr__)
Eq(List, List.__eq__)
Functor(List, List.fmap)
Applicative(List, List.pure)
Monad(List, List.bind)
Foldable(List, List.foldr)
Traversable(List, List.__iter__, List.__getitem__, List.__len__)
Iterator(List, List.__next__)

Functor(Func, Func.fmap)


#=============================================================================#
# REPL tools


def _q(status=None):
    """
    Shorthand for sys.exit() or exit() with no arguments. Equivalent to :q in
    Haskell. Should only be used in the REPL.

    Usage:

    >>> _q()
    """
    if status is None:
        exit()
    exit(status)
    return


def _t(obj):
    """
    Returns a string representing the type of an object, including
    higher-kinded types and ADTs. Equivalent to `:t` in Haskell. Meant to be
    used in the REPL, but might also be useful for debugging.

    Args:
        obj: the object to inspect

    Returns:
        A string representation of the type

    Usage:

    >>> _t(1)
    int

    >>> _t(Just("hello world"))
    Maybe str
    """
    print(str(HM_typeof(obj)))
    return


def _i(obj):
    """
    Show information about an object. Equivalent to `:i` in Haskell or
    help(obj) in Python. Should only be used in the REPL.

    Args:
        obj: the object to inspect

    Usage:

    >>> _i(Just("hello world"))

    >>> _i(Either)
    """
    help(obj)
