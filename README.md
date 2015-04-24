[![Build Status](https://magnum.travis-ci.com/billpmurphy/pythaskell.svg?token=ReCFhAz7SQAeN6Fi4dBx&branch=master)](https://magnum.travis-ci.com/billpmurphy/pythaskell)

# Hask

Wish you could use all those elegant Haskell features in Python? All you have
to do is `import hask`!

Hask is a pure-Python library that mimics most of the core language tools from
Haskell, including:

* Python port of Haskell's type system that supports type checking, function
  type signatures, algebraic data types, and typeclasses
* Easy creation of new algebraic datatypes and typeclasses
* Pattern matching
* Automagical function currying/partial application
* Typeclasses from the Haskell `base` libraries, including `Functor`, `Monad`,
  and all the rest
* Algebraic datatypes from the Haskell `Prelude`, including `Maybe` and `Either`
* Efficient, lazily evaluated lists with Haskell-style list comprehensions
* Easier function composition and application, operator sections, guards, and
  other nifty control flow tools
* Full Python port of (some of) the standard libraries from Haskell's `base`,
  including `Prelude`, `Control.Monad`, `Data.List`, and many more


## Installation

Just `git clone https://github.com/billpmurphy/hask` and then
`python setup.py install`.

To run the tests, just `python tests.py`.


## Introduction


```python
>>> from hask import data, d, deriving
>>> from hask import Read, Show, Eq, Ord

>>> Maybe, Nothing, Just = data("Maybe", "a") == "Nothing" | d("Just", "a") \
                            & deriving(Read, Show, Eq, Ord)
```

```python
>>> Nothing
Nothing

>>> Just(10)
Just(10)
```

You can view the type of an object with `_t` (equivalent to `:t` in ghci).

```python
>>> from hask import _t

>>> \_t(Just("soylent green")
Maybe str

>>> \_t(1)
int
```


Functors can be used with the infix `fmap` operator, `*`:

```python
>>> Just("hello") * (lambda x: x.upper()) * (lambda x: x + "!")
Just(HELLO!)
```

If we have an instance of `Functor`, we can make it an instance of
`Applicative` and then an instance of `Monad` by defining the appropriate
methods.

```python
>>> from hask import Applicative, Monad

>>> Applicative(Maybe, lambda x: Just(x))
>>> Monad(Maybe, ...)
```

Of course, `bind` also has an infix form, which is `>>` in Hask.

```python
>>> Just(3) >> (lambda x: Nothing if x > 5 else Just(x + 5))
Just(8)

```

We also have operator sections:

```python
>>> from hask import __

>>> f = (__ - 20) * (2 ** __) * (__ + 3)
>>> f(10)
8172
```


If you don't need the full power of pattern matching and just want a neater
switch statement, you can use guards, which also happen to play nicely with
sections.

```python
>>> from hask import guard, c, otherwise

>>> porridge_tempurature = 80

>>> ~(guard(porridge_tempurature)
...     | c(__ < 20)  >> "Porridge is too cold!"
...     | c(__ < 90)  >> "Porridge is just right!"
...     | c(__ < 150) >> "Porridge is too hot!"
...     | otherwise() >> "Porridge has gone thermonuclear"
... )
'Porridge is just right!'
```

If no match is found (and an `otherwise()` clause is not present), a
`NoGuardMatchException` will be raised. For more complex guards, you can also
use lambdas or functions in your guard conditions.

```python
>>> def examine_password_security(password):
...     analysis = ~(guard(password)
...         | c(lambda x: len(x) > 20) >> "Wow, that's one secure password"
...         | c(lambda x: len(x) < 5)  >> "You made Bruce Schneier cry"
...         | c(__ == "12345")         >> "Same combination as my luggage!"
...         | otherwise()              >> "Hope it's not `password`"
...     )
...     return analysis
...

>>> nuclear_launch_code = "12345"

>>> examine_password_security(nuclear_lanch_code)
'Same combination as my luggage!'
```

All of your favorite functions from `Prelude`, `Data.List`, `Data.Maybe`, `Data.Either`, `Data.String`, `Data.Tuple`, and `Control.Monad` are implemented too.


```python
```

-------------------------------------------


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


More notes:

`import hask` should give you everything in the language (including all
typeclasses) plus everything in the Prelude. Therefore, you can do `hask.map`
but not `hask.permutations`. To import things in the Base libraries that are
not also in the Prelude, use `from hask import Data` and then
`Data.List.permutations`.


Add more corner case tests for LazyList indexing.


Haskell API status table

| Haskell Feature        | Pythaskell Name | Status |
| :--------------------- | :-------------- | :----: |
| *Syntax*               |                 |        |
| type signatures        | sig             | part   |
| pattern matching (case)| caseof          | idea   |
| data (defining ADTs)   | data            | part   |
| type (type synonym)    |                 | ?      |
| newtype (type wrapper) |                 | nix    |
| list comprehensions    | L (see below)   | part   |
| slicing (e.g. `(+1)`)  | `(__+1)`        |        |
| guards                 | guard           | good   |
| *Typeclasses*          |                 |        |
| Show                   | Show            | good   |
| &nbsp;&nbsp;show       | &nbsp;&nbsp;show|        |
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
