import abc

## Some basic "typeclasses"

class Typeclass(object):
    __metaclass__ = abc.ABCMeta


class Num(Typeclass):
    __metaclass__ = abc.ABCMeta


Num.register(int)
Num.register(float)
Num.register(complex)


class Functor(Typeclass):
    __metaclass__ = abc.ABCMeta

    def __init__(self, _value):
        self._value = _value

    def fmap(self, fn):
        raise NotImplementedError()

    def __mul__(self, fn):
        return self.fmap(fn)


class Applicative(Functor):
    __metaclass__ = abc.ABCMeta

    def pure(self, value):
        raise NotImplementedError()


class Monad(Applicative):
    __metaclass__ = abc.ABCMeta

    def bind(self, fn):
        raise NotImplementedError()

    def __rshift__(self, fn):
        return self.bind(fn)


## Maybe monad


class Maybe(Monad):
    __metaclass__ = abc.ABCMeta

    def __init__(self, value):
        self._is_nothing = False
        self._value = value

    def fmap(self, fn):
        return Nothing if self._is_nothing else Just(fn(self._value))

    def pure(self, value):
        return Just(value)

    def bind(self, fn):
        return Nothing if self._is_nothing else fn(self._value)

    def __eq__(self, other):
        if self._is_nothing and other._is_nothing:
            return True
        elif not self._is_nothing and not other._is_nothing:
            return self._value == other._value
        else:
            return False

    def __repr__(self):
        if self._is_nothing:
            return "Nothing"
        else:
            return "Just(%s)" % self._value

    @staticmethod
    def _make_nothing():
        """
        Build the standard Nothing value.
        """
        nothing = Just(None)
        nothing._is_nothing = True
        return nothing


class Just(Maybe):
    def __init__(self, value):
        super(Maybe, self).__init__(value)
        self._is_nothing = False


Nothing = Maybe._make_nothing()


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


# @maybe decorator: Your function will act as if it is always inside in_maybe


class Either(Monad):
    def __init__(self, value):
        self._value = value

    def fmap(self, fn):
        return self if self._is_left else Right(fn(self.value))

    def pure(self, value):
        return Right(value)

    def bind(self, fn):
        return self if self._is_left else fn(self.value)

    def __eq__(self, other):
        if self._is_left == other._is_left:
            return self._value == other._value
        return False

    def __repr__(self):
        if self._is_left:
            return "Left(%s)" % self._value
        return "Right(%s)" % self._value


class Left(Either):
    def __init__(self, value, is_left=True):
        super(Either, self).__init__(value)
        self._is_left = True


class Right(Either):
    def __init__(self, value, is_left=False):
        super(Either, self).__init__(value)
        self._is_left = False


def in_either(fn, *args, **kwargs):
    def _closure_in_either(*args, **kwargs):
        try:
            return Right(fn(*args, **kwargs))
        except Exception as e:
            return Left(e)
    if len(args) > 0 or len(kwargs) > 0:
        return _closure_in_either(*args, **kwargs)
    return _closure_in_either

# @either decorator: Your function will act as if it is always inside in_either
