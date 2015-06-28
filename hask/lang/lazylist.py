import collections
import itertools

from hindley_milner import TypeVariable
from hindley_milner import ListType

from type_system import typeof
from type_system import build_ADT
from type_system import TypedFunc
from type_system import Hask

from typeclasses import Show
from typeclasses import Eq
from typeclasses import Ord
from typeclasses import Enum
from typeclasses import enumFrom
from typeclasses import enumFromThen
from typeclasses import enumFromTo
from typeclasses import enumFromThenTo
from typeclasses import Bounded
from typeclasses import Read

from syntax import Syntax


#=============================================================================#
# List


class List(collections.Sequence, Hask):
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

    def __rxor__(self, item):
        """
        ^ is the cons operator (equivalent to : in Haskell)
        """
        return List([item]) + self

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

    def __type__(self):
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
            return List([self.evaluated[idx] for idx in indices])

        return self.evaluated[ix]



## Typeclass instances for list
Show.make_instance(List, show=List.__str__)
Eq.make_instance(List, eq=List.__eq__)
Read.make_instance(List, read=eval)
#Foldable.make_instance(List, foldr=List.foldr)
#Traversable.make_instance(List,
#        iter=List.__iter__,
#        getitem=List.__getitem__,
#        len=List.__len__)


#=============================================================================#
# List comprehension


class __list_comprehension__(Syntax):
    """
    Syntactic construct for Haskell-style list comprehensions and lazy list
    creation.

    List comprehensions can be used with any instance of Enum, including the
    built-in types int, long, float, and char.

    There are four basic list comprehension patterns:

    >>> L[1, ...]
    # list from 1 to infinity, counting by ones

    >>> L[1, 3, ...]
    # list from 1 to infinity, counting by twos

    >>> L[1, ..., 20]
    # list from 1 to 20 (inclusive), counting by ones

    >>> L[1, 5, ..., 20]
    # list from 1 to 20 (inclusive), counting by fours
    """
    def __getitem__(self, lst):
        if isinstance(lst, tuple) and len(lst) < 5 and \
                any((Ellipsis is x for x in lst)):
            # L[x, ...]
            if len(lst) == 2 and lst[1] is Ellipsis:
                return List(enumFrom(lst[0]))

            # L[x, y, ...]
            elif len(lst) == 3 and lst[2] is Ellipsis:
                return List(enumFromThen(lst[0], lst[1]))

            # L[x, ..., y]
            elif len(lst) == 3 and lst[1] is Ellipsis:
                return List(enumFromTo(lst[0], lst[2]))

            # L[x, y, ..., z]
            elif len(lst) == 4 and lst[2] is Ellipsis:
                return List(enumFromThenTo(lst[0], lst[1], lst[3]))

            self.raise_invalid()
        return List(lst)


L = __list_comprehension__("Invalid list comprehension")


