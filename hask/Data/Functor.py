from ..lang.type_system import Typeclass
from ..lang.type_system import is_builtin
from ..lang.type_system import build_instance
from ..lang.syntax import H
from ..lang.syntax import sig
from ..lang.syntax import t


class Functor(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, fmap):
        if not is_builtin(cls):
            cls.__mul__ = fmap
        build_instance(Functor, cls, {"fmap":fmap})
        return


@sig(H[(Functor, "f")]/ (H/ "a" >> "b") >> t("f", "a") >> t("f", "b"))
def fmap(f, x):
    return Functor[x].fmap(f, x)
