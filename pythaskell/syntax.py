class Syntax(object):
    """
    Superclass for new syntactic constructs. By default, a piece of syntax
    should raise a syntax error with a standard error message if the syntax
    object is used with a Python buildin operator. Subclasses may override
    these methods to define what syntax is valid.
    """
    def _raise_invalid(self):
        raise SyntaxError(self.__class__._syntax_err_msg)

    def __len__(self, _): self._raise_invalid()
    def __getitem__(self, _): self._raise_invalid()
    def __setitem__(self, _): self._raise_invalid()
    def __delitem__(self, _): self._raise_invalid()
    def __iter__(self, _): self._raise_invalid()
    def __reversed__(self, _): self._raise_invalid()
    def __contains__(self, _): self._raise_invalid()
    def __missing__(self, _): self._raise_invalid()

    def __call__(self, _): self._raise_invalid()
    def __enter__(self): self._raise_invalid()
    def __exit__(self, exception_type, exception_value, traceback):
        self._raise_invalid()

    def __gt__(self, _): self._raise_invalid()
    def __lt__(self, _): self._raise_invalid()
    def __ge__(self, _): self._raise_invalid()
    def __le__(self, _): self._raise_invalid()
    def __pos__(self, _): self._raise_invalid()
    def __neg__(self, _): self._raise_invalid()
    def __abs__(self, _): self._raise_invalid()
    def __invert__(self, _): self._raise_invalid()
    def __round__(self, _): self._raise_invalid()
    def __floor__(self, _): self._raise_invalid()
    def __ceil__(self, _): self._raise_invalid()
    def __trunc__(self, _): self._raise_invalid()

    def __add__(self, _): self._raise_invalid()
    def __sub__(self, _): self._raise_invalid()
    def __mul__(self, _): self._raise_invalid()
    def __floordiv__(self, _): self._raise_invalid()
    def __div__(self, _): self._raise_invalid()
    def __mod__(self, _): self._raise_invalid()
    def __divmod__(self, _): self._raise_invalid()
    def __rpow__(self, _): self._raise_invalid()
    def __lshift__(self, _): self._raise_invalid()
    def __rshift__(self, _): self._raise_invalid()
    def __or__(self, _): self._raise_invalid()
    def __and__(self, _): self._raise_invalid()
    def __xor__(self, _): self._raise_invalid()

    def __radd__(self, _): self._raise_invalid()
    def __rsub__(self, _): self._raise_invalid()
    def __rmul__(self, _): self._raise_invalid()
    def __rfloordiv__(self, _): self._raise_invalid()
    def __rdiv__(self, _): self._raise_invalid()
    def __rmod__(self, _): self._raise_invalid()
    def __rdivmod__(self, _): self._raise_invalid()
    def __rrpow__(self, _): self._raise_invalid()
    def __rlshift__(self, _): self._raise_invalid()
    def __rrshift__(self, _): self._raise_invalid()
    def __ror__(self, _): self._raise_invalid()
    def __rand__(self, _): self._raise_invalid()
    def __rxor__(self, _): self._raise_invalid()

    def __iadd__(self, _): self._raise_invalid()
    def __isub__(self, _): self._raise_invalid()
    def __imul__(self, _): self._raise_invalid()
    def __ifloordiv__(self, _): self._raise_invalid()
    def __idiv__(self, _): self._raise_invalid()
    def __imod__(self, _): self._raise_invalid()
    def __idivmod__(self, _): self._raise_invalid()
    def __irpow__(self, _): self._raise_invalid()
    def __ilshift__(self, _): self._raise_invalid()
    def __irshift__(self, _): self._raise_invalid()
    def __ior__(self, _): self._raise_invalid()
    def __iand__(self, _): self._raise_invalid()
    def __ixor__(self, _): self._raise_invalid()


## Guards! Guards!

class NoGuardMatchException(Exception):
    pass


class c(Syntax):
    """
    Guard condition.
    """
    _syntax_err_msg = "Syntax error in guard condition"

    def __init__(self, fn):
        if not hasattr(fn, "__call__"):
            raise ValueError("Guard condition must be callable")
        self._func = fn

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


class guard(object):
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


## "case of" pattern matching

## clean up this sick filth

class Underscore(object):
    """
    Singleton for `__`.
    __ is the the wildcard pattern that matches anything in a caseof
    expression.
    """
    pass

__ = Underscore()

class NoCaseMatchException(Exception):
    pass

class CaseExprLocalBind(object):
    def __init__(self, key):
        self.key = key

def _p(key):
    """
    _p() is a special function that can only be used inside of a caseof
    expression. Inside a match expression, p() can bind temporary variables
    that can be used in the
    """
    try:
        if caseof._ready_for_pattern:
            return CaseExprLocalBind(key)
        elif key in caseof._caseof_bound_vars:
            return caseof._caseof_bound_vars[key]
        raise NameError("caseof local variable %s doesn't exist" % key)
    except AttributeError:
        raise SyntaxError("Can't use _p() outside a `caseof` expression")
    return


class Wildcard(object):
    pass


class caseof(Syntax):
    """
    Pattern matching similar to Haskell's "case of" syntax.

    Matching values:
    ~(caseof(a)
        / (1, 2)    % a
        / (2, 2)    % a
        / (3, str)  % 2
        / __         % "Not found")

    Matching types:
    ~(caseof(a)
        / str   % a
        / float % str(round(1, 0))
        / __    % str(a))

    Partial matching with both types and values:
    """
    def __init__(self, value):
        self._value = value
        self._return_value = None

        caseof._ready_for_pattern = True
        self._is_matched = False
        self._tried_to_match = False
        self._matching_finished = False

        caseof._caseof_bound_vars = {}

    @staticmethod
    def match(value, pattern):
        caseof._caseof_bound_vars = {}
        if isinstance(pattern, CaseExprLocalBind):
            caseof._caseof_bound_vars[pattern.key] = value
            return True
        elif isinstance(pattern, type):
            return isinstance(value, pattern)
        elif pattern is __:
            return True
        elif type(value) == type(pattern):
            if pattern == value:
                return True
            elif hasattr(pattern, "__iter__") and hasattr(value, "__iter__"):
                return all((caseof.match(v, p) for v,p in zip(value, pattern)))
        return False

    def __div__(self, pattern):
        if not caseof._ready_for_pattern:
            raise SyntaxError("Invalid syntax: `%` expected, found `/`")

        caseof._ready_for_pattern = False

        if self._is_matched:
            return self
        self._is_matched = caseof.match(self._value, pattern)

        self._tried_to_match = True
        return self

    def __mod__(self, return_value):
        if caseof._ready_for_pattern:
            raise SyntaxError("Invalid syntax: `/` expected, found `%`")

        caseof._ready_for_pattern = True

        if self._is_matched and not self._matching_finished:
            self._return_value = return_value
            self._matching_finished = True
        return self

    def __invert__(self):
        if not self._tried_to_match:
            raise SyntaxError("No matches in caseof expression")
        if self._is_matched:
            return self._return_value
        raise NoCaseMatchException("Non-exhaustive patterns in case")

    def __repr__(self):
        return "caseof(%s)" % self._value

    def __del__(self):
        """
        At the end of the caseof expression, we need to clean up those class
        variable flags.
        """
        del caseof._caseof_bound_vars
        del caseof._ready_for_pattern
