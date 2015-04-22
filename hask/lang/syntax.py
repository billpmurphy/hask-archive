class Syntax(object):
    """
    Superclass for new syntactic constructs. By default, a piece of syntax
    should raise a syntax error with a standard error message if the syntax
    object is used with a Python buildin operator. Subclasses may override
    these methods to define what syntax is valid.
    """
    def __init__(self, err_msg):
        self._syntax_err_msg = err_msg

    def _raise_invalid(self):
        if hasattr(self, "_syntax_err_msg"):
            raise SyntaxError(self._syntax_err_msg)
        else:
            raise SyntaxError("Syntax error in `%s`" % self.__name__)

    __syntaxerr__ = lambda s, *a: s._raise_invalid()

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
