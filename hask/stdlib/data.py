import re
import string

from ..lang import syntax


class data(syntax.Syntax):

    def __init__(self, dt_name, *type_args):
        if type(dt_name) != str:
            raise SyntaxError("Data type name must be string")

        if not type_args:
            raise SyntaxError("No type arguments provided in type constructor")

        if not re.match("^[A-Z]\w+$", dt_name):
            raise SyntaxError("Invalid ADT name.")

        for type_arg in type_args:
            if type(type_arg) != str:
                raise SyntaxError("Data type name must be string")

            if type_arg not in string.lowercase:
                raise SyntaxError("Invalid type variable %s" % type_arg)

        if len(set(type_args)) != len(type_args):
            msg = "Cannot use the same type variable twice in type constructor"
            raise SyntaxError(msg)

        self.dt_name = dt_name
        self.type_args = type_args

        self._data_constrs = []

        syntax_err_msg = "Syntax error in `data`"
        super(self.__class__, self).__init__(syntax_err_msg)
        return

    def __eq__(self, data_constructor):
        if type(data_constructor) == typ:
            self._data_constrs.append(data_constructor)

        elif type(data_constructor) == typs:
            for t in data_constructor:
                self._data_constrs.append(t)
        else:
            raise SyntaxError("Use `typ` to create a data constructor")

        # do a lot of checking
        # then figure out whether we want to modify globals()/locals()
        return self



