import operator

import hof
import syntax


def make_section(fn):
    def section(a, b):
        return fn(b, a)

    def applyier(self, y):
        if isinstance(y, Section):
            return hof.flip(section)
        else:
            return hof.F(section, y)

    return applyier


class Section(syntax.Syntax):

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
