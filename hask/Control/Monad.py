from ..lang.typeclasses import build_instance
from ..lang.typeclasses import is_builtin
from Applicative import Applicative

class Monad(Applicative):
    @classmethod
    def make_instance(typeclass, cls, bind):
        build_instance(Monad, cls, {"bind":bind})
        if not is_builtin(cls):
            cls.__rshift__ = bind
        return

