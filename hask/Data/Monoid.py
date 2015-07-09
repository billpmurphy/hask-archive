from ..lang import Typeclass
from ..lang import build_instance
from ..lang import H
from ..lang import sig


class Monoid(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, mempty, mappend, mconcat=None):
        #TODO: mconcat
        attrs = {"mempty":mempty, "mappend":mappend, "mconcat":mconcat}
        build_instance(Monoid, cls, attrs)
        return


@sig(H/ "a" >> "a" >> "a")
def mappend(x, y):
    return Monoid[x].mappend(x, y)


@sig(H[(Monoid, "m")]/ ["m"] >> "m")
def mconcat(m):
    return Monoid[x].mconcat(xs)
