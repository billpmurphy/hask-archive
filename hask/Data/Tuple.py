from ..lang.syntax import sig, H


@sig(H/ ("a", "b") >> "a" )
def fst(tup):
    """
    fst :: (a, b) -> a

    Extract the first component of a pair.
    """
    x, y = tup
    return x


@sig(H/ ("a", "b") >> "b" )
def snd(tup):
    """
    snd :: (a, b) -> b

    Extract the second component of a pair.
    """
    x, y = tup
    return y


def curry(tup_fn, x, y):
    """
    curry :: ((a, b) -> c) -> a -> b -> c

    curry converts an uncurried function to a curried function.
    """
    return tup_fn((a, b))


def uncurry(fn, tup):
    """
    curry :: ((a, b) -> c) -> a -> b -> c

    uncurry converts a curried function to a function on pairs.
    """
    return fn(fst(tup), snd(tup))


@sig(H/ ("a", "b") >> ("b", "a") )
def swap(tup):
    """
    swap :: (a, b) -> (b, a)

    Swap the components of a pair.
    """
    a, b = tup
    return (b, a)