[![Build Status](https://magnum.travis-ci.com/billpmurphy/pythaskell.svg?token=ReCFhAz7SQAeN6Fi4dBx&branch=master)](https://magnum.travis-ci.com/billpmurphy/pythaskell)


***Notes y'all***

This is still in "throw everything at the wall" phase. Goal here is to push the
boundaries as far as physically possible, to get as close to Haskell as Python
can go, then strip out all the hideous hacks and see if there's an actually
useful Haskell-features-and-syntax-that-aren't-ugly-in-Python kinda library in
there.

What needs work:
* the type system. this is #1 priority. need to design datatypes to represent
  higher-kinded types, type signatures, and do some basic typechecking to get
  things rolling, just to make sure no redesign of typeclasses is needed
* the LazyList - tests are failing, figure out why and fix it. Also, do some
  profiling and improve efficiency of some operations *(yo max you got this)*
* HOF - needs more work, coming along though
* ADTs - work on this after type system is built out
* pattern matching (case of) - is there a better way of handling local binidng
  that horrid global state? in general, need to clean this filth up
* immutable data strucures - again look at fn.py, but I think we can do better
  here.
* laziness everywhere - can generators/coroutines-made-from-generators do this?
* immutable variables - can we mess with `globals()` to prevent regular
  assignment? or use coroutines somehow?
* pattern matching in regular assignment
* other monads/functors
* tail call optimization - again, read fn.py's decorator
* port more Haskell standard libraries (probably want to wait for later to do
  this)
* arrows


Key features of Haskell I am forgetting:
* ???????


Haskell API status table

| Haskell Feature        | Pythaskell Name | Status |
| :--------------------- | :-------------- | :----: |
| *Syntax*               |                 |        |
| type signatures        | sig             | part   |
| guards                 | guard           | good   |
| pattern matching (case)| caseof          | idea   |
| data (defining ADTs)   | data            | part   |
| type (type synonym)    |                 | ?      |
| newtype (type wrapper) |                 | nix    |
| list comprehensions    | L (see below)   | part   |
| *Typeclasses*          |                 |        |
| Show                   | Show            | good   |
|   show                 |   show          |        |
| Read                   |                 | ?      |
| Eq                     | Eq              | good   |
| Ord                    | Ord             | good   |
| Enum                   | Enum            |        |
| Bounded                | Bounded         |        |
| Num                    | Num             | part   |
| Integral               |                 | ?      |
| Fractional             |                 | ?      |
| Floating               |                 | ?      |
| RealFloat              |                 | ?      |
| Real                   |                 | ?      |
| RealFrac               |                 | ?      |
| Functor                | Functor         | good   |
|   fmap                 |   fmap          | good   |
| Applicative            | Applicative     | good   |
|   pure                 |   pure          | good   |
| Monad                  | Monad           | good   |
|   >>=                  | >> / bind       | good   |
| Foldable               | Foldable        |        |
| Traversable            | Traversable     | good   |
| Ix                     | Ix              | good   |
|                        | _Iterator_      | good   |
| *Prelude*              |                 |        |
|                        |                 |        |
| *Control.Applicative*  |                 |        |
|                        |                 |        |
| *Control.Monad*        |                 |        |
| >>=                    | >>              | good   |
| >>                     |                 | ?      |
| return                 | pure            | import |
| fail                   |                 |        |
| MonadPlus              |                 |        |
|   mzero                |                 |        |
|   mplus                |                 |        |
| mapM                   |                 |        |
| mapM\_                 |                 |        |
| forM                   |                 |        |
| forM\_                 |                 |        |
| sequence               |                 |        |
| sequence\_             |                 |        |
| =<<                    |                 |        |
| >=>                    |                 |        |
| forever                |                 |        |
| void                   |                 |        |
| join                   |                 |        |
| msum                   |                 |        |
| mfilter                |                 |        |
| filterM                |                 |        |
| mapAndUnzipM           |                 |        |
| zipWithM               |                 |        |
| zipWithM\_             |                 |        |
| foldM                  |                 |        |
| foldM\_                |                 |        |
| replicateM             |                 |        |
| replicateM\_           |                 |        |
| guard                  |                 |        |
| when                   |                 |        |
| unless                 |                 |        |
| liftM                  |                 |        |
| liftM2 .. liftM5       |                 |        |
| ap                     |                 |        |
| <\$!>                  |                 |        |
| *Data.Either*          |                 |        |
| Either                 | Either          |        |
| Left a                 | Left(a)         |        |
| Right a                | Right(a)        |        |
| either                 |                 |        |
| lefts                  |                 |        |
| rights                 |                 |        |
| isLeft                 |                 |        |
| isRight                |                 |        |
| partitionEithers       |                 |        |
| *Data.List*            |                 |        |
| ++                     |                 |        |
| head                   |                 |        |
| last                   |                 |        |
| tail                   |                 |        |
| init                   |                 |        |
| uncons                 |                 |        |
| null                   |                 |        |
| length                 |                 |        |
| map                    |                 |        |
| reverse                |                 |        |
| intersperse            |                 |        |
| intercalate            |                 |        |
| transpose              |                 |        |
| subsequences           |                 |        |
| permutations           |                 |        |
| foldl                  |                 |        |
| foldl'                 |                 |        |
| foldl1                 |                 |        |
| foldr                  |                 |        |
| foldr1                 |                 |        |
| concat                 |                 |        |
| and                    |                 |        |
| or                     |                 |        |
| any                    |                 |        |
| all                    |                 |        |
| sum                    |                 |        |
| product                |                 |        |
| maximum                |                 |        |
| minimum                |                 |        |
| scanl                  |                 |        |
| scanl'                 |                 |        |
| scanl1                 |                 |        |
| scanr                  |                 |        |
| scanr1                 |                 |        |
| mapAccumL              |                 |        |
| mapAccumR              |                 |        |
| iterate                |                 |        |
| repeat                 |                 |        |
| replicate              |                 |        |
| cycle                  |                 |        |
| unfoldr                |                 |        |
| take                   |                 |        |
| drop                   |                 |        |
| splitAt                |                 |        |
| takeWhile              |                 |        |
| dropWhile              |                 |        |
| dropWhileEnd           |                 |        |
| span                   |                 |        |
| break                  |                 |        |
| stripPrefix            |                 |        |
| group                  |                 |        |
| inits                  |                 |        |
| tails                  |                 |        |
| isPrefixOf             |                 |        |
| isSuffixOf             |                 |        |
| isInfixOf              |                 |        |
| isSubsequenceOf        |                 |        |
| elem                   |                 |        |
| notElem                |                 |        |
| lookup                 |                 |        |
| find                   |                 |        |
| filter                 |                 |        |
| partition              |                 |        |
| !!                     |                 | python |
| elemIndex              |                 |        |
| elemIndicies           |                 |        |
| findIndex              |                 |        |
| findIndicies           |                 |        |
| zip                    |                 |        |
| zip3 .. zip7           |                 |        |
| zipWith                |                 |        |
| zipWith3 .. zipWith7   |                 |        |
| unzip                  |                 |        |
| unzip3 .. unzip7       |                 |        |
| lines                  | lines           | import |
| words                  | words           | import |
| unlines                | unlines         | import |
| unwords                | unwords         | import |
| nub                    |                 |        |
| delete                 |                 |        |
| \\\\                   |                 |        |
| union                  |                 |        |
| intersect              |                 |        |
| sort                   |                 |        |
| sortOn                 |                 |        |
| insert                 |                 |        |
| nubBy                  |                 |        |
| deleteBy               |                 |        |
| deleteFirstBy          |                 |        |
| unionBy                |                 |        |
| intersectBy            |                 |        |
| groupBy                |                 |        |
| sortBy                 |                 |        |
| insertBy               |                 |        |
| maximumBy              |                 |        |
| minimumBy              |                 |        |
| genericLength          |                 | nix    |
| genericTake            |                 | nix    |
| genericDrop            |                 | nix    |
| genericSplitAt         |                 | nix    |
| genericIndex           |                 | nix    |
| genericReplicate       |                 | nix    |
| *Data.Maybe*           |                 |        |
| Maybe                  | Maybe           | import |
| Nothing                | Nothing         | import |
| Just a                 | Just(a)         | import |
| maybe                  | maybe           |        |
| isJust                 | isJust          |        |
| isNothing              | isNothing       |        |
| fromJust               | fromJust        |        |
| fromMaybe              | fromMaybe       |        |
| listToMaybe            | listToMaybe     |        |
| maybeToList            | maybeToList     |        |
| catMaybes              | catMaybes       |        |
| mapMaybe               | mapMaybe        |        |
| *Data.String*          |                 |        |
| lines                  | lines           |        |
| words                  | words           |        |
| unlines                | unlines         |        |
| unwords                | unwords         |        |
| *Data.Tuple*           |                 |        |
| fst                    | fst             |        |
| snd                    | snd             |        |
| curry                  | curry           |        |
| uncurry                | uncurry         |        |
| swap                   | swap            |        |
