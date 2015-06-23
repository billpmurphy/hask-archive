from ..lang import build_instance
from ..lang import List
from ..lang import instance
from ..Data.Functor import Functor


class Applicative(Functor):
    @classmethod
    def make_instance(self, cls, pure):
        build_instance(Applicative, cls, {"pure":pure})
        return


instance(Applicative, List).where(
    pure = List.pure
)
