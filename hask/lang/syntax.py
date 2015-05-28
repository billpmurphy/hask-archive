import operator

import hof
from builtins import List
from typeclasses import Enum
from type_system import HM_typeof


#=============================================================================#
# Base class for syntactic constructs


class Syntax(object):
    """
    Base class for new syntactic constructs. All of the new "syntax" elements
    of Hask inherit from this class.

    By default, a piece of syntax will raise a syntax error with a standard
    error message if the syntax object is used with a Python builtin operator.

    Subclasses may override these methods to define what syntax is valid for
    those objects.
    """
    def __init__(self, err_msg=None):
        if err_msg is not None:
            self.__syntax_err_msg = err_msg
        else:
            self.__syntax_err_msg = "Syntax error in `%s`" % self.__name__
        return

    def raise_invalid(self, msg=None):
        if msg is not None:
            raise SyntaxError(msg)
        raise SyntaxError(self.__syntax_err_msg)

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

    __bool__ = __syntaxerr__
    __nonzero__ = __syntaxerr__


#=============================================================================#
# Operator sections


def make_section(fn):
    """
    Create an operator section from a binary operator.
    """
    def section(self, y):
        # double section, e.g. (__+__)
        if isinstance(y, __section__):
            return hof.F(lambda x, y: fn(x, y))

        # single section, e.g. (__+1) or (1+__)
        return hof.F(lambda a: fn(a, y))
    return section


class __section__(Syntax):

    def __init__(self, syntax_err_msg):
        super(__section__, self).__init__(syntax_err_msg)
        return

    __flip = lambda f: lambda x, y: f(y, x)

    __add__ = make_section(operator.add)
    __sub__ = make_section(operator.sub)
    __mul__ = make_section(operator.mul)
    __div__ = make_section(operator.div)
    __truediv__ = make_section(operator.truediv)
    __floordiv__ = make_section(operator.floordiv)
    __mod__ = make_section(operator.mod)
    __divmod__ = make_section(divmod)
    __pow__ = make_section(operator.pow)
    __lshift__ = make_section(operator.lshift)
    __rshift__ = make_section(operator.rshift)
    __or__ =  make_section(operator.or_)
    __and__ = make_section(operator.and_)
    __xor__ = make_section(operator.xor)

    __eq__ = make_section(operator.eq)
    __ne__ = make_section(operator.ne)
    __gt__ = make_section(operator.gt)
    __lt__ = make_section(operator.lt)
    __ge__ = make_section(operator.ge)
    __le__ = make_section(operator.le)

    __radd__ = make_section(__flip(operator.add))
    __rsub__ = make_section(__flip(operator.sub))
    __rmul__ = make_section(__flip(operator.mul))
    __rdiv__ = make_section(__flip(operator.div))
    __rtruediv__ = make_section(__flip(operator.truediv))
    __rfloordiv__ = make_section(__flip(operator.floordiv))
    __rmod__ = make_section(__flip(operator.mod))
    __rdivmod__ = make_section(__flip(divmod))
    __rpow__ = make_section(__flip(operator.pow))
    __rlshift__ = make_section(__flip(operator.lshift))
    __rrshift__ = make_section(__flip(operator.rshift))
    __ror__ = make_section(__flip(operator.or_))
    __rand__ = make_section(__flip(operator.and_))
    __rxor__ = make_section(__flip(operator.xor))


__ = __section__("Error in section")


#=============================================================================#
# Guards! Guards!


class NoGuardMatchException(Exception):
    pass


class __guard_test__(Syntax):
    """
    c creates a new condition that can be used in a guard
    expression.

    otherwise is a guard condition that always evaluates to True.

    Usage:

    ~(guard(<expr to test>)
        | c(<test_fn_1>) >> <return_value_1>
        | c(<test_fn_2>) >> <return_value_2>
        | otherwise      >> <return_value_3>
    )

    See help(guard) for more details.
    """
    def __init__(self, fn):
        if not hasattr(fn, "__call__"):
            raise ValueError("Guard condition must be callable")
        self.__test = fn
        super(__guard_test__, self).__init__("Syntax error in guard condition")

    def __rshift__(self, value):
        if isinstance(value, __guard_test__) or \
           isinstance(value, __guard_conditional__) or \
           isinstance(value, __guard_base__):
            self.raise_invalid()
        return __guard_conditional__(self.__test, value)


class __guard_conditional__(Syntax):
    """
    Object that represents one line of a guard expression, consisting of a
    condition (a test function wrapped in c and a value to be returned if that
    condition is satisfied).

    See help(guard) for more details.
    """
    def __init__(self, fn, return_value):
        self.check = fn
        self.return_value = return_value
        msg = "Syntax error in guard condition"
        super(__guard_conditional__, self).__init__(msg)


class __guard_base__(Syntax):
    """
    Superclass for the classes __unmatched_guard__ and __matched_guard__ below,
    which represent the internal state of a guard expression as it is being
    evaluated.

    See help(guard) for more details.
    """
    def __init__(self, value):
        self.value = value
        super(__guard_base__, self).__init__("Syntax error in guard")


class __unmatched_guard__(__guard_base__):
    """
    Object that represents the state of a guard expression in mid-evaluation,
    before one of the conditions in the expression has been satisfied.

    See help(guard) for more details.
    """
    def __or__(self, cond):
        if isinstance(cond, __guard_test__):
            self.raise_invalid("Guard expression is missing return value")
        elif not isinstance(cond, __guard_conditional__):
            self.raise_invalid()
        elif cond.check(self.value):
            return __matched_guard__(cond.return_value)
        return __unmatched_guard__(self.value)

    def __invert__(self):
        raise NoGuardMatchException("No match found in guard")


class __matched_guard__(__guard_base__):
    """
    Object that represents the state of a guard expression in mid-evaluation,
    after one of the conditions in the expression has been satisfied.

    See help(guard) for more details.
    """
    def __or__(self, cond):
        if isinstance(cond, __guard_conditional__):
            return self
        self.raise_invalid()

    def __invert__(self):
        return self.value


class guard(__unmatched_guard__):
    """
    Usage:

    ~(guard(<expr to test>)
        | c(<test_fn_1>) >> <return_value_1>
        | c(<test_fn_2>) >> <return_value_2>
        | otherwise      >> <return_value_3>
    )

    Examples:

    ~(guard(8)
         | c(lambda x: x < 5) >> "less than 5"
         | c(lambda x: x < 9) >> "less than 9"
         | otherwise          >> "unsure"
    )

    # Using guards with sections. See help(__) for more on sections.
    """
    def __invert__(self):
        self.raise_invalid()


c = __guard_test__
otherwise = c(lambda _: True)


#=============================================================================#
# List comprehension

class __list_comprehension__(Syntax):
    """
    Syntactic construct for Haskell-style list comprehensions.

    List comprehensions can be used with any instance of Enum, including the
    built-in types int, long, float, and char.

    There are four basic list comprehension patterns:

    >>> L[1, ...]

    >>> L[1, 3, ...]

    >>> L[1, ..., 20]

    >>> L[1, 5, ..., 20]

    """
    def __getitem__(self, lst):
        if isinstance(lst, tuple) and len(lst) < 5 and Ellipsis in lst:
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


#=============================================================================#
# Type signatures


from hindley_milner import *


class __constraints__(Syntax):

    def __init__(self, constraints=()):
        self.constraints = constraints
        super(__constraints__, self).__init__("Syntax error in type signature")
        return

    def __getitem__(self, constraints):
        return __constraints__(constraints)

    def __div__(self, arg1):
        return __signature__((arg1,), self.constraints)


class __signature__(Syntax):

    def __init__(self, args, constraints):
        self.args = args
        self.constraints = constraints
        super(__signature__, self).__init__("Syntax error in type signature")
        return

    def __rshift__(self, next_arg):
        return __signature__(self.args + (next_arg,), self.constraints)


class sig(Syntax):
    """
    Usage:

    @sig(H/ int >> int >> t.Maybe . int >> t.Maybe . int)
    def safe_div(x, y):
        if y == 0:
            return Nothing
        return Just(x / y)

    @sig(H[t.Show("a")]/ >> "a" >> str)
    def to_str(x):
        return str(x)
    """
    def __init__(self, signature):
        super(self.__class__, self).__init__("Syntax error in type signature")
        if not isinstance(signature, __signature__):
            self.raise_invalid()
        elif len(signature.args) < 2:
            self.raise_invalid("Not enough type arguments in signature")
        self.signature = signature
        self.fn_type = parse_sig(self.signature.args)
        return

    def __call__(self, fn):
        # convert the list of arguments from the signature into its type
        return TypedFunc(fn, self.fn_type)


class TypedFunc(object):

    def __init__(self, fn, fn_type):
        self.__doc__ = fn.__doc__
        self.func = fn
        self.fn_type = fn_type
        return

    def type(self):
        return self.fn_type

    def __call__(self, *args, **kwargs):
        # the evironment contains the type of the function and the types
        # of the arguments
        env = {id(self.func):self.fn_type}
        env.update({id(arg):HM_typeof(arg) for arg in args})

        ap = Var(id(self.func))
        for arg in args:
            ap = App(ap, Var(id(arg)))

        result_type = analyze(ap, env)
        result = self.func.__call__(*args, **kwargs)
        unify(result_type, HM_typeof(result))

        if hof.F(result) is result:
            return result
        return result


H = __constraints__()


class TypeSignatureError(Exception):
    pass


def parse_sig_item(item, var_dict):
    if isinstance(item, TypeVariable) or isinstance(item, TypeOperator):
        return item

    # string representing type variable
    elif isinstance(item, str):
        if item not in var_dict:
            var_dict[item] = TypeVariable()
        return var_dict[item]

    # an ADT or something else created in hask
    elif hasattr(item, "type"):
        return TypeOperator(item.type().hkt,
                map(lambda x: parse_sig_item(x, var_dict), item.type().params))

    # ("a", "b"), (int, ("a", float)), etc.
    elif isinstance(item, tuple):
        return Tuple(map(lambda x: parse_sig_item(x, var_dict), item))

    # any other type
    elif isinstance(item, type):
        return TypeOperator(item, [])

    raise TypeSignatureError("Invalid item in type signature: %s" % item)


def parse_sig(items):
    def make_fn_type(args):
        if len(args) == 2:
            last_input, return_type = args
            return Function(last_input, return_type)
        return Function(args[0], make_fn_type(args[1:]))

    var_dict = {}
    return make_fn_type([parse_sig_item(i, var_dict) for i in items])
