from ..Prelude import fst
from ..Prelude import snd
from ..Prelude import curry
from ..Prelude import uncurry


#@sig( H/ ("a", "b") >> ("b", "a") )
def swap(tup):
    a, b = tup
    return (b, a)
