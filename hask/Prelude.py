import itertools

from .lang.builtins import List


#=============================================================================#
# Basic data types

from Data.Maybe import maybe



#=============================================================================#
# Tuples


from Data.Tuple import fst
from Data.Tuple import snd
from Data.Tuple import curry
from Data.Tuple import uncurry


#=============================================================================#
# Numeric functions


def subtract(x, y):
    """
    subtract :: Num a => a -> a -> a
    the same as flip(__-__).
    """
    return y - x


#@sig( H[(Integral, "a")]/ "a" >> bool )
def even(x):
    """
    even :: Integral a => a -> Bool
    Returns True if the integral value is even, and False otherwise.
    """
    return x % 2 == 0


#@sig( H[(Integral, "a")]/ "a" >> bool )
def odd(x):
    """
    even :: Integral a => a -> Bool
    Returns True if the integral value is odd, and False otherwise.
    """
    return not even(x)


def gcd(x, y):
    """
    gcd :: Integral a => a -> a -> a
    gcd(x,y) is the non-negative factor of both x and y of which every common
    factor of x and y is also a factor; for example gcd(4,2) = 2, gcd(-4,6) =
    2, gcd(0,4) = 4. gcd(0,0) = 0. (That is, the common divisor that is
    "greatest" in the divisibility preordering.)
    """
    pass


def lcm(x, y):
    """
    lcm :: Integral a => a -> a -> a
    lcm(x,y) is the smallest positive integer that both x and y divide.
    """
    pass


#sig(H/ ("a" >> bool) >> ("a" >> "a") >> "a" >> "a" )
def until(p, f, a):
    """
    until(p, f, a) yields the result of applying f until p(a) holds.
    """
    while not p(a):
        a = f(a)
    return a


#@sig(H/ "a" >> List("a"))
def repeat(x):
    """
    repeat(x) is an infinite list, with x the value of every element.
    """
    return repeat(x)


#sig(H/ ("a" >> "a") >> "a" >> List("a") )
def iterate(f, x):
    """
    iterate(f,x) returns an infinite list of repeated applications of f to x:
       iterate(f,x) == [x, f x, f (f x), ...]
    """
    while True:
        yield x
        x = f(x)


#@sig(H/ str -> "a")
def error(msg):
    """
    error :: str -> a
    error stops execution and displays an error message.
    """
    raise Exception(msg)


#=============================================================================#
# List operations

def map(fn, iterable):
    return List(itertools.imap(fn, iterable))

#@sig(H[Traversable . m]/ ("a" >> bool) >> t.m("a") >> List("a") )
def filter(fn, iterable):
    return List(itertools.ifilter(fn, iterable))


def head(xs):
    """
    head :: [a] -> a
    Extract the first element of a list, which must be non-empty.
    """
    return xs[0]


def last(xs):
    """
    last :: [a] -> a
    Extract the last element of a list, which must be finite and non-empty.
    """
    return xs[-1]


def tail(xs):
    """
    tail :: [a] -> [a]
    Extract the elements after the head of a list, which must be non-empty.
    """
    return List((x for x in xs[1:]))


def init(xs):
    """
    init :: [a] -> [a]
    Return all the elements of a list except the last one. The list must be
    non-empty.
    """
    return List((x for x in xs[:-1]))


def reverse(xs):
    """
    reverse :: [a] -> [a]
    reverse xs returns the elements of xs in reverse order. xs must be finite.
    """
    return List((x for x in xs[::-1]))


#=============================================================================#
## Functions on strings

from Data.String import lines
from Data.String import words
from Data.String import unlines
from Data.String import unwords
