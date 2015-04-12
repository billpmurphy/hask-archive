import collections
import itertools

from ..lang import syntax
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
    Usage: see tests.py
    """

    def __init__(self, iterable=None):
        self.evaluated = collections.deque()
        self.unevaluated = itertools.chain([])

        # ugly type assertion
        if hasattr(iterable, "next") or hasattr(iterable, "__next__"):
            self.unevaluated = itertools.chain(self.unevaluated, iterable)
        else:
            self.evaluated.extend(iterable)
        return

    def eval_all(self):
        self.evaluated.extend(self.unevaluated)
        return

    def __add__(self, iterable):
        self.unevaluated = itertools.chain(self.unevaluated, iterable)
        return self


class _list_builder(syntax.Syntax):

    def __getitem__(self, lst):

        inf = float("inf")
        def list_gen(start, stop, inc):
            while start < stop:
                yield start
                start += inc

        if type(lst) in (tuple, list) and len(lst) < 5 and Ellipsis in lst:
            if len(lst) == 2 and lst[1] is Ellipsis:
                # [x, ...]
                return LazyList(list_gen(lst[0], inf, 1))
            elif len(lst) == 3 and lst[2] is Ellipsis:
                # [x, y, ...]
                inc = lst[1] - lst[0]
                return LazyList(list_gen(lst[0], inf * inc, inc))
            elif len(lst) == 3 and lst[1] is Ellipsis:
                # [x, ..., y]
                return LazyList(list_gen(lst[0], lst[2], 1))
            elif len(lst) == 4 and lst[3] is Ellipsis:
                # [x, y, ..., z]
                inc = lst[1] - lst[0]
                return LazyList(list_gen(lst[0], lst[3], inc))
            else:
                raise SyntaxError("Invalid list comprehension")
        return LazyList(lst)


L = _list_builder("Syntax error in list comprehension")


## typeclass instances

def _seq_show(self):
    # this needs to be better
    return str(list(self.evaluated))[:-1] + "...]"


def _seq_eq(self, other):
    # this is horrifically inefficient
    return list(self) == list(other)


def _seq_fmap(self, fn):
    return LazyList(itertools.imap(fn, iter(self)))


def _seq_pure(self, x):
    return LazyList([x])


def _seq_bind(self, fn):
    return LazyList(itertools.chain.from_iterable(self.fmap(fn)))


def _seq_next(self):
    next_iter = next(self.unevaluated)
    self.evaluated.append(next_iter)
    return next_iter


def _seq_iter(self):
    count = 0
    for item in itertools.chain(self.evaluated, self.unevaluated):
        if count >= len(self.evaluated):
            self.evaluated.append(item)
        count += 1
        yield item


def _seq_getitem(self, ix):
    # if we have a negative index, evaluate the entire sequence
    try:
        if type(ix) == slice:
            i = ix.stop
        else:
            i = ix

        if i >= 0:
            while (i+1) > len(self.evaluated):
                next(self)
        else:
            self.eval_all()

        # bad typecasting is bad (and inefficient)
        return list(self.evaluated)[ix]
    except (StopIteration, IndexError):
        raise IndexError("LazyList index out of range: %s" % i)


Show(LazyList, _seq_show)
Eq(LazyList, _seq_eq)
Functor(LazyList, _seq_fmap)
Applicative(LazyList, _seq_pure)
Monad(LazyList, _seq_bind)
Foldable(LazyList, None) # need to write foldr
Traversable(LazyList, _seq_iter)
Iterator(LazyList, _seq_next)
Ix(LazyList, _seq_getitem)


## todo:

# more testing - something is wrong

# do something interesting with itertools.filter - maybe just overwrite it with
# a version that uses itertools.filter and returns a LazyList?

# add folds and Foldable typeclasses

# actually...just spend a lot of time reading this and seeing how best to make
# Haskell out of it
# https://docs.python.org/2/library/itertools.html
