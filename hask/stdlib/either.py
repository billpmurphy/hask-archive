from ..lang.typeclasses import Show
from ..lang.typeclasses import Eq
from ..lang.typeclasses import Num
from ..lang.typeclasses import Functor
from ..lang.typeclasses import Applicative
from ..lang.typeclasses import Monad


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
