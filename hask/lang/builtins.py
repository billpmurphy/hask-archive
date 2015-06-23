import collections
import itertools

from hindley_milner import TypeVariable
from hindley_milner import ListType

from type_system import Hask
from type_system import typeof
from type_system import build_ADT
from type_system import TypedFunc

from typeclasses import Show
from typeclasses import Eq
from typeclasses import Ord
from typeclasses import Enum
from typeclasses import enumFromThenTo
from typeclasses import Bounded
from typeclasses import Read


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
        (+) :: [a] -> [a] -> [a]

        + is the list concatenation operator, equivalent to ++ in Haskell and +
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

    def type(self):
        if len(self) == 0:
            return ListType(TypeVariable())
        return ListType(typeof(self[0]))

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
                    self.__next__()
                except (StopIteration, IndexError):
                    raise IndexError("List index out of range: %s" % i)
        else:
            # if index is negative, evaluate the entire list
            self.eval_all()

        if is_slice:
            istart, istop, istep = ix.indices(len(self.evaluated))
            indices = enumFromThenTo(istart, istart+istep, istop-istep)
            return [self.evaluated[idx] for idx in indices]

        return self.evaluated[ix]



## Typeclass instances for list
Hask.make_instance(List, type=List.type)
Show.make_instance(List, show=List.__str__)
Eq.make_instance(List, eq=List.__eq__)
#Read.make_instance(List, read=eval)
#Foldable.make_instance(List, foldr=List.foldr)
#Traversable.make_instance(List,
#        iter=List.__iter__,
#        getitem=List.__getitem__,
#        len=List.__len__)


#=============================================================================#
# REPL tools (:q, :t, :i)


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
    print(str(typeof(obj)))
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
