__version__ = "0.0.1"

# Core language

## Standard Hask typeclasses and associated functions
from hask.lang import typeof
from hask.lang import has_instance
from hask.lang import Typeclass
from hask.lang import Hask
from hask.Prelude import Read
from hask.Prelude import Show
from hask.Prelude import Eq
from hask.Prelude import Ord
from hask.Prelude import Bounded
from hask.Prelude import Num
from hask.Prelude import Fractional
from hask.Prelude import Floating
from hask.Prelude import Real
from hask.Prelude import RealFrac
from hask.Prelude import RealFloat
from hask.Prelude import Enum
from hask.Prelude import Functor
from hask.Prelude import Applicative
from hask.Prelude import Monad
from hask.Prelude import Traversable
from hask.Prelude import Foldable
from hask.Prelude import succ
from hask.Prelude import pred
from hask.Prelude import toEnum
from hask.Prelude import fromEnum
from hask.Prelude import enumFrom
from hask.Prelude import enumFromThen
from hask.Prelude import enumFromTo
from hask.Prelude import enumFromThenTo
#from hask.Prelude import foldr
#from hask.Prelude import length

## Builtin types (Python builtins + Hask builtins)
from hask.lang import List
from hask.Prelude import Maybe
from hask.Prelude import Just
from hask.Prelude import Nothing
from hask.Prelude import in_maybe
from hask.Prelude import Either
from hask.Prelude import Left
from hask.Prelude import Right
from hask.Prelude import in_either
from hask.Prelude import Ordering
from hask.Prelude import LT
from hask.Prelude import EQ
from hask.Prelude import GT
from hask.Prelude import fmap


# Core language

## Typeclass instance declaration
from hask.lang import instance

## Operator sections
from hask.lang import __

## Guard expressions
from hask.lang import guard
from hask.lang import c
from hask.lang import otherwise
from hask.lang import NoGuardMatchException

## Lists/list comprehensions
from hask.lang import L

## ADT creation
from hask.lang import data
from hask.lang import d
from hask.lang import deriving

## Type signatures
from hask.lang import sig
from hask.lang import H
from hask.lang import t

## Pattern matching
from hask.lang import caseof
from hask.lang import p
from hask.lang import m
from hask.lang import w
from hask.lang import IncompletePatternError

## REPL tools
from hask.lang import _t
from hask.lang import _i
from hask.lang import _q


# Haskell base
#from Prelude import map
#from Prelude import filter
#from Prelude import read
#from Prelude import show
