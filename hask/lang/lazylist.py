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
from syntax import instance


#=============================================================================#
# List


class List(collections.Sequence, Hask):
    """
    Statically typed lazy sequence datatype.

    See help(L) for more information.
    """
    def __init__(self, head=None, tail=None):
        self.__head = []
        self.__tail = itertools.chain([])
        self.__is_evaluated = True

        if head is not None and len(head) > 0:
            fst = head[0]
            for fst, other in zip(itertools.repeat(fst), head):
                unify(typeof(fst), typeof(other))
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
            self.__next()
            return self.__type__()

        return ListType(typeof(self[0]))

    def __next(self):
        """
        Evaluate the next element of the tail, and add it to the head.
        """
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
            self.__next()
        return

    def __rxor__(self, item):
        """
        ^ is the cons operator (equivalent to : in Haskell)
        """
        unify(self.__type__(), ListType(typeof(item)))
        if self.__is_evaluated:
            return List(head=[item] + self.__head)
        return List(head=[item] + self.__head, tail=self.__tail)

    def __add__(self, other):
        """
        (+) :: [a] -> [a] -> [a]

        + is the list concatenation operator, equivalent to ++ in Haskell and +
        for Python lists
        """
        unify(self.__type__(), typeof(other))
        if self.__is_evaluated and other.__is_evaluated:
            self.__head.extend(other.__head)
        else:
            self.__tail = itertools.chain(self.__tail, iter(other))
        return self

    def __str__(self):
        if len(self.__head) == 0 and self.__is_evaluated:
            return "L[[]]"

        elif len(self.__head) == 1 and self.__is_evaluated:
            return "L[[%s]]" % show(self.__head[0])

        body = ", ".join((show(s) for s in self.__head))
        return "L[%s]" % body if self.__is_evaluated else "L[%s ...]" % body

    def __cmp__(self, other):
        if self.__is_evaluated and other.__is_evaluated:
            return cmp(self.__head, other.__head)

        elif len(self.__head) >= len(other.__head):
            # check the evaluated heads
            heads = zip(self.__head[:len(other.__head)], other.__head)
            heads_comp = ((cmp(h1, h2) for h1, h2 in heads))
            for comp in heads_comp:
                if comp != 0:
                    return comp

            # evaluate the shorter-headed list until it is the same size
            while len(self.__head) > len(other.__head):
                if other.__is_evaluated:
                    return 1
                other.__next()
                comp = cmp(other.__head[-1], self.__head[len(other.__head)-1])
                if comp != 0:
                    return comp

            # evaluate the tails, checking each time
            while not self.__is_evaluated or not other.__is_evaluated:
                if not self.__is_evaluated:
                    self.__next()
                if not other.__is_evaluated:
                    other.__next()

                len_comp = cmp(len(self.__head), len(other.__head))
                if len_comp != 0:
                    return len_comp

                if len(self.__head) > 0:
                    value_comp = cmp(self.__head[-1], other.__head[-1])
                    if value_comp != 0:
                        return value_comp

        elif len(other.__head) > len(self.__head):
            return other.__cmp__(self)

        return 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        return self.__cmp__(other) == -1

    def __gt__(self, other):
        return self.__cmp__(other) == 1

    def __le__(self, other):
        comp = self.__cmp__(other)
        return comp in (-1, 0)

    def __ge__(self, other):
        comp = self.__cmp__(other)
        return comp in (1, 0)

    def __len__(self):
        self.__evaluate()
        return len(self.__head)

    def __iter__(self):
        for item in self.__head:
            yield item

        for item in self.__tail:
            self.__head.append(item)
            yield item

    def __getitem__(self, ix):
        is_slice = isinstance(ix, slice)
        i = ix.stop if is_slice else ix

        # make sure that the list is evaluated enough to do the indexing, but
        # not any more than necessary
        # if index is negative, evaluate the entire list
        if i >= 0:
            while (i+1) > len(self.__head):
                try:
                    self.__next()
                except (StopIteration, IndexError):
                    raise IndexError("List index out of range: %s" % i)
        else:
            self.__evaluate()

        if is_slice:
            istart, istop, istep = ix.indices(len(self.__head))
            indices = enumFromThenTo(istart, istart+istep, istop-istep)
            return List(head=[self.__head[idx] for idx in indices])
        return self.__head[ix]


## Basic typeclass instances for list
instance(Show, List).where(
    show = List.__str__
)

instance(Eq, List).where(
    eq = List.__eq__
)

instance(Ord, List).where(
   lt = List.__lt__,
   gt = List.__gt__,
   le = List.__le__,
   ge = List.__ge__
)

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
