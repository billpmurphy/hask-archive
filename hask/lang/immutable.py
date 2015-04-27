import abc
import collections
import itertools
import types


class ImmutableMeta(abc.ABCMeta):

    def __new__(mcls, name, bases, namespace):
        if name != 'Immutable' or bases != (object,) \
               or namespace['__module__'] != mcls.__module__:
            if '__init__' in namespace:
                init_method = namespace['__init__']
                def init_wrapper(self, *args, **kwargs):
                    self.__init_caller__(init_method, *args, **kwargs)
                namespace['__init__'] = init_wrapper
            for methodname in ['__setattr__', '__delattr__',
                               '__setitem__', '__delitem__']:
                if methodname in namespace:
                    raise TypeError("method %s not allowed " % methodname +
                                    "in an immutable type")
        cls = super(ImmutableMeta, mcls).__new__(mcls, name, bases, namespace)
        return cls

#
# Immutable is an abstract base class for immutable Python objects.
# It allows assignments to attributes only inside __init__, and verifies
# that all attribute values are themselves immutable.
#
class Immutable(object):
    __metaclass__ = ImmutableMeta

    __locked = False
    __init_nesting = 0

    def __init_caller__(self, method, *args, **kwargs):
        if self.__locked:
            raise ValueError("immutable object already initialized")
        try:
            if method is not None:
                self.__init_nesting += 1
                method(self, *args, **kwargs)
                self.__init_nesting -= 1
            if self.__init_nesting == 0:
                for attr, value in  self.__dict__.iteritems():
                    if not isinstance(value, Immutable):
                        raise TypeError("value of attribute %s not immutable"
                                        % attr)
        finally:
            if self.__init_nesting == 0:
                self.__locked = True

    def __init__(self):
        self.__init_caller__(None)

    def __setattr__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__setattr__(self, *args)

    def __delattr__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__delattr__(self, *args)

    def __setitem__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__setitem__(self, *args)

    def __delitem__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__delitem__(self, *args)


def derived_eq(self, other):
    return self.__class__ is other.__class__ \
            and set(self.__dict__.keys()) == set(other.__dict__.keys()) \
            and all(self.__dict__[k] == other.__dict__[k]
                    for k in self.__dict__)

def _derived_ne(self, other):
    return not self.__eq__(other)
