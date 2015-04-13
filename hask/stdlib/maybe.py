from ..lang.type_system import typ
from ..lang.typeclasses import Typeable
from ..lang.typeclasses import Show
from ..lang.typeclasses import Eq
from ..lang.typeclasses import Num
from ..lang.typeclasses import Functor
from ..lang.typeclasses import Applicative
from ..lang.typeclasses import Monad


## Maybe monad

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

    def __eq__(self, other):
        if self._is_nothing and other._is_nothing:
            return True
        elif not self._is_nothing and not other._is_nothing:
            return self._value == other._value
        return False

    def __repr__(self):
        if self._is_nothing:
            return "Nothing"
        return "Just(%s)" % self._value

    def __type__(self):
        return typ(self.__class__, self._value.__class__)

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

Typeable(Maybe, Maybe.__type__)
Show(Maybe, Maybe.__repr__)
Eq(Maybe, Maybe.__eq__)
Functor(Maybe, Maybe.fmap)
Applicative(Maybe, Maybe.pure)
Monad(Maybe, Maybe.bind)


## Decorators - need a clever way of making these into a typeclass or something

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
