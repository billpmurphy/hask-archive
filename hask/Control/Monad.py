import itertools

from ..lang import sig
from ..lang import H
from ..lang import t
from ..lang import L
from ..lang import build_instance
from ..lang import is_builtin
from ..lang import List
from ..lang import instance
from ..Data.Functor import fmap
from Applicative import Applicative


class Monad(Applicative):

    @classmethod
    def make_instance(typeclass, cls, bind):
        bind = bind ** (H[(Monad, "m")]/ t("m", "a") >> (H/ "a" >> t("m", "b")) >> t("m", "b"))
        if not is_builtin(cls):
            def bind_wrap(s, o):
                return Monad[s].bind(s, o)
            cls.__rshift__ = bind_wrap
        build_instance(Monad, cls, {"bind":bind})
        return

@sig(H[(Monad, "m")]/ t("m", "a") >> (H/ "a" >> t("m", "b")) >> t("m", "b"))
def bind(m, fn):
    """
    bind :: Monad m => m a -> (a -> m b) -> m b

    Monadic bind.
    """
    return Monad[m].bind(m, fn)


instance(Monad, List).where(
    bind = lambda x, fn: L[itertools.chain.from_iterable(fmap(fn, x))]
)
