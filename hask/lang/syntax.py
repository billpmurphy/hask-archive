import operator

import hof
from builtins import List
from typeclasses import Enum


class Syntax(object):
    """
    Superclass for new syntactic constructs. By default, a piece of syntax
    should raise a syntax error with a standard error message if the syntax
    object is used with a Python builtin operator. Subclasses may override
    these methods to define what syntax is valid.
    """
    def __init__(self, err_msg=None):
        if err_msg is not None:
            self.syntax_err_msg = err_msg
        else:
            self.syntax_err_msg = "Syntax error in `%s`" % self.__name__
        return

    def raise_invalid(self, msg=None):
        if msg is not None:
            raise SyntaxError(msg)
        raise SyntaxError(self.syntax_err_msg)

    __syntaxerr__ = lambda s, *a: s.raise_invalid()

    __len__ = __syntaxerr__
    __getitem__ = __syntaxerr__
    __setitem__ = __syntaxerr__
    __delitem__ = __syntaxerr__
    __iter__ = __syntaxerr__
    __reversed__ = __syntaxerr__
    __contains__ = __syntaxerr__
    __missing__ = __syntaxerr__

    __call__ = __syntaxerr__
    __enter__ = __syntaxerr__
    __exit__ = __syntaxerr__

    __eq__ = __syntaxerr__
    __ne__ = __syntaxerr__
    __gt__ = __syntaxerr__
    __lt__ = __syntaxerr__
    __ge__ = __syntaxerr__
    __le__ = __syntaxerr__
    __pos__ = __syntaxerr__
    __neg__ = __syntaxerr__
    __abs__ = __syntaxerr__
    __invert__ = __syntaxerr__
    __round__ = __syntaxerr__
    __floor__ = __syntaxerr__
    __ceil__ = __syntaxerr__
    __trunc__ = __syntaxerr__

    __add__ = __syntaxerr__
    __sub__ = __syntaxerr__
    __mul__ = __syntaxerr__
    __div__ = __syntaxerr__
    __truediv__ = __syntaxerr__
    __floordiv__ = __syntaxerr__
    __mod__ = __syntaxerr__
    __divmod__ = __syntaxerr__
    __pow__ = __syntaxerr__
    __lshift__ = __syntaxerr__
    __rshift__ = __syntaxerr__
    __or__ = __syntaxerr__
    __and__ = __syntaxerr__
    __xor__ = __syntaxerr__

    __radd__ = __syntaxerr__
    __rsub__ = __syntaxerr__
    __rmul__ = __syntaxerr__
    __rdiv__ = __syntaxerr__
    __rtruediv__ = __syntaxerr__
    __rfloordiv__ = __syntaxerr__
    __rmod__ = __syntaxerr__
    __rdivmod__ = __syntaxerr__
    __rpow__ = __syntaxerr__
    __rlshift__ = __syntaxerr__
    __rrshift__ = __syntaxerr__
    __ror__ = __syntaxerr__
    __rand__ = __syntaxerr__
    __rxor__ = __syntaxerr__

    __iadd__ = __syntaxerr__
    __isub__ = __syntaxerr__
    __imul__ = __syntaxerr__
    __ifloordiv__ = __syntaxerr__
    __idiv__ = __syntaxerr__
    __imod__ = __syntaxerr__
    __idivmod__ = __syntaxerr__
    __irpow__ = __syntaxerr__
    __ilshift__ = __syntaxerr__
    __irshift__ = __syntaxerr__
    __ior__ = __syntaxerr__
    __iand__ = __syntaxerr__
    __ixor__ = __syntaxerr__


#=============================================================================#
# Operator sections

def make_section(fn):
    def section(a, b):
        return fn(b, a)

    def applyier(self, y):
        if isinstance(y, Section):
            return hof.flip(section)
        return hof.F(section, y)
    return applyier


class Section(Syntax):

    def __init__(self, syntax_err_msg):
        self.__syntax_err_msg = syntax_err_msg
        super(self.__class__, self).__init__(self.__syntax_err_msg)
        return

    __wrap = lambda f: lambda x, y: f(x, y)

    __add__ = make_section(__wrap(operator.add))
    __sub__ = make_section(__wrap(operator.sub))
    __mul__ = make_section(__wrap(operator.mul))
    __div__ = make_section(__wrap(operator.div))
    __truediv__ = make_section(__wrap(operator.truediv))
    __floordiv__ = make_section(__wrap(operator.floordiv))
    __mod__ = make_section(__wrap(operator.mod))
    __divmod__ = make_section(__wrap(divmod))
    __pow__ = make_section(__wrap(operator.pow))
    __lshift__ = make_section(__wrap(operator.lshift))
    __rshift__ = make_section(__wrap(operator.rshift))
    __or__ = make_section(__wrap(operator.or_))
    __and__ = make_section(__wrap(operator.and_))
    __xor__ = make_section(__wrap(operator.xor))

    __eq__ = make_section(__wrap(operator.eq))
    __ne__ = make_section(__wrap(operator.ne))
    __gt__ = make_section(__wrap(operator.gt))
    __lt__ = make_section(__wrap(operator.lt))
    __ge__ = make_section(__wrap(operator.ge))
    __le__ = make_section(__wrap(operator.le))

    __radd__ = make_section(hof.flip(__wrap(operator.add)))
    __rsub__ = make_section(hof.flip(__wrap(operator.sub)))
    __rmul__ = make_section(hof.flip(__wrap(operator.mul)))
    __rdiv__ = make_section(hof.flip(__wrap(operator.div)))
    __rtruediv__ = make_section(hof.flip(__wrap(operator.truediv)))
    __rfloordiv__ = make_section(hof.flip(__wrap(operator.floordiv)))
    __rmod__ = make_section(hof.flip(__wrap(operator.mod)))
    __rdivmod__ = make_section(hof.flip(__wrap(divmod)))
    __rpow__ = make_section(hof.flip(__wrap(operator.pow)))
    __rlshift__ = make_section(hof.flip(__wrap(operator.lshift)))
    __rrshift__ = make_section(hof.flip(__wrap(operator.rshift)))
    __ror__ = make_section(hof.flip(__wrap(operator.or_)))
    __rand__ = make_section(hof.flip(__wrap(operator.and_)))
    __rxor__ = make_section(hof.flip(__wrap(operator.xor)))


__ = Section("Error in section")


#=============================================================================#
# Guards! Guards!

class NoGuardMatchException(Exception):
    pass


class GuardCondition(Syntax):
    """
    Guard condition.
    """
    def __init__(self, fn):
        if not hasattr(fn, "__call__"):
            raise ValueError("Guard condition must be callable")
        self.__func = fn
        self.reset()
        super(self.__class__, self).__init__("Syntax error in guard condition")

    def has_return_value(self):
        return self.__has_return_value

    def return_value(self):
        if not self.has_return_value():
            self.raise_invalid("Guard condition does not have return value")
        return self.__return_value

    def check(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

    def reset(self):
        self.__return_value = None
        self.__has_return_value = False
        return

    def __rshift__(self, value):
        if isinstance(value, c):
            self.raise_invalid()

        if self.has_return_value():
            self.raise_invalid("Multiple return values in guard condition")

        self.__return_value = value
        self.__has_return_value = True
        return self


c = GuardCondition
otherwise = c(lambda _: True)


class guard(Syntax):
    """
    Usage:

    ~(guard(<expr to test>)
        | c(<test 1>) >> <return value 1>
        | c(<test 2>) >> <return value 2>
        | otherwise() >> <return value 3>
    )

    For example:

    ~(guard(8)
         | c(lambda x: x < 5) >> "less than 5"
         | c(lambda x: x < 9) >> "less than 9"
         | otherwise()        >> "unsure"
    )
    """
    def __init__(self, value):
        self.__value = value
        self.__tried_to_match = False
        self.__guard_satisfied = False
        self.conds = []

        self.__syntax_err_msg = "Syntax error in guard"
        super(self.__class__, self).__init__(self.__syntax_err_msg)

    def __or__(self, cond):
        self.conds.append(cond)

        if self.__guard_satisfied:
            return self

        self.__tried_to_match = True

        if not isinstance(cond, c):
            self.raise_invalid("Guard expression contains non-condition")

        if not cond.has_return_value():
            self.raise_invalid("Condition expression is missing return value")

        if cond.check(self.__value):
            self.__guard_satisfied = True
            self.__return_value = cond.return_value()
        return self

    def __invert__(self):
        for cond in self.conds:
            cond.reset()

        if not self.__tried_to_match:
            self.raise_invalid("No conditions in guard expression")

        if self.__guard_satisfied:
            return self.__return_value
        raise NoGuardMatchException("No match found in guard")


#=============================================================================#
# List comprehension

class __list_comprehension__(Syntax):
    """
    Syntactic construct for Haskell-style list comprehensions.
    """
    def __getitem__(self, lst):

        if type(lst) in (tuple, list) and len(lst) < 5 and Ellipsis in lst:
            # L[x, ...]
            if len(lst) == 2 and lst[1] is Ellipsis:
                return List(Enum.enumFrom(lst[0]))

            # L[x, y, ...]
            elif len(lst) == 3 and lst[2] is Ellipsis:
                return List(Enum.enumFromThen(lst[0], lst[1]))

            # L[x, ..., y]
            elif len(lst) == 3 and lst[1] is Ellipsis:
                return List(Enum.enumFromTo(lst[0], lst[2]))

            # L[x, y, ..., z]
            elif len(lst) == 4 and lst[2] is Ellipsis:
                return List(Enum.enumFromThenTo(lst[0], lst[1], lst[3]))

            self.raise_invalid()
        return List(lst)


L = __list_comprehension__("Invalid list comprehension")
