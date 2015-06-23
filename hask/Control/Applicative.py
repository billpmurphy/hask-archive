from ..lang.typeclasses import build_instance
from ..Data.Functor import Functor

class Applicative(Functor):
    @classmethod
    def make_instance(self, cls, pure):
        build_instance(Applicative, cls, {"pure":pure})
        return
