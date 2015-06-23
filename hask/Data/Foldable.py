from ..lang.type_system import Typeclass
from ..lang.type_system import build_instance


class Foldable(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, foldr):
        build_instance(Foldable, cls, {"foldr":foldr})
        return
