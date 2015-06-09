from ..lang.builtins import Either
from ..lang.builtins import Left
from ..lang.builtins import Right
from ..lang.syntax import L


#@sig(H/ (H/ "a" >> "c") >> (H/ "b" >> "c") >> Either("a", "b") >> "c")
def either(f_a, f_b, either_a_b):
    """
    either :: (a -> c) -> (b -> c) -> Either a b -> c

    Case analysis for the Either type. If the value is Left(a), apply the first
    function to a; if it is Right(b), apply the second function to b.
    """
    pass


#@sig(H/ [Either("a", "b")] >> ["a"])
def lefts(xs):
    """
    lefts :: [Either a b] -> [a]

    Extracts from a List of Either all the Left elements. All the Left elements
    are extracted in order.
    """
    pass


#@sig(H/ [Either("a", "b")] >> ["b"])
def rights(xs):
    """
    rights :: [Either a b] -> [b]

    Extracts from a list of Either all the Right elements. All the Right
    elements are extracted in order.
    """
    pass


#@sig(H/ Either("a", "b") >> Bool)
def isLeft(x):
    """
    isLeft :: Either a b -> Bool

    Return True if the given value is a Left-value, False otherwise.
    """
    pass


#@sig(H/ Either("a", "b") >> Bool)
def isRight(x):
    """
    isRight :: Either a b -> Bool

    Return True if the given value is a Right-value, False otherwise.
    """
    pass


#@sig(H/ [Either("a", "b")] >> (["a"], ["b"]))
def partitionEithers(xs):
    """
    partitionEithers :: [Either a b] -> ([a], [b])

    Partitions a List of Either into two lists. All the Left elements are
    extracted, in order, to the first component of the output. Similarly the
    Right elements are extracted to the second component of the output.
    """
    pass
