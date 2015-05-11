from ...lang.builtins import Just
from ...lang.builtins import Nothing

## Data.List

## Basic functions

def head(xs):
    """
    Extract the first element of a list, which must be non-empty.
    """
    return xs[0]


def last(xs):
    """
    Extract the last element of a list, which must be finite and non-empty.
    """
    return xs[-1]


def tail(xs):
    """
    Extract the elements after the head of a list, which must be non-empty.
    """
    for x in xs[1:]:
        yield x


def init(xs):
    """
    Return all the elements of a list except the last one. The list must be
    non-empty.
    """
    for x in xs[:-1]:
        yield x


def uncons(xs):
    """
    Decompose a list into its head and tail. If the list is empty, returns
    Nothing. If the list is non-empty, returns Just (x, xs), where x is the
    head of the list and xs its tail.
    """
    return Just((xs[0], xs[1:])) if xs else Nothing


def null(xs):
    """
    Test whether the structure is empty.
    """
    return bool(xs)


def length(xs):
    """
    Returns the size/length of a finite structure as an Int. The default
    implementation is optimized for structures that are similar to cons-lists,
    because there is no general way to do better.
    """
    return len(x)


## List transformations

def reverse(xs):
    """
    reverse xs returns the elements of xs in reverse order. xs must be finite.
    """
    for x in xs[::-1]:
        yield x


def intersperse(a, xs):
    """
    The intersperse function takes an element and a list and `intersperses'
    that element between the elements of the list.
    """
    pass


def intercalate(xs, xss):
    """
    intercalate(xs,xss) is equivalent to concat(intersperse(xs,xss)). It
    inserts the list xs in between the lists in xss and concatenates the
    result.
    """
    return concat(intersperse(xs, xss))


def transpose(xs):
    """
    The transpose function transposes the rows and columns of its argument.
    """
    pass


def subsequences(xs):
    pass


def permutations(xs):
    pass


## Reducing lists

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


## Special folds

def concat(xss):
    """
    Concatenate a list of lists.
    """
    return (x for xs in xss for x in xs)

def concatMap(f, xs):
    pass

def list_and(xs):
    pass

def list_or(xs):
    pass

def any(xs):
    pass

def all(xs):
    pass

def sum(xs):
    pass

def product(xs):
    pass

def maximum(xs):
    pass

def minimum(xs):
    pass

## Predicates

def isPrefixOf(xs, ys):
    pass

def isSuffixOf(xs, ys):
    pass

def isSubsequenceOf(xs, ys):
    pass


## Searching lists

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

## Indexing lists

## Zipping and unzipping lists

## Functions on strings

def lines(s):
    """
    lines breaks a string up into a list of strings at newline characters. The
    resulting strings do not contain newlines.
    """
    return s.split("\n")


def words(s):
    """
    words breaks a string up into a list of words, which were delimited by
    white space.
    """
    return s.split(" ")


def unlines(lines):
    """
    unlines is an inverse operation to lines. It joins lines, after appending a
    terminating newline to each.
    """
    return "\n".join(lines)


def unwords(words):
    """
    unwords is an inverse operation to words. It joins words with separating
    spaces.
    """
    return " ".join(words)


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


## User-supplied equality


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


## User-supplied comparison

def sortBy(f, xs):
    pass


def insertBy(f, xs):
    pass


def maximumBy(f, xs):
    pass


def minimumBy(f, xs):
    pass
