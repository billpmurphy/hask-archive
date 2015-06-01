from ..lang.builtins import Either
from ..lang.builtins import Left
from ..lang.builtins import Right


def either(f_a, f_b, either_a_b):
    """
    either :: (a -> c) -> (b -> c) -> Either a b -> c

    Case analysis for the Either type. If the value is Left(a), apply the first
    function to a; if it is Right(b), apply the second function to b.
    """
    pass


def lefts(xs):
    pass


def rights(xs):
    pass


def isLeft(x):
    pass


def isRight(x):
    pass


def partitionEithers(xs):
    pass
