import itertools

from ..lang import H
from ..lang import sig
from ..lang import t
from ..lang import L

from Ord import Ord
from Maybe import Maybe
from Maybe import Just
from Maybe import Nothing


#=============================================================================#
# Basic functions


@sig(H/ ["a"] >> "a" )
def head(xs):
    """
    head :: [a] -> a

    Extract the first element of a list, which must be non-empty.
    """
    return xs[0]


@sig(H/ ["a"] >> "a" )
def last(xs):
    """
    last :: [a] -> a

    Extract the last element of a list, which must be finite and non-empty.
    """
    return xs[-1]


@sig(H/ ["a"] >> ["a"] )
def tail(xs):
    """
    tail :: [a] -> [a]

    Extract the elements after the head of a list, which must be non-empty.
    """
    return L[(x for x in xs[1:])]


@sig(H/ ["a"] >> ["a"] )
def init(xs):
    """
    init :: [a] -> [a]

    Return all the elements of a list except the last one. The list must be
    non-empty.
    """
    return L[(x for x in xs[:-1])]


@sig(H/ ["a"] >> t(Maybe, ("a", ["a"])))
def uncons(xs):
    """
    uncons :: [a] -> Maybe (a, [a])

    Decompose a list into its head and tail. If the list is empty, returns
    Nothing. If the list is non-empty, returns Just((x, xs)), where x is the
    head of the list and xs its tail.
    """
    return Just((xs[0], xs[1:])) if xs else Nothing


@sig(H/ ["a"] >> bool)
def null(xs):
    """
    null :: [a] -> bool

    Test whether the structure is empty.
    """
    return bool(xs)


@sig(H/ ["a"] >> int )
def length(xs):
    """
    length :: [a] -> int

    Returns the size/length of a finite structure as an Int. The default
    implementation is optimized for structures that are similar to cons-lists,
    because there is no general way to do better.
    """
    return len(x)


#=============================================================================#
# List transformations


@sig(H/ (H/ "a" >> "b") >> ["a"] >> ["b"])
def map(fn, iterable):
    return L[(itertools.imap(fn, iterable))]


@sig(H/ (H/ "a" >> bool) >> ["a"] >> ["a"])
def filter(fn, iterable):
    return L[(itertools.ifilter(fn, iterable))]


@sig(H/ ["a"] >> ["a"] )
def reverse(xs):
    """
    reverse :: [a] -> [a]

    reverse(xs) returns the elements of xs in reverse order. xs must be finite.
    """
    return L[(x for x in xs[::-1])]


@sig(H/ "a" >> ["a"] >> ["a"] )
def intersperse(a, xs):
    """
    intersperse :: a -> [a] -> [a]

    The intersperse function takes an element and a list and `intersperses'
    that element between the elements of the list.
    """
    pass


@sig(H/ ["a"] >> [["a"]] >> ["a"] )
def intercalate(xs, xss):
    """
    intercalate :: [a] -> [[a]] -> [a]

    intercalate(xs,xss) is equivalent to concat(intersperse(xs,xss)). It
    inserts the list xs in between the lists in xss and concatenates the
    result.

    TODO: make this more efficient
    """
    return concat(intersperse(xs, xss))


@sig(H/ [["a"]] >> [["a"]] )
def transpose(xs):
    """
    transpose :: [[a]] -> [[a]]

    The transpose function transposes the rows and columns of its argument.
    """
    pass


@sig(H/ ["a"] >> [["a"]] )
def subsequences(xs):
    """
    subsequences :: [a] -> [[a]]

    The subsequences function returns the list of all subsequences of the
    argument.

    subsequences(L["a","b","c"]) == L["","a","b","ab","c","ac","bc","abc"]
    """
    pass


@sig(H/ ["a"] >> [["a"]] )
def permutations(xs):
    """
    permutations :: [a] -> [[a]]

    The permutations function returns the list of all permutations of the
    argument.

    permutations(L["a","b","c"]) == L["abc","bac","cba","bca","cab","acb"]
    """
    pass


#=============================================================================#
# Reducing lists (folds)


def foldl(f, b, xs):
    pass

def foldl_(f, b, xs):
    pass

def foldl1(f, b, xs):
    pass

def foldl1_(f, b, xs):
    pass

def foldr(f, b, xs):
    pass

def foldr1(f, b, xs):
    pass


#=============================================================================#
## Special folds


@sig(H/ [["a"]] >> ["a"] )
def concat(xss):
    """
    Concatenate a list of lists.
    """
    return L[(x for xs in xss for x in xs)]


def concatMap(f, xs):
    pass

def and_(xs):
    pass

def or_(xs):
    pass

def any_(xs):
    pass

def all_(xs):
    pass

#def sum(xs):
#    pass

def product(xs):
    pass

def maximum(xs):
    pass

def minimum(xs):
    pass


#=============================================================================#
# Building lists


#=============================================================================#
## Scans


#=============================================================================#
## Accumulating maps


#=============================================================================#
## Infinite lists


@sig(H/ (H/ "a" >> "a") >> "a" >> ["a"])
def iterate(f, x):
    """
    iterate :: (a -> a) -> a -> [a]

    iterate(f, x) returns an infinite List of repeated applications of f to x:
    iterate(f, x) == [x, f(x), f(f(x)), ...]
    """
    def __iterate(f, x):
        while True:
            yield x
            x = f(x)
    return L[__iterate(f, x)]


@sig(H/ "a" >> ["a"])
def repeat(x):
    """
    repeat :: a -> [a]

    repeat(x) is an infinite list, with x the value of every element.
    """
    def __repeat(x):
        while True:
            yield x
    return L[__repeat(x)]


@sig(H/ int >> "a" >> ["a"])
def replicate(n, x):
    """
    replicate :: Int -> a -> [a]

    replicate(n, x) is a list of length n with x the value of every element.
    """
    def __replicate(n, x):
        for _ in range(n):
            yield x
    return L[__replicate(n, x)]


@sig(H/ ["a"] >> ["a"])
def cycle(x):
    """
    cycle :: [a] -> [a]

    cycle ties a finite list into a circular one, or equivalently, the infinite
    repetition of the original list. It is the identity on infinite lists.
    """
    def __cycle(x):
        while True:
            for i in x:
                yield i
    return L[__cycle(x)]


#=============================================================================#
## Unfolding


def unfoldr(f, x):
    pass


#=============================================================================#
# Sublists

#=============================================================================#
## Exctracting sublists



#=============================================================================#
## Predicates

def isPrefixOf(xs, ys):
    pass

def isSuffixOf(xs, ys):
    pass

def isSubsequenceOf(xs, ys):
    pass


#=============================================================================#
# Searching lists

#=============================================================================#
## Searching by equality


def elem(a, list_a):
    """
    elem is the list membership predicate, elem(x, xs). For the result to be
    False, the list must be finite; True, however, results from an element
    equal to x found at a finite index of a finite or infinite list.
    """
    return a in list_a


def notElem(a, list_a):
    """
    notElem is the negation of elem.
    """
    return not elem(a, list_a)


def lookup(a, assoc_list):
    """
    """
    for key, value in assoc_list:
        if key == a:
            return Just(value)
    return Nothing


#=============================================================================#
## Searching with a predicate


def find(f, xs):
    """
    The find function takes a predicate and a structure and returns the
    leftmost element of the structure matching the predicate, or Nothing if
    there is no such element.
    """
    for x in xs:
        if f(x):
            return Just(x)
    return Nothing


def partition(f, xs):
    """
    The partition function takes a predicate a list and returns the pair of
    lists of elements which do and do not satisfy the predicate.
    """
    return (x for x in xs if f(x)), (y for y in xs if not f(y))


#=============================================================================#
# Indexing lists


#=============================================================================#
# Zipping and unzipping lists


#=============================================================================#
# Special lists


#=============================================================================#
## Functions on strings

from String import lines
from String import words
from String import unlines
from String import unwords


#=============================================================================#
## "Set" operations

def nub(xs):
    pass


def delete(a, xs):
    pass


def diff(xs, ys):
    pass


def union(xs, ys):
    pass


def intersect(xs, ys):
    pass


#=============================================================================#
## Ordered lists


@sig(H[(Ord, "a")]/ ["a"] >> ["a"])
def sort(xs):
    pass


@sig(H[(Ord, "b")]/ (H/ "a" >> "b") >> ["a"] >> ["a"])
def sortOn(f, xs):
    pass


@sig(H[(Ord, "a")]/ "a" >> ["a"] >> ["a"])
def insert(x, xs):
    """
    insert :: Ord a => a -> [a] -> [a]

    The insert function takes an element and a list and inserts the element
    into the list at the first position where it is less than or equal to the
    next element. In particular, if the list is sorted before the call, the
    result will also be sorted.
    """
    def __insert(x, xs):
        for i in xs:
            if i > x:
                yield x
            yield i
    return L[__insert(x, xs)]


#=============================================================================#
# Generalized functions


#=============================================================================#
## The "By" operations


#=============================================================================#
### User-supplied equality (replacing an Eq context)


def nubBy(f, xs):
    pass


def deleteBy(f, xs):
    pass


def deleteFirstBy(f, xs, ys):
    pass


def unionBy(f, xs, ys):
    pass


def intersectBy(f, xs, ys):
    pass


def groupBy(f, xs):
    pass


#=============================================================================#
### User-supplied comparison (replacing an Ord context)

def sortBy(f, xs):
    pass


def insertBy(f, xs):
    pass


def maximumBy(f, xs):
    pass


def minimumBy(f, xs):
    pass
