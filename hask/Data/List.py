from ..lang.syntax import H
from ..lang.syntax import sig
from ..lang.syntax import L

from ..lang.builtins import Maybe
from ..lang.builtins import Just
from ..lang.builtins import Nothing


#=============================================================================#
# Basic functions


def uncons(xs):
    """
    uncons :: [a] -> Maybe (a, [a])

    Decompose a list into its head and tail. If the list is empty, returns
    Nothing. If the list is non-empty, returns Just((x, xs)), where x is the
    head of the list and xs its tail.
    """
    return Just((xs[0], xs[1:])) if xs else Nothing


@sig( H/ ["a"] >> bool )
def null(xs):
    """
    null :: [a] -> bool

    Test whether the structure is empty.
    """
    return bool(xs)


@sig( H/ ["a"] >> int )
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


@sig( H/ "a" >> ["a"] >> ["a"] )
def intersperse(a, xs):
    """
    intersperse :: a -> [a] -> [a]

    The intersperse function takes an element and a list and `intersperses'
    that element between the elements of the list.
    """
    pass


@sig( H/ ["a"] >> [["a"]] >> ["a"] )
def intercalate(xs, xss):
    """
    intercalate :: [a] -> [[a]] -> [a]

    intercalate(xs,xss) is equivalent to concat(intersperse(xs,xss)). It
    inserts the list xs in between the lists in xss and concatenates the
    result.
    """
    # this can probably be made more efficient
    return concat(intersperse(xs, xss))


@sig( H/ [["a"]] >> [["a"]] )
def transpose(xs):
    """
    transpose :: [[a]] -> [[a]]

    The transpose function transposes the rows and columns of its argument.
    """
    pass


@sig( H/ ["a"] >> [["a"]] )
def subsequences(xs):
    """
    subsequences :: [a] -> [[a]]

    The subsequences function returns the list of all subsequences of the
    argument.

    subsequences(L["a","b","c"]) == L["","a","b","ab","c","ac","bc","abc"]
    """
    pass


@sig( H/ ["a"] >> [["a"]] )
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


@sig( H/ [["a"]] >> ["a"] )
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

def iterate(f, x):
    def __iterate(f, x):
        while True:
            yield x
            x = f(x)
    return L[__iterate(f, x)]


def repeat(a):
    pass


def replicate(i, a):
    pass


def cycle(a):
    pass


#=============================================================================#
## Unfolding


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

def sort(xs):
    pass


def sortOn(f, xs):
    pass


def insert(x, xs):
    """
    The insert function takes an element and a list and inserts the element
    into the list at the first position where it is less than or equal to the
    next element. In particular, if the list is sorted before the call, the
    result will also be sorted.
    """
    for i in xs:
        if i > x:
            yield x
        yield i


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
