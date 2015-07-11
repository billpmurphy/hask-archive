import itertools

from ..lang import H
from ..lang import t
from ..lang import build_instance
from ..lang import is_builtin
from ..lang import List
from ..lang import instance
from ..Data.Functor import fmap
from Applicative import Applicative


class Monad(Applicative):

    @classmethod
    def make_instance(typeclass, cls, bind):
        #bind = bind ** (H[(Monad, "m")]/ t("m", "a") >> (H/ "a" >> t("m", "b")) >> t("m", "b"))
        build_instance(Monad, cls, {"bind":bind})
        if not is_builtin(cls):
            cls.__rshift__ = bind
        return


instance(Monad, List).where(
    bind = lambda fn, x: L[itertools.chain.from_iterable(fmap(fn, x))]
)
