from ..lang import build_instance
from ..Control.Applicative import Applicative
from ..Control.Monad import Monad
from Foldable import Foldable
from Functor import Functor


class Traversable(Foldable, Functor):
    @classmethod
    def make_instance(typeclass, cls, traverse, sequenceA=None, mapM=None,
                      sequence=None):
        attrs = {"traverse":traverse, "sequenceA":sequenceA, "mapM":mapM,
                 "sequence":sequence}
        build_instance(Traversable, cls, attrs)
        return
