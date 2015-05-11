__version__ = "0.0.1"

# Core language
from hask.lang.type_system import in_typeclass
from hask.lang.type_system import typ
from hask.lang.type_system import _t
from hask.lang.type_system import H
from hask.lang.type_system import arity
from hask.lang.type_system import sig
from hask.lang.type_system import sig2
from hask.lang.type_system import Typeable
from hask.lang.type_system import Typeclass

from hask.lang.typeclasses import Read
from hask.lang.typeclasses import Show
from hask.lang.typeclasses import Eq
from hask.lang.typeclasses import Ord
from hask.lang.typeclasses import Bounded
from hask.lang.typeclasses import Num
from hask.lang.typeclasses import Enum
from hask.lang.typeclasses import Functor
from hask.lang.typeclasses import Applicative
from hask.lang.typeclasses import Monad
from hask.lang.typeclasses import Traversable
from hask.lang.typeclasses import Ix
from hask.lang.typeclasses import Foldable
from hask.lang.typeclasses import Iterator

read = Read.read
show = Show.show
succ = Enum.succ
pred = Enum.pred
toEnum = Enum.toEnum
fromEnum = Enum.fromEnum
enumFrom = Enum.enumFrom
enumFromThen = Enum.enumFromThen
enumFromTo = Enum.enumFromTo
enumFromThenTo = Enum.enumFromThenTo
fmap = Functor.fmap
foldr = Foldable.foldr
length = Ix.length

from hask.lang.hof import const
from hask.lang.hof import flip
from hask.lang.hof import id
from hask.lang.hof import F
from hask.lang.hof import Func

from hask.lang.builtins import Int
from hask.lang.builtins import Float
from hask.lang.builtins import String
from hask.lang.builtins import List
from hask.lang.builtins import Maybe
from hask.lang.builtins import Just
from hask.lang.builtins import Nothing
from hask.lang.builtins import in_maybe
from hask.lang.builtins import Either
from hask.lang.builtins import Left
from hask.lang.builtins import Right
from hask.lang.builtins import in_either

from hask.lang.syntax import __
from hask.lang.syntax import guard
from hask.lang.syntax import c
from hask.lang.syntax import otherwise
from hask.lang.syntax import NoGuardMatchException
from hask.lang.syntax import L

from hask.lang.caseof import caseof

from hask.lang.adt import data
from hask.lang.adt import d
from hask.lang.adt import deriving


# Haskell base
from base import Control
from base import Data
from base import Prelude

from base.prelude import map
from base.prelude import filter
