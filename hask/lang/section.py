import operator

import hof
import syntax


def __make_section__(fn):
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

    __wrap__ = lambda f: lambda x, y: f(x, y)

    __add__ = __make_section__(__wrap__(operator.add))
    __sub__ = __make_section__(__wrap__(operator.sub))
    __mul__ = __make_section__(__wrap__(operator.mul))
    __div__ = __make_section__(__wrap__(operator.div))
    __truediv__ = __make_section__(__wrap__(operator.truediv))
    __floordiv__ = __make_section__(__wrap__(operator.floordiv))
    __mod__ = __make_section__(__wrap__(operator.mod))
    __divmod__ = __make_section__(__wrap__(divmod))
    __pow__ = __make_section__(__wrap__(operator.pow))
    __lshift__ = __make_section__(__wrap__(operator.lshift))
    __rshift__ = __make_section__(__wrap__(operator.rshift))
    __or__ = __make_section__(__wrap__(operator.or_))
    __and__ = __make_section__(__wrap__(operator.and_))
    __xor__ = __make_section__(__wrap__(operator.xor))

    __eq__ = __make_section__(__wrap__(operator.eq))
    __ne__ = __make_section__(__wrap__(operator.ne))
    __gt__ = __make_section__(__wrap__(operator.gt))
    __lt__ = __make_section__(__wrap__(operator.lt))
    __ge__ = __make_section__(__wrap__(operator.ge))
    __le__ = __make_section__(__wrap__(operator.le))

    __radd__ = __make_section__(hof.flip(__wrap__(operator.add)))
    __rsub__ = __make_section__(hof.flip(__wrap__(operator.sub)))
    __rmul__ = __make_section__(hof.flip(__wrap__(operator.mul)))
    __rdiv__ = __make_section__(hof.flip(__wrap__(operator.div)))
    __rtruediv__ = __make_section__(hof.flip(__wrap__(operator.truediv)))
    __rfloordiv__ = __make_section__(hof.flip(__wrap__(operator.floordiv)))
    __rmod__ = __make_section__(hof.flip(__wrap__(operator.mod)))
    __rdivmod__ = __make_section__(hof.flip(__wrap__(divmod)))
    __rpow__ = __make_section__(hof.flip(__wrap__(operator.pow)))
    __rlshift__ = __make_section__(hof.flip(__wrap__(operator.lshift)))
    __rrshift__ = __make_section__(hof.flip(__wrap__(operator.rshift)))
    __ror__ = __make_section__(hof.flip(__wrap__(operator.or_)))
    __rand__ = __make_section__(hof.flip(__wrap__(operator.and_)))
    __rxor__ = __make_section__(hof.flip(__wrap__(operator.xor)))


__ = Section("Error in section")
