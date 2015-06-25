import operator

from builtins import List
from typeclasses import Enum
from typeclasses import enumFrom
from typeclasses import enumFromThen
from typeclasses import enumFromTo
from typeclasses import enumFromThenTo
from type_system import Hask
from type_system import Typeclass
from type_system import TypedFunc
from type_system import TypeSignature
from type_system import TypeSignatureHKT
from type_system import __ADT__
from type_system import build_ADT
from type_system import build_sig
from type_system import PatternMatchBind
from type_system import Wildcard
from type_system import pattern_match

from hindley_milner import TypeVariable


#=============================================================================#
# Base class for syntactic constructs


basic_attrs = set(("len", "getitem", "setitem", "delitem", "iter", "reversed",
    "contains", "missing", "delattr", "call", "enter", "exit", "eq", "ne",
    "gt", "lt", "ge", "le", "pos", "neg", "abs", "invert", "round", "floor",
    "ceil", "trunc", "add", "sub", "mul", "div", "truediv", "floordiv", "mod",
    "divmod", "pow", "lshift", "rshift", "or", "and", "xor", "radd", "rsub",
    "rmul", "rdiv", "rtruediv", "rfloordiv", "rmod", "rdivmod", "rpow",
    "rlshift", "rrshift", "ror", "rand", "rxor", "isub", "imul", "ifloordiv",
    "idiv", "imod", "idivmod", "irpow", "ilshift", "irshift", "ior", "iand",
    "ixor", "nonzero"))


def wipe_attrs(cls, fn):
    for attr in ("__%s__" % b for b in basic_attrs):
        setattr(cls, attr, fn)
    return


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


wipe_attrs(Syntax, Syntax.__syntaxerr__)


#=============================================================================#
# Typeclass instance declaration


class instance(Syntax):

    def __init__(self, typeclass, cls):
        if not issubclass(typeclass, Typeclass):
            raise TypeError("%s is not a typeclass" % typeclass)
        self.typeclass = typeclass
        self.cls = cls
        return

    def where(self, **kwargs):
        self.typeclass.make_instance(self.cls, **kwargs)
        return


#=============================================================================#
# Type signatures


class __constraints__(Syntax):
    """
    H/ creates a new function type signature.

    Usage:

    See help(sig) for more information on type signature decorators.
    """
    def __init__(self, constraints=()):
        self.constraints = constraints
        super(__constraints__, self).__init__("Syntax error in type signature")
        return

    def __getitem__(self, constraints):
        return __constraints__(constraints)

    def __div__(self, arg):
        return __signature__((), self.constraints).__rshift__(arg)


class __signature__(Syntax):
    """
    """
    def __init__(self, args, constraints):
        self.sig = TypeSignature(args, constraints)
        super(__signature__, self).__init__("Syntax error in type signature")
        return

    def __rshift__(self, arg):
        arg = arg.sig if isinstance(arg, __signature__) else arg
        return __signature__(self.sig.args + (arg,), self.sig.constraints)

    def __rpow__(self, fn):
        return sig(self)(fn)


H = __constraints__()


class sig(Syntax):
    """
    Decorator to convert a Python function into a statically typed function
    (TypedFunc object).

    TypedFuncs are automagically curried, and polymorphic type arguments will
    be inferred by the type system.

    Usage:

    @sig(H/ int >> int >> int )
    def add(x, y):
        return x + y


    @sig(H/ int >> int >> Maybe(int) >> Maybe(int))
    def safe_div(x, y):
        if y == 0:
            return Nothing
        return Just(x / y)


    @sig(H[(Show, "a")]/ >> "a" >> str)
    def to_str(x):
        return str(x)
    """
    def __init__(self, signature):
        super(self.__class__, self).__init__("Syntax error in type signature")

        if not isinstance(signature, __signature__):
            msg = "Signature expected in sig(); found %s" % signature
            self.raise_invalid(msg)

        elif len(signature.sig.args) < 2:
            self.raise_invalid("Not enough type arguments in signature")

        self.fn_type = build_sig(signature.sig.args)
        return

    def __call__(self, fn):
        return TypedFunc(fn, self.fn_type)


def t(type_constructor, *params):
    if isinstance(type_constructor, __ADT__) and \
       len(type_constructor.__params__) != len(params):
            raise TypeError("Incorrect number of type parameters to %s" % \
                            type_constructor.__name__)
    return TypeSignatureHKT(type_constructor, params)


def typify(fn, hkt=None):
    args = [chr(i) for i in range(97, 98 + fn.func_code.co_argcount)]
    if hkt is not None:
        args[-1] = hkt(args[-1])
    return sig(__signature__(args, []))


#=============================================================================#
# Undefined values


class __undefined__(object):
    """
    A weird object with no concrete type. Used to create `undefined` and in
    pattern matching
    """
    __make_undefined__ = lambda s, *a: undefined


wipe_attrs(__undefined__, __undefined__.__make_undefined__)
Hask.make_instance(__undefined__, lambda __: TypeVariable())

undefined = __undefined__()



#=============================================================================#
# Pattern matching


class IncompletePatternError(Exception):
    pass


class MatchVars(object):
    __cache__ = {}
    __value__ = undefined


class __var_bind__(Syntax):
    def __getattr__(self, name):
        return PatternMatchBind(name)

    def __call__(self, pattern):
        is_match, env = pattern_match(MatchVars.__value__, pattern)
        MatchVars.__cache__ = env
        return __match_test__(is_match)


class __var_access__(Syntax):
    def __getattr__(self, name):
        return MatchVars.__cache__.get(name, undefined)


m = __var_bind__("Error in pattern match")
p = __var_access__("Error in pattern match")
w = Wildcard()


class __match_line__(Syntax):
    """
    Represents one line of a caseof
    """
    def __init__(self, is_match, return_value):
        self.is_match = is_match
        self.return_value = return_value
        return


class __match_test__(Syntax):
    """
    represents the pattern part of one caseof line
    """
    def __init__(self, is_match):
        self.is_match = is_match
        return
    def __rshift__(self, value):
        MatchVars.__cache__ = {}
        return __match_line__(self.is_match, value)


class __unmatched_case__(Syntax):
    def __or__(self, line):
        if line.is_match:
            return __matched_case__(line.return_value)
        return self
    def __invert__(self):
        MatchVars.__cache__ = {}
        MatchVars.__value__ = undefined
        raise IncompletePatternError()


class __matched_case__(Syntax):
    def __init__(self, return_value):
        self.value = return_value
        return
    def __or__(self, line):
        return self
    def __invert__(self):
        MatchVars.__cache__ = {}
        MatchVars.__value__ = undefined
        return self.value


class caseof(__unmatched_case__):
    """
    """
    def __init__(self, value):
        MatchVars.__value__ = value
        return

#=============================================================================#
# ADT creation syntax ("data" expressions)


## "data"/type constructor half of the expression

class __data__(Syntax):
    """
    Examples:

    Maybe, Nothing, Just =\
    data.Maybe("a") == d.Nothing | d.Just("a") & deriving(Read, Show, Eq, Ord)
    """
    def __init__(self):
        super(__data__, self).__init__("Syntax error in `data`")

    def __getattr__(self, value):
        return __new_tcon_enum__(value)


class __new_tcon__(Syntax):
    """
    """
    def __init__(self, name, args=()):
        self.name = name
        self.args = args
        super(__new_tcon__, self).__init__("Syntax error in `data`")

    def __eq__(self, d):
        # one data constructor, no derived typedclasses
        if isinstance(d, __new_dcon__):
            return build_ADT(self.name, self.args, [(d.name, d.args)], ())

        # one data constructor, one or more derived typeclasses
        elif isinstance(d, __new_dcon_deriving__):
            return build_ADT(self.name, self.args, [(d.name, d.args)],
                             d.classes)

        # one or more data constructors, no derived typeclasses
        elif isinstance(d, __new_dcons__):
            return build_ADT(self.name, self.args, d.dcons, ())

        # one or more data constructors, one or more derived typeclasses
        elif isinstance(d, __new_dcons_deriving__):
            return build_ADT(self.name, self.args, d.dcons, d.classes)

        self.raise_invalid()
        return


class __new_tcon_enum__(__new_tcon__):
    """
    Examples:

    data.Either

    data.Ordering
    """
    def __call__(self, *typeargs):
        if len(typeargs) < 1:
            msg = "Missing type args in statement: `data.%s()`" % self.name
            self.raise_invalid(msg)

        # make sure all type params are strings
        if not all((type(arg) == str for arg in typeargs)):
            self.raise_invalid("Type parameters must be strings")

        # all type parameters must have unique names
        if len(typeargs) != len(set(typeargs)):
            self.raise_invalid("Type parameters are not unique")

        return __new_tcon_hkt__(self.name, typeargs)


class __new_tcon_hkt__(__new_tcon__):
    """
    Example:

    data.Either("a", "b")
    """
    pass


## "d"/data constructor half of the expression


class __d__(Syntax):
    """
    `d` is part of hask's special syntax for defining algebraic data types.

    See help(data) for more information.
    """
    def __init__(self):
        super(__d__, self).__init__("Syntax error in `d`")

    def __getattr__(self, value):
        return __new_dcon_enum__(value)


class __new_dcon__(Syntax):

    def __init__(self, dcon_name, args=(), classes=()):
        self.name = dcon_name
        self.args = args
        self.classes = classes
        super(__new_dcon__, self).__init__("Syntax error in `d`")
        return


class __new_dcon_params__(__new_dcon__):

    def __and__(self, derive_exp):
        if not isinstance(derive_exp, deriving):
            self.raise_invalid()
        return __new_dcon_deriving__(self.name, self.args, derive_exp.classes)

    def __or__(self, dcon):
        if isinstance(dcon, __new_dcon__):
            constructors = ((self.name, self.args), (dcon.name, dcon.args))

            if isinstance(dcon, __new_dcon_deriving__):
                return __new_dcons_deriving__(constructors, dcon.classes)
            return __new_dcons__(constructors)

        self.raise_invalid()
        return


class __new_dcon_deriving__(__new_dcon__):
    pass


class __new_dcon_enum__(__new_dcon_params__):

    def __call__(self, *typeargs):
        return __new_dcon_params__(self.name, typeargs)


class __new_dcons_deriving__(Syntax):

    def __init__(self, data_consts, classes=()):
        self.dcons = data_consts
        self.classes = classes
        super(__new_dcons_deriving__, self).__init__("Syntax error in `d`")
        return


class __new_dcons__(__new_dcons_deriving__):

    def __init__(self, data_consts):
        super(__new_dcons__, self).__init__(data_consts)
        return

    def __or__(self, new_dcon):
        if isinstance(new_dcon, __new_dcon__):
            constructor = ((new_dcon.name, new_dcon.args),)

            if isinstance(new_dcon, __new_dcon_deriving__):
                return __new_dcons_deriving__(self.dcons + constructor,
                                              new_dcon.classes)
            return __new_dcons__(self.dcons + constructor)
        self.raise_invalid()


data = __data__()
d = __d__()


class deriving(Syntax):
    """
    `deriving` is part of hask's special syntax for defining algebraic data
    types.

    See help(data) for more information.
    """
    def __init__(self, *tclasses):
        for tclass in tclasses:
            if not issubclass(tclass, Typeclass):
                raise TypeError("Cannot derive non-typeclass %s" % tclass)
        self.classes = tclasses
        super(deriving, self).__init__("Syntax error in `deriving`")
        return


#=============================================================================#
# Operator sections


class __section__(Syntax):
    """
    Special syntax for operator sections.

    """
    def __init__(self, syntax_err_msg):
        super(__section__, self).__init__(syntax_err_msg)
        return

    @staticmethod
    def __make_section(fn):
        """
        Create an operator section from a binary operator.
        """
        def section_wrapper(self, y):
            # double section, e.g. (__+__)
            if isinstance(y, __section__):
                @sig(H/ "a" >> "b" >> "c")
                def double_section(a, b):
                    return fn(a, b)
                return double_section

            # single section, e.g. (__+1) or (1+__)
            @sig(H/ "a" >> "b")
            def section(a):
                return fn(a, y)
            return section
        return section_wrapper

    # left section, e.g. (__+1)
    __wrap = __make_section.__func__

    # right section, e.g. (1+__)
    __flip = lambda f: lambda x, y: f(y, x)

    __add__ = __wrap(operator.add)
    __sub__ = __wrap(operator.sub)
    __mul__ = __wrap(operator.mul)
    __div__ = __wrap(operator.div)
    __truediv__ = __wrap(operator.truediv)
    __floordiv__ = __wrap(operator.floordiv)
    __mod__ = __wrap(operator.mod)
    __divmod__ = __wrap(divmod)
    __pow__ = __wrap(operator.pow)
    __lshift__ = __wrap(operator.lshift)
    __rshift__ = __wrap(operator.rshift)
    __or__ =  __wrap(operator.or_)
    __and__ = __wrap(operator.and_)
    __xor__ = __wrap(operator.xor)

    __eq__ = __wrap(operator.eq)
    __ne__ = __wrap(operator.ne)
    __gt__ = __wrap(operator.gt)
    __lt__ = __wrap(operator.lt)
    __ge__ = __wrap(operator.ge)
    __le__ = __wrap(operator.le)

    __radd__ = __wrap(__flip(operator.add))
    __rsub__ = __wrap(__flip(operator.sub))
    __rmul__ = __wrap(__flip(operator.mul))
    __rdiv__ = __wrap(__flip(operator.div))
    __rtruediv__ = __wrap(__flip(operator.truediv))
    __rfloordiv__ = __wrap(__flip(operator.floordiv))
    __rmod__ = __wrap(__flip(operator.mod))
    __rdivmod__ = __wrap(__flip(divmod))
    __rpow__ = __wrap(__flip(operator.pow))
    __rlshift__ = __wrap(__flip(operator.lshift))
    __rrshift__ = __wrap(__flip(operator.rshift))
    __ror__ = __wrap(__flip(operator.or_))
    __rand__ = __wrap(__flip(operator.and_))
    __rxor__ = __wrap(__flip(operator.xor))


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
    Object that represents one line of a guard expression, consisting of:
        1) a condition (a test function wrapped in c and a value to be returned
           if that condition is satisfied).
        2) a return value, which will be returned if the condition evaluates
           to True
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
        # Consume the next line of the guard expression

        if isinstance(cond, __guard_test__):
            self.raise_invalid("Guard expression is missing return value")

        elif not isinstance(cond, __guard_conditional__):
            self.raise_invalid("Guard condition expected, got %s" % cond)

        # If the condition is satisfied, change the evaluation state to
        # __matched_guard__, setting the return value to the value provided on
        # the current line
        elif cond.check(self.value):
            return __matched_guard__(cond.return_value)

        # If the condition is not satisfied, continue on with the next line,
        # still in __unmatched_guard__ state with the return value not set
        return __unmatched_guard__(self.value)

    def __invert__(self):
        raise NoGuardMatchException("No match found in guard(%s)" % self.value)


class __matched_guard__(__guard_base__):
    """
    Object that represents the state of a guard expression in mid-evaluation,
    after one of the conditions in the expression has been satisfied.

    See help(guard) for more details.
    """
    def __or__(self, cond):
        # Consume the next line of the guard expression
        # Since a condition has already been satisfied, we can ignore the rest
        # of the lines in the guard expression
        if isinstance(cond, __guard_conditional__):
            return self
        self.raise_invalid()

    def __invert__(self):
        return self.value


class guard(__unmatched_guard__):
    """
    Special syntax for guard expression.

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

    # Using guards with sections. See help(__) for information on sections.
    ~(guard(20)
        | c(__ > 10)  >> 20
        | c(__ == 10) >> 10
        | c(__ > 5)   >> 5
        | otherwise   >> 0)

    Args:
        value: the value being tested in the guard expression

    Returns:
        the return value corresponding to the first matching condition

    Raises:
        NoGuardMatchException (if no match is found)

    """
    def __invert__(self):
        self.raise_invalid()


c = __guard_test__
otherwise = c(lambda _: True)


#=============================================================================#
# List comprehension


class __list_comprehension__(Syntax):
    """
    Syntactic construct for Haskell-style list comprehensions and lazy list
    creation.

    List comprehensions can be used with any instance of Enum, including the
    built-in types int, long, float, and char.

    There are four basic list comprehension patterns:

    >>> L[1, ...]
    # list from 1 to infinity, counting by ones

    >>> L[1, 3, ...]
    # list from 1 to infinity, counting by twos

    >>> L[1, ..., 20]
    # list from 1 to 20 (inclusive), counting by ones

    >>> L[1, 5, ..., 20]
    # list from 1 to 20 (inclusive), counting by fours
    """
    def __getitem__(self, lst):
        if isinstance(lst, tuple) and len(lst) < 5 and Ellipsis in lst:
            # L[x, ...]
            if len(lst) == 2 and lst[1] is Ellipsis:
                return List(enumFrom(lst[0]))

            # L[x, y, ...]
            elif len(lst) == 3 and lst[2] is Ellipsis:
                return List(enumFromThen(lst[0], lst[1]))

            # L[x, ..., y]
            elif len(lst) == 3 and lst[1] is Ellipsis:
                return List(enumFromTo(lst[0], lst[2]))

            # L[x, y, ..., z]
            elif len(lst) == 4 and lst[2] is Ellipsis:
                return List(enumFromThenTo(lst[0], lst[1], lst[3]))

            self.raise_invalid()
        return List(lst)


L = __list_comprehension__("Invalid list comprehension")
