import collections
import itertools


from types import Show


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

    def next(self):
        return self.__next__()

    def __next__(self):
        next_iter = next(self._gen)
        self._evaluated.append(next_iter)
        return next_iter

    def __getitem__(self, i):
        # if we have a negative index, evaluate the entire sequence
        try:
            if i >= 0:
                while (i+1) > len(self._evaluated):
                    next(self)
            else:
                self._full_evaluate()
            return self._evaluated[i]
        except (StopIteration, IndexError):
            raise IndexError("Seq index out of range: %s" % i)

    def __iter__(self):
        count = 0
        for item in itertools.chain(self._evaluated, self._gen):
            if count > len(self._evaluated):
                self._evaluated.append(item)
            count += 1
            yield item
        raise StopIteration()


## typeclass instances

def _show_seq(self):
    # this needs to be better
    return str(list(self._evaluated))[:-1] + "...]"

Show(Seq, _show_seq)


## todo:

# more testing

# Functor instance that uses itertools.map (and returns a Seq, obvs)
# Applicative instance
# Monad instance that uses itertools.chain.from_iterable and returns a Seq

# do something interesting with itertools.filter - maybe just overwrite it with
# a version that uses itertools.filter and returns a Seq?

# add Traversable and Foldable typeclasses

# actually...just spend a lot of time reading this and seeing how best to make
# Haskell out of it
# https://docs.python.org/2/library/itertools.html
