__version__ = "0.0.1"

# Core language

## Standard Hask typeclasses and associated functions
from hask.lang.type_system import in_typeclass
from hask.lang.type_system import Typeclass
from hask.lang.type_system import Hask
from hask.lang.typeclasses import Read
from hask.lang.typeclasses import Show
from hask.lang.typeclasses import Eq
from hask.lang.typeclasses import Ord
from hask.lang.typeclasses import Bounded
from hask.lang.typeclasses import Num
from hask.lang.typeclasses import Fractional
from hask.lang.typeclasses import Floating
from hask.lang.typeclasses import Real
from hask.lang.typeclasses import RealFrac
from hask.lang.typeclasses import RealFloat
from hask.lang.typeclasses import Enum
from hask.lang.typeclasses import Functor
from hask.lang.typeclasses import Applicative
from hask.lang.typeclasses import Monad
from hask.lang.typeclasses import Traversable
from hask.lang.typeclasses import Foldable
from hask.lang.typeclasses import Iterator
from hask.lang.typeclasses import succ
from hask.lang.typeclasses import pred
from hask.lang.typeclasses import toEnum
from hask.lang.typeclasses import fromEnum
from hask.lang.typeclasses import enumFrom
from hask.lang.typeclasses import enumFromThen
from hask.lang.typeclasses import enumFromTo
from hask.lang.typeclasses import enumFromThenTo
from hask.lang.typeclasses import fmap
from hask.lang.typeclasses import foldr
from hask.lang.typeclasses import length
from hask.lang.typeclasses import mempty
from hask.lang.typeclasses import mappend

# TODO: deprecate
from hask.lang.hof import const
from hask.lang.hof import flip
from hask.lang.hof import id
from hask.lang.hof import F
from hask.lang.hof import Func

## Builtin types (Python builtins + Hask builtins)
from hask.lang.builtins import List
from hask.lang.builtins import Maybe
from hask.lang.builtins import Just
from hask.lang.builtins import Nothing
from hask.lang.builtins import in_maybe
from hask.lang.builtins import Either
from hask.lang.builtins import Left
from hask.lang.builtins import Right
from hask.lang.builtins import in_either
from hask.lang.builtins import Ordering
from hask.lang.builtins import LT
from hask.lang.builtins import EQ
from hask.lang.builtins import GT

## REPL tools
from hask.lang.builtins import _t
from hask.lang.builtins import _i
from hask.lang.builtins import _q


# Syntax

## Operator sections
from hask.lang.syntax import __

## Guard expressions
from hask.lang.syntax import guard
from hask.lang.syntax import c
from hask.lang.syntax import otherwise
from hask.lang.syntax import NoGuardMatchException

## Lists/list comprehensions
from hask.lang.syntax import L

## ADT creation
from hask.lang.syntax import data
from hask.lang.syntax import d
from hask.lang.syntax import deriving

## Type signatures
from hask.lang.syntax import sig
from hask.lang.syntax import H
from hask.lang.syntax import t

## Pattern matching
from hask.lang.caseof import caseof


# Haskell base
from Prelude import map
from Prelude import filter
from Prelude import read
from Prelude import show
