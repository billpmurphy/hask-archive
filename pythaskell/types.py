## Some basic typeclasses

class Functor(object):
    def __init__(self, _value):
        self._value = _value

    def fmap(self, fn):
        raise NotImplementedError()

    def __ne__(self, fn):
        return self.fmap(fn)


class Monad(Functor):
    def pure(self, value):
        raise NotImplementedError()

    def bind(self, fn):
        raise NotImplementedError()

    def __rshift__(self, fn):
        return self.bind(fn)

## Maybe monad

class NothingException(Exception):
    pass

class Maybe(Monad):
    def __init__(self, value):
        self._is_nothing = False
        self._value = value

    def fmap(self, fn):
        return Nothing if self._is_nothing else Just(fn(self._value))

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


class Either(Monad):
    def __init__(self, value, is_left):
        self._value = value
        self._is_left = is_left

    def fmap(self, fn):
        pass

    def bind(self, fn):
        pass

    def __eq__(self, other):
        if self._is_left == other._is_left:
            return self._value == other._value
        return False

    def __repr__(self):
        if self._is_left:
            return "Left(%s)" % self._value
        return "Right(%s)" % self._value


class Left(Either):
    def __init__(self, value):
        super(Either, self).__init__(value, is_left=True)


class Right(Either):
    def __init__(self, value):
        super(Either, self).__init__(value, is_left=False)
