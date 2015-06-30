import types
import functools
from collections import namedtuple

from hindley_milner import TypeVariable
from hindley_milner import TypeOperator
from hindley_milner import Var
from hindley_milner import App
from hindley_milner import Lam
from hindley_milner import unify
from hindley_milner import analyze
from hindley_milner import Function
from hindley_milner import Tuple
from hindley_milner import ListType


#=============================================================================#
# Typeclasses


__python_builtins__ = set((
    types.NoneType, types.TypeType, types.BooleanType, types.IntType,
    types.LongType, types.FloatType, types.ComplexType, types.StringType,
    types.UnicodeType, types.TupleType, types.ListType, types.DictType,
    types.DictionaryType, types.FunctionType, types.LambdaType,
    types.GeneratorType, types.CodeType, types.ClassType, types.InstanceType,
    types.MethodType, types.UnboundMethodType, types.BuiltinFunctionType,
    types.BuiltinMethodType, types.ModuleType, types.FileType,
    types.XRangeType, types.EllipsisType, types.TracebackType, types.FrameType,
    types.BufferType, types.DictProxyType, types.NotImplementedType,
    types.GetSetDescriptorType, types.MemberDescriptorType))


def is_builtin(cls):
    """
    Test whether a class or type is a Python builtin.

    Args:
        cls: The class or type to examine

    Returns:
        True if a type is a Python builtin type, and False otherwise.
    """
    return cls in __python_builtins__


def nt_to_tuple(nt):
    """
    Convert an instance of namedtuple (or an instance of a subclass of
    namedtuple) to a tuple, even if the instance's __iter__
    method has been changed. Useful for writing derived instances of
    typeclasses.

    Args:
        nt: an instance of namedtuple

    Returns:
        A tuple containing each of the items in nt
    """
    return tuple((getattr(nt, f) for f in nt.__class__._fields))


class TypeMeta(type):
    """
    Metaclass for Typeclass type. Ensures that all typeclasses are instantiated
    with a dictionary to map instances to their member functions, and a list of
    dependencies.
    """
    def __init__(self, *args):
        super(TypeMeta, self).__init__(*args)
        self.__instances__ = {}
        self.__dependencies__ = self.mro()[1:-2] # excl. self, Typeclass, object

    def __getitem__(self, item):
        try:
            if is_builtin(type(item)):
                return self.__instances__[id(type(item))]
            elif isinstance(item, ADT):
                return self.__instances__[id(item.__type_constructor__)]
            return self.__instances__[id(typeof(item))]
        except KeyError:
            raise TypeError("No instance for {0}".format(item))


class Typeclass(object):
    """
    Base class for Hask typeclasses.

    All subclasses should implement make_instance, which controls what happens
    when a new instance is added. This method should set up whatever
    attributes/functions belong to the typeclass, and then call build_instance.
    See typeclasses.py for examples.
    """
    __metaclass__ = TypeMeta

    @classmethod
    def make_instance(typeclass, type_, *args):
        raise NotImplementedError("Typeclasses must implement make_instance")

    @classmethod
    def derive_instance(typeclass, type_):
        raise NotImplementedError("Typeclasses must implement derive_instance")


def build_instance(typeclass, cls, attrs):
    """
    Add a new instance to a typeclass, i.e. modify the typeclass's instance
    dictionary to include the new instance.

    Args:
        typeclass: The typeclass for which we are adding an instance
        type_: The class or type to be added
        attrs: A dict of {str:function}, mapping function names to functions
               for the typeclass instance

    Returns: None

    Raises:
        TypeError, if type_ is not a member of all superclasses of typeclass
    """
    # 1) check dependencies
    for dep in typeclass.__dependencies__:
        if id(cls) not in dep.__instances__:
            raise TypeError("Missing dependency: %s" % dep.__name__)

    # 2) add type and its instance method to typeclass's instance dictionary
    __methods__ = namedtuple("__%s__" % str(id(cls)), attrs.keys())(**attrs)
    typeclass.__instances__[id(cls)] = __methods__
    return


def has_instance(cls, typeclass):
    """
    Test whether a class is a member of a particular typeclass.

    Args:
        cls: The class or type to test for membership
        typeclass: The typeclass to check. Must be a subclass of Typeclass.

    Returns:
        True if cls is a member of typeclass, and False otherwise.
    """
    if not issubclass(typeclass, Typeclass):
        return False
    return id(cls) in typeclass.__instances__



#=============================================================================#
# Static typing and type signatures

class Hask(object):
    """
    Base class for objects within hask.

    ADTs, TypedFunc, List, Undefined, and other hask-related types are all
    subclasses of Hask.

    All subclasses must define __type__, which returns a representation of the
    object in the internal type system language.
    """
    def __type__(self):
        raise TypeError()


class Undefined(Hask):
    """
    A class with no concrete type definition (so its type can unify with any
    other type). Used to create `undefined` and to enable psuedo-laziness in
    pattern matching.
    """
    def __type__(self):
        return TypeVariable()


def typeof(obj):
    """
    Returns the type of an object within the internal type system.

    Args:
        obj: the object to inspect

    Returns:
        An object representing the type in the internal type system language
        (i.e., a TypeOperator or TypeVariable)
    """
    if isinstance(obj, Hask):
        return obj.__type__()

    elif isinstance(obj, tuple):
        return Tuple(map(typeof, obj))

    elif obj is None:
        return TypeOperator(None, [])

    return TypeOperator(type(obj), [])


class TypeSignature(object):
    """
    Internal representation of a type signature, consisting of a list of
    function type arguments and a list of (typeclass, type_variable) typeclass
    constraint pairs.
    """
    def __init__(self, args, constraints):
        self.args = args
        self.constraints = constraints


class TypeSignatureHKT(object):
    """
    Internal representation of a higher-kinded type within a type signature,
    consisting of the type constructor and its type parameter names.
    """
    def __init__(self, tcon, params):
        self.tcon = tcon
        self.params = params


class TypeSignatureError(Exception):
    pass


def build_sig_arg(arg, var_dict):
    if isinstance(arg, TypeVariable) or isinstance(arg, TypeOperator):
        return arg

    # string representing type variable
    elif isinstance(arg, str):
        if arg not in var_dict:
            var_dict[arg] = TypeVariable()
        return var_dict[arg]

    # subsignature, e.g. H/ (H/ int >> int) >> int >> int
    elif isinstance(arg, TypeSignature):
        return make_fn_type([build_sig_arg(i, var_dict) for i in arg.args])

    # HKT, e.g. t(Maybe "a") or t("m", "a", "b")
    elif isinstance(arg, TypeSignatureHKT):
        if type(arg.tcon) == str:
            hkt = build_sig_arg(arg.tcon, var_dict)
        else:
            hkt = arg.tcon
        return TypeOperator(hkt,
                            [build_sig_arg(a, var_dict) for a in arg.params])

    # None (the unit type)
    elif arg is None:
        return TypeOperator(None, [])

    # Tuples: ("a", "b"), (int, ("a", float)), etc.
    elif isinstance(arg, tuple):
        return Tuple(map(lambda x: build_sig_arg(x, var_dict), arg))

    # Lists: ["a"], [int], etc.
    elif isinstance(arg, list) and len(arg) == 1:
        return ListType(build_sig_arg(arg[0], var_dict))

    # any other type, builtin or user-defined
    elif isinstance(arg, type):
        return TypeOperator(arg, [])

    raise TypeSignatureError("Invalid item in type signature: %s" % arg)


def make_fn_type(params):
    """
    Turn a list of type parameters into the corresponding internal type system
    object that represents the type of a function over the parameters.

    Args:
        params: a list of type paramaters, e.g. from a type signature. These
                should be instances of TypeOperator or TypeVariable

    Returns:
        An instance of TypeOperator representing the function type
    """
    if len(params) == 2:
        last_input, return_type = params
        return Function(last_input, return_type)
    return Function(params[0], make_fn_type(params[1:]))


def build_sig(type_signature, var_dict=None):
    """
    Parse a TypeSignature object and convert it to the internal type system
    language.
    """
    args = type_signature.args
    var_dict = {} if var_dict is None else var_dict
    return [build_sig_arg(i, var_dict) for i in args]


class TypedFunc(Hask):

    def __init__(self, fn, fn_args, fn_type):
        self.__doc__ = fn.__doc__
        self.func = fn
        self.fn_args = fn_args
        self.fn_type = fn_type
        return

    def __type__(self):
        return self.fn_type

    def __call__(self, *args):
        # the environment contains the type of the function and the types
        # of the arguments
        env = {id(self):self.fn_type}
        env.update({id(arg):typeof(arg) for arg in args})
        ap = Var(id(self))

        for arg in args:
            if isinstance(arg, Undefined):
                return arg
            ap = App(ap, Var(id(arg)))
        result_type = analyze(ap, env)

        if len(self.fn_args) - 1 == len(args):
            result = self.func(*args)
            unify(result_type, typeof(result))
            return result
        return TypedFunc(functools.partial(self.func, *args),
                         self.fn_args[len(args):], result_type)

    def __mod__(self, arg):
        """
        (%) :: (a -> b) -> a -> b

        % is the apply operator, equivalent to $ in Haskell
        """
        return self.__call__(arg)

    def __mul__(self, fn):
        """
        (*) :: (b -> c) -> (a -> b) -> (a -> c)

        * is the function compose operator, equivalent to . in Haskell
        """
        if not isinstance(fn, TypedFunc):
            raise TypeError("Cannot compose non-TypedFunc with TypedFunc")

        env = {id(self):self.fn_type, id(fn):fn.fn_type}
        ap = Lam("arg", App(Var(id(self)), App(Var(id(fn)), Var("arg"))))
        newtype = analyze(ap, env)

        composed = lambda x: self.func(fn.func(x))
        newargs = [fn.fn_args[0]] + self.fn_args[1:]

        return TypedFunc(composed, fn_args=newargs, fn_type=newtype)


#=============================================================================#
# ADT creation


class ADT(Hask):
    """Base class for Hask algebraic data types."""
    pass


def make_type_const(name, typeargs):
    """
    Build a new type constructor given a name and the type parameters.

    Args:
        name: the name of the new type constructor to be created
        typeargs: the type parameters to the constructor

    Returns:
        A new class that acts as a type constructor
    """
    def raise_fn(err):
        raise err()

    default_attrs = {"__params__":tuple(typeargs), "__constructors__":()}
    cls = type(name, (ADT,), default_attrs)

    cls.__type__ = lambda self: \
        TypeOperator(cls, [TypeVariable() for i in cls.__params__])

    # Unless typeclasses are derived, ADTs do not support any of these
    # attributes
    cls.__iter__ = lambda self: raise_fn(TypeError)
    cls.__contains__ = lambda self, other: raise_fn(TypeError)
    cls.__add__ = lambda self, other: raise_fn(TypeError)
    cls.__rmul__ = lambda self, other: raise_fn(TypeError)
    cls.__mul__ = lambda self, other: raise_fn(TypeError)
    cls.__lt__ = lambda self, other: raise_fn(TypeError)
    cls.__gt__ = lambda self, other: raise_fn(TypeError)
    cls.__le__ = lambda self, other: raise_fn(TypeError)
    cls.__ge__ = lambda self, other: raise_fn(TypeError)
    cls.__eq__ = lambda self, other: raise_fn(TypeError)
    cls.__ne__ = lambda self, other: raise_fn(TypeError)
    cls.__repr__ = object.__repr__
    cls.__str__ = object.__str__
    return cls


def make_data_const(name, fields, type_constructor, slot_num):
    """
    Build a data constructor given the name, the list of field types, and the
    corresponding type constructor.

    The general approach is to create a subclass of the type constructor and a
    new class created with `namedtuple`, with some of the features from
    `namedtuple` such as equality and comparison operators stripped out.
    """
    # create the data constructor
    base = namedtuple(name, ["i%s" % i for i, _ in enumerate(fields)])
    cls = type(name, (type_constructor, base), {})
    cls.__type_constructor__ = type_constructor
    cls.__ADT_slot__ = slot_num

    if len(fields) == 0:
        # If the data constructor takes no arguments, create an instance of it
        # and return that instance rather than returning the class
        cls = cls()
    else:
        # Otherwise, modify __type__ so that it matches up fields from the data
        # constructor with type params from the type constructor
        def __type__(self):
            args = [typeof(self[fields.index(p)]) \
                    if p in fields else TypeVariable()
                    for p in type_constructor.__params__]
            return TypeOperator(type_constructor, args)
        cls.__type__ = __type__

    type_constructor.__constructors__ += (cls,)
    return cls


def build_ADT(typename, typeargs, data_constructors, to_derive):
    """
    Returns:
        The type constructor, followed by each of the data constructors (in the
        order they were defined)
    """
    # 1) Create the new type constructor and data constructors
    newtype = make_type_const(typename, typeargs)
    dcons = [make_data_const(d[0], d[1], newtype, n)
             for n, d in enumerate(data_constructors)]

    # 2) Derive typeclass instances for the new type constructor
    for tclass in to_derive:
        tclass.derive_instance(newtype)

    # 3) Wrap data constructors in TypedFunc instances
    for i, dc_spec in enumerate(data_constructors):
        if len(dc_spec[1]) == 0:
            continue

        return_type = TypeSignatureHKT(newtype, typeargs)
        sig = TypeSignature(list(dc_spec[1]) + [return_type], [])
        sig_args = build_sig(sig, {})
        dcons[i] = TypedFunc(dcons[i], sig_args, make_fn_type(sig_args))
    return tuple([newtype,] + dcons)


#=============================================================================#
# Pattern matching


class PatternMatchBind(object):
    """Represents a local variable bound by pattern matching."""
    def __init__(self, name):
        self.name = name
        return


class PatternMatchListBind(object):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        return


def pattern_match(value, pattern, env=None):
    """
    Pattern match a value and a pattern.

    Args:
        value: the value to pattern-match on
        pattern: a pattern, consisting of literals and/or locally bound
                 variables
        env: a dictionary of local variables bound while matching

    Returns: (True, env) if the match is successful, and (False, env) otherwise
    """
    env = {} if env is None else env
    if isinstance(pattern, PatternMatchBind):
        if pattern.name in env:
            raise SyntaxError("Conflicting definitions for %s" % pattern.name)
        env[pattern.name] = value
        return True, env

    elif isinstance(pattern, PatternMatchListBind):
        head, tail = list(value[:len(pattern.head)]), value[len(pattern.head):]
        matches, env = pattern_match(head, pattern.head, env)
        if matches:
            return pattern_match(tail, pattern.tail, env)
        return False, env

    elif type(value) == type(pattern):
        if isinstance(value, ADT):
            return pattern_match(nt_to_tuple(value), nt_to_tuple(pattern), env)

        elif hasattr(value, "__iter__"):
            matches = []
            if len(value) != len(pattern):
                return False, env

            for v, p in zip(value, pattern):
                match_status, env = pattern_match(v, p, env)
                matches.append(match_status)
            return all(matches), env

        elif value == pattern:
            return True, env

    return False, env
