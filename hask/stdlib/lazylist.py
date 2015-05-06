import collections
import itertools

from ..lang import syntax
from ..lang.typeclasses import Enum
from ..lang.typeclasses import Read
from ..lang.typeclasses import Show
from ..lang.typeclasses import Eq
from ..lang.typeclasses import Functor
from ..lang.typeclasses import Applicative
from ..lang.typeclasses import Monad
from ..lang.typeclasses import Traversable
from ..lang.typeclasses import Ix
from ..lang.typeclasses import Iterator
from ..lang.typeclasses import Foldable


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

    def __add__(self, iterable):
        self.unevaluated = itertools.chain(self.unevaluated, iterable)
        return self

    def __repr__(self):
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
Traversable(List, List.__iter__)
Iterator(List, List.__next__)
Ix(List, List.__getitem__)


class __list_comprehension__(syntax.Syntax):
    """
    Syntactic construct for Haskell-style list comprehensions.
    """
    def __getitem__(self, lst):

        if type(lst) in (tuple, list) and len(lst) < 5 and Ellipsis in lst:
            # L[x, ...]
            if len(lst) == 2 and lst[1] is Ellipsis:
                return List(Enum.enumFrom(lst[0]))

            # L[x, y, ...]
            elif len(lst) == 3 and lst[2] is Ellipsis:
                return List(Enum.enumFromThen(lst[0], lst[1]))

            # L[x, ..., y]
            elif len(lst) == 3 and lst[1] is Ellipsis:
                return List(Enum.enumFromTo(lst[0], lst[2]))

            # L[x, y, ..., z]
            elif len(lst) == 4 and lst[2] is Ellipsis:
                return List(Enum.enumFromThenTo(lst[0], lst[1], lst[3]))

            else:
                raise SyntaxError("Invalid list comprehension")
        return List(lst)


L = __list_comprehension__("Syntax error in list comprehension")
