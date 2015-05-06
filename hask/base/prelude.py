import itertools

from ..stdlib.lazylist import List


def map(fn, iterable):
    return List(itertools.imap(fn, iterable))


def filter(fn, iterable):
    return List(itertools.ifilter(fn, iterable))


def repeat(x):
    """
    repeat(x) is an infinite list, with x the value of every element.
    """
    return repeat(x)

def iterate(f, x):
    """
    iterate(f,x) returns an infinite list of repeated applications of f to x:
       iterate(f,x) == [x, f x, f (f x), ...]
    """
    while True:
        yield x
        x = f(x)


def error(msg):
    raise Exception(msg)


def undefined():
    error("Prelude.undefined")

## IO ops
