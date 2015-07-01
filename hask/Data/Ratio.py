from ..lang import sig
from ..lang import H
from ..lang import t

Ratio, R =\
        data.Ratio("a") == d.R("a", "a") & deriving(Eq)

Rational = t(Ratio, int)
