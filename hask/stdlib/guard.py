from ..lang import syntax


## Guards! Guards!

class NoGuardMatchException(Exception):
    pass


class GuardCondition(syntax.Syntax):
    """
    Guard condition.
    """

    def __init__(self, fn):
        if not hasattr(fn, "__call__"):
            raise ValueError("Guard condition must be callable")
        self.__func = fn
        self.__return_value = None
        self.__has_return_value = False
        self.__syntax_err_msg = "Syntax error in guard condition"
        super(self.__class__, self).__init__(self.__syntax_err_msg)

    def has_return_value(self):
        return self.__has_return_value

    def return_value(self):
        if not self.has_return_value():
            raise SyntaxError("Guard condition does not have return value")
        else:
            return self.__return_value

    def check(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

    def __rshift__(self, value):
        if isinstance(value, c):
            raise SyntaxError(self.__syntax_err_msg)

        if self.has_return_value():
            raise SyntaxError("Multiple return values in guard condition")

        self.__return_value = value
        self.__has_return_value = True
        return self


c = GuardCondition
otherwise = lambda: c(lambda _: True)


class guard(syntax.Syntax):
    """
    Usage:

    >>> ~(guard(8)
    ...    | c(lambda x: x < 5) >> "less than 5"
    ...    | c(lambda x: x < 9) >> "less than 9"
    ...    | otherwise          >> "unsure"
    ... )
    """
    def __init__(self, value):
        self.__value = value
        self.__tried_to_match = False
        self.__guard_satisfied = False

        self.__syntax_err_msg = "Syntax error in guard"
        super(self.__class__, self).__init__(self.__syntax_err_msg)

    def __or__(self, cond):
        if self.__guard_satisfied:
            return self

        self.__tried_to_match = True

        if not isinstance(cond, c):
            raise SyntaxError("Guard expression contains non-condition")

        if not cond.has_return_value():
            raise SyntaxError("Condition expression is missing return value")

        if cond.check(self.__value):
            self.__guard_satisfied = True
            self.__return_value = cond.return_value()
        return self

    def __invert__(self):
        if not self.__tried_to_match:
            raise SyntaxError("No conditions in guard expression")

        if self.__guard_satisfied:
            return self.__return_value
        raise NoGuardMatchException("No match found in guard")
