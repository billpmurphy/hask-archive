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

    def __cmp__(self, ): self._raise_invalid()
    def __eq__(self, ): self._raise_invalid()
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
