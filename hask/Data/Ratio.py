import fractions

from ..lang import sig
from ..lang import H
from ..lang import t


# Current implementation is just a wrapper around Python's Fraction. This is
# not a long-term solution (not extensible beyond builtin types) but it will do
# for now.

from Num import Integral
from Num import Ratio
from Num import R
from Num import Rational
from Num import toRatio
from Num import toRational


@sig(H[(Integral, "a")]/ t(Ratio, "a") >> "a")
def numerator(ratio):
    return toRatio(ratio[0], ratio[1])[0]


@sig(H[(Integral, "a")]/ t(Ratio, "a") >> "a")
def denominator(ratio):
    return toRatio(ratio[0], ratio[1])[1]
