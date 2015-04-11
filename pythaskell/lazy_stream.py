import collections
import itertools

import syntax
from types import Show
from types import Functor
from types import Applicative
from types import Monad
from types import Traversable
from types import Ix

class Seq(object):
    """
    Efficient lazy sequence datatype.
    Usage: see tests.py
    """

    def __init__(self, iterable=None):
        self._evaluated = collections.deque()
        self._gen = itertools.chain([])

        # ugly type assertion
        if type(iterable) in (list, tuple):
            self._evaluated.extend(iterable)
        else:
            self._gen = itertools.chain(self._gen, iterable)
        return

    def _full_evaluate(self):
        self._evaluated.extend(self._gen)
        return

    def __add__(self, iterable):
        self._gen = itertools.chain(self._gen, iterable)
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
                return Seq(list_gen(lst[0], inf, 1))
            elif len(lst) == 3 and lst[2] is Ellipsis:
                # [x, y, ...]
                inc = lst[1] - lst[0]
                return Seq(list_gen(lst[0], inf * inc, inc))
            elif len(lst) == 3 and lst[1] is Ellipsis:
                # [x, ..., y]
                return Seq(list_gen(lst[0], [2], 1))
            elif len(lst) == 4 and lst[3] is Ellipsis:
                # [x, y, ..., z]
                inc = lst[1] - lst[0]
                return Seq(list_gen(lst[0], lst[3], inc))
        return Seq(lst)


l = _list_builder("Syntax error in list comprehension")


## typeclass instances

def _seq_show(self):
    # this needs to be better
    return str(list(self._evaluated))[:-1] + "...]"


def _seq_fmap(self, fn):
    return Seq(itertools.imap(fn, iter(self)))


def _seq_pure(self, x):
    return Seq([x])


def _seq_bind(self, fn):
    return Seq(itertools.chain.from_iterable(self.fmap(fn)))


def _seq_next(self):
    next_iter = next(self._gen)
    self._evaluated.append(next_iter)
    return next_iter


def _seq_iter(self):
    count = 0
    for item in itertools.chain(self._evaluated, self._gen):
        if count > len(self._evaluated):
            self._evaluated.append(item)
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
            while (i+1) > len(self._evaluated):
                next(self)
        else:
            self._full_evaluate()

        # bad typecasting is bad (and inefficient)
        return list(self._evaluated)[ix]
    except (StopIteration, IndexError):
        raise IndexError("Seq index out of range: %s" % i)


Show(Seq, _seq_show)
Functor(Seq, _seq_fmap)
Applicative(Seq, _seq_pure)
Monad(Seq, _seq_bind)
Traversable(Seq, _seq_next, _seq_iter)
Ix(Seq, _seq_getitem)



## todo:

# more testing

# do something interesting with itertools.filter - maybe just overwrite it with
# a version that uses itertools.filter and returns a Seq?

# add folds and Foldable typeclasses

# actually...just spend a lot of time reading this and seeing how best to make
# Haskell out of it
# https://docs.python.org/2/library/itertools.html
