import itertools
import functools

from ..lang import H
from ..lang import sig
from ..lang import t
from ..lang import L

from Eq import Eq
from Ord import Ord
from Num import Num
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
def map_(fn, iterable):
    return L[itertools.imap(fn, iterable)]


@sig(H/ (H/ "a" >> bool) >> ["a"] >> ["a"])
def filter_(fn, iterable):
    return L[itertools.ifilter(fn, iterable)]


@sig(H/ ["a"] >> ["a"] )
def reverse(xs):
    """
    reverse :: [a] -> [a]

    reverse(xs) returns the elements of xs in reverse order. xs must be finite.
    """
    return L[(x for x in xs[::-1])]


@sig(H/ "a" >> ["a"] >> ["a"] )
def intersperse(x, xs):
    """
    intersperse :: a -> [a] -> [a]

    The intersperse function takes an element and a list and `intersperses'
    that element between the elements of the list.
    """
    def __intersperse(x, xs):
        for y in init(xs):
            yield y
            yield x
        yield last(xs)
    return L[__intersperse(x, xs)]


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
    return L[[L[x] for x in zip(*xs)]]


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
    return L[itertools.permutations(xs)]


#=============================================================================#
# Reducing lists (folds)


@sig(H/ (H/ "a" >> "b" >> "a") >> "a" >> ["b"] >> "a")
def foldl(f, b, xs):
    """
    foldl :: (a -> b -> a) -> a -> [b] -> a
    """
    pass


@sig(H/ (H/ "a" >> "b" >> "a") >> "a" >> ["b"] >> "a")
def foldl_(f, b, xs):
    """
    foldl' :: (a -> b -> a) -> a -> [b] -> a
    """
    pass


@sig(H/ (H/ "a" >> "a" >> "a") >> ["a"] >> "a")
def foldl1(f, b, xs):
    pass


@sig(H/ (H/ "a" >> "a" >> "a") >> ["a"] >> "a")
def foldl1_(f, b, xs):
    """
    foldl1' :: (a -> a -> a) -> [a] -> a
    """
    pass


@sig(H/ (H/ "a" >> "b" >> "b") >> "b" >> ["a"] >> "b")
def foldr(f, b, xs):
    """
    foldr :: (a -> b -> b) -> b -> [a] -> b
    """
    pass


@sig(H/ (H/ "a" >> "a" >> "a") >> ["a"] >> "a")
def foldr1(f, b, xs):
    """
    foldr1 :: (a -> a -> a) -> [a] -> a
    """
    pass


#=============================================================================#
## Special folds


@sig(H/ [["a"]] >> ["a"] )
def concat(xss):
    """
    Concatenate a list of lists.
    """
    return L[(x for xs in xss for x in xs)]


@sig(H/ (H/ "a" >> ["b"]) >> ["a"] >> ["b"])
def concatMap(f, xs):
    """
    concatMap :: (a -> [b]) -> [a] -> [b]
    """
    return bind(xs, f)


@sig(H/ [bool] >> bool)
def and_(xs):
    """
    and :: [Bool] -> Bool
    """
    return all(xs)


@sig(H/ [bool] >> bool)
def or_(xs):
    """
    or :: [Bool] -> Bool
    """
    return any(xs)


@sig(H/ (H/ "a" >> bool) >> ["a"] >> bool)
def any_(xs):
    """
    any :: (a -> Bool) -> [a] -> Bool
    """
    return any((p(x) for x in xs))


@sig(H/ (H/ "a" >> bool) >> ["a"] >> bool)
def all_(p, xs):
    """
    all :: (a -> Bool) -> [a] -> Bool
    """
    return all((p(x) for x in xs))


@sig(H[(Num, "a")]/ ["a"] >> "a")
def sum_(xs):
    return functools.reduce(operator.add, xs)


@sig(H[(Num, "a")]/ ["a"] >> "a")
def product(xs):
    return functools.reduce(operator.mul, xs)


@sig(H[(Ord, "a")]/ ["a"] >> "a")
def maximum(xs):
    return max(xs)


@sig(H[(Ord, "a")]/ ["a"] >> "a")
def minimum(xs):
    return min(xs)


#=============================================================================#
# Building lists
## Scans


def scanl(f, z, xs):
    pass


def scanl_(f, z, xs):
    pass


def scanl1(f, xs):
    pass


def scanr(f, z, xs):
    pass

def scanr1(f, xs):
    pass


#=============================================================================#
## Accumulating maps


def mapAccumL(f, a, tb):
    pass

def mapAccumR(f, a, tb):
    pass


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
## Extracting sublists


def take(n, xs):
    pass

def drop(n, xs):
    pass

def splitAt(n, xs):
    pass

def takeWhile(p, xs):
    pass

def dropWhile(p, xs):
    pass

def dropWhileEnd(p, xs):
    pass

def span(p, xs):
    pass

def break_(p, xs):
    pass

def stripPrefix(xs, ys):
    pass

def group(xs):
    pass

def inits(xs):
    pass

def tails(xs):
    pass



#=============================================================================#
## Predicates


def isPrefixOf(xs, ys):
    return xs == ys[:len(xs)]


def isSuffixOf(xs, ys):
    return xs == ys[-len(xs):]


def isSubsequenceOf(xs, ys):
    """
    """
    for i in xrange(len(ys)-len(xs)+1):
        for j in xrange(len(xs)):
            if ys[i+j] != xs[j]:
                break
        else:
            return True
    return False


#=============================================================================#
# Searching lists
## Searching by equality


@sig(H[(Eq, "a")]/ "a" >> ["a"] >> bool)
def elem(x, xs):
    """
    elem :: Eq a => a -> [a] -> Bool

    elem is the list membership predicate, elem(x, xs). For the result to be
    False, the list must be finite; True, however, results from an element
    equal to x found at a finite index of a finite or infinite list.
    """
    return x in xs


@sig(H[(Eq, "a")]/ "a" >> ["a"] >> bool)
def notElem(x, xs):
    """
    notElem :: Eq a => a -> [a] -> Bool

    notElem is the negation of elem.
    """
    return not elem(x, xs)


@sig(H[(Eq, "a")]/ "a" >> [("a", "b")] >> t(Maybe, "b"))
def lookup(a, assoc_list):
    """
    lookup :: Eq a => a -> [(a, b)] -> Maybe b

    """
    for key, value in assoc_list:
        if key == a:
            return Just(value)
    return Nothing


#=============================================================================#
## Searching with a predicate


@sig(H/ (H/ "a" >> bool) >> ["a"] >> t(Maybe, "a"))
def find(p, xs):
    """
    find :: (a -> Bool) -> [a] -> Maybe a

    The find function takes a predicate and a structure and returns the
    leftmost element of the structure matching the predicate, or Nothing if
    there is no such element.
    """
    for x in xs:
        if p(x):
            return Just(x)
    return Nothing


@sig(H/ (H/ "a" >> bool) >> ["a"] >> (["a"], ["a"]))
def partition(f, xs):
    """
    partition :: (a -> Bool) -> [a] -> ([a], [a])

    The partition function takes a predicate a list and returns the pair of
    lists of elements which do and do not satisfy the predicate.
    """
    return L[(x for x in xs if f(x))], L[(y for y in xs if not f(y))]


#=============================================================================#
# Indexing lists


def elemIndex(x, xs):
    pass


#=============================================================================#
# Zipping and unzipping lists

def zip_(xs, ys):
    pass

def zip3(a, b, c):
    pass

def zip4(a, b, c, d):
    pass

def zip5(a, b, c, d, e):
    pass

def zip6(a, b, c, d, e, f):
    pass

def zip7(a, b, c, d, e, f, g):
    pass

def zipWith(fn, xs, ys):
    pass

def zipWith3(fn, a, b, c):
    pass

def zipWith4(fn, a, b, c, d):
    pass

def zipWith5(fn, a, b, c, d, e):
    pass

def zipWith6(fn, a, b, c, d, e, f):
    pass

def zipWith7(fn, a, b, c, d, e, f):
    pass

def unzip(xs):
    pass

def unzip3(xs):
    pass

def unzip4(xs):
    pass

def unzip5(xs):
    pass

def unzip6(xs):
    pass

def unzip7(xs):
    pass


#=============================================================================#
# Special lists
## Functions on strings

from String import lines
from String import words
from String import unlines
from String import unwords


#=============================================================================#
## "Set" operations

def nub(xs):
    return


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
## The "By" operations
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


## The "generic" operators

def genericLength(xs):
    pass

def genericTake(n, xs):
    pass

def genericDrop(n, xs):
    pass

def genericSplitAt(n, xs):
    pass
