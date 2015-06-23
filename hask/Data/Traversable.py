from ..lang import build_instance
from Foldable import Foldable
from Functor import Functor


class Traversable(Foldable, Functor):
    @classmethod
    def make_instance(typeclass, cls, iter, getitem=None, len=None):
        def default_len(self):
            count = 0
            for _ in iter(self):
                count += 1
            return count

        def default_getitem(self, i):
            return list(iter(self))[i]

        len = default_len if len is None else len
        getitem = default_getitem if getitem is None else getitem

        attrs = {"iter":iter, "getitem":getitem, "len":len}
        build_instance(Traversable, cls, attrs)
        return

    @staticmethod
    def length(a):
        return len(a)
