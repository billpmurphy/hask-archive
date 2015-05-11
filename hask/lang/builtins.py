import collections
import itertools

from type_system import _t
from typeclasses import Typeable
from typeclasses import Enum
from typeclasses import Num
from typeclasses import Read
from typeclasses import Show
from typeclasses import Eq
from typeclasses import Functor
from typeclasses import Applicative
from typeclasses import Monad
from typeclasses import Traversable
from typeclasses import Ix
from typeclasses import Iterator
from typeclasses import Foldable


# Wrappers for Python builtins (for cosmetic purposes only)

Int = int
Float = float
String = str

Show.register(int)
Show.register(float)
Show.register(complex)

Eq.register(int)
Eq.register(float)
Eq.register(complex)

Num.register(int)
Num.register(float)
Num.register(complex)


# Maybe

class Maybe(object):

    def __init__(self, value):
        self._is_nothing = False
        self._value = value

    @staticmethod
    def _make_nothing():
        """
        Build the standard Nothing value.
        """
        nothing = Just(None)
        nothing._is_nothing = True
        return nothing

    def _type(self):
        return (Maybe, self._value.__class__)

    def __eq__(self, other):
        if _t(self) != _t(other):
            return False
        elif self._is_nothing and other._is_nothing:
            return True
        elif not self._is_nothing and not other._is_nothing:
            return self._value == other._value
        return False

    def __repr__(self):
        if self._is_nothing:
            return "Nothing"
        return "Just(%s)" % repr(self._value)

    def fmap(self, fn):
        return Nothing if self._is_nothing else Just(fn(self._value))

    def pure(self, value):
        return Just(value)

    def bind(self, fn):
        return Nothing if self._is_nothing else fn(self._value)


class Just(Maybe):
    def __init__(self, value):
        super(self.__class__, self).__init__(value)
        self._is_nothing = False


Nothing = Maybe._make_nothing()

Typeable(Maybe, Maybe._type)
Show(Maybe, Maybe.__repr__)
Eq(Maybe, Maybe.__eq__)
Functor(Maybe, Maybe.fmap)
Applicative(Maybe, Maybe.pure)
Monad(Maybe, Maybe.bind)


def in_maybe(fn, *args, **kwargs):
    """
    Apply arguments to a function. If the function call raises an exception,
    return Nothing. Otherwise, take the result and wrap it in a Just.
    """
    def _closure_in_maybe(*args, **kwargs):
        try:
            return Just(fn(*args, **kwargs))
        except:
            return Nothing
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_maybe(*args, **kwargs)
    return _closure_in_maybe


# Either

class Either(object):
    def __init__(self, value):
        self._value = value

    def __eq__(self, other):
        if self._is_left == other._is_left:
            return self._value == other._value
        return False

    def __repr__(self):
        if self._is_left:
            return "Left(%s)" % self._value
        return "Right(%s)" % self._value

    def fmap(self, fn):
        return self if self._is_left else Right(fn(self._value))

    def pure(self, value):
        return Right(value)

    def bind(self, fn):
        return self if self._is_left else fn(self._value)



class Left(Either):
    def __init__(self, value, is_left=True):
        super(self.__class__, self).__init__(value)
        self._is_left = True


class Right(Either):
    def __init__(self, value, is_left=False):
        super(self.__class__, self).__init__(value)
        self._is_left = False


## Either instances

Show(Either, Either.__repr__)
Eq(Either, Either.__eq__)
Functor(Either, Either.fmap)
Applicative(Either, Either.pure)
Monad(Either, Either.bind)


def in_either(fn, *args, **kwargs):
    """
    Apply arguments to a function. If the function call raises an exception,
    return the exception inside Left. Otherwise, take the result and wrap it in
    a Right.
    """
    def _closure_in_either(*args, **kwargs):
        try:
            return Right(fn(*args, **kwargs))
        except Exception as e:
            return Left(e)
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_either(*args, **kwargs)
    return _closure_in_either


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
