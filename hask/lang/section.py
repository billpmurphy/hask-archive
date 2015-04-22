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

    __add__ = __make_section__(operator.add)
    __sub__ = __make_section__(operator.sub)
    __mul__ = __make_section__(operator.mul)
    __div__ = __make_section__(operator.div)
    __truediv__ = __make_section__(operator.truediv)
    __floordiv__ = __make_section__(operator.floordiv)
    __mod__ = __make_section__(operator.mod)
    __divmod__ = __make_section__(divmod)
    __pow__ = __make_section__(operator.pow)
    __lshift__ = __make_section__(operator.lshift)
    __rshift__ = __make_section__(operator.rshift)
    __or__ = __make_section__(operator.or_)
    __and__ = __make_section__(operator.and_)
    __xor__ = __make_section__(operator.xor)

    __eq__ = __make_section__(operator.eq)
    __ne__ = __make_section__(operator.ne)
    __gt__ = __make_section__(operator.gt)
    __lt__ = __make_section__(operator.lt)
    __ge__ = __make_section__(operator.ge)
    __le__ = __make_section__(operator.le)

    __radd__ = __make_section__(hof.flip(operator.add))
    __rsub__ = __make_section__(hof.flip(operator.sub))
    __rmul__ = __make_section__(hof.flip(operator.mul))
    __rdiv__ = __make_section__(hof.flip(operator.div))
    __rtruediv__ = __make_section__(hof.flip(operator.truediv))
    __rfloordiv__ = __make_section__(hof.flip(operator.floordiv))
    __rmod__ = __make_section__(hof.flip(operator.mod))
    __rdivmod__ = __make_section__(hof.flip(divmod))
    __rpow__ = __make_section__(hof.flip(operator.pow))
    __rlshift__ = __make_section__(hof.flip(operator.lshift))
    __rrshift__ = __make_section__(hof.flip(operator.rshift))
    __ror__ = __make_section__(hof.flip(operator.or_))
    __rand__ = __make_section__(hof.flip(operator.and_))
    __rxor__ = __make_section__(hof.flip(operator.xor))


__ = Section("Error in section")
