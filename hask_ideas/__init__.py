__version__ = "0.0.1"


#=============================================================================#
# Module imports


import lang
import Data.Char
import Data.Either
import Data.Eq
import Data.Foldable
import Data.Functor
import Data.List
import Data.Maybe
import Data.Monoid
import Data.Num
import Data.Ord
import Data.Ratio
import Data.String
import Data.Traversable
import Data.Tuple
import Control.Applicative
import Control.Monad
import Python.builtins


#=============================================================================#
# Core language

## Typeclass instance declaration
from lang import instance

## Operator sections
from lang import __

## Guard expressions
from lang import guard
from lang import c
from lang import otherwise
from lang import NoGuardMatchException

## Lists/list comprehensions
from lang import L

## ADT creation
from lang import data
from lang import d
from lang import deriving

## Type signatures
from lang import sig
from lang import H
from lang import t
from lang import func
from lang import TypeSignatureError

## Pattern matching
from lang import caseof
from lang import p
from lang import m
from lang import IncompletePatternError

## REPL tools
from lang import _t
from lang import _i
from lang import _q

## Type system/typeclasses
from lang import typeof
from lang import has_instance
from lang import Typeclass
from lang import Hask


#=============================================================================#
# Other imports

# Basic Typeclasses
from Prelude import Read
from Prelude import Show
from Prelude import Eq
from Prelude import Ord
from Prelude import Enum
from Prelude import Bounded
from Prelude import Num
from Prelude import Real
from Prelude import Integral
from Prelude import Fractional
from Prelude import Floating
from Prelude import RealFrac
from Prelude import RealFloat
from Prelude import Functor
from Prelude import Applicative
from Prelude import Monad
from Prelude import Traversable
from Prelude import Foldable


# Standard types
from Prelude import Maybe
from Prelude import Just
from Prelude import Nothing
from Prelude import in_maybe

from Prelude import Either
from Prelude import Left
from Prelude import Right
from Prelude import in_either

from Prelude import Ordering
from Prelude import LT
from Prelude import EQ
from Prelude import GT
