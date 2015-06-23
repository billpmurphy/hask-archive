from ..lang import Typeclass
from ..lang import build_instance
from ..lang import List


class Foldable(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, foldr):
        build_instance(Foldable, cls, {"foldr":foldr})
        return
