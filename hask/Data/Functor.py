from ..lang.typeclasses import Functor

def fmap(x, f):
    return Functor[x].fmap(x, f)
