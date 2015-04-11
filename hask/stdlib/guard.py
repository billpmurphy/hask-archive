from ..lang import syntax

## Guards! Guards!

class NoGuardMatchException(Exception):
    pass


class c(syntax.Syntax):
    """
    Guard condition.
    """

    def __init__(self, fn):
        if not hasattr(fn, "__call__"):
            raise ValueError("Guard condition must be callable")
        self._func = fn

        syntax_err_msg = "Syntax error in guard condition"
        super(self.__class__, self).__init__(syntax_err_msg)

    def has_return_value(self):
        return hasattr(self, "_return_value")

    def return_value(self):
        if not self.has_return_value():
            raise SyntaxError("Guard condition does not have return value")
        else:
            return self._return_value

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def __rshift__(self, value):
        if self.has_return_value():
            raise SyntaxError("Multiple return values in guard condition")
        self._return_value = value
        return self


otherwise = c(lambda _: True)


class guard(syntax.Syntax):
    """
    Usage:

    ~(guard(8)
        | c(lambda x: x < 5) >> "less than 5"
        | c(lambda x: x < 9) >> "less than 9"
        | otherwise          >> "unsure"
    )
    """
    def __init__(self, value):
        self._value = value
        self._tried_to_match = False
        self._guard_satisfied = False

        syntax_err_msg = "Syntax error in guard"
        super(self.__class__, self).__init__(syntax_err_msg)

    def __or__(self, cond):
        if self._guard_satisfied:
            return self

        self._tried_to_match = True

        if not isinstance(cond, c):
            raise SyntaxError("Guard expression contains non-condition")

        if not cond.has_return_value():
            raise SyntaxError("Condition expression is missing return value")

        if cond(self._value):
            self._guard_satisfied = True
            self._return_value = cond.return_value()
        return self

    def __invert__(self):
        if not self._tried_to_match:
            raise SyntaxError("No conditions in guard expression")

        if self._guard_satisfied:
            return self._return_value
        raise NoGuardMatchException("No match found in guard")


