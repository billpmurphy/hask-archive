import operator

import hof
import syntax


class Section(syntax.Syntax):

    def __init__(self, syntax_err_msg):
        self.__syntax_err_msg = syntax_err_msg
        super(self.__class__, self).__init__(self.__syntax_err_msg)
        return

    def __add__(self, other):
        return lambda x: x + other


__ = Section("Error in section")
