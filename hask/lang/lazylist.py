import collections
import itertools

from hindley_milner import TypeVariable
from hindley_milner import ListType
from hindley_milner import unify

from type_system import typeof
from type_system import build_ADT
from type_system import TypedFunc
from type_system import Hask

from typeclasses import Show
from typeclasses import show
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
    def __init__(self, head=None, tail=None):
        self.__head = collections.deque()
        self.__tail = itertools.chain([])
        self.__is_evaluated = True

        if head is not None:
            self.__head.extend(head)
        if tail is not None:
            self.__tail = itertools.chain(self.__tail, tail)
            self.__is_evaluated = False
        return

    def __type__(self):
        if self.__is_evaluated:
            if len(self.__head) == 0:
                return ListType(TypeVariable())
            return ListType(typeof(self[0]))
        elif len(self.__head) == 0:
            self.__next__()
            return self.__type__()
        return ListType(typeof(self[0]))

    def __next__(self):
        if self.__is_evaluated:
            raise StopIteration
        else:
            try:
                next_iter = next(self.__tail)
                if len(self.__head) > 0:
                    unify(typeof(self[0]), typeof(next_iter))
                self.__head.append(next_iter)
            except StopIteration as si:
                self.__is_evaluated = True
        return

    def __evaluate(self):
        """
        Evaluate the entire List.
        """
        while not self.__is_evaluated:
            self.__next__()
        return

    def __rxor__(self, item):
        """
        ^ is the cons operator (equivalent to : in Haskell)
        """
        unify(self.__type__(), ListType(typeof(item)))
        self.__head.appendleft(item)
        return self

    def __add__(self, other):
        """
        (+) :: [a] -> [a] -> [a]

        + is the list concatenation operator, equivalent to ++ in Haskell and +
        for Python lists
        """
        unify(self.__type__(), other.__type__())
        self.__tail = itertools.chain(self.__tail, other)
        return self

    def __str__(self):
        if len(self.__head) == 0 and self.__is_evaluated:
            return "L[[]]"
        elif len(self.__head) == 1 and self.__is_evaluated:
            return "L[[%s]]" % show(self.__head[0])
        body = ", ".join((show(s) for s in self.__head))
        return "L[%s]" % body if self.__is_evaluated else "L[%s ...]" % body

    def __eq__(self, other):
        # this is horrifically inefficient
        return list(self) == list(other)

    def __len__(self):
        self.__evaluate()
        return len(self.__head)

    def __iter__(self):
        count = 0
        # TODO: wrong
        for item in itertools.chain(self.__head, self.__tail):
            if count >= len(self.__head):
                self.__head.append(item)
            count += 1
            yield item

    def __contains__(self, item):
        """Requires an Eq instance"""
        for i in self:
            if i == item:
                return True
        return False

    def __getitem__(self, ix):
        is_slice = isinstance(ix, slice)
        i = ix.stop if is_slice else ix

        # make sure that the list is evaluated enough to do the indexing, but
        # not any more than necessary
        # if index is negative, evaluate the entire list
        if i >= 0:
            while (i+1) > len(self.__head):
                try:
                    self.__next__()
                except (StopIteration, IndexError):
                    raise IndexError("List index out of range: %s" % i)
        else:
            self.__evaluate()

        if is_slice:
            istart, istop, istep = ix.indices(len(self.__head))
            indices = enumFromThenTo(istart, istart+istep, istop-istep)
            return List(head=[self.__head[idx] for idx in indices])
        return self.__head[ix]

    def fmap(self, fn):
        return List(itertools.imap(fn, iter(self)))

    def pure(self, x):
        return List(head=[x])

    def bind(self, fn):
        return List(itertools.chain.from_iterable(self.fmap(fn)))

    def foldr(self, fn, a):
        # note that this is not lazy
        for i in reversed(self):
            a = fn(i, a)
        return a


## Typeclass instances for list
Show.make_instance(List, show=List.__str__)
Eq.make_instance(List, eq=List.__eq__)
Read.make_instance(List, read=eval)


#=============================================================================#
# List comprehension syntax


class __list_comprehension__(Syntax):
    """
    L is the syntactic construct for Haskell-style list comprehensions and lazy
    list creation. To create a new List, just wrap an interable in L[ ].

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
        if isinstance(lst, List):
            return lst

        elif isinstance(lst, tuple) and len(lst) < 5 and \
                any((Ellipsis is x for x in lst)):
            # L[x, ...]
            if len(lst) == 2 and lst[1] is Ellipsis:
                return List(tail=enumFrom(lst[0]))

            # L[x, y, ...]
            elif len(lst) == 3 and lst[2] is Ellipsis:
                return List(tail=enumFromThen(lst[0], lst[1]))

            # L[x, ..., y]
            elif len(lst) == 3 and lst[1] is Ellipsis:
                return List(tail=enumFromTo(lst[0], lst[2]))

            # L[x, y, ..., z]
            elif len(lst) == 4 and lst[2] is Ellipsis:
                return List(tail=enumFromThenTo(lst[0], lst[1], lst[3]))

            self.raise_invalid("Invalid list comprehension: %s" % lst)

        elif hasattr(lst, "next") or hasattr(lst, "__next__"):
            return List(tail=lst)

        return List(head=lst)


L = __list_comprehension__("Invalid input to list constructor")
