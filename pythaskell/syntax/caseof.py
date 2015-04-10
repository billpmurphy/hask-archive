import syntax

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


class caseof(syntax.Syntax):
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
