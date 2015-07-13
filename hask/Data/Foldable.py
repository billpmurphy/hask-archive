import functools
import operator

from ..lang import sig
from ..lang import H
from ..lang import t
from ..lang import Typeclass
from ..lang import build_instance
from ..lang import List
from ..lang import Ord

from Num import Num


class Foldable(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, foldr):
        build_instance(Foldable, cls, {"foldr":foldr})
        return
