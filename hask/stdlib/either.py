from ..lang.typeclasses import Show
from ..lang.typeclasses import Eq
from ..lang.typeclasses import Num
from ..lang.typeclasses import Functor
from ..lang.typeclasses import Applicative
from ..lang.typeclasses import Monad


class Either(object):
    def __init__(self, value):
        self._value = value


class Left(Either):
    def __init__(self, value, is_left=True):
        super(self.__class__, self).__init__(value)
        self._is_left = True


class Right(Either):
    def __init__(self, value, is_left=False):
        super(self.__class__, self).__init__(value)
        self._is_left = False



## Either instances

def _either_eq(self, other):
    if self._is_left == other._is_left:
        return self._value == other._value
    return False


def _either_repr(self):
    if self._is_left:
        return "Left(%s)" % self._value
    return "Right(%s)" % self._value


def _either_fmap(self, fn):
    return self if self._is_left else Right(fn(self._value))


def _either_pure(self, value):
    return Right(value)


def _either_bind(self, fn):
    return self if self._is_left else fn(self._value)


Show(Either, _either_repr)
Eq(Either, _either_eq)
Functor(Either, _either_fmap)
Applicative(Either, _either_pure)
Monad(Either, _either_bind)


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
