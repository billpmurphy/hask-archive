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


class LazyList(object):
    """
    Efficient lazy sequence datatype.
    """
    def __init__(self, iterable=None):
        self.evaluated = collections.deque()
        self.unevaluated = itertools.chain([])

        if hasattr(iterable, "next") or hasattr(iterable, "__next__"):
            self.unevaluated = itertools.chain(self.unevaluated, iterable)
        else:
            self.evaluated.extend(iterable)
        return

    def eval_all(self):
        """
        Evaluate the entire list.
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

    def fmap(self, fn):
        return LazyList(itertools.imap(fn, iter(self)))

    def pure(self, x):
        return LazyList([x])

    def bind(self, fn):
        return LazyList(itertools.chain.from_iterable(self.fmap(fn)))

    def __next__(self):
        next_iter = next(self.unevaluated)
        self.evaluated.append(next_iter)
        return next_iter

    def __iter__(self):
        count = 0
        for item in itertools.chain(self.evaluated, self.unevaluated):
            if count >= len(self.evaluated):
                self.evaluated.append(item)
            count += 1
            yield item

    def __getitem__(self, ix):
        is_slice = isinstance(ix, slice)
        i = ix.stop if is_slice else ix
        if i >= 0:
            while (i+1) > len(self.evaluated):
                try:
                    next(self)
                except (StopIteration, IndexError):
                    raise IndexError("LazyList index out of range: %s" % i)
        else:
            # if index is negative, evaluate the entire list
            self.eval_all()

        if is_slice:
            istart, istop, istep = ix.indices(len(self.evaluated))
            indices = Enum.enumFromThenTo(istart, istart+istep, istop-istep)
            return [self.evaluated[idx] for idx in indices]
        return self.evaluated[ix]


## typeclass instances

Read(LazyList)
Show(LazyList, LazyList.__repr__)
Eq(LazyList, LazyList.__eq__)
Functor(LazyList, LazyList.fmap)
Applicative(LazyList, LazyList.pure)
Monad(LazyList, LazyList.bind)
Foldable(LazyList, None) # need to write foldr
Traversable(LazyList, LazyList.__iter__)
Iterator(LazyList, LazyList.__next__)
Ix(LazyList, LazyList.__getitem__)


class __list_builder__(syntax.Syntax):

    def __getitem__(self, lst):

        if type(lst) in (tuple, list) and len(lst) < 5 and Ellipsis in lst:
            # L[x, ...]
            if len(lst) == 2 and lst[1] is Ellipsis:
                return LazyList(Enum.enumFrom(lst[0]))

            # L[x, y, ...]
            elif len(lst) == 3 and lst[2] is Ellipsis:
                return LazyList(Enum.enumFromThen(lst[0], lst[1]))

            # L[x, ..., y]
            elif len(lst) == 3 and lst[1] is Ellipsis:
                return LazyList(Enum.enumFromTo(lst[0], lst[2]))

            # L[x, y, ..., z]
            elif len(lst) == 4 and lst[2] is Ellipsis:
                return LazyList(Enum.enumFromThenTo(lst[0], lst[1], lst[3]))

            else:
                raise SyntaxError("Invalid list comprehension")
        return LazyList(lst)


L = __list_builder__("Syntax error in list comprehension")


## Haskellified versions of basic list functions

def map(fn, iterable):
    return LazyList(itertools.imap(fn, iterable))


def filter(fn, iterable):
    return LazyList(itertools.ifilter(fn, iterable))
