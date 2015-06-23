from ..lang.type_system import Typeclass
from ..lang.type_system import build_instance
from ..lang.syntax import H
from ..lang.syntax import sig


class Monoid(Typeclass):
    @classmethod
    def make_instance(typeclass, cls, mempty, mappend, mconcat=None):
        #TODO: mconcat
        attrs = {"mempty":mempty, "mappend":mappend}
        build_instance(Monoid, cls, attrs)
        return


@sig(H/ "a" >> "a" >> "a")
def mappend(x, y):
    Monoid[x].mappend(x, y)


#@sig(H/ "a")
#def mempty():
#    return Monoid[x].mempty
